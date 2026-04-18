"""Streamlit — `GET /ten-eyes?mode=summaries` 점수 카드."""

from __future__ import annotations

import datetime
import html

import requests
import streamlit as st

from teneyes.utils.api import resolve_ten_eyes_url

from .dateutil import to_date_str


def render_score_card(
    date: str | datetime.date,
    *,
    ten_eyes_url: str | None = None,
    timeout: int = 60,
) -> None:
    """
    `ten_eyes_url`이 없으면 `resolve_ten_eyes_url()`(세션·환경 변수·기본값)을 사용합니다.
    """
    url = ten_eyes_url or resolve_ten_eyes_url()
    date_s = to_date_str(date)
    params = {"date": date_s, "mode": "summaries"}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    response = r.json()

    data = response["data"]
    score_today = float(data["score_today"])
    change = data.get("change")
    interpretation = str(data["interpretation"])
    requested_date = str(response["meta"]["requested_date"])

    if score_today >= 70:
        color = "#4CAF50"
    elif score_today >= 40:
        color = "#FFC107"
    else:
        color = "#F44336"

    if change is None:
        change_text = "전일 데이터 없음"
    else:
        ch = float(change)
        arrow = "▲" if ch > 0 else "▼" if ch < 0 else "—"
        change_text = f"{ch:+.1f} {arrow}"

    safe_interp = html.escape(interpretation)
    safe_date = html.escape(requested_date)
    safe_change = html.escape(change_text)

    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:25px;
            border-radius:15px;
            color:white;
            text-align:center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        ">
            <h1 style="margin-bottom:5px;">{score_today:.1f}</h1>
            <h3 style="margin-top:0; font-weight:400;">{safe_interp}</h3>
            <p style="margin-top:15px; font-size:16px;">날짜: {safe_date}</p>
            <p style="margin-top:5px; font-size:16px;">전일 대비: {safe_change}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
