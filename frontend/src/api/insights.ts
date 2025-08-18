import { api } from "./client";
import type { InsightsResponse, RecommendResponse } from "./types"; // <-- Added RecommendResponse
import { DEFAULT_PERSONA, DEFAULT_TASK } from "../config";

/**
 * Fetches relevant snippets from the backend based on selected text.
 * This function calls the /recommend endpoint.
 */
export async function getRecommendations(persona: string, job: string, top_k = 5): Promise<RecommendResponse> {
  // Use URLSearchParams for form-encoded data, which is common in Python backends.
  const form = new URLSearchParams();
  form.append("persona", persona);
  form.append("job", job);
  form.append("top_k", String(top_k));

  const { data } = await api.post<RecommendResponse>("/recommend", form.toString(), {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

/**
 * Fetches AI-generated insights based on a list of text sections.
 */
export async function getInsights(section_texts: string[], persona = DEFAULT_PERSONA, task = DEFAULT_TASK) {
  const payload = { section_texts, persona, task };
  const { data } = await api.post<InsightsResponse>("/insights", payload);
  return data;
}

/**
 * Sends a message to the chat endpoint with context.
 */
export async function chat(message: string, context: string[]) {
  try {
    const { data } = await api.post("/chat", { message, context });
    return { text: data?.text ?? "Sorry, I couldn't process that." };
  } catch (error) {
    // Fallback in case the /chat endpoint doesn't exist.
    console.error("Chat endpoint failed, falling back to insights:", error);
    const i = await getInsights(context, "Chat user", message);
    const text = i?.parsed?.insights?.join("\n• ") || i?.raw || "No response available.";
    return { text };
  }
}