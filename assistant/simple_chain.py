from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from utils.llm.llm import llm_initializer


def create_prompt_template(template):
    """
    Create a prompt template for the G6PD assistant.

    Returns:
        PromptTemplate: The initialized prompt template.
    """
    return PromptTemplate(input_variables=["question"], template=template)


def create_simple_chain(prompt, llm):
    llm_chain = LLMChain(
        prompt=prompt,
        llm=llm,
        verbose=True,
    )
    return llm_chain


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    llm = llm_initializer()
    template = (
        "Bạn là một trợ lý hữu ích chuyên về thiếu men G6PD. "
        "Hãy trả lời chính xác câu hỏi sau:\n\n"
        "Câu hỏi: {question}\n"
        "Trả lời:"
    )
    prompt = create_prompt_template(template)
    chain = create_simple_chain(prompt, llm)

    question = "TRUNG TÂM SÀNG LỌC SƠ SINH BIONET VIỆT NAM có địa chỉ ở đâu?"
    response = chain.invoke({"question": question})
    print(f"Response: {response}")
