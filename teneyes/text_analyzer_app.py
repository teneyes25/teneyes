"""
TEN EYES 텍스트 분석기.

실행 (teneyes 폴더): streamlit run text_analyzer_app.py

API 전체 URL은 환경 변수 ``TENEYES_API_URL`` 로 지정합니다.
기본값은 로컬 FastAPI ``http://127.0.0.1:8000/ten-eyes`` 입니다.
"""

from __future__ import annotations

import datetime
import os

import requests
import streamlit as st

API_URL = os.environ.get(
    "TENEYES_API_URL",
    "http://127.0.0.1:8000/ten-eyes",
).rstrip("/")


def calculate_ten_eyes_score(text: str, date: str) -> dict:
    """GET /ten-eyes — `date`는 응답 meta, 동일 텍스트면 점수는 API 로직상 같을 수 있음."""
    r = requests.get(
        API_URL,
        params={"text": text, "date": date},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def ten_eyes_value(payload: dict) -> float | None:
    """응답 JSON에서 `data.ten_eyes_score` 추출. 없으면 None."""
    try:
        return float(payload["data"]["ten_eyes_score"])
    except (KeyError, TypeError, ValueError):
        return None


st.set_page_config(page_title="TEN EYES 분석기", layout="centered")
st.title("TEN EYES 분석기")

text = st.text_area("분석할 텍스트를 입력하세요")
date = st.date_input("날짜를 선택하세요", datetime.date.today())

if st.button("분석하기"):
    try:
        date_str = date.isoformat()
        requested_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        yesterday_date = requested_date - datetime.timedelta(days=1)
        yesterday_str = yesterday_date.strftime("%Y-%m-%d")

        payload_today = calculate_ten_eyes_score(text, date_str)
        payload_yesterday = calculate_ten_eyes_score(text, yesterday_str)

        score_today = ten_eyes_value(payload_today)
        score_yesterday = ten_eyes_value(payload_yesterday)

        if score_yesterday is not None:
            change = score_today - score_yesterday if score_today is not None else None
        else:
            change = None

        st.caption(
            "텍스트 분석 모드에서는 점수는 동일하고 `meta.requested_date`만 다를 수 있습니다."
        )
        if change is not None:
            st.metric("전일 대비 TEN EYES 변화", f"{change:+.2f}")
        elif score_today is not None:
            st.info("전일 점수를 계산할 수 없어 변화량을 표시하지 않습니다.")
        st.subheader("선택한 날짜 기준")
        st.json(payload_today)
        st.subheader("전일 기준")
        st.json(payload_yesterday)
    except requests.HTTPError as e:
        st.error(f"API 오류: {e.response.status_code if e.response else e}")
    except Exception as e:
        st.error(f"요청 실패: {e}")
