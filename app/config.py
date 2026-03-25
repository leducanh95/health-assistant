import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Centralised configuration read from environment variables / .env file."""

    def __init__(self) -> None:
        self.google_api_key: str = os.environ.get("GOOGLE_API_KEY", "")
        self.google_genai_use_vertexai: str = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")
        self.llm_model: str = os.environ.get("LLM_MODEL", "gemini-2.5-flash")
        self.llm_provider: str = os.environ.get("LLM_PROVIDER", "google_genai")
        self.text_embedding_model: str = os.environ.get(
            "TEXT_EMBEDDING_MODEL", "models/text-embedding-004"
        )
        self.vector_db_path: str = os.environ.get("VECTOR_DB_PATH", "vector_db/faiss_index")
        self.pdf_folder_path: str = os.environ.get("PDF_FOLDER_PATH", "documents/pdf")
        self.app_name: str = "g6pd_health_assistant"
        self.cors_origins: list[str] = [
            "http://localhost:5173",
            "http://localhost:3000",
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
