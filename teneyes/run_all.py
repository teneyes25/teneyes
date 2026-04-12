from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collectors.news_collector import collect_news, save_news
from collectors.gov_collector import collect_gov, save_gov
from collectors.econ_collector import collect_econ, save_econ


def run_all() -> None:
    news = collect_news()
    save_news(news)

    gov = collect_gov()
    save_gov(gov)

    econ = collect_econ()
    save_econ(econ)

    print("TEN EYES data pipeline completed.")


if __name__ == "__main__":
    run_all()
