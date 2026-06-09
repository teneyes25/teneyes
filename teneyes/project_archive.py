"""TEN EYES 분석 기록 아카이브 화면."""

from __future__ import annotations

import path_setup  # noqa: F401
import streamlit as st

from components.history_section import render_history_section


def render_project_archive() -> None:
    st.title("프로젝트 아카이브")
    st.caption("지금까지 수집·분석한 TEN EYES 기록을 한곳에서 확인합니다.")

    render_history_section(tail=None, title="전체 분석 기록")


if __name__ == "__main__":
    st.set_page_config(page_title="프로젝트 아카이브 · TEN EYES", layout="wide")
    render_project_archive()
