import { config } from "../config.js";
import { query } from "../db/pool.js";
import { chatWithLlm, type ChatMessage } from "./ai.js";

export type AgentSource = {
  type: "approval" | "industry-news" | "brand" | "document";
  title: string;
  excerpt: string;
  updatedAt?: string;
};

export type AgentChatInput = {
  message: string;
  context?: "general" | "approval" | "industry-news" | "brand";
  draftTitle?: string;
  draftBody?: string;
};

function normalize(value: unknown) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

function excerpt(value: unknown, limit = 320) {
  const text = normalize(value);
  return text.length > limit ? `${text.slice(0, limit)}...` : text;
}

function searchPattern(input: AgentChatInput) {
  const text = [input.message, input.draftTitle, input.draftBody].map(normalize).join(" ");
  const tokens = text
    .split(/[\s,./()[\]{}'"`~!?:;|]+/)
    .map((token) => token.trim())
    .filter((token) => token.length >= 2);
  const preferred = tokens.find((token) => /브랜드|자료|대리점|기안|업계|뉴스|제품|카탈로그/.test(token)) ?? tokens[0] ?? text.slice(0, 40);
  return `%${preferred}%`;
}

function fallbackAdvice(input: AgentChatInput, sources: AgentSource[]) {
  const sourceLine = sources.length > 0
    ? `참고한 사내 자료: ${sources.slice(0, 3).map((source) => source.title).join(", ")}`
    : "아직 참고할 사내 자료가 충분하지 않습니다.";

  if (input.context === "approval" || input.draftTitle || input.draftBody) {
    return [
      "메종이입니다. 사내 자료와 기안 작성 원칙을 바탕으로 먼저 정리해드릴게요.",
      sourceLine,
      [
        "권장 기안 구조:",
        "1. 목적: 대리점에 최신 브랜드 자료집을 배포해 대외 커뮤니케이션 기준을 통일합니다.",
        "2. 배경/필요성: 자료 버전 차이로 인한 메시지 불일치, 영업 응대 품질 편차를 줄입니다.",
        "3. 요청 사항: 자료집 배포 승인, 대상 대리점 범위, 배포 채널, 담당 부서를 명확히 적습니다.",
        "4. 실행 계획: 배포 일정, 안내 메일/교육 여부, 수신 확인 방법을 포함합니다.",
        "5. 리스크/후속 관리: 구버전 자료 회수, 문의 대응 창구, 업데이트 주기를 적으면 승인자가 판단하기 쉽습니다."
      ].join("\n"),
      input.draftBody ? `현재 초안 보강 포인트: ${excerpt(input.draftBody, 220)} → 승인 요청 범위와 배포 후 확인 방법을 추가하세요.` : "기안 초안을 보내주시면 누락 항목과 더 명확한 문장으로 다듬어 드릴 수 있습니다."
    ].join("\n\n");
  }

  return [
    "메종이입니다. 사내 지식 기반으로 요약해 안내드립니다.",
    sourceLine,
    "업계뉴스, 브랜드 자료, 전자결재 사례를 함께 참고해 영업/제품/대리점 관점의 실행 포인트를 정리해 드릴 수 있습니다."
  ].join("\n\n");
}

function isLowQualityAnswer(answer: string) {
  const text = answer.trim();
  if (text.length < 20) {
    return true;
  }

  const promptLeakMarkers = ["사내 지식:", "유형:", "일시:", "You are", "I'm sorry"];
  if (promptLeakMarkers.some((marker) => text.includes(marker))) {
    return true;
  }

  const koreanCharacters = text.match(/[가-힣]/g)?.length ?? 0;
  return koreanCharacters < Math.max(8, text.length * 0.08);
}

export async function collectAgentSources(input: AgentChatInput) {
  const sources: AgentSource[] = [];
  const search = searchPattern(input);

  const approvals = await query<{
    title: string;
    body: string;
    status: string;
    updated_at: Date;
  }>(
    `select title, body, status, updated_at
     from approvals
     where $1::text != ''
       and (title ilike $2 or body ilike $2)
     order by updated_at desc
     limit 3`,
    [input.message, search]
  );

  for (const row of approvals.rows) {
    sources.push({
      type: "approval",
      title: `[전자결재/${row.status}] ${row.title}`,
      excerpt: excerpt(row.body),
      updatedAt: row.updated_at?.toISOString()
    });
  }

  const moduleItems = await query<{
    module_key: string;
    title: string;
    body: string;
    tags: string[];
    updated_at: Date;
  }>(
    `select module_key, title, body, tags, updated_at
     from module_items
     where module_key in ('industry-news', 'product-catalog')
       and (
         title ilike $1
         or body ilike $1
         or tags::text ilike $1
         or $2::text in ('general', 'industry-news', 'brand')
       )
     order by updated_at desc
     limit 4`,
    [search, input.context ?? "general"]
  );

  for (const row of moduleItems.rows) {
    sources.push({
      type: row.module_key === "industry-news" ? "industry-news" : "brand",
      title: `[${row.module_key}] ${row.title}`,
      excerpt: excerpt(row.body),
      updatedAt: row.updated_at?.toISOString()
    });
  }

  const documents = await query<{
    title: string;
    file_name: string;
    tags: string[];
    created_at: Date;
  }>(
    `select title, file_name, tags, created_at
     from documents
     where title ilike $1
       or file_name ilike $1
       or tags::text ilike $1
       or tags && array['brand', '브랜드', 'catalog', '카탈로그', 'product-catalog']::text[]
     order by created_at desc
     limit 4`,
    [search]
  );

  for (const row of documents.rows) {
    sources.push({
      type: "document",
      title: `[브랜드 자료집] ${row.title}`,
      excerpt: `파일명: ${row.file_name}, 태그: ${(row.tags ?? []).join(", ") || "없음"}`,
      updatedAt: row.created_at?.toISOString()
    });
  }

  return sources.slice(0, 6);
}

export async function chatWithMaejongAgent(input: AgentChatInput) {
  const sources = await collectAgentSources(input);
  const knowledge = sources.slice(0, 4).map((source, index) => [
    `#${index + 1} ${source.title}`,
    `유형: ${source.type}`,
    source.updatedAt ? `일시: ${source.updatedAt}` : undefined,
    `내용: ${source.excerpt}`
  ].filter(Boolean).join("\n")).join("\n\n");

  const system = [
    "너는 매종 인트라넷 전용 무료 LLM AI Agent '메종이'다.",
    "역할: 사내 컨설턴트, 전자결재 기안 코치, 업계뉴스/브랜드 자료 기반 상담자.",
    "답변은 한국어로 5개 bullet 이내로 작성한다.",
    "전자결재 기안은 목적/배경/요청/근거/리스크/실행계획을 점검한다.",
    "제공된 사내 지식에 없는 내용은 추측하지 말고 확인이 필요하다고 말한다.",
    `현재 LLM provider: ${config.AI_PROVIDER}, model: ${config.AI_PROVIDER === "ollama" ? config.OLLAMA_MODEL : config.OPENAI_MODEL}`
  ].join("\n");

  const user = [
    `사용자 질문: ${input.message}`,
    input.context ? `요청 맥락: ${input.context}` : undefined,
    input.draftTitle ? `기안 제목: ${input.draftTitle}` : undefined,
    input.draftBody ? `기안 초안: ${excerpt(input.draftBody, 500)}` : undefined,
    knowledge ? `사내 지식:\n${knowledge}` : "사내 지식: 아직 검색된 자료가 없습니다."
  ].filter(Boolean).join("\n\n");

  const messages: ChatMessage[] = [
    { role: "system", content: system },
    { role: "user", content: user }
  ];

  if (config.AI_PROVIDER === "ollama" && config.OLLAMA_MODEL === "smollm2:135m") {
    return {
      answer: fallbackAdvice(input, sources),
      provider: config.AI_PROVIDER,
      model: config.OLLAMA_MODEL,
      fallback: true,
      fallbackReason: "small-local-model-consultant-mode",
      sources
    };
  }

  try {
    const answer = await chatWithLlm(messages);
    if (isLowQualityAnswer(answer)) {
      return {
        answer: fallbackAdvice(input, sources),
        provider: config.AI_PROVIDER,
        model: config.AI_PROVIDER === "ollama" ? config.OLLAMA_MODEL : config.OPENAI_MODEL,
        fallback: true,
        fallbackReason: "llm-quality-guard",
        sources
      };
    }

    return {
      answer: answer.trim() || fallbackAdvice(input, sources),
      provider: config.AI_PROVIDER,
      model: config.AI_PROVIDER === "ollama" ? config.OLLAMA_MODEL : config.OPENAI_MODEL,
      fallback: false,
      sources
    };
  } catch (error) {
    console.warn("Maejong agent LLM failed; using fallback.", error);
    return {
      answer: fallbackAdvice(input, sources),
      provider: config.AI_PROVIDER,
      model: config.AI_PROVIDER === "ollama" ? config.OLLAMA_MODEL : config.OPENAI_MODEL,
      fallback: true,
      sources
    };
  }
}
