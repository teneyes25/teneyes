import { Router } from "express";
import { z } from "zod";
import { config } from "../config.js";
import { chatWithMaejongAgent, collectAgentSources } from "../services/maejongAgent.js";

export const agentRouter = Router();

const chatSchema = z.object({
  message: z.string().min(1),
  context: z.enum(["general", "approval", "industry-news", "brand"]).default("general"),
  draftTitle: z.string().optional(),
  draftBody: z.string().optional()
});

agentRouter.get("/status", async (_req, res) => {
  const sources = await collectAgentSources({ message: "브랜드 업계뉴스 전자결재", context: "general" });

  res.json({
    name: "메종이",
    enabled: true,
    provider: config.AI_PROVIDER,
    model: config.AI_PROVIDER === "ollama" ? config.OLLAMA_MODEL : config.OPENAI_MODEL,
    roles: ["사내 컨설턴트", "전자결재 기안 코치", "업계뉴스 분석", "브랜드 자료 상담"],
    knowledgeSources: sources.map((source) => ({
      type: source.type,
      title: source.title
    }))
  });
});

agentRouter.post("/chat", async (req, res) => {
  const input = chatSchema.parse(req.body);
  const result = await chatWithMaejongAgent(input);
  res.json(result);
});
