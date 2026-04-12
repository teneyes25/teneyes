from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def collect_gov() -> list[dict[str, Any]]:
    return []


def save_gov(data: list[dict[str, Any]]) -> Path:
    today = datetime.date.today().isoformat()
    path = _project_root() / "data" / f"gov_{today}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


class GovCollector:
    """정부/공공 소스 수집기 스텁."""

    def collect(self) -> list[dict[str, Any]]:
        return collect_gov()

    def save_gov(self, data: list[dict[str, Any]]) -> Path:
        return save_gov(data)
