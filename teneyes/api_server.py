"""
TEN EYES REST API.

실행:
  저장소 루트: uvicorn teneyes_api:app --reload --host 127.0.0.1 --port 8000
  teneyes 폴더: uvicorn api_server:app --reload --host 127.0.0.1 --port 8000

예:
  GET http://127.0.0.1:8000/conflict?date=2026-04-12
  GET http://127.0.0.1:8000/happiness?date=2026-04-12
  GET http://127.0.0.1:8000/ten-eyes?date=2026-04-12
  GET http://127.0.0.1:8000/keywords?date=2026-04-12
  GET http://127.0.0.1:8000/news-summary?date=2026-04-12
  GET http://127.0.0.1:8000/briefing?date=2026-04-12
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder

from analyzers.conflict_index_v2 import ConflictIndexCalculatorV2
from analyzers.happiness_index import HappinessIndexCalculator
from analyzers.keywords.conflict_keywords import CONFLICT_KEYWORDS
from analyzers.keywords.happiness_keywords import HAPPINESS_KEYWORDS
from analyzers.summary import (
    generate_daily_briefing,
    get_top_articles_for_summary,
)
from utils.keyword_extract import extract_keywords

app = FastAPI(title="TEN EYES API", version="1.0")

API_VERSION = "1.0"
KEYWORD_TOP_N = 10

conf_calc = ConflictIndexCalculatorV2()
happy_calc = HappinessIndexCalculator()


def response_wrapper(data: dict[str, Any], date: str) -> dict[str, Any]:
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "meta": {
            "requested_date": date,
            "version": API_VERSION,
        },
    }


@app.get("/conflict")
def get_conflict(
    date: str = Query(..., description="날짜 YYYY-MM-DD", examples=["2026-04-12"]),
):
    try:
        result = conf_calc.run(date)
        data = {
            "conflict_index": result["conflict_index_raw"],
            "scores": result["scores"],
            "top_keywords": [
                {"keyword": kw, "count": cnt}
                for kw, cnt in result["keywords"].most_common(10)
            ],
        }
        return jsonable_encoder(response_wrapper(data, date))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"해당 날짜 뉴스 파일이 없습니다: data/news_{date}.json",
        ) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/happiness")
def get_happiness(
    date: str = Query(..., description="날짜 YYYY-MM-DD", examples=["2026-04-12"]),
):
    try:
        result = happy_calc.run(date)
        data = {
            "happiness_index": result["happiness_index_raw"],
            "scores": result["scores"],
            "top_keywords": [
                {"keyword": kw, "count": cnt}
                for kw, cnt in result["keywords"].most_common(10)
            ],
        }
        return jsonable_encoder(response_wrapper(data, date))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"해당 날짜 뉴스 파일이 없습니다: data/news_{date}.json",
        ) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/ten-eyes")
def get_ten_eyes(
    date: str = Query(..., description="날짜 YYYY-MM-DD", examples=["2026-04-12"]),
):
    try:
        c = conf_calc.run(date)["conflict_index_raw"]
        h = happy_calc.run(date)["happiness_index_raw"]
        score = max(0, min(100, 50 + (h - c)))

        interpretation = (
            "오늘은 긍정 흐름이 우세한 안정적인 하루입니다."
            if score > 55
            else "오늘은 갈등 신호가 강하게 나타난 불안정한 하루입니다."
            if score < 45
            else "긍정과 부정 신호가 균형을 이루는 중립적인 하루입니다."
        )

        data = {
            "ten_eyes_score": score,
            "conflict_index": c,
            "happiness_index": h,
            "interpretation": interpretation,
        }
        return jsonable_encoder(response_wrapper(data, date))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"해당 날짜 뉴스 파일이 없습니다: data/news_{date}.json",
        ) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/keywords")
def get_keywords(
    date: str = Query(..., description="날짜 YYYY-MM-DD", examples=["2026-04-12"]),
):
    try:
        articles = conf_calc.load_news(date)
        conf_kw = extract_keywords(articles, CONFLICT_KEYWORDS)
        happy_kw = extract_keywords(articles, HAPPINESS_KEYWORDS)
        data = {
            "article_count": len(articles),
            "conflict_keywords": [
                {"keyword": k, "count": c}
                for k, c in conf_kw.most_common(KEYWORD_TOP_N)
            ],
            "happiness_keywords": [
                {"keyword": k, "count": c}
                for k, c in happy_kw.most_common(KEYWORD_TOP_N)
            ],
        }
        return jsonable_encoder(response_wrapper(data, date))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"해당 날짜 뉴스 파일이 없습니다: data/news_{date}.json",
        ) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/news-summary")
def get_news_summary(
    date: str = Query(..., description="날짜 YYYY-MM-DD", examples=["2026-04-12"]),
):
    try:
        articles = conf_calc.load_news(date)
        top_articles = get_top_articles_for_summary(
            articles, conf_calc.sentiment, 5
        )
        data = {"top_articles": top_articles}
        return jsonable_encoder(response_wrapper(data, date))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"해당 날짜 뉴스 파일이 없습니다: data/news_{date}.json",
        ) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/briefing")
def get_briefing(
    date: str = Query(..., description="날짜 YYYY-MM-DD", examples=["2026-04-12"]),
):
    try:
        articles = conf_calc.load_news(date)
        c = conf_calc.run(date)
        h = happy_calc.run(date)
        score = max(
            0,
            min(
                100,
                50 + (h["happiness_index_raw"] - c["conflict_index_raw"]),
            ),
        )
        briefing = generate_daily_briefing(
            c["conflict_index_raw"],
            h["happiness_index_raw"],
            score,
            c["keywords"],
            h["keywords"],
            articles,
            conf_calc.sentiment,
        )
        data = {"briefing": briefing}
        return jsonable_encoder(response_wrapper(data, date))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"해당 날짜 뉴스 파일이 없습니다: data/news_{date}.json",
        ) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
