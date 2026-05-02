# Baby Health Assistant

An AI-powered full-stack application for tracking infant health (0–24 months), grounded in WHO Child Growth Standards. Combines growth tracking, motor milestones, vaccination schedules, and complementary feeding guidance with a bilingual (Vietnamese/English) conversational AI agent.

## Features

- **Growth Tracking** — Record weight, length, and head circumference; compute WHO Z-scores and percentiles with visual growth charts
- **Motor Milestones** — Track the 6 WHO gross-motor milestones with age-window status (on-track / late / overdue)
- **Vaccination Schedule** — Log immunizations against the WHO schedule; see due-soon and overdue doses
- **Feeding Guidance** — Age-appropriate complementary feeding stages (0–6 m → 18–24 m) with nutritional guidelines
- **AI Chat Agent** — Bilingual Gemini-powered agent that reads the child's actual profile before answering
- **Multi-baby Support** — Manage multiple children per account under JWT-based authentication

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI 0.115+, Uvicorn 0.30 |
| AI Agent | Google ADK ≥ 1.0, Gemini 2.5-flash |
| Embeddings / RAG | FAISS-cpu 1.11, LangChain, `text-embedding-004` |
| Database | SQLAlchemy 2.0 + SQLite (configurable) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Frontend | React 18.3 + Vite 5.4 + Recharts 2.12 |
| Deployment | Docker (multi-stage) + Google Cloud Run |

## Project Structure

```
health-assistant/
├── app/
│   ├── config.py               # Settings (reads from .env)
│   ├── agent/
│   │   ├── agent.py            # Google ADK root_agent (baby_health_assistant)
│   │   └── tools.py            # 6 agent tools (search_knowledge, get_baby_profile, …)
│   ├── core/
│   │   ├── age.py              # WHO age calculations (months / weeks / days)
│   │   ├── db.py               # SQLAlchemy session & engine setup
│   │   ├── growth.py           # WHO LMS Z-score & percentile calculations
│   │   ├── models.py           # ORM models (User, Baby, GrowthMeasurement, …)
│   │   ├── security.py         # JWT creation & password hashing
│   │   ├── vector_store.py     # Lazy-loading FAISS singleton
│   │   └── who_data.py         # Cached WHO reference data loaders
│   └── api/
│       ├── app.py              # FastAPI app factory + SPA mount
│       ├── deps.py             # Auth & ownership dependency injection
│       ├── schemas.py          # Pydantic request / response models
│       └── routes/
│           ├── auth.py         # /api/auth/*
│           ├── babies.py       # /api/babies CRUD
│           ├── chat.py         # /chat (agent)
│           ├── measurements.py # /api/babies/{id}/measurements
│           ├── milestones.py   # /api/babies/{id}/milestones
│           ├── vaccinations.py # /api/babies/{id}/vaccinations
│           ├── reference.py    # /api/reference (read-only WHO data)
│           └── health.py       # /health liveness probe
├── g6pd_agent/
│   └── __init__.py             # Thin shim — re-exports root_agent for ADK CLI
├── scripts/
│   └── build_index.py          # Build FAISS index from PDF / Markdown documents
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Shell: sidebar + tabs (Growth, Milestones, Vaccines, Feeding, Chat)
│   │   ├── components/         # Panel components + selectors
│   │   ├── state/              # State management
│   │   └── i18n/               # Vietnamese / English translations
│   ├── package.json
│   └── vite.config.js
├── data/who/                   # WHO reference JSON files (LMS tables, schedules, …)
├── documents/
│   ├── pdf/                    # Source PDFs (G6PD, Vietnamese medical docs)
│   └── who/                    # WHO summary Markdown files
├── vector_db/faiss_index/      # Pre-built FAISS index (baked into Docker image)
├── Dockerfile                  # Multi-stage: Node 20 → Python 3.11
├── deploy_cloud_run.sh         # One-command Cloud Run deployment
├── .env.example
└── requirements.txt
```

## Setup

### 1. Create Python environment

```bash
conda create -n health-assistant python=3.11
conda activate health-assistant
pip install -r requirements.txt
```

### 2. Configure `.env`

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Google Gemini
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
TEXT_EMBEDDING_MODEL=models/text-embedding-004
LLM_MODEL=gemini-2.5-flash

# Paths
PDF_FOLDER_PATH=documents/pdf
VECTOR_DB_PATH=vector_db/faiss_index
WHO_DOCS_PATH=documents/who
WHO_DATA_PATH=data/who

# Database (SQLite by default)
DATABASE_URL=sqlite:///./data/app.db

# Auth
SECRET_KEY=change-me-in-production

# Cloud Run (only needed for deployment)
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=asia-southeast1
SERVICE_NAME=baby-health-assistant
CLOUD_RUN_MEMORY=1Gi
```

### 3. Build the FAISS knowledge index

Run once to embed the PDF and Markdown documents into the vector database:

```bash
python scripts/build_index.py
```

## Running Locally

**Backend**

```bash
uvicorn app.api.app:app --reload --port 8000
```

**Frontend** (separate terminal)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The Vite dev server proxies `/chat`, `/api/*`, and `/health` to the backend on port 8000.

**ADK CLI (optional)**

```bash
adk run g6pd_agent   # interactive terminal
adk web              # built-in ADK web UI
```

## API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/health` | GET | — | Liveness probe |
| `/api/auth/signup` | POST | — | Register new user |
| `/api/auth/login` | POST | — | Get JWT token |
| `/api/auth/me` | GET | ✓ | Current user info |
| `/chat` | POST | ✓ | Chat with AI agent |
| `/api/babies` | GET, POST | ✓ | List / create babies |
| `/api/babies/{id}` | GET, PATCH | ✓ | Get / update baby |
| `/api/babies/{id}/measurements` | GET, POST | ✓ | Growth measurements |
| `/api/babies/{id}/measurements/{mid}` | DELETE | ✓ | Remove measurement |
| `/api/babies/{id}/growth-status` | GET | ✓ | Z-scores & percentiles |
| `/api/babies/{id}/milestones` | GET, POST | ✓ | Milestone records |
| `/api/babies/{id}/milestone-status` | GET | ✓ | Current milestone status |
| `/api/babies/{id}/vaccinations` | GET, POST | ✓ | Vaccination records |
| `/api/babies/{id}/vaccinations/status` | GET | ✓ | Vaccination schedule status |
| `/api/reference/milestones` | GET | ✓ | WHO milestone definitions |
| `/api/reference/vaccines` | GET | ✓ | WHO vaccine schedule |
| `/api/reference/feeding` | GET | ✓ | Feeding stage definitions |
| `/api/reference/feeding/nutrition` | GET | ✓ | Nutritional guidelines |
| `/api/reference/growth-curves` | GET | ✓ | Growth percentile curves |
| `/api/reference/growth-table` | GET | ✓ | p3 / p50 / p97 table |

## AI Agent

The agent (`baby_health_assistant`) runs on Gemini 2.5-flash via Google ADK. Each chat request is prefixed with the authenticated user and selected baby IDs so the agent can look up real data before responding.

**Tools available to the agent:**

| Tool | Description |
|---|---|
| `search_knowledge` | RAG over WHO documents and G6PD PDFs (FAISS) |
| `get_baby_profile` | Name, sex, birth date, current age, notes |
| `get_growth_status` | Latest measurements with WHO Z-scores and status |
| `get_milestone_status` | 6 gross-motor milestones with age-window status |
| `get_upcoming_vaccinations` | WHO schedule with per-dose status (received / due / overdue) |
| `get_feeding_guidance` | Age-appropriate feeding stage and bilingual recommendations |

The agent flags Z-scores outside ±2, overdue vaccines, and late milestones, and recommends a pediatric visit when findings are concerning.

## Data Models

```
User
└── Baby (1 → many)
    ├── GrowthMeasurement  (weight_kg, length_cm, head_circ_cm, measured_at)
    ├── MilestoneRecord    (milestone_key, achieved_at)
    ├── Vaccination        (vaccine_code, dose_number, given_at)
    └── FeedingLog         (feeding_type, log_date)
```

## Deployment (Cloud Run)

The Dockerfile builds the React frontend and embeds it into the Python image — one service serves both the API and the UI.

Make sure the FAISS index is already built, then:

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

```
User message
    │
    ▼
FastAPI /chat
    │  injects [CONTEXT] active_user_id / active_baby_id
    ▼
Google ADK Agent (Gemini 2.5-flash)
    │  calls tools as needed
    ├─► search_knowledge     → FAISS (WHO docs + PDFs)
    ├─► get_baby_profile     → SQLite
    ├─► get_growth_status    → SQLite + WHO LMS tables
    ├─► get_milestone_status → SQLite + WHO milestone windows
    ├─► get_upcoming_vaccinations → SQLite + WHO schedule
    └─► get_feeding_guidance → WHO feeding stages
    │
    ▼
Bilingual response (VI / EN) with WHO citations
```

## License

MIT
