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
    `핵심 요약: ${source || item.title}`,
    "업계 영향: 관련 시장 동향과 경쟁 환경 변화를 확인할 필요가 있습니다.",
    "검토 포인트: 영업, 제품, 대리점 커뮤니케이션 관점에서 후속 영향을 점검하세요."
  ].join("\n");
}

export function buildIndustryNewsBody(item: NewsItem, summary: string, summaryProvider: "ai" | "fallback") {
  return [
    summary,
    "",
    "---",
    `출처: ${item.link}`,
    item.published ? `게시일: ${item.published}` : undefined,
    `요약 방식: ${summaryProvider === "ai" ? "Maejong AI" : "RSS 원문 기반 fallback"}`
  ].filter(Boolean).join("\n");
}

async function summarizeItem(item: NewsItem) {
  const prompt = [
    "다음 업계뉴스 1건을 사내 인트라넷 카드뉴스로 올릴 수 있게 한국어로 요약해 주세요.",
    "형식: 핵심 요약 2문장, 업계 영향 1문장, 검토 포인트 1문장.",
    `제목: ${item.title}`,
    `본문/설명: ${textFromHtml(item.summarySource)}`,
    `링크: ${item.link}`
  ].join("\n");

  try {
    const summary = await summarizeForCardNews(prompt);
    if (summary.trim()) {
      return { summary: summary.trim(), provider: "ai" as const };
    }
  } catch (error) {
    console.warn("Industry news AI summary failed; using fallback.", error);
  }

  return { summary: fallbackSummary(item), provider: "fallback" as const };
}

async function fetchCandidates() {
  const feed = await parser.parseURL(config.INDUSTRY_NEWS_RSS_URL);

  return feed.items.slice(0, config.INDUSTRY_NEWS_MAX_CANDIDATES).map((item): NewsItem => ({
    title: textFromHtml(item.title ?? "제목 없음"),
    link: item.link ?? item.guid ?? "",
    published: item.pubDate ?? item.isoDate,
    summarySource: item.contentSnippet ?? item.content ?? item.summary ?? ""
  })).filter((item) => item.title && item.link);
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
