from __future__ import annotations

import glob
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd

from analyzers.conflict_index_v2 import ConflictIndexCalculatorV2
from analyzers.happiness_index import HappinessIndexCalculator


def load_history(data_dir: Path | None = None) -> pd.DataFrame:
    """
    `data/news_*.json` 파일을 날짜순으로 읽어 갈등·행복·TEN EYES 이력을 만듭니다.

    `data_dir`: 기본은 ten_eyes 루트의 `data/` 폴더.
    감성 모델은 파일마다 재로딩하지 않도록 계산기 인스턴스를 한 번만 씁니다.
    """
    base = (data_dir if data_dir is not None else _ROOT / "data").resolve()
    files = sorted(glob.glob(str(base / "news_*.json")))

    conf_calc = ConflictIndexCalculatorV2()
    happy_calc = HappinessIndexCalculator()

    rows: list[dict[str, Any]] = []
    for f in files:
        name = Path(f).name
        date_str = name.split("news_")[1].split(".json")[0]

        try:
            conflict = float(conf_calc.run(date_str)["conflict_index_raw"])
            happiness = float(happy_calc.run(date_str)["happiness_index_raw"])
            ten_eyes = 50.0 + happiness - conflict
            ten_eyes = max(0.0, min(100.0, ten_eyes))

            rows.append(
                {
                    "date": date_str,
                    "conflict": conflict,
                    "happiness": happiness,
                    "ten_eyes": ten_eyes,
                }
            )
        except Exception:
            continue

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)
