from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from analyzers.relevance_score import get_relevance_score


def summarize_article(article: Mapping[str, Any]) -> str:
    title = str(article.get("title", "") or "")
    summary = str(article.get("summary", "") or "")

    if len(summary) > 120:
        summary = summary[:120] + "..."

    return f"• {title}: {summary}"


def rank_articles(
    articles: list[dict[str, Any]], sentiment_analyzer: Any
) -> list[dict[str, Any]]:
    ranked: list[tuple[float, dict[str, Any]]] = []

    for a in articles:
        text = str(a.get("title", "")) + " " + str(a.get("summary", ""))
        sentiment = sentiment_analyzer.analyze(text)
        relevance = float(get_relevance_score(a))

        score = (
            float(sentiment["negative"]) * 0.4
            + float(sentiment["positive"]) * 0.4
            + relevance * 0.2
        )

        ranked.append((score, a))

    ranked.sort(reverse=True, key=lambda x: x[0])
    return [item for _, item in ranked]


def get_top_articles_for_summary(
    articles: list[dict[str, Any]], sentiment_analyzer: Any, n: int = 5
) -> list[dict[str, str]]:
    ranked = rank_articles(articles, sentiment_analyzer)
    out: list[dict[str, str]] = []
    for a in ranked[:n]:
        title = str(a.get("title", "") or "")
        summary = str(a.get("summary", "") or "")
        if len(summary) > 120:
            summary = summary[:120] + "..."
        out.append({"title": title, "summary": summary})
    return out


def generate_daily_news_summary(
    articles: list[dict[str, Any]], sentiment_analyzer: Any
) -> str:
    items = get_top_articles_for_summary(articles, sentiment_analyzer, 5)
    return "\n".join(f"• {it['title']}: {it['summary']}" for it in items)


def extract_topics(articles: list[dict[str, Any]]) -> list[str]:
    counter: Counter[str] = Counter()
    for a in articles:
        text = str(a.get("title", "")) + " " + str(a.get("summary", ""))
        nouns = re.findall(r"[가-힣]{2,}", text)
        counter.update(nouns)

    return [kw for kw, _ in counter.most_common(3)]


def topic_sentiment(
    topic: str, articles: list[dict[str, Any]], sentiment_analyzer: Any
) -> float:
    scores: list[float] = []
    for a in articles:
        text = str(a.get("title", "")) + " " + str(a.get("summary", ""))
        if topic in text:
            s = sentiment_analyzer.analyze(text)
            scores.append(float(s["positive"]) - float(s["negative"]))

    return sum(scores) / len(scores) if scores else 0.0


def generate_advanced_summary(
    articles: list[dict[str, Any]], sentiment_analyzer: Any
) -> str:
    topics = extract_topics(articles)
    lines: list[str] = []

    for t in topics:
        score = topic_sentiment(t, articles, sentiment_analyzer)
        if score > 0.05:
            mood = "긍정적 영향"
        elif score < -0.05:
            mood = "부정적 영향"
        else:
            mood = "중립적 영향"

        lines.append(
            f"- **{t}**: 오늘 뉴스에서 자주 등장했으며, 정서적으로는 *{mood}*을 준 것으로 분석됩니다."
        )

    return "\n".join(lines)
