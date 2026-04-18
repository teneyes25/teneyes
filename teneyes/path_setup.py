"""프로젝트 루트의 ``src``를 ``sys.path``에 넣어 ``import teneyes`` 가 동작하게 합니다."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_src_on_path() -> None:
    root = Path(__file__).resolve().parent
    src = root / "src"
    s = str(src)
    if s not in sys.path:
        sys.path.insert(0, s)


ensure_src_on_path()
