# Ten Eyes

데이터 수집용 스캐폴딩 프로젝트입니다.

## 구조

- `data/` — 수집 결과 저장
- `src/collectors/` — 뉴스·정부·경제 수집기
- `src/utils/` — 공통 fetch·파서
- `src/main.py` — CLI 진입점

## 실행

프로젝트 루트(`teneyes/`)에서:

```bash
python -m src.main
python -m src.main news
```

Python 3.10+ 권장 (`list[str]` 등 타입 문법).
