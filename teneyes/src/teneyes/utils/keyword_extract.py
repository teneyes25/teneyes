from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence


def extract_keywords(
    articles: Sequence[Mapping[str, Any]],
    keyword_dict: Mapping[str, Sequence[str]],
) -> Counter[str]:
    """
    기사 목록에서 `keyword_dict`의 모든 키워드가 본문(제목+요약)에 등장한 횟수를 센다.
    """
    counter: Counter[str] = Counter()
    for a in articles:
        text = str(a.get("title", "")) + " " + str(a.get("summary", ""))
        for _category, keywords in keyword_dict.items():
            for kw in keywords:
                if kw in text:
                    counter[kw] += 1
    return counter
