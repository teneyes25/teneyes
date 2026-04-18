"""
TEN EYES REST API.

실행:
  저장소 루트: uvicorn teneyes_api:app --reload --host 127.0.0.1 --port 8000
  teneyes 폴더: uvicorn api_server:app --reload --host 127.0.0.1 --port 8000

예:
  GET http://127.0.0.1:8000/conflict?date=2026-04-12
  GET http://127.0.0.1:8000/happiness?date=2026-04-12
  GET http://127.0.0.1:8000/ten-eyes?date=2026-04-12
  GET http://127.0.0.1:8000/ten-eyes?date=2026-04-12&mode=summaries
    (응답 data에 summaries_text, articles[], sentiment, pos/neu/neg 등)
  GET http://127.0.0.1:8000/keywords?date=2026-04-12
  GET http://127.0.0.1:8000/news-summary?date=2026-04-12
  GET http://127.0.0.1:8000/briefing?date=2026-04-12
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import path_setup  # noqa: F401 — ``src`` 를 ``sys.path`` 에 등록
from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder

from teneyes.analyzers.conflict_index_v2 import ConflictIndexCalculatorV2
from teneyes.analyzers.happiness_index import HappinessIndexCalculator
from teneyes.analyzers.keywords.conflict_keywords import CONFLICT_KEYWORDS
from teneyes.analyzers.keywords.happiness_keywords import HAPPINESS_KEYWORDS
from teneyes.analyzers.summary import (
    generate_daily_briefing,
    get_top_articles_for_summary,
)
from teneyes.paths import repo_root
from teneyes.utils.keyword_extract import extract_keywords

app = FastAPI(title="TEN EYES API", version="1.0")

API_VERSION = "1.0"
KEYWORD_TOP_N = 10

conf_calc = ConflictIndexCalculatorV2()
happy_calc = HappinessIndexCalculator()


def _yesterday_iso(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (d - timedelta(days=1)).isoformat()


def _news_ten_eyes_score(date_str: str) -> float:
    c = conf_calc.run(date_str)["conflict_index_raw"]
    h = happy_calc.run(date_str)["happiness_index_raw"]
    return max(0, min(100, 50 + (h - c)))


def load_news_summaries(date_str: str) -> str:
    """`data/news_{date}.json`에서 기사 summary만 이어 붙인 문자열."""
    path = repo_root() / "data" / f"news_{date_str}.json"
    if not path.is_file():
        raise FileNotFoundError(f"뉴스 파일 없음: {path}")

    with path.open("r", encoding="utf-8") as f:
        articles = json.load(f)

    if not isinstance(articles, list):
        raise ValueError("뉴스 JSON은 기사 객체의 배열이어야 합니다.")

    summaries: list[str] = []
    for item in articles:
        if not isinstance(item, dict):
            continue
        s = item.get("summary")
        if s is None:
            continue
        t = str(s).strip()
        if t:
            summaries.append(t)

    if not summaries:
        raise ValueError("요약(summary) 데이터가 없습니다.")

    return " ".join(summaries)


def load_news_articles_list(date_str: str) -> list[dict[str, Any]]:
    """`data/news_{date}.json`에서 제목·요약·링크만 담은 리스트 (없으면 빈 배열)."""
    path = repo_root() / "data" / f"news_{date_str}.json"
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8") as f:
        articles = json.load(f)
    if not isinstance(articles, list):
        return []
    out: list[dict[str, Any]] = []
    for item in articles:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "title": str(item.get("title") or ""),
                "summary": str(item.get("summary") or ""),
                "link": str(item.get("link") or ""),
            }
        )
    return out


def analyze_text(text: str) -> tuple[float, float, float, str, float, float, float]:
    """감성 분석 기반 TEN EYES 스타일 점수·해석·감성 비율 (텍스트 블록용)."""
    if not text.strip():
        raise ValueError("분석할 텍스트가 비어 있습니다.")

    s = conf_calc.sentiment.analyze(text)
    pos = float(s["positive"])
    neu = float(s["neutral"])
    neg = float(s["negative"])

    happiness = pos * 42.0 + neu * 8.0
    conflict = neg * 42.0 + neu * 6.0
    score = max(0.0, min(100.0, 50.0 + (happiness - conflict)))

    interpretation = (
        "텍스트는 긍정적 톤이 우세합니다."
        if score > 55
        else "텍스트는 부정·갈등 톤이 상대적으로 강합니다."
        if score < 45
        else "텍스트는 긍정과 부정이 비슷한 중립에 가깝습니다."
    )
    return score, conflict, happiness, interpretation, pos, neu, neg


def ten_eyes_from_summaries(date_str: str) -> dict[str, Any]:
    """당일·전일 뉴스 summary 합본을 각각 analyze_text로 점수화."""
    combined_today = load_news_summaries(date_str)
    score_today, c_t, h_t, interpretation, pos, neu, neg = analyze_text(
        combined_today
    )

    score_yesterday: float | None = None
    change: float | None = None
    conflict_yesterday: float | None = None
    happiness_yesterday: float | None = None
    try:
        ys = _yesterday_iso(date_str)
        combined_y = load_news_summaries(ys)
        score_yesterday, c_y, h_y, _, _, _, _ = analyze_text(combined_y)
        change = score_today - score_yesterday
        conflict_yesterday = c_y
        happiness_yesterday = h_y
    except (FileNotFoundError, ValueError):
        pass

    data: dict[str, Any] = {
        "ten_eyes_score": score_today,
        "score_today": score_today,
        "score_yesterday": score_yesterday,
        "change": change,
        "conflict_index": c_t,
        "happiness_index": h_t,
        "conflict_yesterday": conflict_yesterday,
        "happiness_yesterday": happiness_yesterday,
        "interpretation": interpretation,
        "summaries_text": combined_today,
        "articles": load_news_articles_list(date_str),
        "mode": "summaries",
        "sentiment": {"positive": pos, "neutral": neu, "negative": neg},
        "pos": pos,
        "neu": neu,
        "neg": neg,
    }
    return response_wrapper(data, date_str)


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


def ten_eyes_from_text(
    text: str, *, meta_date: str | None = None
) -> dict[str, Any]:
    """단일 텍스트에 대해 감성 분석 기반 TEN EYES 스타일 점수(데모)."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="빈 텍스트입니다.")

    try:
        score, conflict, happiness, _gen_interp, pos, neu, neg = analyze_text(
            text.strip()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    score_yesterday: float | None = None
    change: float | None = None
    if meta_date:
        try:
            ys = _yesterday_iso(meta_date)
            score_yesterday = _news_ten_eyes_score(ys)
            change = score - score_yesterday
        except FileNotFoundError:
            pass

    data = {
        "ten_eyes_score": score,
        "score_today": score,
        "score_yesterday": score_yesterday,
        "change": change,
        "conflict_index": conflict,
        "happiness_index": happiness,
        "interpretation": (
            "입력 문장은 긍정적 톤이 우세합니다."
            if score > 55
            else "입력 문장은 부정·갈등 톤이 상대적으로 강합니다."
            if score < 45
            else "입력 문장은 긍정과 부정이 비슷한 중립에 가깝습니다."
        ),
        "sentiment": {"positive": pos, "neutral": neu, "negative": neg},
    }
    return response_wrapper(data, meta_date or "text")


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
    date: str | None = Query(
        None,
        description="뉴스 일자 YYYY-MM-DD (text 미사용 시 필수)",
        examples=["2026-04-12"],
    ),
    text: str | None = Query(
        None,
        description="직접 입력 텍스트 분석 (지정 시 일자 기반 분석 대신 사용)",
    ),
    mode: str | None = Query(
        None,
        description="summaries: 해당 일·전일 뉴스 summary 합본 감성 분석 (text 미사용 시)",
    ),
):
    if text is not None and text.strip():
        return jsonable_encoder(
            ten_eyes_from_text(text.strip(), meta_date=date)
        )
    if not date:
        raise HTTPException(
            status_code=400,
            detail="쿼리 파라미터 date(YYYY-MM-DD) 또는 text 중 하나를 지정하세요.",
        )
    if mode == "summaries":
        try:
            return jsonable_encoder(ten_eyes_from_summaries(date))
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
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

        score_yesterday: float | None = None
        change: float | None = None
        try:
            ys = _yesterday_iso(date)
            score_yesterday = _news_ten_eyes_score(ys)
            change = score - score_yesterday
        except FileNotFoundError:
            pass

        data = {
            "ten_eyes_score": score,
            "score_today": score,
            "score_yesterday": score_yesterday,
            "change": change,
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
