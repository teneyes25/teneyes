# 매종 인트라넷

Next.js 프론트엔드, Express API, PostgreSQL, MinIO, Keycloak, Nginx, SMTP, Ollama/OpenAI 전환형 AI를 포함한 Phase 2 준비용 인트라넷 구현입니다.

> 참고: 요청에 언급된 `인트라넷 구축계획.pdf`는 현재 저장소에 없어, 요청 본문에 명시된 모듈과 Phase 2 항목을 기준으로 구조를 영속화했습니다.

## 포함 모듈

- 공지사항, 산업뉴스, Q&A, 규정, 전자결재, 문서함, 조직도, 내 프로필, 제품 카탈로그, 대리점, 근태, 관리자
- Maejong AI 카드뉴스 요약: `AI_PROVIDER=ollama|openai`
- 감사 로그: 로그인 확장 지점, 다운로드, 결재, 근태, 문서 업로드
- 산업뉴스 스케줄러: 월~금 오전 9시(`Asia/Seoul`) 침구/수면 키워드 뉴스 수집, 중요도 1건 선정, 요약, `industry-news` 업로드
- 메종이 AI Agent: 우측 하단 상담창에서 전자결재 기안, 업계뉴스, 브랜드 자료집 기반 상담

## 실행

```bash
cd intranet
npm install
npm run dev
```

로컬 인프라까지 실행:

```bash
cd intranet
sh scripts/bind-intranet-ip.sh
mkdir -p infra/nginx/certs
openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
  -keyout infra/nginx/certs/intranet.key \
  -out infra/nginx/certs/intranet.crt \
  -subj "/CN=localhost"
docker compose -f infra/docker-compose.local.yml up --build
```

`infra/nginx/certs/`는 로컬 개발용 인증서 위치이며 Git에는 저장하지 않습니다.

개발 기준 접속 위치는 `http://192.168.0.6:3000`이며, 앞으로 이 메인 페이지를 **인트라넷 홈페이지**라고 부릅니다. Cloud/VM 재시작 후 이 주소가 응답하지 않으면 `sh scripts/bind-intranet-ip.sh`를 먼저 실행합니다.

## 산업뉴스 스케줄러

기본값은 평일 오전 9시 1건 업로드입니다.

```bash
INDUSTRY_NEWS_SCHEDULER_ENABLED=true
INDUSTRY_NEWS_CRON="0 9 * * 1-5"
INDUSTRY_NEWS_TIMEZONE=Asia/Seoul
INDUSTRY_NEWS_KEYWORDS=침구,매트리스,이불,베개,베게,냉감,모달,양모,침대,극세사,세사,순면,토퍼,쇼파,소파
```

뉴스 후보는 Google News RSS에서 키워드별로 수집하고, 키워드 일치 수, 여러 검색어에서 반복 노출된 빈도, 출시/광고/판매/시장/브랜드 같은 상업 신호, 최신성을 합산해 중요도 점수가 높은 1건을 업로드합니다.

오늘 수동으로 1건 실행:

```bash
curl -X POST http://localhost:4000/api/scheduler/industry-news/run
```

상태 확인:

```bash
curl http://localhost:4000/api/scheduler/industry-news
```

## 메종이 AI Agent

기본 무료 LLM은 Ollama `smollm2:135m`입니다. 더 좋은 한국어 품질이 필요하면 운영 장비에서 안정적으로 구동되는 Ollama 모델명으로 `OLLAMA_MODEL`을 교체합니다.

- 기본 역할: 국내 매트리스·침구·수면 업계 컨설턴트
- 대화 기억: 사용자별 대화는 최대 3일간만 저장하고 만료 시 자동 삭제
- 학습 자료: 채팅창에서 텍스트 파일, 자료집 메모, 캡처 이미지를 업로드하면 메종이 지식으로 저장
- 전자결재 지원: 행안부식 기안문 기본 원칙을 seed 지식으로 포함하고, 관리자 페르소나/추가 서식을 업로드해 확장 가능

```bash
docker exec infra-ollama-1 ollama pull smollm2:135m
curl http://localhost:4000/api/agent/status
curl -X POST http://localhost:4000/api/agent/chat \
  -H "content-type: application/json" \
  -d '{"context":"approval","message":"기안문 구성을 도와줘","draftTitle":"브랜드 자료집 배포","draftBody":"대리점에 새 브랜드 자료집을 배포하려고 합니다."}'
```

메종이는 전자결재 기안문, `industry-news` 요약, `product-catalog` 콘텐츠, 브랜드/카탈로그 태그 문서 메타데이터를 참조합니다.

관리자 페르소나 지정:

```bash
curl -X PUT http://localhost:4000/api/agent/admin/persona \
  -H "content-type: application/json" \
  -d '{"persona":"메종이는 프리미엄 매트리스와 침구 시장 컨설턴트로 답변한다."}'
```

파일/캡처 학습:

```bash
curl -X POST http://localhost:4000/api/agent/knowledge/upload \
  -F title="브랜드 자료집" \
  -F tags="브랜드,매트리스,침구" \
  -F memo="신규 브랜드 자료집" \
  -F file=@./brand-note.txt
```

## 주요 URL

- Web: `http://localhost:3000`
- API: `http://localhost:4000/healthz`
- Keycloak: `http://localhost:8080`
- MinIO Console: `http://localhost:9001`
- MailHog: `http://localhost:8025`
- Ollama: `http://localhost:11434`

## Phase 2 배포 체크

- `infra/keycloak/realm-export.json`: AD LDAP 설정과 AD 그룹→Keycloak 역할 매핑
- `infra/nginx/default.conf`: HTTPS 443 리버스 프록시와 HSTS
- `infra/postgres/init.sql`: 업무 모듈, 문서, 근태, 감사 로그 스키마
- `infra/docker-compose.local.yml`: PostgreSQL, MinIO, Keycloak, MailHog, Ollama, API, Web, Nginx
