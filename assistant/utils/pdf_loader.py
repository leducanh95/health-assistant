from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader


def pdf_loader(pdf_folder_path):
    """
    Load a PDF file and return its content as a string.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The content of the PDF file.
    """

    loader = DirectoryLoader(path=pdf_folder_path, glob="*.pdf", loader_cls=PyPDFLoader)
    pdf_documents = loader.load()

    return pdf_documents


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()
    pdf_folder_path = os.environ.get("PDF_FOLDER_PATH")
    documents = pdf_loader(pdf_folder_path)
    for doc in documents:
        print(f"Document content: {doc.page_content}")
        print(f"Metadata: {doc.metadata}")
