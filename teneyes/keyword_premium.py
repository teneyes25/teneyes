"""
키워드 심층 분석 (Premium) — `utils.api.fetch_daily` 연동.

단독 실행: teneyes 폴더에서 `streamlit run keyword_premium.py`
통합 앱: `app.py`에서 `render_keyword_insight()` 호출

API: 저장소 루트에서 `uvicorn teneyes_api:app --reload --host 127.0.0.1 --port 8000`
"""

from __future__ import annotations

import datetime

import path_setup  # noqa: F401
import pandas as pd
import requests
import streamlit as st

from teneyes.utils.api import fetch_daily
from teneyes.utils.text_utils import extract_co_keywords, extract_keyword_articles


def render_keyword_insight(*, ten_eyes_url: str | None = None) -> None:
    st.title("키워드 심층 분석 (Premium)")

    if not st.session_state.get("is_premium", False):
        st.warning("Premium 기능입니다. 업그레이드가 필요합니다.")
        st.stop()

    keyword = st.text_input("키워드 입력", "")

    if not keyword:
        return

    try:
        data = fetch_daily(ten_eyes_url=ten_eyes_url)
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
        return
    except requests.RequestException as e:
        st.error(f"API에 연결할 수 없습니다. ({e})")
        return

    summaries = str(data.get("summaries_text") or "")
    articles = extract_keyword_articles(summaries, keyword)
    co_keywords = extract_co_keywords(summaries, keyword, top_n=12)

    st.metric("관련 기사 수", len(articles))
    st.write("연관 키워드:", ", ".join(co_keywords) if co_keywords else "(없음)")

    st.subheader("관련 기사")
    if articles:
        for a in articles:
            st.write("-", a)
    else:
        st.caption("해당 키워드가 포함된 문장이 없습니다.")

    st.subheader("키워드 트렌드")

    today = datetime.date.today()
    dates = [
        (today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)
    ]
    freq: list[int] = []
    for d in dates:
        try:
            d_data = fetch_daily(d, ten_eyes_url=ten_eyes_url)
            d_sum = str(d_data.get("summaries_text") or "")
            freq.append(d_sum.count(keyword))
        except requests.RequestException:
            freq.append(0)

    trend_df = pd.DataFrame({"date": dates, "frequency": freq})
    st.line_chart(trend_df.set_index("date"))


if __name__ == "__main__":
    st.set_page_config(page_title="키워드 심층 분석 · TEN EYES", layout="wide")
    if "api_base" not in st.session_state:
        st.session_state.api_base = "http://127.0.0.1:8000"
    if "is_premium" not in st.session_state:
        st.session_state.is_premium = True
    render_keyword_insight()
