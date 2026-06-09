import OpenAI from "openai";
import { config } from "../config.js";

export type ChatMessage = {
  role: "system" | "user" | "assistant";
  content: string;
};

export async function chatWithLlm(messages: ChatMessage[]) {
  if (config.AI_PROVIDER === "openai") {
    if (!config.OPENAI_API_KEY) {
      throw new Error("OPENAI_API_KEY is required when AI_PROVIDER=openai");
    }

    const client = new OpenAI({ apiKey: config.OPENAI_API_KEY });
    const response = await client.chat.completions.create({
      model: config.OPENAI_MODEL,
      messages
    });

    return response.choices[0]?.message.content ?? "";
  }

  const response = await fetch(`${config.OLLAMA_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      model: config.OLLAMA_MODEL,
      stream: false,
      options: {
        num_ctx: 2048,
        num_predict: 320,
        temperature: 0.2
      },
      messages
    })
  });

  if (!response.ok) {
    throw new Error(`Ollama request failed: ${response.status}`);
  }

  const payload = (await response.json()) as { message?: { content?: string } };
  return payload.message?.content ?? "";
}

export async function summarizeForCardNews(prompt: string) {
  return chatWithLlm([
    { role: "system", content: "사내 인트라넷 카드뉴스용으로 핵심만 한국어로 요약합니다." },
    { role: "user", content: prompt }
  ]);
}
