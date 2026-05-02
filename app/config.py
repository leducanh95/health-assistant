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
        self.who_docs_path: str = os.environ.get("WHO_DOCS_PATH", "documents/who")
        self.who_data_path: str = os.environ.get("WHO_DATA_PATH", "data/who")
        self.data_dir: str = os.environ.get("DATA_DIR", "data")
        self.database_url: str = os.environ.get(
            "DATABASE_URL", "sqlite:///./data/app.db"
        )
        self.secret_key: str = os.environ.get(
            "SECRET_KEY", "dev-secret-change-me-in-production"
        )
        self.jwt_algorithm: str = "HS256"
        self.access_token_expire_minutes: int = int(
            os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 14))
        )
        self.app_name: str = "baby_health_assistant"
        self.cors_origins: list[str] = [
            "http://localhost:5173",
            "http://localhost:3000",
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
