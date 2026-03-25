#!/usr/bin/env bash
set -euo pipefail

# ── Locate gcloud ─────────────────────────────────────────────────────────────
if ! command -v gcloud &>/dev/null; then
  # Common install locations (Homebrew, default installer, snap)
  for candidate in \
    "${HOME}/google-cloud-sdk/bin" \
    "/opt/homebrew/share/google-cloud-sdk/bin" \
    "/usr/local/share/google-cloud-sdk/bin" \
    "/usr/lib/google-cloud-sdk/bin" \
    "/snap/bin"; do
    if [[ -x "${candidate}/gcloud" ]]; then
      export PATH="${candidate}:${PATH}"
      break
    fi
  done
fi

if ! command -v gcloud &>/dev/null; then
  echo "ERROR: gcloud not found. Install the Google Cloud SDK:" >&2
  echo "       https://cloud.google.com/sdk/docs/install" >&2
  exit 1
fi

# ── Load environment variables from .env ──────────────────────────────────────
ENV_FILE="$(dirname "$0")/.env"
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "ERROR: .env file not found at ${ENV_FILE}" >&2
  exit 1
fi

# Parse and export KEY=VALUE lines; skip comments (#) and blank lines
while IFS='=' read -r key remainder || [[ -n "$key" ]]; do
  key="${key#"${key%%[![:space:]]*}"}"
  key="${key%"${key##*[![:space:]]}"}"
  [[ -z "$key" || "$key" == \#* ]] && continue
  [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || continue
  export "$key"="$remainder"
done < "${ENV_FILE}"

# ── Validate required variables ────────────────────────────────────────────────
REQUIRED_VARS=(GCP_PROJECT_ID GCP_REGION SERVICE_NAME ARTIFACT_REPO GOOGLE_API_KEY)
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: Required variable '${var}' is not set in .env" >&2
    exit 1
  fi
done

# ── Derived values ────────────────────────────────────────────────────────────
TAG="$(date +%Y%m%d-%H%M%S)"
IMAGE="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REPO}/${SERVICE_NAME}:${TAG}"

# Resource limits (with defaults)
PORT="${CLOUD_RUN_PORT:-8080}"
MEMORY="${CLOUD_RUN_MEMORY:-1Gi}"
CPU="${CLOUD_RUN_CPU:-1}"
TIMEOUT="${CLOUD_RUN_TIMEOUT:-300}"

# ── Build --set-env-vars from .env app keys ───────────────────────────────────
# Collect runtime env vars to inject into the Cloud Run service.
# PDF_FOLDER_PATH is intentionally excluded — only needed for index building.
# VECTOR_DB_PATH is overridden to the absolute path inside the container.
build_env_vars() {
  local pairs=()
  local keys=(
    GOOGLE_API_KEY
    GOOGLE_GENAI_USE_VERTEXAI
    TEXT_EMBEDDING_MODEL
    LLM_MODEL
    LLM_PROVIDER
  )
  for key in "${keys[@]}"; do
    local val="${!key:-}"
    if [[ -n "${val}" ]]; then
      pairs+=("${key}=${val}")
    fi
  done
  # Always use the absolute container path — the .env value is for local dev only
  pairs+=("VECTOR_DB_PATH=/app/vector_db/faiss_index")
  local IFS=','
  echo "${pairs[*]}"
}

ENV_VARS="$(build_env_vars)"

echo "========================================================"
echo "  G6PD Health Assistant — Cloud Run Deployment"
echo "========================================================"
echo "  Project  : ${GCP_PROJECT_ID}"
echo "  Region   : ${GCP_REGION}"
echo "  Service  : ${SERVICE_NAME}"
echo "  Image    : ${IMAGE}"
echo "  Memory   : ${MEMORY}  CPU: ${CPU}  Timeout: ${TIMEOUT}s"
echo "========================================================"
echo ""

# ── Authenticate & set project ────────────────────────────────────────────────
echo ">> Setting active project: ${GCP_PROJECT_ID}"
gcloud config set project "${GCP_PROJECT_ID}"

# ── Enable required APIs (safe to re-run; skipped if already enabled) ─────────
echo ">> Enabling required GCP APIs (this may take ~1 min on first run)..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    --project="${GCP_PROJECT_ID}"

# ── Ensure Artifact Registry repo exists ──────────────────────────────────────
echo ">> Ensuring Artifact Registry repository '${ARTIFACT_REPO}' exists..."
gcloud artifacts repositories describe "${ARTIFACT_REPO}" \
    --location="${GCP_REGION}" \
    --project="${GCP_PROJECT_ID}" > /dev/null 2>&1 \
|| gcloud artifacts repositories create "${ARTIFACT_REPO}" \
    --repository-format=docker \
    --location="${GCP_REGION}" \
    --project="${GCP_PROJECT_ID}" \
    --description="G6PD Health Assistant images"

# ── Configure Docker auth ─────────────────────────────────────────────────────
echo ">> Configuring Docker for Artifact Registry..."
gcloud auth configure-docker "${GCP_REGION}-docker.pkg.dev" --quiet

# ── Build & push image via Cloud Build ───────────────────────────────────────
echo ">> Building and pushing image: ${IMAGE}"
gcloud builds submit . \
    --tag="${IMAGE}" \
    --project="${GCP_PROJECT_ID}" \
    --timeout=1200

# ── Deploy to Cloud Run ───────────────────────────────────────────────────────
echo ">> Deploying to Cloud Run service '${SERVICE_NAME}'..."
gcloud run deploy "${SERVICE_NAME}" \
    --image="${IMAGE}" \
    --region="${GCP_REGION}" \
    --project="${GCP_PROJECT_ID}" \
    --platform=managed \
    --allow-unauthenticated \
    --port="${PORT}" \
    --memory="${MEMORY}" \
    --cpu="${CPU}" \
    --timeout="${TIMEOUT}" \
    --set-env-vars="${ENV_VARS}"

echo ""
echo ">> Deployment complete."
echo ">> Service URL:"
gcloud run services describe "${SERVICE_NAME}" \
    --region="${GCP_REGION}" \
    --project="${GCP_PROJECT_ID}" \
    --format="value(status.url)"
