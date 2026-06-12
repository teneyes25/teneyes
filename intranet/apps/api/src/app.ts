import cors from "cors";
import express from "express";
import helmet from "helmet";
import { requireAuth } from "./auth/keycloak.js";
import { config } from "./config.js";
import { adminRouter } from "./modules/adminRoutes.js";
import { agentRouter } from "./modules/agentRoutes.js";
import { aiRouter } from "./modules/aiRoutes.js";
import { approvalRouter } from "./modules/approvalRoutes.js";
import { attendanceRouter } from "./modules/attendanceRoutes.js";
import { authRouter } from "./modules/authRoutes.js";
import { contentRouter } from "./modules/contentRoutes.js";
import { documentRouter } from "./modules/documentRoutes.js";
import { schedulerRouter } from "./modules/schedulerRoutes.js";

export function createApp() {
  const app = express();
  const corsOrigins = config.CORS_ORIGINS.split(",").map((origin) => origin.trim()).filter(Boolean);

  app.use(helmet());
  app.use(cors({
    origin: (origin, callback) => {
      if (!origin || corsOrigins.includes(origin)) {
        callback(null, true);
        return;
      }

      callback(new Error(`허용되지 않은 CORS origin입니다: ${origin}`));
    },
    credentials: true
  }));
  app.use(express.json({ limit: "2mb" }));

  app.get("/healthz", (_req, res) => {
    res.json({ ok: true, service: "maejong-intranet-api" });
  });

  app.use("/api/auth", authRouter);
  app.use(requireAuth);
  app.use("/api/attendance", attendanceRouter);
  app.use("/api/approvals", approvalRouter);
  app.use("/api/documents", documentRouter);
  app.use("/api/agent", agentRouter);
  app.use("/api/admin", adminRouter);
  app.use("/api/ai", aiRouter);
  app.use("/api/scheduler", schedulerRouter);
  app.use("/api", contentRouter);

  app.use((error: unknown, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
    const message = error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.";
    res.status(400).json({ message });
  });

  return app;
}
