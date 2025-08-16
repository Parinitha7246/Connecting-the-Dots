import { api } from "./client";
import type { InsightsResponse } from "./types";
import { DEFAULT_PERSONA, DEFAULT_TASK } from "../config";

export async function getInsights(section_texts: string[], persona=DEFAULT_PERSONA, task=DEFAULT_TASK) {
  const payload = { section_texts, persona, task };
  const { data } = await api.post<InsightsResponse>("/insights", payload);
  return data;
}

// optional chat endpoint; fallback to insights
export async function chat(message: string, context: string[]) {
  try {
    const { data } = await api.post("/chat", { message, context });
    return { text: data?.text ?? "" };
  } catch {
    const i = await getInsights(context, "Chat user", message);
    const text = i?.parsed?.insights?.join("\n• ") || i?.raw || "No response";
    return { text };
  }
}
