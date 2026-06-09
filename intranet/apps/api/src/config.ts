import dotenv from "dotenv";
import { z } from "zod";

dotenv.config();

const schema = z.object({
  NODE_ENV: z.string().default("development"),
  PORT: z.coerce.number().default(4000),
  DATABASE_URL: z.string().default("postgres://intranet:intranet@localhost:5432/intranet"),
  CORS_ORIGIN: z.string().default("http://localhost:3000"),
  KEYCLOAK_ISSUER: z.string().default("http://localhost:8080/realms/maejong-intranet"),
  KEYCLOAK_AUDIENCE: z.string().default("intranet-api"),
  AUTH_REQUIRED: z.coerce.boolean().default(false),
  MINIO_ENDPOINT: z.string().default("localhost"),
  MINIO_PORT: z.coerce.number().default(9000),
  MINIO_USE_SSL: z.coerce.boolean().default(false),
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
  OPENAI_MODEL: z.string().default("gpt-4o-mini")
});

export const config = schema.parse(process.env);
