import { Router } from "express";
import { z } from "zod";
import { summarizeForCardNews } from "../services/ai.js";
import { sendCardNewsEmail } from "../services/mailer.js";

export const aiRouter = Router();

const cardNewsSchema = z.object({
  prompt: z.string().min(1),
  recipients: z.array(z.string().email()).default([])
});

aiRouter.post("/card-news", async (req, res) => {
  const input = cardNewsSchema.parse(req.body);
  const summary = await summarizeForCardNews(input.prompt);

  if (input.recipients.length > 0) {
    await sendCardNewsEmail(input.recipients, "[매종 인트라넷] 카드뉴스 요약", `<p>${summary.replace(/\n/g, "<br />")}</p>`);
  }

  return res.json({ summary, emailed: input.recipients.length });
});
