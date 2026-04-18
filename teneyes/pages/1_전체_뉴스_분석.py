"""
전체 뉴스 분석 (멀티페이지).

`app.py` 홈에서 「이 날짜 분석하기」로 이동하거나, 사이드바에서 직접 엽니다.
`st.session_state["selected_date"]`가 홈과 공유됩니다.
"""

from __future__ import annotations

import datetime

import path_setup  # noqa: F401
import streamlit as st

from news_analysis import render_daily_report


def _ensure_defaults() -> None:
    if "api_base" not in st.session_state:
        st.session_state.api_base = "http://127.0.0.1:8000"
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.date.today()


_ensure_defaults()

api_base = str(st.session_state.api_base).rstrip("/")
ten_eyes_url = f"{api_base}/ten-eyes"

st.page_link("app.py", label="← 홈으로")
render_daily_report(ten_eyes_url)
