import dotenv from "dotenv";
import { z } from "zod";

dotenv.config();

const envBoolean = z.preprocess((value) => {
  if (typeof value !== "string") {
    return value;
  }

  if (["true", "1", "yes", "on"].includes(value.toLowerCase())) {
    return true;
  }

  if (["false", "0", "no", "off"].includes(value.toLowerCase())) {
    return false;
  }

  return value;
}, z.boolean());

export const configSchema = z.object({
  NODE_ENV: z.string().default("development"),
  PORT: z.coerce.number().default(4000),
  DATABASE_URL: z.string().default("postgres://intranet:intranet@localhost:5432/intranet"),
  CORS_ORIGIN: z.string().default("http://localhost:3000"),
  KEYCLOAK_ISSUER: z.string().default("http://localhost:8080/realms/maejong-intranet"),
  KEYCLOAK_AUDIENCE: z.string().default("intranet-api"),
  AUTH_REQUIRED: envBoolean.default(false),
  MINIO_ENDPOINT: z.string().default("localhost"),
  MINIO_PORT: z.coerce.number().default(9000),
  MINIO_USE_SSL: envBoolean.default(false),
  MINIO_ACCESS_KEY: z.string().default("minioadmin"),
  MINIO_SECRET_KEY: z.string().default("minioadmin"),
  MINIO_BUCKET: z.string().default("documents"),
  SMTP_HOST: z.string().default("localhost"),
  SMTP_PORT: z.coerce.number().default(1025),
  SMTP_FROM: z.string().email().default("intranet@maejong.local"),
  AI_PROVIDER: z.enum(["ollama", "openai"]).default("ollama"),
  OLLAMA_BASE_URL: z.string().url().default("http://localhost:11434"),
  OLLAMA_MODEL: z.string().default("llama3.1"),
  OPENAI_API_KEY: z.string().optional(),
  OPENAI_MODEL: z.string().default("gpt-4o-mini"),
  INDUSTRY_NEWS_SCHEDULER_ENABLED: envBoolean.default(true),
  INDUSTRY_NEWS_CRON: z.string().default("0 9 * * 1-5"),
  INDUSTRY_NEWS_TIMEZONE: z.string().default("Asia/Seoul"),
  INDUSTRY_NEWS_RSS_URL: z.string().url().default("https://news.google.com/rss/search?q=%EC%9E%90%EB%8F%99%EC%B0%A8%20%EC%82%B0%EC%97%85&hl=ko&gl=KR&ceid=KR:ko"),
  INDUSTRY_NEWS_MAX_CANDIDATES: z.coerce.number().int().positive().default(10)
});

export const config = configSchema.parse(process.env);
