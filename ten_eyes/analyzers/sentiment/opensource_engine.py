from __future__ import annotations

import os
import warnings

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from .base import BaseSentimentEngine, SentimentScores

# 기본: KcBERT 토크나이저 + (비공개/삭제 시 HF_TOKEN 필요할 수 있음) 감성 헤드
_PRIMARY_TOKENIZER = "beomi/KcBERT-base"
_PRIMARY_MODEL = "nlp04/kcbert-base-sentiment"
# 기본 모델을 불러올 수 없을 때만 사용 (logits: 0=negative, 1=neutral, 2=positive)
_FALLBACK_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"


def _hf_token() -> str | None:
    return os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")


class OpenSourceSentimentEngine(BaseSentimentEngine):
    def __init__(self) -> None:
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        token = _hf_token()
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                _PRIMARY_TOKENIZER, token=token
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                _PRIMARY_MODEL, token=token
            )
        except OSError as err:
            warnings.warn(
                f"'{_PRIMARY_MODEL}' 로드 실패 ({err!s}). "
                f"대체 모델 '{_FALLBACK_ID}' 사용. "
                "비공개 저장소면 HF_TOKEN 환경 변수를 설정하세요.",
                UserWarning,
                stacklevel=1,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(_FALLBACK_ID)
            self.model = AutoModelForSequenceClassification.from_pretrained(_FALLBACK_ID)
        self.model.to(self._device)
        self.model.eval()

    def analyze(self, text: str) -> SentimentScores:
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=256
        )
        inputs = {k: v.to(self._device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        scores = torch.softmax(outputs.logits, dim=1)[0].tolist()

        return {
            "positive": float(scores[2]),
            "neutral": float(scores[1]),
            "negative": float(scores[0]),
        }
