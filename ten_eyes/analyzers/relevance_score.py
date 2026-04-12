from __future__ import annotations

from typing import Any


def get_relevance_score(article: dict[str, Any]) -> float:
    text = (
        article.get("title", "") + " " + article.get("summary", "")
    ).lower()

    domestic_keywords = ["한국", "국내", "서울", "정부", "국회", "대한민국"]
    if any(k in text for k in domestic_keywords):
        return 1.0

    near_keywords = ["북한", "중국", "일본", "미국", "러시아"]
    if any(k in text for k in near_keywords):
        return 0.7

    mid_keywords = ["유럽", "eu", "나토", "동남아", "중동"]
    if any(k in text for k in mid_keywords):
        return 0.4

    return 0.2
