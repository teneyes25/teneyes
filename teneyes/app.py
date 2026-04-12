"""
TEN EYES — Streamlit 대시보드 (FastAPI 연동).

1) API: teneyes 폴더에서 `uvicorn api_server:app --reload --host 127.0.0.1 --port 8000`
2) UI:  `streamlit run app.py`
"""

from __future__ import annotations

import datetime
from datetime import timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# -----------------------------
# API 서버 주소
# -----------------------------
API_URL = "http://127.0.0.1:8000"


# -----------------------------
# API 호출
# -----------------------------
def call_api(endpoint: str, date: str) -> dict:
    url = f"{API_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    r = requests.get(url, params={"date": date}, timeout=60)
    r.raise_for_status()
    return r.json()


def load_period_data(end: datetime.date, days: int) -> pd.DataFrame:
    """종료일부터 과거 days일(당일 포함). 뉴스 없는 날은 건너뜀."""
    dates = [(end - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    records = []

    for d in dates:
        try:
            c = call_api("conflict", d)
            h = call_api("happiness", d)
            t = call_api("ten-eyes", d)
        except requests.HTTPError:
            continue

        records.append(
            {
                "date": d,
                "conflict": c["data"]["conflict_index"],
                "happiness": h["data"]["happiness_index"],
                "ten_eyes": t["data"]["ten_eyes_score"],
            }
        )

    df = pd.DataFrame(records)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="TEN EYES Dashboard",
    layout="wide",
)

# -----------------------------
# 로고 base64 문자열
# -----------------------------
white_logo = ""  # ← Shinhee가 변환한 WHITE.png base64
navy_logo = ""  # ← 필요하면 네이비 로고도 사용 가능

# -----------------------------
# 다크모드 + 헤더 스타일
# -----------------------------
st.markdown(
    f"""
    <style>
        body {{
            background-color: #0D1117;
            color: #E6EDF3;
        }}
        .stApp {{
            background-color: #0D1117;
            color: #E6EDF3;
        }}
        .ten-eyes-header {{
            background-color: #161B22;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .ten-eyes-header h1 {{
            color: #E6EDF3;
            margin: 0;
            font-size: 32px;
        }}
        .ten-card {{
            background-color: #1E2530;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: fadeIn 0.8s ease-in-out;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>

    <div class="ten-eyes-header">
        <img src="data:image/png;base64,{white_logo}" width="60">
        <h1>TEN EYES Dashboard</h1>
    </div>
""",
    unsafe_allow_html=True,
)

st.caption("한국 사회의 갈등·행복 지수를 기반으로 한 정서 분석 시스템 · API: " + API_URL)

# -----------------------------
# 날짜 선택
# -----------------------------
date = st.date_input("날짜 선택", value=datetime.date.today())
date_str = date.strftime("%Y-%m-%d")

# -----------------------------
# 탭 구조
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Keywords", "News", "Trends"])

# -----------------------------
# Overview 탭
# -----------------------------
with tab1:
    st.subheader("📊 오늘의 지수")

    try:
        conflict = call_api("conflict", date_str)
        happiness = call_api("happiness", date_str)
        teneyes = call_api("ten-eyes", date_str)
        briefing = call_api("briefing", date_str)
    except requests.HTTPError as e:
        detail = ""
        if e.response is not None:
            try:
                detail = str(e.response.json())
            except Exception:
                detail = (e.response.text or "")[:500]
        st.error(
            f"API HTTP 오류: {e.response.status_code if e.response else '?'} — {detail}"
        )
        st.stop()
    except requests.RequestException as e:
        st.error(
            f"API 서버에 연결할 수 없습니다. `{API_URL}` 에서 uvicorn이 떠 있는지 확인하세요. ({e})"
        )
        st.stop()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="ten-card">', unsafe_allow_html=True)
        st.metric("🔮 TEN EYES Score", teneyes["data"]["ten_eyes_score"])
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="ten-card">', unsafe_allow_html=True)
        st.metric("⚠️ 갈등지수", conflict["data"]["conflict_index"])
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="ten-card">', unsafe_allow_html=True)
        st.metric("🌱 행복지수", happiness["data"]["happiness_index"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("📝 일일 브리핑")
    st.write(briefing["data"]["briefing"])

# -----------------------------
# Keywords 탭 (Overview에서 받은 conflict / happiness 재사용)
# -----------------------------
with tab2:
    st.subheader("📌 핵심 키워드")

    col_a, col_b = st.columns(2)

    with col_a:
        st.write("### 갈등 키워드")
        for item in conflict["data"]["top_keywords"]:
            st.write(f"- {item['keyword']} ({item['count']})")

    with col_b:
        st.write("### 행복 키워드")
        for item in happiness["data"]["top_keywords"]:
            st.write(f"- {item['keyword']} ({item['count']})")

# -----------------------------
# News 탭
# -----------------------------
with tab3:
    st.subheader("📰 뉴스 요약")

    try:
        summary = call_api("news-summary", date_str)
    except requests.HTTPError as e:
        detail = ""
        if e.response is not None:
            try:
                detail = str(e.response.json())
            except Exception:
                detail = (e.response.text or "")[:500]
        st.error(
            f"API HTTP 오류: {e.response.status_code if e.response else '?'} — {detail}"
        )
        st.stop()
    except requests.RequestException as e:
        st.error(
            f"API 서버에 연결할 수 없습니다. `{API_URL}` 에서 uvicorn이 떠 있는지 확인하세요. ({e})"
        )
        st.stop()

    for article in summary["data"]["top_articles"]:
        st.write(f"- **{article['title']}**: {article['summary']}")

# -----------------------------
# Trends 탭 (기간 분석)
# -----------------------------
with tab4:
    st.subheader("📈 기간 분석 그래프")

    period = st.selectbox("기간 선택", ["7일", "30일", "90일"])
    days = {"7일": 7, "30일": 30, "90일": 90}[period]

    df = load_period_data(date, days)

    if df.empty:
        st.info(
            "선택한 기간에 뉴스 데이터가 있는 날이 없어 그래프를 그릴 수 없습니다."
        )
    else:
        fig = px.line(
            df,
            x="date",
            y=["conflict", "happiness", "ten_eyes"],
            color_discrete_map={
                "conflict": "#E85A5A",
                "happiness": "#4FD1A1",
                "ten_eyes": "#3A7BFF",
            },
        )
        st.plotly_chart(fig, use_container_width=True)
