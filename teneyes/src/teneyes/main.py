from __future__ import annotations

import argparse

from teneyes.collectors.econ_collector import EconCollector
from teneyes.collectors.gov_collector import GovCollector
from teneyes.collectors.news_collector import NewsCollector


def _run_news(collector: NewsCollector) -> int:
    data = collector.collect()
    collector.save_news(data)
    return len(data)


def _run_gov(collector: GovCollector) -> int:
    data = collector.collect()
    collector.save_gov(data)
    return len(data)


def _run_econ(collector: EconCollector) -> int:
    data = collector.collect()
    collector.save_econ(data)
    return len(data)


def main() -> None:
    parser = argparse.ArgumentParser(prog="teneyes")
    parser.add_argument(
        "source",
        nargs="?",
        choices=("news", "gov", "econ", "all"),
        default="all",
        help="수집할 소스",
    )
    args = parser.parse_args()
    mapping = {
        "news": NewsCollector(),
        "gov": GovCollector(),
        "econ": EconCollector(),
    }
    if args.source == "all":
        for name, collector in mapping.items():
            if name == "news":
                n = _run_news(collector)
                print(f"{name}: {n} items (saved)")
            elif name == "gov":
                n = _run_gov(collector)
                print(f"{name}: {n} items (saved)")
            elif name == "econ":
                n = _run_econ(collector)
                print(f"{name}: {n} sources (saved)")
    elif args.source == "news":
        n = _run_news(mapping["news"])
        print(f"{args.source}: {n} items")
    elif args.source == "gov":
        n = _run_gov(mapping["gov"])
        print(f"{args.source}: {n} items")
    elif args.source == "econ":
        n = _run_econ(mapping["econ"])
        print(f"{args.source}: {n} sources (saved)")


if __name__ == "__main__":
    main()
