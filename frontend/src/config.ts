export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL as string;
export const ADOBE_CLIENT_ID = import.meta.env.VITE_ADOBE_EMBED_API_KEY as string;

console.log("Key from .env file:", import.meta.env.VITE_ADOBE_EMBED_API_KEY);
// Tab defaults / constants
export const MAX_SNIPPETS = 5;
export const DEFAULT_PERSONA = "General researcher";
export const DEFAULT_TASK = "Understand and compare the selected concept across documents";
