# 매종 인트라넷

Next.js 프론트엔드, Express API, PostgreSQL, MinIO, Keycloak, Nginx, SMTP, Ollama/OpenAI 전환형 AI를 포함한 Phase 2 준비용 인트라넷 구현입니다.

> 참고: 요청에 언급된 `인트라넷 구축계획.pdf`는 현재 저장소에 없어, 요청 본문에 명시된 모듈과 Phase 2 항목을 기준으로 구조를 영속화했습니다.

## 포함 모듈

- 공지사항, 산업뉴스, Q&A, 규정, 전자결재, 문서함, 조직도, 내 프로필, 제품 카탈로그, 대리점, 근태, 관리자
- Maejong AI 카드뉴스 요약: `AI_PROVIDER=ollama|openai`
- 감사 로그: 로그인 확장 지점, 다운로드, 결재, 근태, 문서 업로드
- 산업뉴스 스케줄러: 월~금 오전 9시(`Asia/Seoul`) RSS 1건 수집, 요약, `industry-news` 업로드

## 실행

```bash
cd intranet
npm install
npm run dev
```

로컬 인프라까지 실행:

```bash
cd intranet
mkdir -p infra/nginx/certs
openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
  -keyout infra/nginx/certs/intranet.key \
  -out infra/nginx/certs/intranet.crt \
  -subj "/CN=localhost"
docker compose -f infra/docker-compose.local.yml up --build
```

`infra/nginx/certs/`는 로컬 개발용 인증서 위치이며 Git에는 저장하지 않습니다.

## 산업뉴스 스케줄러

기본값은 평일 오전 9시 1건 업로드입니다.

```bash
INDUSTRY_NEWS_SCHEDULER_ENABLED=true
INDUSTRY_NEWS_CRON="0 9 * * 1-5"
INDUSTRY_NEWS_TIMEZONE=Asia/Seoul
```

오늘 수동으로 1건 실행:

```bash
curl -X POST http://localhost:4000/api/scheduler/industry-news/run
```

상태 확인:

```bash
curl http://localhost:4000/api/scheduler/industry-news
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
