"use client";

import { FormEvent, useMemo, useState } from "react";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

function apiBaseUrl() {
  if (typeof window === "undefined") {
    return "";
  }

  if (window.location.port === "3000") {
    return `${window.location.protocol}//${window.location.hostname}:4000`;
  }

  return "";
}

export function MaejongChatWidget() {
  const [open, setOpen] = useState(false);
  const [context, setContext] = useState("general");
  const [message, setMessage] = useState("");
  const [draftTitle, setDraftTitle] = useState("");
  const [draftBody, setDraftBody] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "안녕하세요, 메종이입니다. 전자결재 기안, 업계뉴스, 브랜드 자료 상담을 도와드릴게요."
    }
  ]);
  const [loading, setLoading] = useState(false);
  const baseUrl = useMemo(apiBaseUrl, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!message.trim() || loading) {
      return;
    }

    const userMessage = message.trim();
    setMessages((current) => [...current, { role: "user", content: userMessage }]);
    setMessage("");
    setLoading(true);

    try {
      const effectiveContext = draftTitle || draftBody ? "approval" : context;
      const response = await fetch(`${baseUrl}/api/agent/chat`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          context: effectiveContext,
          draftTitle: draftTitle || undefined,
          draftBody: draftBody || undefined
        })
      });
      const payload = await response.json();
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: payload.answer ?? "메종이가 응답을 생성하지 못했습니다."
        }
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: "메종이 API에 연결하지 못했습니다. API 포트와 Docker 상태를 확인해 주세요."
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="maejong-chat">
      {open ? (
        <section className="maejong-chat-window" aria-label="메종이 AI Agent">
          <header>
            <div>
              <strong>메종이</strong>
              <span>인트라넷 전용 무료 AI Agent</span>
            </div>
            <button type="button" className="ghost" onClick={() => setOpen(false)}>닫기</button>
          </header>
          <div className="chat-controls">
            <label>
              상담 범위
              <select value={context} onChange={(event) => {
                setContext(event.target.value);
              }}>
                <option value="general">일반 상담</option>
                <option value="approval">전자결재 기안 도움</option>
                <option value="industry-news">업계뉴스 분석</option>
                <option value="brand">브랜드 자료 상담</option>
              </select>
            </label>
            <div className="draft-box">
              <span className="draft-label">전자결재 기안 도움(선택)</span>
              <input value={draftTitle} onChange={(event) => setDraftTitle(event.target.value)} placeholder="기안 제목" />
              <textarea value={draftBody} onChange={(event) => setDraftBody(event.target.value)} placeholder="기안 초안 또는 고민되는 문장을 붙여넣으세요." />
            </div>
          </div>
          <div className="chat-log">
            {messages.map((item, index) => (
              <p className={item.role} key={`${item.role}-${index}`}>{item.content}</p>
            ))}
            {loading ? <p className="assistant">메종이가 사내 자료를 확인 중입니다...</p> : null}
          </div>
          <form onSubmit={submit}>
            <input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="메종이에게 물어보기" />
            <button type="submit" disabled={loading}>전송</button>
          </form>
        </section>
      ) : (
        <button type="button" className="maejong-chat-button" onClick={() => setOpen(true)}>
          메종이에게 묻기
        </button>
      )}
    </div>
  );
}
