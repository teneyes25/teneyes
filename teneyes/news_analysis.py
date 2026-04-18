"""
전체 뉴스 분석 페이지 (`mode=summaries` API).

단독 실행: teneyes 폴더에서 `streamlit run news_analysis.py`
통합 앱: `app.py`에서 `render_daily_report()` 호출
"""

from __future__ import annotations

import datetime
import html

import path_setup  # noqa: F401
import pandas as pd
import requests
import streamlit as st

from teneyes.utils.api import fetch_daily
from teneyes.utils.layout import page_title
from teneyes.utils.text_utils import extract_keywords


def _sentiment_triple(data: dict) -> tuple[float, float, float]:
    if all(k in data for k in ("pos", "neu", "neg")):
        return (
            float(data["pos"]),
            float(data["neu"]),
            float(data["neg"]),
        )
    s = data.get("sentiment") or {}
    return (
        float(s.get("positive") or 0.0),
        float(s.get("neutral") or 0.0),
        float(s.get("negative") or 0.0),
    )


def render_daily_report(ten_eyes_url: str | None = None) -> None:
    page_title("전체 뉴스 분석")

    st.date_input("분석 날짜", key="selected_date")
    date = st.session_state.get("selected_date", datetime.date.today())

    try:
        data = fetch_daily(date, ten_eyes_url=ten_eyes_url)
    except requests.HTTPError as e:
        st.error(
            f"API 오류 ({e.response.status_code if e.response else '?'}): "
            f"{e.response.text[:500] if e.response else e}"
        )
        return
    except requests.RequestException as e:
        url_hint = ten_eyes_url or "session_state.api_base / TEN_EYES_API_BASE"
        st.error(f"API에 연결할 수 없습니다. ({url_hint}) — {e}")
        return
    except (KeyError, ValueError, TypeError) as e:
        st.error(f"응답을 해석할 수 없습니다: {e}")
        return

    summaries = str(data.get("summaries_text") or "")
    date_str = date.strftime("%Y-%m-%d")

    st.subheader("요약")
    score = float(data["score_today"])
    delta = float(data["change"]) if data.get("change") is not None else None
    st.metric("TEN EYES 점수", f"{score:.1f}", delta)
    st.write("주요 키워드:", ", ".join(extract_keywords(summaries, top_n=12)))
    st.info(html.escape(str(data.get("interpretation") or "")))

    st.subheader("감정 분포")
    pos, neu, neg = _sentiment_triple(data)
    sentiment_df = pd.DataFrame(
        {"감정": ["긍정", "중립", "부정"], "비율": [pos, neu, neg]}
    )
    st.bar_chart(sentiment_df.set_index("감정"))

    st.subheader("주요 기사")
    articles = data.get("articles")
    if isinstance(articles, list) and articles:
        for article in articles:
            if not isinstance(article, dict):
                continue
            title = str(article.get("title") or "")
            st.markdown(f"### {html.escape(title)}")
            st.write(str(article.get("summary") or ""))
            link = str(article.get("link") or "")
            if link:
                st.caption(link)
    else:
        st.write("기사 데이터가 아직 API에 포함되지 않았습니다.")

    st.subheader("전체 브리핑")
    keywords = extract_keywords(summaries, top_n=8)
    parts = [p.strip() for p in summaries.split(".") if p.strip()]
    short_summary = ". ".join(parts[:3]) + ("." if parts else "")
    kw5 = ", ".join(html.escape(k) for k in keywords[:5]) if keywords else "(없음)"
    interp = html.escape(str(data.get("interpretation") or ""))
    pos_s, neu_s, neg_s = (f"{pos:.3f}", f"{neu:.3f}", f"{neg:.3f}")
    short_esc = html.escape(short_summary) if short_summary else ""

    full_summary = (
        f"오늘({date_str})의 뉴스는 전반적으로 {interp} 분위기를 보였습니다. "
        f"주요 키워드는 {kw5} 등이었으며, "
        f"긍정/중립/부정 비율은 각각 {pos_s}, {neu_s}, {neg_s} 입니다. "
        f"전체적으로 {short_esc}"
    )
    st.markdown(full_summary, unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(page_title="전체 뉴스 분석", layout="wide")
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.date.today()
    render_daily_report()
