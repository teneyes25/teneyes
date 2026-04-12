"""
뉴스 요약·일일 브리핑 생성 API.

`utils.news_summary`, `utils.briefing`의 얇은 래퍼로, FastAPI 등에서
`from analyzers.summary import ...` 형태로 가져다 쓸 수 있습니다.
"""

from __future__ import annotations

from utils.briefing import generate_daily_briefing
from utils.news_summary import (
    generate_advanced_summary,
    generate_daily_news_summary,
    get_top_articles_for_summary,
)

__all__ = [
    "generate_advanced_summary",
    "generate_daily_briefing",
    "generate_daily_news_summary",
    "get_top_articles_for_summary",
]
