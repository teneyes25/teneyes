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
