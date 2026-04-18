"""Streamlit — summaries_text 앞부분을 잘라 짧은 요약 카드로 표시."""

from __future__ import annotations

import datetime
import html

import requests
import streamlit as st

from teneyes.utils.api import resolve_ten_eyes_url

from .dateutil import to_date_str


def render_news_summary_card(
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

    summaries_text = response["data"].get("summaries_text")
    if not summaries_text or not str(summaries_text).strip():
        st.write("뉴스 요약을 불러올 수 없습니다.")
        return

    text = str(summaries_text)
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    if not sentences:
        short_summary = html.escape(text[:500] + ("…" if len(text) > 500 else ""))
    else:
        chunk = ". ".join(sentences[:3]).strip()
        short_summary = html.escape(chunk + ("." if chunk and not chunk.endswith(".") else ""))

    st.markdown(
        f"""
        <div style="
            background-color:#F5F5F5;
            padding:20px;
            border-radius:12px;
            color:#333;
            line-height:1.6;
            box-shadow:0 4px 10px rgba(0,0,0,0.1);
        ">
            {short_summary}
        </div>
        """,
        unsafe_allow_html=True,
    )
