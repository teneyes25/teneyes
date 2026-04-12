from __future__ import annotations

from typing import Any

__all__ = [
    "extract_keywords",
    "load_logo_base64",
    "summarize_emotional_signals",
    "last_weekday_on_or_before",
    "load_history",
    "moving_average",
    "previous_weekday",
    "three_business_days_ending_at",
]

_LAZY: dict[str, tuple[str, str]] = {
    "summarize_emotional_signals": (".emotional_summary", "summarize_emotional_signals"),
    "load_history": (".history", "load_history"),
    "extract_keywords": (".keyword_extract", "extract_keywords"),
    "load_logo_base64": (".logo", "load_logo_base64"),
    "last_weekday_on_or_before": (".moving_average", "last_weekday_on_or_before"),
    "moving_average": (".moving_average", "moving_average"),
    "previous_weekday": (".moving_average", "previous_weekday"),
    "three_business_days_ending_at": (".moving_average", "three_business_days_ending_at"),
}


def __getattr__(name: str) -> Any:
    if name in _LAZY:
        mod, attr = _LAZY[name]
        import importlib

        module = importlib.import_module(mod, __name__)
        return getattr(module, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
