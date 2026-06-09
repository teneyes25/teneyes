import { Router } from "express";
import multer from "multer";
import { z } from "zod";
import { requireRole } from "../auth/keycloak.js";
import { config } from "../config.js";
import { extractUploadText, getAgentPersona, saveAgentKnowledge, setAgentPersona } from "../services/agentMemory.js";
import { chatWithMaejongAgent, collectAgentSources } from "../services/maejongAgent.js";

export const agentRouter = Router();
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 20 * 1024 * 1024 } });

const chatSchema = z.object({
  message: z.string().min(1),
  context: z.enum(["general", "approval", "industry-news", "brand"]).default("general"),
  draftTitle: z.string().optional(),
  draftBody: z.string().optional(),
  conversationId: z.string().uuid().optional()
});

const personaSchema = z.object({
  persona: z.string().min(1)
});

agentRouter.get("/status", async (_req, res) => {
  const sources = await collectAgentSources({ message: "브랜드 업계뉴스 전자결재", context: "general" });

  res.json({
    name: "메종이",
    enabled: true,
    provider: config.AI_PROVIDER,
    model: config.AI_PROVIDER === "ollama" ? config.OLLAMA_MODEL : config.OPENAI_MODEL,
    persona: await getAgentPersona(),
    roles: ["사내 컨설턴트", "전자결재 기안 코치", "업계뉴스 분석", "브랜드 자료 상담"],
    knowledgeSources: sources.map((source) => ({
      type: source.type,
      title: source.title
    }))
  });
});

agentRouter.post("/chat", async (req, res) => {
  const input = chatSchema.parse(req.body);
  const result = await chatWithMaejongAgent({
    ...input,
    userId: req.user?.id ?? "dev-user"
  });
  res.json(result);
});

agentRouter.post("/knowledge/upload", upload.single("file"), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: "학습할 파일이 필요합니다." });
  }

  const memo = typeof req.body.memo === "string" ? req.body.memo : undefined;
  const sourceType = req.file.mimetype.startsWith("image/") ? "screenshot" : "upload";
  const content = await extractUploadText(req.file, memo);
  const tags = typeof req.body.tags === "string"
    ? req.body.tags.split(",").map((tag: string) => tag.trim()).filter(Boolean)
    : ["upload", sourceType];

  const id = await saveAgentKnowledge({
    title: typeof req.body.title === "string" && req.body.title ? req.body.title : req.file.originalname,
    content,
    sourceType,
    tags,
    createdBy: req.user?.id ?? "dev-user",
    metadata: {
      fileName: req.file.originalname,
      mimeType: req.file.mimetype,
      size: req.file.size,
      memo
    }
  });

  res.status(201).json({
    id,
    sourceType,
    learned: true,
    extractedPreview: content.slice(0, 500)
  });
});

agentRouter.put("/admin/persona", requireRole("admin"), async (req, res) => {
  const input = personaSchema.parse(req.body);
  await setAgentPersona(input.persona);
  res.json({ updated: true, persona: input.persona });
});
