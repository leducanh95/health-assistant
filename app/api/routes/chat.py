from fastapi import APIRouter, HTTPException
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent.agent import root_agent
from app.api.schemas import ChatRequest, ChatResponse
from app.config import get_settings

router = APIRouter()

_settings = get_settings()
_session_service = InMemorySessionService()
_runner = Runner(
    agent=root_agent,
    app_name=_settings.app_name,
    session_service=_session_service,
)
_active_sessions: set[str] = set()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id if req.session_id in _active_sessions else None

    if not session_id:
        session = await _session_service.create_session(
            app_name=_settings.app_name, user_id="user"
        )
        session_id = session.id
        _active_sessions.add(session_id)

    parts: list[str] = []
    try:
        async for event in _runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=req.message)]
            ),
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    # Skip function_call / function_response parts — text only
                    if hasattr(part, "function_call") and part.function_call:
                        continue
                    if hasattr(part, "text") and part.text:
                        parts.append(part.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        response="".join(parts) or "Xin lỗi, tôi không thể trả lời lúc này.",
        session_id=session_id,
    )
