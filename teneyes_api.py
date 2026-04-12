"""Uvicorn 진입점: 저장소 루트에서 `uvicorn teneyes_api:app --reload --host 127.0.0.1 --port 8000`"""

from __future__ import annotations

import sys
from pathlib import Path

_teneyes_dir = Path(__file__).resolve().parent / "teneyes"
if str(_teneyes_dir) not in sys.path:
    sys.path.insert(0, str(_teneyes_dir))

from api_server import app

__all__ = ["app"]
