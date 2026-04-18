"""Streamlit·스크립트 공용 — TEN EYES `ten-eyes?mode=summaries` 호출."""

from __future__ import annotations

import datetime
import os

import requests

DEFAULT_API_BASE = os.environ.get("TEN_EYES_API_BASE", "http://127.0.0.1:8000")


def _date_str(date: datetime.date | str) -> str:
    if isinstance(date, datetime.date):
        return date.strftime("%Y-%m-%d")
    return str(date)


def resolve_ten_eyes_url() -> str:
    """`TEN_EYES_API_BASE` 환경 변수, 또는 Streamlit `session_state.api_base` 기준 `/ten-eyes` URL."""
    base = DEFAULT_API_BASE.rstrip("/")
    try:
        import streamlit as st

        if "api_base" in st.session_state:
            base = str(st.session_state.api_base).rstrip("/")
    except Exception:
        pass
    return f"{base}/ten-eyes"


def fetch_daily(
    date: datetime.date | str | None = None,
    *,
    ten_eyes_url: str | None = None,
    timeout: int = 60,
) -> dict:
    """
    `date`가 없으면 오늘(`datetime.date.today()`)을 사용합니다.
    `ten_eyes_url`이 없으면 `resolve_ten_eyes_url()`을 사용합니다.
    """
    d = date if date is not None else datetime.date.today()
    url = ten_eyes_url or resolve_ten_eyes_url()
    params = {"date": _date_str(d), "mode": "summaries"}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()["data"]
