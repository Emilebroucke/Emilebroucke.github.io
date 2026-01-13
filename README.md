# NotebookLM-Style Local App

This repository now includes a complete NotebookLM-style app with a FastAPI backend and a Vite + React frontend.

## Structure

- `backend/` – FastAPI API for ingestion, indexing, retrieval, and streaming chat.
- `frontend/` – Vite React UI for notebooks, sources, and chat.

## Quick start

```bash
# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Set env vars
export LLM_PROVIDER=openai
export LLM_API_KEY=YOUR_KEY

uvicorn backend.app.main:app --reload --port 8000
```

```bash
# Frontend
cd frontend
npm install
npm run dev
```

## Environment variables

- `LLM_PROVIDER` = `openai` | `anthropic` | `gemini` | `local`
- `LLM_BASE_URL` = optional override (defaults to provider URL)
- `LLM_API_KEY` = provider key (required)
- `LLM_MODEL` = model name
- `EMBEDDING_MODEL` = sentence-transformers model
- `MAX_UPLOAD_MB` = upload size limit
- `DATA_DIR` = location for project indexes (default: `backend/data`)

## Provider notes

- `local` uses OpenAI-compatible API (e.g., Ollama, vLLM).
- For Anthropic/Gemini, set `LLM_PROVIDER` and `LLM_API_KEY`.

