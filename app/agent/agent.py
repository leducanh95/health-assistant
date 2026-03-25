from google.adk.agents import Agent

from app.agent.tools import search_g6pd_knowledge
from app.config import get_settings

_settings = get_settings()

root_agent = Agent(
    name="g6pd_health_assistant",
    model=_settings.llm_model,
    description=(
        "Trợ lý sức khỏe chuyên về bệnh thiếu men G6PD "
        "(Glucose-6-phosphate dehydrogenase), hỗ trợ người dùng và gia đình "
        "hiểu rõ về bệnh, cách phòng ngừa và quản lý."
    ),
    instruction=(
        "Bạn là một trợ lý sức khỏe chuyên về thiếu men G6PD. "
        "Luôn sử dụng công cụ search_g6pd_knowledge để tra cứu thông tin từ tài liệu y tế "
        "trước khi trả lời bất kỳ câu hỏi nào liên quan đến G6PD. "
        "Trả lời chính xác, rõ ràng và dựa trên thông tin từ tài liệu. "
        "Nếu không tìm thấy thông tin liên quan, hãy nói thẳng rằng bạn không có thông tin đó. "
        "Không tự suy diễn hoặc bịa đặt thông tin y tế. "
        "Trả lời bằng tiếng Việt."
    ),
    tools=[search_g6pd_knowledge],
)
