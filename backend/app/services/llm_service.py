import os
import json
import re  # Import the regular expression module for cleaning JSON

TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT", "30"))  # Increased timeout for LLM calls


class LLMError(Exception):
    pass


class LLMService:
    def __init__(self):
        self.provider = (os.getenv("LLM_PROVIDER") or "gemini").lower()
        self.model = os.getenv("GEMINI_MODEL") or os.getenv("OPENAI_MODEL") or os.getenv("OLLAMA_MODEL")

        print(f"[INFO] Initializing LLMService with provider: {self.provider}")

        if not self.provider:
            raise LLMError("LLM_PROVIDER is not set. Set to 'gemini'/'openai'/'azure'/'ollama'.")

        if self.provider == "gemini":
            self._init_gemini()
        elif self.provider in ("openai", "azure"):
            self._init_openai()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            raise LLMError(f"Unsupported LLM_PROVIDER: {self.provider}")

    def _init_gemini(self):
        try:
            import google.generativeai as genai
            print("[INFO] Gemini library imported successfully.")
        except Exception as e:
            raise LLMError("google.generativeai library is required for GEMINI provider.") from e

        # This logic correctly handles credentials for the hackathon environment
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            print("[INFO] Configuring Gemini with GOOGLE_APPLICATION_CREDENTIALS.")
            # No explicit configure call is needed when using application default credentials
        elif os.getenv("GEMINI_API_KEY"):
            print("[INFO] Configuring Gemini with GEMINI_API_KEY.")
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        else:
            raise LLMError("No Gemini credentials found. Set GEMINI_API_KEY or GOOGLE_APPLICATION_CREDENTIALS.")

        self._gemini = genai
        self._gemini_model = self.model or "gemini-1.5-flash"
        print(f"[INFO] Gemini initialized with model: {self._gemini_model}")

    def _init_openai(self):
        # ... (openai init logic remains the same)
        pass

    def _init_ollama(self):
        # ... (ollama init logic remains the same)
        pass

    # --- GENERATION DISPATCH ---
    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        if self.provider == "gemini":
            return self._gen_gemini(prompt)
        # Add elif blocks here for openai/ollama if you need them
        else:
            raise LLMError(f"Provider '{self.provider}' is configured, but its generation logic is not implemented in generate().")

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

    # --- EXISTING FUNCTION: enrich_with_context ---
    def enrich_with_context(self, context_chunks: list[str], persona: str, task: str):
        context = "\n---\n".join(context_chunks[:5])

        prompt = f"""
        Analyze the following text snippets retrieved from several documents. The user is a '{persona}' performing the task: '{task}'.
        Your goal is to synthesize these snippets to find connections, contradictions, and deeper insights that are not obvious.
        Do not simply summarize each snippet. Your value is in creating new knowledge by connecting the dots between the provided context.

        CONTEXT SNIPPETS:
        ---
        {context}
        ---

        Based on the provided context ONLY, generate a structured JSON object with the following keys.
        The JSON object must be clean, valid, and not enclosed in markdown backticks.

        - "themes": An array of 3-5 key themes or topics present across the snippets.
        - "insights": An array of 2-3 bullet-point "Key Takeaways" derived from the context.
        - "did_you_know": A single, interesting "Did you know?" fact discovered from the snippets, phrased as a question or statement.
        - "contradictions": A single string describing a potential contradiction or differing viewpoint found between snippets. If none, state that the snippets are in agreement.
        - "connections": An array of 2 "Cross-document inspirations" or links between ideas found in different snippets.
        - "examples": An array of 1-2 concrete examples mentioned in the text that illustrate a key point.

        Generate the JSON now.
        """
        raw_response = self.generate(prompt)

        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            return json_match.group(0)

        print(f"[WARN] Could not find a valid JSON object in the LLM response. Returning raw text.")
        return f'{{"insights": ["LLM returned non-JSON response: {raw_response}"]}}'

    # --- NEW FUNCTION: classify_snippet_relations ---
    def classify_snippet_relations(self, selection: str, snippets: list[dict]) -> list[dict]:
        """
        Uses an LLM to classify the relationship of each snippet to the user's selection.
        """
        # Create a numbered list of snippets for the LLM to reference
        snippet_context = ""
        for i, s in enumerate(snippets):
            # Use the shorter, cleaner 'snippet' text for the prompt
            snippet_text = s.get('snippet', s.get('text', ''))
            snippet_context += f"Snippet {i+1} (from document '{s.get('document')}'):\n\"{snippet_text}\"\n\n"

        prompt = f"""
        Analyze the following user's text selection and the numbered snippets retrieved from a document library.
        For each snippet, determine its relationship to the user's selection.

        USER'S SELECTION: "{selection}"

        RETRIEVED SNIPPETS:
        {snippet_context}

        TASK:
        For each snippet, classify its relationship to the USER'S SELECTION.
        The valid relationship types are: "overlap", "example", "contradiction", or "related".

        - "overlap": The snippet discusses the exact same concept or provides directly supporting information.
        - "example": The snippet provides a specific instance, case study, or data point illustrating the selection.
        - "contradiction": The snippet presents an opposing viewpoint or highlights a limitation of the concept in the selection.
        - "related": The snippet discusses a connected topic but is not a direct overlap, example, or contradiction.

        Your response MUST be a clean JSON object containing a single key "classifications", which is a list of objects.
        Each object in the list must have two keys: "snippet_index" (the number of the snippet) and "relation_type" (the classification string).

        Example of a perfect JSON output format:
        {{
          "classifications": [
            {{ "snippet_index": 1, "relation_type": "overlap" }},
            {{ "snippet_index": 2, "relation_type": "example" }},
            {{ "snippet_index": 3, "relation_type": "contradiction" }}
          ]
        }}

        Generate the JSON now.
        """

        try:
            raw_response = self.generate(prompt, max_tokens=512, temperature=0.1)
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                classifications_data = json.loads(json_match.group(0))
                classifications = classifications_data.get("classifications", [])
                for classification in classifications:
                    index = classification.get("snippet_index")
                    relation = classification.get("relation_type")
                    if index is not None and 1 <= index <= len(snippets):
                        snippets[index - 1]['relation_type'] = relation
            return snippets
        except Exception as e:
            print(f"[WARN] LLM snippet classification failed: {e}. Falling back to default labels.")
            for s in snippets:
                if 'relation_type' not in s:
                    s['relation_type'] = 'related'
            return snippets