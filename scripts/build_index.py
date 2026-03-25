#!/usr/bin/env python3
"""Build the FAISS vector index from PDF documents.

Usage:
    python scripts/build_index.py
"""
import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import get_settings


def build_index() -> None:
    settings = get_settings()

    print(f"Loading PDFs from: {settings.pdf_folder_path}")
    loader = DirectoryLoader(
        path=settings.pdf_folder_path,
        glob="*.pdf",
        loader_cls=PyPDFLoader,
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} pages")

    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=100)
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
