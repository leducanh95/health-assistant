# G6PD Deficiency Health Assistant

An AI-powered chatbot specialized in answering questions about G6PD deficiency, built with Google ADK, LangChain, and a FAISS vector database for grounded knowledge retrieval.

## Overview

This project is a full-stack conversational assistant that provides accurate, Vietnamese-language information about G6PD deficiency from curated medical documents. It uses:

- **Google ADK** — agent framework with tool-calling capabilities
- **Gemini** (`gemini-2.5-flash`) — underlying LLM
- **FastAPI** — backend API server (also serves the React frontend as static files)
- **React + Vite** — responsive chat UI (mobile + desktop)
- **FAISS** — vector database for efficient document retrieval
- **Google Generative AI Embeddings** (`text-embedding-004`) — text vectorization
- **LangChain** — PDF loading and text splitting utilities

## Project Structure

```
health-assistant/
├── app/                            # Main Python package
│   ├── config.py                   # Centralised Settings (reads from .env)
│   ├── core/
│   │   └── vector_store.py         # VectorStoreRepository — lazy FAISS singleton
│   ├── agent/
│   │   ├── tools.py                # search_g6pd_knowledge tool
│   │   └── agent.py                # root_agent definition
│   └── api/
│       ├── schemas.py              # ChatRequest / ChatResponse models
│       ├── app.py                  # create_app() factory — FastAPI entrypoint
│       └── routes/
│           ├── chat.py             # POST /chat
│           └── health.py           # GET /health
├── g6pd_agent/
│   └── __init__.py                 # Thin shim — re-exports root_agent for ADK CLI
├── scripts/
│   └── build_index.py              # Build FAISS index from PDF documents
├── frontend/                       # React + Vite chat UI
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                 # Responsive chat component
│       ├── App.css
│       └── index.css
├── documents/
│   └── pdf/                        # Source PDF documents (Vietnamese)
├── vector_db/
│   └── faiss_index/                # Pre-built FAISS index (baked into Docker image)
├── Dockerfile                      # Multi-stage build (Node → Python)
├── .dockerignore
├── deploy_cloud_run.sh             # One-command Cloud Run deployment
├── .env                            # Environment variables (not committed)
├── .env.example                    # Environment variable template
└── requirements.txt                # Python dependencies
```

## Setup

### 1. Create environment

```bash
conda create -n health-assistant python=3.11
conda activate health-assistant
pip install -r requirements.txt
```

### 2. Configure `.env`

Copy `.env.example` to `.env` and fill in your values:

```bash
# Google Gemini
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
TEXT_EMBEDDING_MODEL=models/text-embedding-004
LLM_MODEL=gemini-2.5-flash
LLM_PROVIDER=google_genai

# Paths
PDF_FOLDER_PATH=documents/pdf
VECTOR_DB_PATH=vector_db/faiss_index

# Cloud Run deployment
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=asia-southeast1
SERVICE_NAME=g6pd-assistant
ARTIFACT_REPO=g6pd-assistant
CLOUD_RUN_PORT=8080
CLOUD_RUN_MEMORY=1Gi
CLOUD_RUN_CPU=1
CLOUD_RUN_TIMEOUT=300
```

### 3. Build the FAISS index

Run once to chunk the PDF documents and create the vector database:

```bash
python scripts/build_index.py
```

## Running Locally

### Backend

```bash
uvicorn app.api.app:app --reload --port 8000
```

### Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser. The Vite dev server proxies `/chat` and `/health` to the backend on port 8000.

### ADK CLI (optional)

```bash
# Interactive terminal
adk run g6pd_agent

# ADK built-in web UI
adk web
```

## Deployment (Cloud Run)

The Dockerfile builds the React frontend and embeds it into the Python image — a single Cloud Run service serves both the API and the UI.

Make sure the FAISS index is built, then run:

```bash
chmod +x deploy_cloud_run.sh
./deploy_cloud_run.sh
```

The script will:
1. Enable required GCP APIs
2. Create the Artifact Registry repository if needed
3. Build and push the Docker image via Cloud Build (FAISS index baked in)
4. Deploy to Cloud Run with runtime env vars from `.env`
5. Print the public service URL

## How It Works

The assistant follows a RAG (Retrieval-Augmented Generation) pattern:

1. User sends a question via the chat UI
2. The FastAPI backend forwards it to the Google ADK agent
3. The agent calls the `search_g6pd_knowledge` tool
4. The tool queries FAISS to retrieve the most relevant passages from the medical PDFs
5. The agent generates a grounded, accurate answer in Vietnamese

## About G6PD Deficiency

G6PD (Glucose-6-phosphate dehydrogenase) deficiency is a genetic disorder affecting red blood cells. The assistant covers:

- Causes and symptoms
- Diagnosis and treatment
- Foods and medications to avoid
- Daily management strategies

## License

MIT
