import OpenAI from "openai";
import { config } from "../config.js";

export async function summarizeForCardNews(prompt: string) {
  if (config.AI_PROVIDER === "openai") {
    if (!config.OPENAI_API_KEY) {
      throw new Error("OPENAI_API_KEY is required when AI_PROVIDER=openai");
    }

    const client = new OpenAI({ apiKey: config.OPENAI_API_KEY });
    const response = await client.chat.completions.create({
      model: config.OPENAI_MODEL,
      messages: [
        { role: "system", content: "사내 인트라넷 카드뉴스용으로 핵심만 한국어로 요약합니다." },
        { role: "user", content: prompt }
      ]
    });

    return response.choices[0]?.message.content ?? "";
  }

  const response = await fetch(`${config.OLLAMA_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      model: config.OLLAMA_MODEL,
      stream: false,
      messages: [
        { role: "system", content: "사내 인트라넷 카드뉴스용으로 핵심만 한국어로 요약합니다." },
        { role: "user", content: prompt }
      ]
    })
  });

  if (!response.ok) {
    throw new Error(`Ollama request failed: ${response.status}`);
  }

  const payload = (await response.json()) as { message?: { content?: string } };
  return payload.message?.content ?? "";
}
