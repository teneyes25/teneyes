"""뉴스 요약 텍스트 등에서 간단 키워드 추출."""

from __future__ import annotations

import re
from collections import Counter


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    if not text or not str(text).strip():
        return []
    words = re.findall(r"[가-힣A-Za-z]+", str(text))
    stopwords = {"오늘", "기자", "대한", "관련", "이번", "정부", "발표"}
    filtered = [w for w in words if len(w) > 1 and w not in stopwords]
    counts = Counter(filtered)
    return [w for w, _ in counts.most_common(top_n)]


def extract_keyword_articles(summaries: str, keyword: str) -> list[str]:
    articles = str(summaries).split(".")
    return [a.strip() for a in articles if keyword in a and a.strip()]


def extract_co_keywords(text: str, keyword: str, top_n: int = 10) -> list[str]:
    words = re.findall(r"[가-힣A-Za-z]+", str(text))
    filtered = [w for w in words if len(w) > 1 and w != keyword]
    counts = Counter(filtered)
    return [w for w, _ in counts.most_common(top_n)]
