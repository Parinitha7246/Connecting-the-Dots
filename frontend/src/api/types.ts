// --- Blueprint for a single snippet object (merged + cleaned) ---
export type Snippet = {
  // --- Core fields ---
  document: string;          // raw backend reference
  doc_id: string;            // reliable ID/filename for loading
  doc_name: string;          // pretty title for display
  page_number?: number;      // page where snippet comes from
  text: string;              // raw/full text
  score: number;             // relevance score

  // --- Legacy / Compatibility aliases ---
  document_id?: string;      // alias for backend/Adobe consistency
  document_name?: string;    // alias for frontend display
  snippet_text?: string;     // cleaner snippet field
  excerpt?: string;          // short excerpt (legacy)
  snippet?: string;          // snippet body (legacy)

  // --- Extended metadata ---
  relation_type?: "overlap" | "example" | "contradiction" | "related" | "supporting";
  section_heading?: string;  // optional section/heading label
  coordinates?: number[];    // Adobe API expects [x0, y0, x1, y1]
};

// --- Blueprint for a single document object ---
export type DocMeta = {
  id: string;       // unique doc identifier
  name: string;     // display name
  url: string;      // storage or fetch URL
  pages?: number;   // number of pages (optional)
};

// --- Blueprint for the /recommend endpoint response ---
export type RecommendResponse = {
  source: string;
  recommendations: Snippet[];
};

// --- Blueprint for the /hybrid recommend response ---
export type HybridResponse = {
  source: string;
  recommendations: Snippet[];
  online?: string | {
    themes?: string[];
    insights?: string[];
    did_you_know?: string;
    contradictions?: string;
    connections?: string[];
    examples?: string[];
  };
  online_error?: string;
};

// --- Blueprint for the /insights endpoint response ---
export type InsightsResponse = {
  source: string;
  parsed: {
    themes?: string[];
    insights?: string[];
    did_you_know?: string;
    contradictions?: string;
    connections?: string[];
    examples?: string[];
  };
  raw?: string;
};

// --- Blueprint for the /podcast endpoint response ---
export type PodcastResponse = {
  script: string;
  tts?: { url?: string; audio_path?: string };
};
