import assert from "node:assert/strict";
import { test } from "node:test";
import request from "supertest";
import { createApp } from "./app.js";

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
