"""저장소 루트(``app.py``, ``data/`` 가 있는 디렉터리) 경로."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path


@lru_cache
def repo_root() -> Path:
    """``src/teneyes/paths.py`` 기준으로 프로젝트 루트를 반환합니다."""
    return Path(__file__).resolve().parents[2]
