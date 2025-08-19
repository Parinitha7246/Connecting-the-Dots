// Blueprint for a single snippet object from the backend
export type Snippet = {
  document: string;
  page_number?: number;
  excerpt: string;
  snippet: string;
  text: string;
  score: number;
  doc_id: string; 
  doc_name: string;
};

// Blueprint for a single document object from the /documents endpoint
export type DocMeta = { id: string; name: string; url: string; pages?: number };

// This is the blueprint for the full response from the /recommend endpoint.
export type HybridResponse = {
  source: string;
  offline: {
    recommendations: Snippet[];
  };
  online?: string | {
    themes?: string[]; 
    insights?: string[];
    did_you_know?: string;
    contradictions?: string;
    connections?: string[];
    examples?: string[]; // <-- ADDED THIS NEW FIELD
  };
  online_error?: string;
};

// We keep these for other parts of the app, like the podcast feature.
export type InsightsResponse = {
  parsed: {
    themes?: string[]; 
    insights: string[];
    did_you_know: string;
    contradictions: string;
    connections: string[];
    examples?: string[];
  };
  raw: string;
};

export type PodcastResponse = {
  script: string;
  tts?: { url?: string; saved_path?: string };
};