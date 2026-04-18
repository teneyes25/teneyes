"""Streamlit 공통 레이아웃 헬퍼."""

from __future__ import annotations

import html

import streamlit as st


def page_title(title: str) -> None:
    safe = html.escape(str(title))
    st.markdown(
        f"<h1 style='margin-bottom:20px;'>{safe}</h1>",
        unsafe_allow_html=True,
    )
