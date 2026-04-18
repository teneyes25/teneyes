"""Streamlit — summaries 모드 갈등·행복 지수 카드 (전일 대비)."""

from __future__ import annotations

import datetime
import html

import requests
import streamlit as st

from teneyes.utils.api import resolve_ten_eyes_url

from .dateutil import to_date_str


def render_index_cards(
    date: str | datetime.date,
    *,
    ten_eyes_url: str | None = None,
    timeout: int = 60,
) -> None:
    """
    `ten_eyes_url`이 없으면 `resolve_ten_eyes_url()`을 사용합니다.
    응답 `data`에 `conflict_yesterday`, `happiness_yesterday`가 있어야 전일 대비가 채워집니다.
    """
    url = ten_eyes_url or resolve_ten_eyes_url()
    date_s = to_date_str(date)
    params = {"date": date_s, "mode": "summaries"}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    response = r.json()
    data = response["data"]

    conflict = data.get("conflict_index")
    happiness = data.get("happiness_index")
    conflict_y = data.get("conflict_yesterday")
    happiness_y = data.get("happiness_yesterday")

    def diff(today: float | None, yesterday: float | None) -> str:
        if today is None or yesterday is None:
            return "전일 데이터 없음"
        d = today - yesterday
        arrow = "▲" if d > 0 else "▼" if d < 0 else "—"
        return f"{d:+.1f} {arrow}"

    conflict_change = html.escape(diff(conflict, conflict_y))
    happiness_change = html.escape(diff(happiness, happiness_y))

    def color_conflict(value: float | None) -> str:
        if value is None:
            return "#9E9E9E"
        if value >= 70:
            return "#F44336"
        if value >= 40:
            return "#FFC107"
        return "#4CAF50"

    def color_happiness(value: float | None) -> str:
        if value is None:
            return "#9E9E9E"
        if value >= 70:
            return "#4CAF50"
        if value >= 40:
            return "#FFC107"
        return "#F44336"

    def fmt_main(value: float | None) -> str:
        return f"{value:.1f}" if value is not None else "N/A"

    c_main = html.escape(fmt_main(conflict))
    h_main = html.escape(fmt_main(happiness))
    c_color = color_conflict(float(conflict) if conflict is not None else None)
    h_color = color_happiness(float(happiness) if happiness is not None else None)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div style="
                background-color:{c_color};
                padding:20px;
                border-radius:12px;
                color:white;
                text-align:center;
                box-shadow:0 4px 10px rgba(0,0,0,0.15);
            ">
                <h3 style="margin-bottom:10px;">갈등 지수</h3>
                <h2 style="margin:0;">{c_main}</h2>
                <p style="margin-top:10px;">전일 대비: {conflict_change}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                background-color:{h_color};
                padding:20px;
                border-radius:12px;
                color:white;
                text-align:center;
                box-shadow:0 4px 10px rgba(0,0,0,0.15);
            ">
                <h3 style="margin-bottom:10px;">행복 지수</h3>
                <h2 style="margin:0;">{h_main}</h2>
                <p style="margin-top:10px;">전일 대비: {happiness_change}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
