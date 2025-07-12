import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings


def text_embedding_initializer():
    """
    Initialize the Google Generative AI embeddings model.

    Returns:
        GoogleGenerativeAIEmbeddings: The initialized embeddings model.
    """
    return GoogleGenerativeAIEmbeddings(model=os.environ.get("TEXT_EMBEDDING_MODEL"))


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    embeddings = text_embedding_initializer()
    response = embeddings.embed_query("What is G6PD deficiency?")
    print(f"Embedding: {response}")
