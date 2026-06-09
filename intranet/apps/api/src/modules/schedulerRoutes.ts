import { Router } from "express";
import { requireRole } from "../auth/keycloak.js";
import { getIndustryNewsSchedulerStatus, runIndustryNewsScheduler } from "../services/industryNewsScheduler.js";

export const schedulerRouter = Router();

schedulerRouter.use(requireRole("admin"));

schedulerRouter.get("/industry-news", (_req, res) => {
  res.json(getIndustryNewsSchedulerStatus());
});

schedulerRouter.post("/industry-news/run", async (_req, res) => {
  const result = await runIndustryNewsScheduler("manual");
  res.json(result);
});
