#!/usr/bin/env python3
"""Build the FAISS vector index from the knowledge corpus.

Ingests:
  - PDF documents in `documents/pdf/`  (G6PD reference, Vietnamese)
  - Markdown documents in `documents/who/`  (WHO summaries, VI + EN)

Usage:
    python scripts/build_index.py
"""
import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.text_splitter import RecursiveCharacterTextSplitter  # noqa: E402
from langchain_community.document_loaders import (  # noqa: E402
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_community.vectorstores import FAISS  # noqa: E402
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # noqa: E402

from app.config import get_settings  # noqa: E402


def build_index() -> None:
    settings = get_settings()

    documents = []

    if os.path.isdir(settings.pdf_folder_path):
        print(f"Loading PDFs from: {settings.pdf_folder_path}")
        pdf_loader = DirectoryLoader(
            path=settings.pdf_folder_path,
            glob="*.pdf",
            loader_cls=PyPDFLoader,
        )
        pdf_docs = pdf_loader.load()
        print(f"  → {len(pdf_docs)} PDF pages")
        documents.extend(pdf_docs)

    if os.path.isdir(settings.who_docs_path):
        print(f"Loading WHO markdown from: {settings.who_docs_path}")
        md_loader = DirectoryLoader(
            path=settings.who_docs_path,
            glob="*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        md_docs = md_loader.load()
        print(f"  → {len(md_docs)} markdown files")
        documents.extend(md_docs)

    if not documents:
        raise SystemExit(
            "No documents found. Add files under documents/pdf or "
            "documents/who and try again."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=100
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.text_embedding_model,
        api_version="v1",
    )
    vector_db = FAISS.from_documents(chunks, embeddings)
    vector_db.save_local(settings.vector_db_path)
    print(f"Index saved to: {settings.vector_db_path}")


if __name__ == "__main__":
    build_index()
