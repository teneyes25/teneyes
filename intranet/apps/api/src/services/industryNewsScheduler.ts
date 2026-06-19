import cron, { type ScheduledTask } from "node-cron";
import Parser from "rss-parser";
import { config } from "../config.js";
import { query } from "../db/pool.js";
import { summarizeForCardNews } from "./ai.js";

type NewsItem = {
  title: string;
  link: string;
  published?: string;
  summarySource: string;
  matchedKeywords: string[];
  score: number;
  scoreReasons: string[];
};

export type IndustryNewsRunResult = {
  status: "uploaded" | "skipped";
  trigger: "cron" | "manual";
  item?: {
    id: string;
    title: string;
    link: string;
    summaryProvider: "ai" | "fallback";
  };
  reason?: string;
  ranAt: string;
};

const parser = new Parser();
let task: ScheduledTask | undefined;
let lastRun: IndustryNewsRunResult | undefined;

function textFromHtml(value = "") {
  return value
    .replace(/<[^>]*>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, "\"")
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

function fallbackSummary(item: NewsItem) {
  const source = textFromHtml(item.summarySource).slice(0, 500);
  return [
    `핵심 요약: ${item.title}`,
    source ? `상세 내용: ${source}` : undefined,
    `업계 영향: ${item.matchedKeywords.join(", ")} 관련 시장 동향과 경쟁 환경 변화를 확인할 필요가 있습니다.`,
    "검토 포인트: 상품기획, 영업, 대리점 커뮤니케이션 관점에서 가격, 소재, 시즌 프로모션 영향을 점검하세요."
  ].filter(Boolean).join("\n");
}

function isLowQualitySummary(summary: string) {
  const text = summary.trim();
  if (text.length < 40) return true;
  if (text.includes("사내 인트라넷 카드뉴스") || text.includes("형식:") || text.includes("제목:")) return true;
  const koreanCharacters = text.match(/[가-힣]/g)?.length ?? 0;
  return koreanCharacters < Math.max(12, text.length * 0.12);
}

export function buildIndustryNewsBody(item: NewsItem, summary: string, summaryProvider: "ai" | "fallback") {
  return [
    summary,
    "",
    "---",
    `출처: ${item.link}`,
    item.published ? `게시일: ${item.published}` : undefined,
    `선정 키워드: ${item.matchedKeywords.join(", ") || "없음"}`,
    `중요도 점수: ${item.score}`,
    `선정 근거: ${item.scoreReasons.join(", ")}`,
    `요약 방식: ${summaryProvider === "ai" ? "Maejong AI" : "RSS 원문 기반 fallback"}`
  ].filter(Boolean).join("\n");
}

async function summarizeItem(item: NewsItem) {
  const prompt = [
    "다음 침구/수면/홈패브릭 업계뉴스 1건을 사내 인트라넷 카드뉴스로 올릴 수 있게 한국어로 요약해 주세요.",
    "형식: 핵심 요약 2문장, 업계 영향 1문장, 검토 포인트 1문장.",
    `제목: ${item.title}`,
    `본문/설명: ${textFromHtml(item.summarySource)}`,
    `선정 키워드: ${item.matchedKeywords.join(", ")}`,
    `중요도 점수/근거: ${item.score} (${item.scoreReasons.join(", ")})`,
    `링크: ${item.link}`
  ].join("\n");

  try {
    const summary = await summarizeForCardNews(prompt);
    if (summary.trim() && !isLowQualitySummary(summary)) {
      return { summary: summary.trim(), provider: "ai" as const };
    }
  } catch (error) {
    console.warn("Industry news AI summary failed; using fallback.", error);
  }

  return { summary: fallbackSummary(item), provider: "fallback" as const };
}

function industryKeywords() {
  return config.INDUSTRY_NEWS_KEYWORDS.split(",").map((keyword) => keyword.trim()).filter(Boolean);
}

function rssUrlForKeyword(keyword: string) {
  if (config.INDUSTRY_NEWS_RSS_URL) {
    return config.INDUSTRY_NEWS_RSS_URL;
  }

  const query = encodeURIComponent(`${keyword} 침구 OR 매트리스 OR 이불 OR 베개 when:1d`);
  return `https://news.google.com/rss/search?q=${query}&hl=ko&gl=KR&ceid=KR:ko`;
}

function commercialSignalScore(text: string) {
  const signals = ["출시", "신제품", "광고", "판매", "매출", "인기", "시장", "브랜드", "프로모션", "할인", "체험", "캠페인", "홈쇼핑"];
  return signals.filter((signal) => text.includes(signal)).length;
}

function recencyScore(published?: string) {
  if (!published) {
    return 0;
  }

  const ageHours = (Date.now() - new Date(published).getTime()) / (1000 * 60 * 60);
  if (Number.isNaN(ageHours)) {
    return 0;
  }

  if (ageHours <= 24) return 5;
  if (ageHours <= 72) return 3;
  if (ageHours <= 168) return 1;
  return 0;
}

function scoreCandidate(item: Omit<NewsItem, "matchedKeywords" | "score" | "scoreReasons">, exposureCount: number) {
  const keywords = industryKeywords();
  const text = `${item.title} ${textFromHtml(item.summarySource)}`;
  const matchedKeywords = keywords.filter((keyword) => text.includes(keyword));
  const keywordScore = matchedKeywords.length * 8;
  const exposureScore = Math.min(exposureCount, 5) * 5;
  const signalScore = commercialSignalScore(text) * 3;
  const recentScore = recencyScore(item.published);
  const score = keywordScore + exposureScore + signalScore + recentScore;
  const scoreReasons = [
    matchedKeywords.length ? `키워드 ${matchedKeywords.length}개 일치` : "키워드 직접 일치 없음",
    `노출 빈도 ${exposureCount}회`,
    `상업/광고 신호 ${signalScore / 3}개`,
    recentScore ? `최신성 +${recentScore}` : "최신성 점수 없음"
  ];

  return {
    ...item,
    matchedKeywords,
    score,
    scoreReasons
  };
}

async function fetchCandidates() {
  const seen = new Map<string, Omit<NewsItem, "matchedKeywords" | "score" | "scoreReasons"> & { exposureCount: number }>();
  const keywords = industryKeywords();

  for (const keyword of keywords) {
    const feed = await parser.parseURL(rssUrlForKeyword(keyword));
    for (const item of feed.items.slice(0, 10)) {
      const link = item.link ?? item.guid ?? "";
      const title = textFromHtml(item.title ?? "제목 없음");
      if (!title || !link) {
        continue;
      }

      const current = seen.get(link);
      if (current) {
        current.exposureCount += 1;
        continue;
      }

      seen.set(link, {
        title,
        link,
        published: item.pubDate ?? item.isoDate,
        summarySource: item.contentSnippet ?? item.content ?? item.summary ?? "",
        exposureCount: 1
      });
    }
  }

  return [...seen.values()]
    .map(({ exposureCount, ...item }) => scoreCandidate(item, exposureCount))
    .filter((item) => item.matchedKeywords.length > 0)
    .sort((left, right) => right.score - left.score)
    .slice(0, config.INDUSTRY_NEWS_MAX_CANDIDATES);
}

async function isAlreadyUploaded(item: NewsItem) {
  const { rows } = await query(
    `select id
     from module_items
     where module_key = 'industry-news'
       and (title = $1 or position($2 in body) > 0)
     limit 1`,
    [item.title, item.link]
  );

  return rows.length > 0;
}

export async function runIndustryNewsScheduler(trigger: "cron" | "manual" = "manual") {
  const candidates = await fetchCandidates();

  for (const item of candidates) {
    if (await isAlreadyUploaded(item)) {
      continue;
    }

    const { summary, provider } = await summarizeItem(item);
    const body = buildIndustryNewsBody(item, summary, provider);
    const { rows } = await query<{ id: string; title: string }>(
      `insert into module_items (module_key, title, body, tags, status, author_id)
       values ('industry-news', $1, $2, $3, 'published', 'scheduler:industry-news')
       returning id, title`,
      [item.title, body, ["industry-news", "scheduled", provider]]
    );

    lastRun = {
      status: "uploaded",
      trigger,
      item: {
        id: rows[0].id,
        title: rows[0].title,
        link: item.link,
        summaryProvider: provider
      },
      ranAt: new Date().toISOString()
    };
    return lastRun;
  }

  lastRun = {
    status: "skipped",
    trigger,
    reason: "새로 업로드할 업계뉴스 후보가 없습니다.",
    ranAt: new Date().toISOString()
  };
  return lastRun;
}

export function startIndustryNewsScheduler() {
  if (!config.INDUSTRY_NEWS_SCHEDULER_ENABLED) {
    console.log("Industry news scheduler disabled.");
    return;
  }

  if (!cron.validate(config.INDUSTRY_NEWS_CRON)) {
    throw new Error(`Invalid INDUSTRY_NEWS_CRON: ${config.INDUSTRY_NEWS_CRON}`);
  }

  task?.stop();
  task = cron.schedule(
    config.INDUSTRY_NEWS_CRON,
    () => {
      void runIndustryNewsScheduler("cron").catch((error) => {
        console.error("Industry news scheduler failed.", error);
      });
    },
    { timezone: config.INDUSTRY_NEWS_TIMEZONE }
  );

  console.log(`Industry news scheduler started: ${config.INDUSTRY_NEWS_CRON} (${config.INDUSTRY_NEWS_TIMEZONE})`);
}

export function getIndustryNewsSchedulerStatus() {
  return {
    enabled: config.INDUSTRY_NEWS_SCHEDULER_ENABLED,
    cron: config.INDUSTRY_NEWS_CRON,
    timezone: config.INDUSTRY_NEWS_TIMEZONE,
    rssUrl: config.INDUSTRY_NEWS_RSS_URL,
    running: Boolean(task),
    lastRun
  };
}
