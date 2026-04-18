# TEN EYES

뉴스·정부·경제 데이터 수집, 지표 분석, Streamlit 대시보드, FastAPI 서버를 한 저장소에서 다룹니다.

## 디렉터리 구조

| 경로 | 설명 |
|------|------|
| `src/teneyes/` | **단일 Python 패키지** — `analyzers/`, `collectors/`, `utils/`, `paths.py`, `main.py` |
| `path_setup.py` | `src`를 `sys.path`에 넣어 `import teneyes`가 되게 함 (앱·API·스크립트가 먼저 import) |
| `app.py`, `home_dashboard.py`, … | Streamlit UI (프로젝트 루트에 둔 진입 스크립트) |
| `components/`, `pages/` | Streamlit 컴포넌트·멀티페이지 |
| `api_server.py` | FastAPI 앱 (`teneyes/`에서 `uvicorn api_server:app`) |
| `data/` | 수집 JSON 등 (`.gitkeep` 유지) |
| `assets/` | 정적 자산용 (예: `.gitkeep`; 로고는 루트 `teneyes.png`, `WHITE.png`) |
| `preview_logos.py` | 로고 base64 미리보기 스크립트 |
| `.streamlit/` | Streamlit 설정 |

분석·수집·HTTP 유틸은 모두 `teneyes.*` 아래로 통합되어 있습니다.

## 환경

- Python 3.10+ 권장  
- 의존성: `pip install -r requirements.txt`  
- 작업 디렉터리는 항상 **이 프로젝트 루트**(`teneyes/`)로 맞춥니다.

## 실행

### 수집 CLI

```bash
python -m src.main
python -m src.main news
```

### 전체 수집 스크립트

```bash
python run_all.py
```

### API (FastAPI)

`teneyes/` 작업 디렉터리에서:

```bash
uvicorn api_server:app --reload --host 127.0.0.1 --port 8000
```

저장소 루트에서 실행할 때는 상위 폴더의 `teneyes_api.py`를 쓰는 방식이 동일합니다 (`uvicorn teneyes_api:app ...`).

### Streamlit 대시보드

```bash
streamlit run app.py
```

별도 분석기 UI: `streamlit run text_analyzer_app.py`

## 코드에서 패키지 쓰기

애플리케이션 모듈에서는 가능한 한 파일 맨 위에 다음을 둡니다.

```python
import path_setup  # noqa: F401
from teneyes.analyzers.conflict_index_v2 import ConflictIndexCalculatorV2
from teneyes.utils.api import resolve_ten_eyes_url
```

`path_setup` 없이 `import teneyes`만 하려면 `PYTHONPATH`에 프로젝트의 `src`를 추가하거나, 편집 가능 설치(`pip install -e .`)를 구성하면 됩니다.

## 데이터 경로

`teneyes.paths.repo_root()`가 `app.py`와 `data/`가 있는 프로젝트 루트를 가리킵니다. 수집기·분석기는 이 기준으로 `data/` 아래 파일을 읽고 씁니다.
