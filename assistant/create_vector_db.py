import os

from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_community.vectorstores import FAISS
from utils.llm.embedding import text_embedding_initializer
from utils.pdf_loader import pdf_loader


def create_vector_db_from_pdfs(pdf_folder_path):
    pdf_documents = pdf_loader(pdf_folder_path)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=100, length_function=len
    )
    split_documents = text_splitter.split_documents(pdf_documents)

    embedding_model = text_embedding_initializer()
    vector_db = FAISS.from_documents(split_documents, embedding_model)
    vector_db.save_local(os.environ.get("VECTOR_DB_PATH"))

    return vector_db


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()
    pdf_folder_path = os.environ.get("PDF_FOLDER_PATH")
    vector_db = create_vector_db_from_pdfs(pdf_folder_path)
