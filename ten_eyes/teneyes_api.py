"""Uvicorn 진입점: `uvicorn teneyes_api:app --reload` (ten_eyes 디렉터리에서 실행)."""

from api_server import app

__all__ = ["app"]
