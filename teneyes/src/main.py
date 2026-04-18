"""CLI 진입: 프로젝트 루트에서 ``python -m src.main``."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import path_setup  # noqa: E402

from teneyes.main import main

if __name__ == "__main__":
    main()
