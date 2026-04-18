from __future__ import annotations

import urllib.request
from typing import Optional


def fetch_text(url: str, *, timeout: float = 30.0, encoding: Optional[str] = None) -> str:
    """URL 본문을 문자열로 가져옵니다. (표준 라이브러리만 사용)"""
    req = urllib.request.Request(url, headers={"User-Agent": "TenEyes/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset()
    if encoding:
        return raw.decode(encoding, errors="replace")
    return raw.decode(charset or "utf-8", errors="replace")
