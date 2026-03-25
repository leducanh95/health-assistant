from app.core.vector_store import VectorStoreRepository


def search_g6pd_knowledge(query: str) -> str:
    """Search the G6PD deficiency knowledge base for relevant medical information.

    Use this tool to look up facts about G6PD deficiency from the medical documents,
    including causes, symptoms, diagnosis, treatment, foods and medications to avoid,
    and management strategies.

    Args:
        query: The question or topic to search for in the G6PD knowledge base.

    Returns:
        Relevant passages from the medical documents about G6PD deficiency.
    """
    try:
        results = VectorStoreRepository.get_instance().similarity_search(query)
        if not results:
            return "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
        return "\n\n".join(results)
    except Exception as e:
        return f"Lỗi khi tìm kiếm: {str(e)}"
