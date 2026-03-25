from __future__ import annotations

import threading

from app.config import get_settings


class VectorStoreRepository:
    """Thread-safe lazy-loading FAISS vector store (Repository pattern)."""

    _instance: VectorStoreRepository | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._db = None

    @classmethod
    def get_instance(cls) -> VectorStoreRepository:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _load(self):
        from langchain_community.vectorstores import FAISS
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        settings = get_settings()
        embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.text_embedding_model,
            api_version="v1",
        )
        return FAISS.load_local(
            settings.vector_db_path,
            embeddings,
            allow_dangerous_deserialization=True,
        )

    def similarity_search(self, query: str, k: int = 5) -> list[str]:
        if self._db is None:
            self._db = self._load()
        docs = self._db.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
