import axios from "axios";
import { BACKEND_URL } from "../config";

export const api = axios.create({
  baseURL: BACKEND_URL,
  // This is the crucial change. We are giving the backend
  // up to 2 minutes (120,000ms) to respond, which should be
  // more than enough for PDF processing and embedding.
  timeout: 120000, 
});

// This console log helps confirm the connection is correct.
if (!BACKEND_URL) {
  console.error("FATAL ERROR: VITE_BACKEND_URL is not defined in your .env file!");
  alert("FATAL ERROR: The backend URL is not configured. Please check the console.");
} else {
  console.log(`API client is configured to talk to the backend at: ${BACKEND_URL}`);
}