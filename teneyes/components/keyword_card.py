"""Streamlit — summaries 응답의 `summaries_text`에서 간단 키워드 태그."""

from __future__ import annotations

import datetime
import html

import requests
import streamlit as st

from teneyes.utils.api import resolve_ten_eyes_url
from teneyes.utils.text_utils import extract_keywords

from .dateutil import to_date_str


def render_keyword_card(
    date: str | datetime.date,
    *,
    ten_eyes_url: str | None = None,
    timeout: int = 60,
) -> None:
    url = ten_eyes_url or resolve_ten_eyes_url()
    date_s = to_date_str(date)
    params = {"date": date_s, "mode": "summaries"}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    response = r.json()

    summaries = response["data"].get("summaries_text")
    if not summaries or not str(summaries).strip():
        st.write("키워드를 추출할 수 있는 뉴스 요약이 없습니다.")
        return

    keywords = extract_keywords(str(summaries), top_n=12)

    tag_style = (
        "display:inline-block;background-color:#E0E0E0;color:#333;"
        "padding:6px 12px;margin:4px;border-radius:20px;font-size:14px;"
    )

    tags_html = "".join(
        f"<span style='{tag_style}'>{html.escape(kw)}</span>" for kw in keywords
    )

    st.markdown(
        f"""
        <div style="padding:10px 0;">
            {tags_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
