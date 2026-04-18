"""
TEN EYES 홈 대시보드 (탭 없이 한 페이지).

단독 실행: teneyes 폴더에서 `streamlit run home_dashboard.py`
통합 앱: `app.py`에서 `render_home_dashboard(ten_eyes_url=...)` 호출
API: `uvicorn teneyes_api:app --reload --host 127.0.0.1 --port 8000` (저장소 루트)
"""

from __future__ import annotations

import datetime

import path_setup  # noqa: F401
import streamlit as st

from components.history_section import render_history_section
from components.index_cards import render_index_cards
from components.keyword_card import render_keyword_card
from components.news_summary_card import render_news_summary_card
from components.score_card import render_score_card
from components.trend_section import render_trend_section


def render_home_dashboard(ten_eyes_url: str | None = None) -> None:
    st.title("TEN EYES 홈 대시보드")

    st.date_input("날짜 선택", key="selected_date")
    date = st.session_state.get("selected_date", datetime.date.today())

    if st.button("이 날짜 분석하기"):
        st.session_state["selected_date"] = date
        st.switch_page("pages/1_전체_뉴스_분석.py")

    render_score_card(date, ten_eyes_url=ten_eyes_url)
    st.markdown("---")

    render_index_cards(date, ten_eyes_url=ten_eyes_url)
    st.markdown("---")

    render_keyword_card(date, ten_eyes_url=ten_eyes_url)
    st.markdown("---")

    render_news_summary_card(date, ten_eyes_url=ten_eyes_url)
    st.markdown("---")

    render_trend_section(ten_eyes_url=ten_eyes_url)
    st.markdown("---")

    render_history_section()


if __name__ == "__main__":
    st.set_page_config(page_title="TEN EYES Dashboard", layout="wide")
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.date.today()
    render_home_dashboard()
