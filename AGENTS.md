# Ten Eyes Platform — 에이전트·협업 가이드

이 저장소는 **Ten Eyes Platform(구축 프로젝트)** 입니다. Cursor·기타 도구는 이 파일과 `README.md`를 **단일 제품·단일 워크스페이스**의 기준으로 삼습니다.

## 범위

- **루트**: `ten eyes platform/` 디렉터리 전체가 프로젝트 경계입니다. 이 밖의 경로는 기본적으로 변경하지 않습니다.
- **`teneyes/`**: 메인 애플리케이션 — Streamlit(`app.py`), FastAPI(`api_server.py`), Python 패키지 `src/teneyes/`, `data/`, `path_setup.py`.
- **`teneyes_api.py`**: 플랫폼 루트에서 Uvicorn으로 API를 띄울 때 `teneyes` 경로를 등록하는 진입점입니다.

## 작업 원칙

- 웹 배포·리팩터·의존성 변경은 **`teneyes/`** 를 단일 소스에 가깝게 유지하는 방향이 좋습니다.
- `import teneyes` 를 쓰려면 `teneyes/path_setup.py` 를 먼저 로드하거나, `pip install -e .` 로 패키지를 편집 가능 설치합니다.
- 사용자 대면 문서·주석은 **한국어**를 기본으로 합니다.

## 실행 (요약)

| 목적 | 명령 |
|------|-----------------|
| API (저장소 루트) | `uvicorn teneyes_api:app --reload --host 127.0.0.1 --port 8000` |
| API (`teneyes/`에서) | `uvicorn api_server:app --reload --host 127.0.0.1 --port 8000` |
| 메인 UI | `cd teneyes` 후 `streamlit run app.py` |

## 식별자

- **프로젝트 표시 이름**: Ten Eyes Platform  
- **패키지/배포 이름** (`pyproject.toml`): `teneyes-platform`  
- **런타임 Python 패키지**: `teneyes` (`teneyes/src/teneyes/`)

## Cursor Cloud specific instructions

### 가상환경

- 저장소 루트에 `.venv`를 만들고 `pip install -e .`로 설치합니다. 명령 전 `source .venv/bin/activate`를 사용하세요.
- Ubuntu 등에서 `python3 -m venv`가 실패하면 일회성으로 `sudo apt-get install -y python3.12-venv`가 필요할 수 있습니다.

### 실행 스택 (E2E)

| 서비스 | 포트 | 명령 (루트, venv 활성화 후) |
|--------|------|------------------------------|
| FastAPI | 8000 | `uvicorn teneyes_api:app --host 127.0.0.1 --port 8000` |
| Streamlit | 8501 | `cd teneyes && streamlit run app.py --server.headless true` |

Streamlit은 API(`TEN_EYES_API_BASE`, 기본 `http://127.0.0.1:8000`)에 의존합니다. **두 프로세스를 모두 띄운 뒤** UI를 확인하세요.

### 샘플 데이터

- 번들 JSON은 `teneyes/data/*_2026-04-10.json`입니다. UI 기본 날짜는 오늘이므로, 수집기를 돌리지 않을 때는 사이드바에서 **2026-04-10**을 선택하세요.
- API 스모크: `curl "http://127.0.0.1:8000/ten-eyes?date=2026-04-10"`

### 린트·테스트

- 저장소에 `pytest`/`ruff` 설정이나 `tests/` 디렉터리는 없습니다.
- 구문 검사: `python -m compileall -q teneyes teneyes_api.py`
- 첫 감성 분석 요청 시 Hugging Face 모델(`transformers`/`torch`) 다운로드로 API 응답이 수십 초 걸릴 수 있습니다.

### 선택 환경 변수

- `TEN_EYES_API_BASE` — Streamlit이 호출할 API 베이스 URL (기본 `http://127.0.0.1:8000`)
- `TENEYES_API_URL` — `text_analyzer_app.py`용 `/ten-eyes` 전체 URL
- `HF_TOKEN` / `HUGGINGFACE_HUB_TOKEN` — 비공개 HF 모델 사용 시에만
