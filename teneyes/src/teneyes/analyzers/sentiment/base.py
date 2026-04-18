from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class SentimentScores(TypedDict):
    positive: float
    neutral: float
    negative: float


class BaseSentimentEngine(ABC):
    @abstractmethod
    def analyze(self, text: str) -> SentimentScores:
        """
        Return sentiment scores as:
        {
            "positive": float,
            "neutral": float,
            "negative": float
        }
        """
        ...
