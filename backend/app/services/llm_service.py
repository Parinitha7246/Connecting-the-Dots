# backend/app/services/llm_service.py
import os
import json
import time

TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT", "20"))

class LLMError(Exception):
    pass

class LLMService:
    def __init__(self):
        self.provider = (os.getenv("LLM_PROVIDER") or "").lower()
        self.model = os.getenv("GEMINI_MODEL") or os.getenv("OPENAI_MODEL") or os.getenv("OLLAMA_MODEL")

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

    # ---------- Gemini ----------
    def _init_gemini(self):
        try:
            import google.generativeai as genai
        except Exception as e:
            raise LLMError("google.generativeai library is required for GEMINI provider.") from e

        api_key = os.getenv("GEMINI_API_KEY")
        creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if api_key:
            genai.configure(api_key=api_key)
        elif creds and os.path.exists(creds):
            genai.configure(credentials=creds)
        else:
            raise LLMError("No Gemini credentials found. Set GEMINI_API_KEY or GOOGLE_APPLICATION_CREDENTIALS.")

        self._gemini = genai
        self._gemini_model = self.model or "gemini-1.5-flash"

    # ---------- OpenAI / Azure ----------
    def _init_openai(self):
        try:
            from openai import OpenAI
        except Exception as e:
            raise LLMError("openai python package is required for openai/azure provider.") from e

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMError("OPENAI_API_KEY is required for openai/azure provider.")

        if self.provider == "azure":
            api_base = os.getenv("AZURE_OPENAI_BASE") or os.getenv("OPENAI_API_BASE")
            api_version = os.getenv("AZURE_API_VERSION")
            self._openai_client = OpenAI(api_key=api_key, base_url=f"{api_base}/openai/deployments/{self.model}", default_query={"api-version": api_version})
        else:
            self._openai_client = OpenAI(api_key=api_key)

        self._openai_model = self.model or "gpt-4o"

    # ---------- Ollama ----------
    def _init_ollama(self):
        import requests
        self._ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._ollama_model = self.model or os.getenv("OLLAMA_MODEL", "llama3")

    # ---------- Public API ----------
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        if self.provider == "gemini":
            return self._gen_gemini(prompt, max_tokens)
        elif self.provider in ("openai", "azure"):
            return self._gen_openai(prompt, max_tokens, temperature)
        elif self.provider == "ollama":
            return self._gen_ollama(prompt, max_tokens, temperature)
        else:
            raise LLMError("No provider initialized")

    # ---------- Provider Implementations ----------
    def _gen_gemini(self, prompt: str, max_tokens: int):
        try:
            resp = self._gemini.GenerativeModel(self._gemini_model).generate_content(prompt)
            return resp.text.strip()
        except Exception as e:
            raise LLMError(f"Gemini call failed: {e}")

    def _gen_openai(self, prompt: str, max_tokens: int, temperature: float):
        try:
            resp = self._openai_client.chat.completions.create(
                model=self._openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            raise LLMError(f"OpenAI/Azure call failed: {e}")

    def _gen_ollama(self, prompt: str, max_tokens: int, temperature: float):
        import requests
        url = f"{self._ollama_base}/v1/generate"
        payload = {"model": self._ollama_model, "prompt": prompt, "max_tokens": max_tokens}
        try:
            r = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
            r.raise_for_status()
            data = r.json()
            if "text" in data:
                return data["text"]
            if "choices" in data and data["choices"]:
                return data["choices"][0].get("text", "")
            return json.dumps(data)
        except Exception as e:
            raise LLMError(f"Ollama call failed: {e}")
        
    def enrich_with_context(self, offline_chunks, persona, task):
        context = "\n\n".join(offline_chunks[:5]) if isinstance(offline_chunks, list) else ""
        prompt = f"""
        Persona: {persona}
        Task: {task}
        Context (from verified documents):
        {context}

        Produce JSON:
        - insights: 3 short bullets
        - did_you_know: 1 fact
        - contradictions: 1 point
        - connections: 2 cross-doc links
        """
        return self.generate(prompt, max_tokens=500, temperature=0.2)





