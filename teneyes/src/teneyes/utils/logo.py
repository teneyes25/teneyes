from __future__ import annotations

import base64
from pathlib import Path


def load_logo_base64(path: str | Path) -> str:
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
