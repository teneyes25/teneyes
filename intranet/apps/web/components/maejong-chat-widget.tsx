"use client";

import { ChangeEvent, FormEvent, useMemo, useState } from "react";

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
  const [conversationId, setConversationId] = useState<string>();
  const [uploadStatus, setUploadStatus] = useState("");
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
          draftBody: draftBody || undefined,
          conversationId
        })
      });
      const payload = await response.json();
      if (payload.conversationId) {
        setConversationId(payload.conversationId);
      }
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

  async function uploadKnowledge(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setUploadStatus("파일을 분석하고 학습 중입니다...");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", file.name);
    formData.append("tags", "메종이,업로드,매트리스,침구");
    formData.append("memo", "인트라넷 홈페이지 메종이 채팅창에서 사용자가 업로드한 자료입니다.");

    try {
      const response = await fetch(`${baseUrl}/api/agent/knowledge/upload`, {
        method: "POST",
        body: formData
      });
      const payload = await response.json();
      setUploadStatus(payload.learned ? `학습 완료: ${file.name}` : "학습 처리에 실패했습니다.");
    } catch {
      setUploadStatus("파일 업로드 API에 연결하지 못했습니다.");
    } finally {
      event.target.value = "";
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
            <label className="upload-box">
              파일/캡처 학습
              <input accept=".txt,.md,.csv,.json,.html,.png,.jpg,.jpeg,.webp" onChange={uploadKnowledge} type="file" />
              {uploadStatus ? <span>{uploadStatus}</span> : <span>자료집, 메모, 캡처 이미지를 올리면 메종이가 3일 대화 기억과 별도로 지식으로 참고합니다.</span>}
            </label>
          </div>
          <div className="chat-log">
            {messages.map((item, index) => (
              <p className={item.role} key={`${item.role}-${index}`}>{item.content}</p>
            ))}
            {loading ? <p className="assistant">메종이가 사내 자료를 확인 중입니다...</p> : null}
          </div>
          <form onSubmit={submit}>
            <input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="메시지를 입력하고 전송을 누르세요" />
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
