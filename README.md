# DocuWise – Adobe India Hackathon 2025

DocuWise is a full-stack application that transforms PDF libraries into interactive, AI-powered knowledge companions. It enables users to upload, browse, analyze, and interact with documents, while providing generative AI insights, semantic snippet recommendations, and even podcast-style narrations.

## ✨ Features

### 📂 Document Management
- Upload single current PDFs and multiple historical PDFs.
- Highlight the latest "current" document (color-coded for easy identification).
- Delete PDFs directly from the sidebar.

### 📖 High-Fidelity Viewer
- Seamless PDF rendering using Adobe PDF Embed API.
- Sidebar navigation and jump-to-snippet functionality.

### 🤖 AI-Powered Insights
- Extract cross-document snippets dynamically.
- Insights categorized with color codes:
  - 🟢 Did you know? facts
  - 🔵 Examples
  - 🔴 Contradictions / Counterpoints
  - 🟡 Key Takeaways

### 🎙 Podcast Generation
- Generate natural-sounding audio summaries of insights using Google TTS.
- Multi-speaker mode supported.

### 💬 AI Chat
- Ask follow-up, context-aware questions about any PDF section.

### 🌐 Hybrid Online/Offline Mode
- **Online Mode** → Uses Gemini 2.5 LLM + Google TTS for powerful insights.
- **Offline Mode** → Local inference for faster but lightweight results.

---

## 📂 Project Structure

```
Connecting-the-Dots/
│
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI entry
│   │   ├── routes/             # API endpoints (/ingest, /recommend, /insights, /podcast)
│   │   ├── services/           # LLM + TTS services
│   │   └── engines/
│   │       ├── round1a/        # Challenge 1A: PDF structure extraction
│   │       └── round1b/        # Challenge 1B: Persona-driven insights
│   ├── storage/                # Uploaded documents, outputs
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                  # React + Vite + TS frontend
│   ├── src/
│   │   ├── components/         # PDF viewer, Sidebar, Snippet cards
│   │   ├── api/                # Axios API clients
│   │   ├── store/              # Zustand state management
│   │   └── App.tsx
│   ├── public/
│   ├── .env.example
│   └── package.json
│
└── README.md
```

---

## 🔑 Environment Variables

**Frontend (`frontend/.env`):**
```
VITE_BACKEND_URL=http://localhost:8080
ADOBE_EMBED_API_KEY=af20ec0567274e08b77b9473d6f0485f 
```

**Backend / Docker:**  
These are passed at runtime (not hardcoded in code):

- `ADOBE_EMBED_API_KEY` → (provided by candidate)
- `LLM_PROVIDER=gemini`
- `GOOGLE_APPLICATION_CREDENTIALS=/credentials/adbe-gcp.json`
- `GEMINI_MODEL=gemini-2.5-flash`
- `TTS_PROVIDER=gcp`
- `AZURE_TTS_KEY`, `AZURE_TTS_ENDPOINT` (for evaluation, set by Adobe)

---

## 🖥 Local Development

### 1. Backend
```sh
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

# Run with Gemini + Google TTS (online mode)
$env:MODE="online"
$env:GEMINI_API_KEY="your_gemini_api_key"
$env:LLM_PROVIDER="gemini"
$env:GEMINI_MODEL="gemini-2.5-flash"
$env:TTS_PROVIDER="gcp"

uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 2. Frontend
```sh
cd frontend
npm install
npm run dev
```

- Backend → http://localhost:8080
- Frontend → http://localhost:5173

---

## 🐳 Docker (Evaluation Mode)

**Build**
```sh
docker build --platform linux/amd64 -t docuwise .
```

**Run**
```sh
docker run \
  -v /path/to/credentials:/credentials \
  -e ADOBE_EMBED_API_KEY=<ADOBE_EMBED_API_KEY> \
  -e LLM_PROVIDER=gemini \
  -e GOOGLE_APPLICATION_CREDENTIALS=/credentials/adbe-gcp.json \
  -e GEMINI_MODEL=gemini-2.5-flash \
  -e TTS_PROVIDER=azure \
  -e AZURE_TTS_KEY=<TTS_KEY> \
  -e AZURE_TTS_ENDPOINT=<TTS_ENDPOINT> \
  -p 8080:8080 docuwise
```

👉 Open: http://localhost:8080  
This will serve both frontend + backend from the same container.

---

## 📦 Dependencies

**Main backend dependencies (`backend/requirements.txt`):**
- langchain==0.3.27
- langchain-openai==0.3.29
- langchain-google-genai==2.0.10
- langchain-community==0.3.27
- google-generativeai==0.8.5
- google-cloud-texttospeech==2.27.0
- pydub>=0.25.0
- requests>=2.25.0
- fastapi
- uvicorn

**Frontend:**
- React + Vite + TypeScript
- Zustand (state)
- TailwindCSS (styling)
- Axios (API)

---

## 🧪 Notes for Evaluators

- ✅ Single Docker image serves frontend + backend on port 8080.
- ✅ No keys are hardcoded — all are injected via environment variables.
- ✅ Supports Gemini 2.5 for LLM and Google/Azure TTS for podcasting.
- ✅ Works fully offline with fallback
