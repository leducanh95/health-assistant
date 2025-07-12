import os

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from utils.llm.embedding import text_embedding_initializer
from utils.llm.llm import llm_initializer


def create_prompt_template(template):
    """
    Create a prompt template for the G6PD assistant.

    Returns:
        PromptTemplate: The initialized prompt template.
    """
    return PromptTemplate(input_variables=["context", "question"], template=template)


def create_qa_chain(prompt, llm, vector_db):
    llm_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    return llm_chain


def read_vector_db():
    embedding_model = text_embedding_initializer()
    vector_db = FAISS.load_local(
        os.environ.get("VECTOR_DB_PATH"),
        embedding_model,
        allow_dangerous_deserialization=True,
    )
    return vector_db


def main():
    from dotenv import load_dotenv

    load_dotenv()
    llm = llm_initializer()
    vector_db = read_vector_db()

    # template = (
    #     "You are a helpful assistant specialized in G6PD deficiency. "
    #     "Answer the following question correctly based on the provided context\n\n"
    #     "If you don't know the answer, just say you don't know.\n\n"
    #     "Context: {context}\n\n"
    #     "Question: {question}\n"
    #     "Answer:"
    # )

    template = (
        "Bạn là một trợ lý hữu ích chuyên về thiếu men G6PD. "
        "Hãy trả lời chính xác câu hỏi sau dựa trên ngữ cảnh được cung cấp\n\n"
        "Nếu bạn không biết câu trả lời, chỉ cần nói rằng bạn không biết.\n\n"
        "Ngữ cảnh: {context}\n\n"
        "Câu hỏi: {question}\n"
        "Trả lời:"
    )

    prompt = create_prompt_template(template)
    chain = create_qa_chain(prompt, llm, vector_db)

    question = "TRUNG TÂM SÀNG LỌC SƠ SINH BIONET VIỆT NAM có địa chỉ ở đâu?"
    response = chain.invoke({"query": question})
    print(f"Response: {response['result']}")
    # print(f"Source Documents: {[doc.metadata for doc in response['source_documents']]}")


if __name__ == "__main__":
    main()
