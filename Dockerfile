
# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ── Stage 2: Python backend ────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd --create-home appuser

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY g6pd_agent/ ./g6pd_agent/

# Copy pre-built FAISS index (baked into image)
COPY vector_db/ ./vector_db/

# Copy built frontend from stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Hand ownership to non-root user
RUN chown -R appuser /app
USER appuser

ENV VECTOR_DB_PATH=/app/vector_db/faiss_index

EXPOSE 8080

CMD ["uvicorn", "app.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
