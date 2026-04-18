"""
TEN EYES — Streamlit 통합 앱 (사이드바 메뉴).

1) API: 저장소 루트에서 `uvicorn teneyes_api:app --reload --host 127.0.0.1 --port 8000`
2) UI: teneyes 폴더에서 `streamlit run app.py`
"""

from __future__ import annotations

import datetime

import path_setup  # noqa: F401
import streamlit as st

from home_dashboard import render_home_dashboard
from keyword_premium import render_keyword_insight
from news_analysis import render_daily_report


def _ensure_session_defaults() -> None:
    if "api_base" not in st.session_state:
        st.session_state.api_base = "http://127.0.0.1:8000"
    if "is_premium" not in st.session_state:
        st.session_state.is_premium = False
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.date.today()


def _apply_dark_theme() -> None:
    if not st.session_state.get("dark_mode"):
        return
    st.markdown(
        """
        <style>
            .stApp { background-color: #0d1117; }
            [data-testid="stSidebar"] { background-color: #161b22; }
            [data-testid="stAppViewContainer"] .main { color: #e6edf3; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_settings() -> None:
    st.title("설정")

    st.checkbox("다크 모드", key="dark_mode")
    st.checkbox("Premium 구독 활성화", key="is_premium")
    st.write("계정 정보, 데이터 업데이트 설정 등…")

    with st.expander("API 연결"):
        st.text_input(
            "API 서버 베이스 URL",
            key="api_base",
            help="예: http://127.0.0.1:8000 (끝 슬래시 없이)",
        )
        st.caption("변경 후 다른 메뉴로 이동하면 이 주소로 요청합니다.")


st.set_page_config(
    page_title="TEN EYES",
    layout="wide",
)

_ensure_session_defaults()
_apply_dark_theme()

st.sidebar.title("TEN EYES 메뉴")

menu = st.sidebar.radio(
    "이동",
    ["홈 대시보드", "전체 뉴스 분석", "키워드 심층 분석 (Premium)", "설정"],
)

api_base = str(st.session_state.api_base).rstrip("/")
ten_eyes_url = f"{api_base}/ten-eyes"

if menu == "홈 대시보드":
    render_home_dashboard(ten_eyes_url)

elif menu == "전체 뉴스 분석":
    render_daily_report(ten_eyes_url)

elif menu == "키워드 심층 분석 (Premium)":
    render_keyword_insight(ten_eyes_url=ten_eyes_url)

elif menu == "설정":
    render_settings()
