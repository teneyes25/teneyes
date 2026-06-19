"use client";

import { useEffect, useState } from "react";

type IndustryNewsItem = {
  id: string;
  title: string;
  body: string;
  tags: string[];
  created_at: string;
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

function preview(body: string) {
  return body.split("---")[0]?.trim() ?? body;
}

export function IndustryNewsBoard() {
  const [items, setItems] = useState<IndustryNewsItem[]>([]);
  const [status, setStatus] = useState("업계뉴스를 불러오는 중입니다.");

  useEffect(() => {
    async function loadIndustryNews() {
      try {
        const response = await fetch(`${apiBaseUrl()}/api/industry-news`, { cache: "no-store" });
        const payload = await response.json();
        setItems(payload.items ?? []);
        setStatus("월~금 오전 9시 자동 업로드 · 침구/수면 키워드 중요도 기준");
      } catch {
        setStatus("업계뉴스를 불러오지 못했습니다. API 상태를 확인해 주세요.");
      }
    }

    void loadIndustryNews();
  }, []);

  return (
    <section className="panel industry-board">
      <div className="section-heading">
        <p>업계 뉴스 게시판</p>
        <span>{status}</span>
      </div>
      {items.length === 0 ? (
        <p className="empty">아직 업로드된 업계뉴스가 없습니다.</p>
      ) : (
        <div className="industry-list">
          {items.slice(0, 3).map((item, index) => (
            <article className={index === 0 ? "industry-item featured" : "industry-item"} key={item.id}>
              <div>
                <strong>{item.title}</strong>
                <time>{new Date(item.created_at).toLocaleString("ko-KR")}</time>
              </div>
              <p>{preview(item.body)}</p>
              <div className="tag-row">
                {item.tags.map((tag) => <span key={tag}>#{tag}</span>)}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
