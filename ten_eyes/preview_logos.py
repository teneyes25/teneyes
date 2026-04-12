"""
로고 파일 base64 앞부분 확인용 (ten_eyes 폴더에서 실행):
  python preview_logos.py
"""

from __future__ import annotations

import base64
from pathlib import Path


def load_logo_base64(path: str | Path) -> str:
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


_ROOT = Path(__file__).resolve().parent

# Shinhee의 로고 파일 경로 (ten_eyes 루트의 teneyes.png, WHITE.png)
navy_logo = load_logo_base64(_ROOT / "teneyes.png")
white_logo = load_logo_base64(_ROOT / "WHITE.png")

print(navy_logo[:200])
print(white_logo[:200])
