import assert from "node:assert/strict";
import { test } from "node:test";
import request from "supertest";
import { createApp } from "./app.js";
import { configSchema } from "./config.js";
import { buildIndustryNewsBody } from "./services/industryNewsScheduler.js";

test("health endpoint reports API status", async () => {
  const response = await request(createApp()).get("/healthz").expect(200);
  assert.equal(response.body.service, "maejong-intranet-api");
});

test("module registry exposes all required intranet modules", async () => {
  const response = await request(createApp()).get("/api/modules").expect(200);
  const keys = response.body.modules.map((module: { key: string }) => module.key);

  assert.deepEqual(keys, [
    "notices",
    "industry-news",
    "qna",
    "policies",
    "approvals",
    "documents",
    "org-chart",
    "profile",
    "product-catalog",
    "dealers",
    "attendance",
    "admin"
  ]);
});

test("signin endpoint redirects to Keycloak authorization flow", async () => {
  const response = await request(createApp()).get("/api/auth/signin").expect(302);
  assert.match(response.header.location, /\/realms\/maejong-intranet\/protocol\/openid-connect\/auth/);
  assert.match(response.header.location, /client_id=intranet-web/);
  assert.match(response.header.location, /response_type=code/);
});

test("environment booleans parse string false correctly", () => {
  const parsed = configSchema.parse({
    AUTH_REQUIRED: "false",
    MINIO_USE_SSL: "false",
    SMTP_FROM: "intranet@maejong.local"
  });

  assert.equal(parsed.AUTH_REQUIRED, false);
  assert.equal(parsed.MINIO_USE_SSL, false);
});

test("industry news body stores source link and summary provider", () => {
  const body = buildIndustryNewsBody(
    {
      title: "테스트 업계뉴스",
      link: "https://example.com/news",
      published: "Tue, 09 Jun 2026 09:00:00 +0900",
      summarySource: "매트리스 신제품 출시",
      matchedKeywords: ["매트리스"],
      score: 21,
      scoreReasons: ["키워드 1개 일치", "노출 빈도 1회", "상업/광고 신호 1개"]
    },
    "요약 본문",
    "fallback"
  );

  assert.match(body, /요약 본문/);
  assert.match(body, /출처: https:\/\/example.com\/news/);
  assert.match(body, /선정 키워드: 매트리스/);
  assert.match(body, /중요도 점수: 21/);
  assert.match(body, /요약 방식: RSS 원문 기반 fallback/);
});
