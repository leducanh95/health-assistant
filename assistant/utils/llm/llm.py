import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


def llm_initializer():
    """
    Initialize the Google Generative AI chat model.

    Returns:
        ChatModel: The initialized chat model.
    """
    return init_chat_model(
        os.environ.get("LLM_MODEL"),
        model_provider=os.environ.get("LLM_PROVIDER"),
        temperature=0.2,
    )


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    llm = llm_initializer()
    response = llm.invoke("What is G6PD deficiency?")
    print(f"Response: {response}")
