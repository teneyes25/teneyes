from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

import requests

ECON_SOURCES = {
    "usd_krw": "https://api.exchangerate.host/latest?base=USD&symbols=KRW",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def collect_econ() -> dict[str, Any]:
    results: dict[str, Any] = {}
    for name, url in ECON_SOURCES.items():
        r = requests.get(url)
        results[name] = r.json()
    return results


def save_econ(data: dict[str, Any]) -> Path:
    today = datetime.date.today().isoformat()
    path = _project_root() / "data" / f"econ_{today}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


class EconCollector:
    """경제 API 수집 (v0.1)."""

    sources: dict[str, str] = ECON_SOURCES

    def collect(self) -> dict[str, Any]:
        return collect_econ()

    def save_econ(self, data: dict[str, Any]) -> Path:
        return save_econ(data)


if __name__ == "__main__":
    data = collect_econ()
    save_econ(data)
    print("Economic data collected.")
