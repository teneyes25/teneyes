import { randomUUID } from "node:crypto";
import { createWorker } from "tesseract.js";
import { query } from "../db/pool.js";

export type AgentMemoryMessage = {
  conversationId?: string;
  userId: string;
  role: "user" | "assistant";
  content: string;
  metadata?: Record<string, unknown>;
};

export type AgentKnowledgeInput = {
  title: string;
  content: string;
  sourceType: "upload" | "screenshot" | "admin-persona" | "mattress-expertise" | "approval-template";
  tags: string[];
  createdBy: string;
  metadata?: Record<string, unknown>;
};

export async function ensureAgentMemoryTables() {
  await query(`
    create table if not exists agent_settings (
      key text primary key,
      value text not null,
      updated_at timestamptz not null default now()
    );

    create table if not exists agent_conversations (
      id uuid primary key default gen_random_uuid(),
      user_id text not null,
      title text,
      expires_at timestamptz not null default now() + interval '3 days',
      created_at timestamptz not null default now(),
      updated_at timestamptz not null default now()
    );

    create table if not exists agent_messages (
      id uuid primary key default gen_random_uuid(),
      conversation_id uuid not null references agent_conversations(id) on delete cascade,
      role text not null check (role in ('user', 'assistant')),
      content text not null,
      metadata jsonb not null default '{}',
      created_at timestamptz not null default now()
    );

    create table if not exists agent_knowledge (
      id uuid primary key default gen_random_uuid(),
      title text not null,
      content text not null,
      source_type text not null,
      tags text[] not null default '{}',
      metadata jsonb not null default '{}',
      created_by text not null,
      created_at timestamptz not null default now()
    );

    create index if not exists agent_conversations_user_idx on agent_conversations (user_id, updated_at desc);
    create index if not exists agent_messages_conversation_idx on agent_messages (conversation_id, created_at asc);
    create index if not exists agent_knowledge_tags_idx on agent_knowledge using gin (tags);
    create index if not exists agent_knowledge_text_idx on agent_knowledge using gin (to_tsvector('simple', title || ' ' || content));
  `);

  await seedDefaultKnowledge();
  await cleanupExpiredAgentMemory();
}

export async function cleanupExpiredAgentMemory() {
  await query(`delete from agent_conversations where expires_at < now()`);
}

async function seedDefaultKnowledge() {
  await query(
    `insert into agent_knowledge (title, content, source_type, tags, created_by)
     select $1, $2, 'mattress-expertise', $3, 'system'
     where not exists (select 1 from agent_knowledge where title = $1)`,
    [
      "메종이 기본 페르소나 - 매트리스/침구 업계 컨설턴트",
      [
        "메종이는 국내 매트리스, 침구, 수면용품 업계 컨설턴트로 답변한다.",
        "상담 시 소재(냉감, 모달, 양모, 순면, 극세사), 사용 계절, 가격대, 대리점 판매 포인트, 브랜드 메시지를 함께 고려한다.",
        "사용자 질문에는 상품기획, 영업, 대리점 교육, 고객 상담 관점의 실무 조언을 제공한다."
      ].join("\n"),
      ["persona", "mattress", "bedding", "consulting"]
    ]
  );

  await query(
    `insert into agent_knowledge (title, content, source_type, tags, created_by)
     select $1, $2, 'approval-template', $3, 'system'
     where not exists (select 1 from agent_knowledge where title = $1)`,
    [
      "행안부식 기안문 작성 기본 원칙",
      [
        "기안문은 제목, 목적, 배경 및 필요성, 주요 내용, 추진 일정, 예산/비용, 협조 사항, 검토 의견, 결재 요청 사항 순서로 명확히 쓴다.",
        "문장은 간결하게 쓰고, 근거 자료와 기대 효과를 분리한다.",
        "승인자가 판단해야 할 선택지, 리스크, 후속 조치를 마지막에 정리한다."
      ].join("\n"),
      ["approval", "template", "행안부", "기안문"]
    ]
  );
}

export async function getAgentPersona() {
  const { rows } = await query<{ value: string }>(`select value from agent_settings where key = 'persona'`);
  return rows[0]?.value;
}

export async function setAgentPersona(persona: string) {
  await query(
    `insert into agent_settings (key, value, updated_at)
     values ('persona', $1, now())
     on conflict (key) do update set value = excluded.value, updated_at = now()`,
    [persona]
  );

  await saveAgentKnowledge({
    title: "관리자 지정 메종이 페르소나",
    content: persona,
    sourceType: "admin-persona",
    tags: ["persona", "admin"],
    createdBy: "admin"
  });
}

export async function saveAgentMessage(input: AgentMemoryMessage) {
  await cleanupExpiredAgentMemory();
  const conversationId = input.conversationId ?? randomUUID();

  await query(
    `insert into agent_conversations (id, user_id, title, expires_at, updated_at)
     values ($1, $2, $3, now() + interval '3 days', now())
     on conflict (id) do update set updated_at = now(), expires_at = now() + interval '3 days'`,
    [conversationId, input.userId, input.content.slice(0, 80)]
  );

  await query(
    `insert into agent_messages (conversation_id, role, content, metadata)
     values ($1, $2, $3, $4)`,
    [conversationId, input.role, input.content, input.metadata ?? {}]
  );

  return conversationId;
}

export async function recentConversationContext(userId: string, conversationId?: string) {
  await cleanupExpiredAgentMemory();

  const { rows } = await query<{ role: string; content: string; created_at: Date }>(
    `select m.role, m.content, m.created_at
     from agent_messages m
     join agent_conversations c on c.id = m.conversation_id
     where c.user_id = $1
       and c.expires_at >= now()
       and ($2::uuid is null or c.id = $2)
     order by m.created_at desc
     limit 10`,
    [userId, conversationId ?? null]
  );

  return rows.reverse().map((row) => `${row.role}: ${row.content}`).join("\n");
}

export async function saveAgentKnowledge(input: AgentKnowledgeInput) {
  const { rows } = await query<{ id: string }>(
    `insert into agent_knowledge (title, content, source_type, tags, metadata, created_by)
     values ($1, $2, $3, $4, $5, $6)
     returning id`,
    [input.title, input.content, input.sourceType, input.tags, input.metadata ?? {}, input.createdBy]
  );

  return rows[0].id;
}

export async function searchAgentKnowledge(search: string) {
  const pattern = `%${search}%`;
  const { rows } = await query<{
    title: string;
    content: string;
    source_type: string;
    tags: string[];
    created_at: Date;
  }>(
    `select title, content, source_type, tags, created_at
     from agent_knowledge
     where title ilike $1
       or content ilike $1
       or tags::text ilike $1
       or tags && array['mattress', 'bedding', 'approval', 'template', '행안부', '침구', '매트리스']::text[]
     order by created_at desc
     limit 8`,
    [pattern]
  );

  return rows;
}

export async function extractUploadText(file: Express.Multer.File, memo?: string) {
  const base = [
    memo ? `사용자 메모: ${memo}` : undefined,
    `파일명: ${file.originalname}`,
    `MIME: ${file.mimetype}`,
    `크기: ${file.size} bytes`
  ].filter(Boolean).join("\n");

  if (/^text\//.test(file.mimetype) || /json|csv|xml|html/.test(file.mimetype)) {
    return `${base}\n\n${file.buffer.toString("utf8").slice(0, 12000)}`;
  }

  if (/^image\//.test(file.mimetype)) {
    try {
      const worker = await createWorker("eng");
      const result = await worker.recognize(file.buffer);
      await worker.terminate();
      return `${base}\n\nOCR 분석 결과:\n${result.data.text.slice(0, 12000) || "이미지에서 추출된 텍스트가 없습니다."}`;
    } catch (error) {
      return `${base}\n\n이미지 분석 메모: OCR 처리에 실패했습니다. 파일 메타데이터와 사용자 메모를 우선 학습합니다.\n오류: ${error instanceof Error ? error.message : "unknown"}`;
    }
  }

  return `${base}\n\n파일 본문 자동 추출은 지원되지 않는 형식입니다. 사용자 메모와 메타데이터를 학습합니다.`;
}
