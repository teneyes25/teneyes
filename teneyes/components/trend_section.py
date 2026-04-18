"""최근 N일 `mode=summaries` API 기반 라인 차트."""

from __future__ import annotations

import datetime

import pandas as pd
import requests
import streamlit as st

from teneyes.utils.api import resolve_ten_eyes_url

from .dateutil import to_date_str


def fetch_daily_summaries(
    ten_eyes_url: str,
    date: str | datetime.date,
    *,
    timeout: int = 60,
) -> dict:
    date_s = to_date_str(date)
    r = requests.get(
        ten_eyes_url,
        params={"date": date_s, "mode": "summaries"},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()["data"]


def render_trend_section(
    ten_eyes_url: str | None = None,
    *,
    days: int = 7,
    end: str | datetime.date | None = None,
    timeout: int = 60,
) -> None:
    """
    `ten_eyes_url`이 없으면 `resolve_ten_eyes_url()`을 씁니다.
    `end`가 없으면 오늘을 기준으로, 있으면 해당 날짜를 구간 끝으로 최근 `days`일을 조회합니다.
    """
    url = ten_eyes_url or resolve_ten_eyes_url()
    if end is None:
        end_d = datetime.date.today()
    elif isinstance(end, datetime.date):
        end_d = end
    else:
        end_d = datetime.datetime.strptime(to_date_str(end), "%Y-%m-%d").date()

    st.subheader(f"최근 {days}일 트렌드")

    dates = [
        (end_d - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(days - 1, -1, -1)
    ]

    records = []
    for d in dates:
        try:
            data = fetch_daily_summaries(url, d, timeout=timeout)
            records.append(
                {
                    "date": d,
                    "score": data.get("score_today"),
                    "conflict": data.get("conflict_index"),
                    "happiness": data.get("happiness_index"),
                }
            )
        except (requests.RequestException, KeyError, TypeError, ValueError):
            records.append(
                {
                    "date": d,
                    "score": None,
                    "conflict": None,
                    "happiness": None,
                }
            )

    df = pd.DataFrame(records)
    for col in ("score", "conflict", "happiness"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    chart_df = df.set_index("date")[["score", "conflict", "happiness"]]
    if chart_df.isna().all().all():
        st.info("선택한 기간에 표시할 요약 지표가 없습니다.")
        return

    st.line_chart(chart_df)
