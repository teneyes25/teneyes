# Ten Eyes Platform (구축 프로젝트)

**Ten Eyes Platform**은 TEN EYES 서비스를 위한 **플랫폼 구축용 모노레포**입니다.  
Cursor·CI·패키지 매니저는 이 디렉터리를 **하나의 프로젝트 루트**(`teneyes-platform`, `pyproject.toml`)로 인식합니다.

| 문서·설정 | 역할 |
|-----------|------|
| [`pyproject.toml`](./pyproject.toml) | 프로젝트 메타데이터·의존성·`teneyes` 패키지 검색 경로 |
| [`AGENTS.md`](./AGENTS.md) | AI·협업용 범위·실행 규칙 |
| [`.cursor/rules/teneyes-platform.mdc`](./.cursor/rules/teneyes-platform.mdc) | Cursor 에이전트 항상 적용 규칙 |

## 구성 요약

앱·API·수집 파이프라인은 **`teneyes/`** 한 디렉터리에서 실행합니다.  
웹 배포(Streamlit Cloud, Railway, Docker 등)도 **`teneyes/`** + 루트 **`teneyes_api.py`** 를 기준으로 구성하면 됩니다.

## 레이아웃

```
repo_root/                    ← 이 폴더 = Ten Eyes Platform 루트
    pyproject.toml
    AGENTS.md
    teneyes/                  # 메인: Streamlit, FastAPI, src/teneyes, data/
    teneyes_api.py            # 루트에서 uvicorn 진입 시 teneyes/ 를 path에 추가
    requirements.txt          # pip 용 (pyproject와 동기화 권장)
    README.md
```

## 설치（편집 가능 설치）

```bash
cd "ten eyes platform"
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

의존성만 빠르게 맞출 때는 `pip install -r requirements.txt` 도 가능합니다.

## API（저장소 루트）

```bash
uvicorn teneyes_api:app --reload --host 127.0.0.1 --port 8000
```

## Streamlit（`teneyes`）

```bash
cd teneyes
streamlit run app.py
```

텍스트만 빠르게 시험할 때: `cd teneyes` 후 `streamlit run text_analyzer_app.py` (API URL은 환경 변수 `TENEYES_API_URL`로 지정 가능, 기본값 로컬 API).
