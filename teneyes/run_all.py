from __future__ import annotations

import path_setup  # noqa: F401

from teneyes.collectors.econ_collector import collect_econ, save_econ
from teneyes.collectors.gov_collector import collect_gov, save_gov
from teneyes.collectors.news_collector import collect_news, save_news


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
