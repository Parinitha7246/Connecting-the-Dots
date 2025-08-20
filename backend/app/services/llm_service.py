import os
import json
import re
from typing import List, Dict

# Optional imports for LangChain-based hackathon test
from langchain_google_genai import ChatGoogleGenerativeAI

TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT", "30"))

class LLMError(Exception):
    pass

class LLMService:
    def __init__(self):
        self.provider = (os.getenv("LLM_PROVIDER") or "gemini").lower()
        self.model = os.getenv("GEMINI_MODEL") or os.getenv("OPENAI_MODEL") or os.getenv("OLLAMA_MODEL")

        print(f"[INFO] Initializing LLMService with provider: {self.provider}")

        if self.provider == "gemini":
            self._init_gemini()
        else:
            raise LLMError(f"Unsupported LLM_PROVIDER for LLMService: {self.provider}")

    def _init_gemini(self):
        try:
            import google.generativeai as genai
            print("[INFO] Gemini library imported successfully.")
        except ImportError as e:
            raise LLMError("google.generativeai library is required for GEMINI provider.") from e

        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            print("[INFO] Configuring Gemini with GOOGLE_APPLICATION_CREDENTIALS.")
        elif os.getenv("GEMINI_API_KEY"):
            print("[INFO] Configuring Gemini with GEMINI_API_KEY.")
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        else:
            raise LLMError("No Gemini credentials found. Set GEMINI_API_KEY or GOOGLE_APPLICATION_CREDENTIALS.")

        self._gemini = genai
        self._gemini_model = self.model or "gemini-1.5-flash"
        print(f"[INFO] Gemini initialized with model: {self._gemini_model}")

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        if self.provider == "gemini":
            return self._gen_gemini(prompt)
        else:
            raise LLMError(f"Provider '{self.provider}' generation logic not implemented.")

    def _gen_gemini(self, prompt: str):
        try:
            print(f"[INFO] Sending request to Gemini with model {self._gemini_model}...")
            model = self._gemini.GenerativeModel(self._gemini_model)
            response = model.generate_content(prompt)
            print("[INFO] Received response from Gemini.")
            return response.text.strip()
        except Exception as e:
            print(f"[ERROR] Gemini API call failed: {e}")
            raise LLMError(f"Gemini call failed: {e}")

    # --- Robust JSON enrichment with fallback ---
    def enrich_with_context(self, context_chunks: List[str], persona: str, task: str) -> dict:
        context = "\n---\n".join(context_chunks[:5])
        prompt = f"""
        Analyze the following text snippets retrieved from several documents. 
        The user is a '{persona}' performing the task: '{task}'.
        Your goal is to synthesize these snippets to find connections, contradictions, and deeper insights.

        CONTEXT SNIPPETS:
        ---
        {context}
        ---

        Based on the provided context ONLY, generate a structured JSON object with the following keys:
        - "themes": array of 3-5 strings
        - "insights": array of 2-3 strings
        - "did_you_know": a single string
        - "contradictions": a single string
        - "connections": array of 2 strings
        - "examples": array of 1-2 strings

        Your response MUST be a clean, valid JSON object and nothing else. Do not wrap it in markdown.
        """
        raw_response = self.generate(prompt)

        try:
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return json.loads(raw_response)
        except json.JSONDecodeError as e:
            print(f"[WARN] Initial JSON parse failed: {e}")
            print(f"Malformed string: {raw_response}")
            print("[INFO] Attempting LLM to fix JSON...")
            correction_prompt = f"""
            The following text is a malformed JSON object. Please fix it so it is valid JSON.
            Only return the JSON object.

            MALFORMED TEXT:
            ---
            {raw_response}
            ---

            Corrected JSON:
            """
            try:
                corrected_response = self.generate(correction_prompt)
                return json.loads(corrected_response)
            except Exception as final_e:
                print(f"[FATAL ERROR] LLM failed to correct JSON: {final_e}")
                raise LLMError("LLM failed to produce valid JSON after correction.")

    # --- Classify snippet relations ---
    def classify_snippet_relations(self, selection: str, snippets: List[Dict]) -> List[Dict]:
        snippet_context = ""
        for i, s in enumerate(snippets):
            snippet_text = s.get('snippet', s.get('text', ''))
            snippet_context += f"Snippet {i+1} (from document '{s.get('document')}'):\n\"{snippet_text}\"\n\n"
        prompt = f"""
        Analyze the following user's text selection and snippets to classify relation types.
        User selection:
        "{selection}"

        Snippets:
        {snippet_context}

        Generate JSON with "classifications": list of objects with keys:
        - "snippet_index": 1-based index
        - "relation_type": "overlap", "example", or "contradiction"
        """
        try:
            raw_response = self.generate(prompt, max_tokens=512, temperature=0.1)
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                classifications_data = json.loads(json_match.group(0))
                classifications = classifications_data.get("classifications", [])
                for c in classifications:
                    idx = c.get("snippet_index")
                    rel = c.get("relation_type")
                    if idx is not None and 1 <= idx <= len(snippets):
                        snippets[idx - 1]['relation_type'] = rel
            return snippets
        except Exception as e:
            print(f"[WARN] LLM snippet classification failed: {e}. Defaulting to 'related'.")
            for s in snippets:
                if 'relation_type' not in s:
                    s['relation_type'] = 'related'
            return snippets


# --- Hackathon-compliant standalone test function ---
def get_llm_response(messages: List[Dict]) -> str:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "gemini":
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        if os.getenv("GOOGLE_API_KEY"):
            llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0.3)
        elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.3)
        else:
            raise ValueError("Set GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS for Gemini.")

        try:
            print(f"[TEST SCRIPT] Invoking Gemini with model {model_name}...")
            response = llm.invoke(messages)
            print("[TEST SCRIPT] Received response.")
            return response.content
        except Exception as e:
            raise RuntimeError(f"LangChain Gemini call failed: {e}")

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


# --- Optional: standalone debug test ---
if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    try:
        reply = get_llm_response(messages)
        print("\nLLM Response:", reply)
    except Exception as e:
        print("\nError:", str(e))
