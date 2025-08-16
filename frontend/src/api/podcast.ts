import { api } from "./client";
import type { PodcastResponse } from "./types";
import { DEFAULT_PERSONA, DEFAULT_TASK } from "../config";

export async function createPodcast(section_texts: string[], persona=DEFAULT_PERSONA, task=DEFAULT_TASK) {
  const { data } = await api.post<PodcastResponse>("/podcast", { section_texts, persona, task });
  return data;
}
