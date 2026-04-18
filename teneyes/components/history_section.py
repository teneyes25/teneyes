"""로컬 `data/news_*.json` 기반 지표 히스토리 표."""

from __future__ import annotations

import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from teneyes.utils.history import load_history

from .dateutil import to_date_str


@st.cache_data(ttl=120)
def _cached_history(data_dir_resolved: str) -> pd.DataFrame:
    base = Path(data_dir_resolved) if data_dir_resolved else None
    return load_history(base)


def render_history_section(
    *,
    data_dir: Path | None = None,
    end: str | datetime.date | None = None,
    tail: int = 30,
) -> None:
    """
    `end`가 있으면 해당 날짜 이하만 남기고, 최신 `tail`행을 표로 표시합니다.
    `data_dir` 기본값은 `teneyes/data/`.
    """
    st.subheader("히스토리")

    resolved = (data_dir.resolve() if data_dir is not None else Path(__file__).resolve().parents[1] / "data")
    df = _cached_history(str(resolved))

    if df.empty:
        st.info("로컬 `data/news_*.json`에서 불러온 이력이 없습니다.")
        return

    out = df.copy()
    if end is not None:
        end_ts = pd.Timestamp(to_date_str(end))
        out = out[out["date"] <= end_ts]
    if out.empty:
        st.info("선택한 날짜 이전에 표시할 이력이 없습니다.")
        return

    out = out.sort_values("date").tail(tail)
    display = out.copy()
    display["date"] = display["date"].dt.strftime("%Y-%m-%d")
    display = display.rename(
        columns={
            "date": "날짜",
            "conflict": "갈등",
            "happiness": "행복",
            "ten_eyes": "TEN EYES",
        }
    )

    st.dataframe(display, use_container_width=True, hide_index=True)
