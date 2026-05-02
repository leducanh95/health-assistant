import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from sqlalchemy.orm import Session

from app.agent.agent import root_agent
from app.api.deps import get_current_user
from app.api.schemas import ChatRequest, ChatResponse
from app.config import get_settings
from app.core.db import get_session
from app.core.models import Baby, User

logger = logging.getLogger(__name__)

router = APIRouter()

_settings = get_settings()
_session_service = InMemorySessionService()
_runner = Runner(
    agent=root_agent,
    app_name=_settings.app_name,
    session_service=_session_service,
)
_active_sessions: set[str] = set()


def _build_message(req: ChatRequest, user_id: int) -> str:
    parts: list[str] = []
    parts.append(f"[CONTEXT] active_user_id={user_id}")
    if req.baby_id:
        parts.append(f"[CONTEXT] active_baby_id={req.baby_id}")
    if req.language:
        parts.append(f"[CONTEXT] preferred_language={req.language}")
    parts.append(req.message)
    return "\n".join(parts)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if req.baby_id:
        baby = db.query(Baby).filter(
            Baby.id == req.baby_id, Baby.user_id == user.id
        ).first()
        if not baby:
            raise HTTPException(status_code=403, detail="Forbidden")

    user_id_str = str(user.id)
    session_id = req.session_id if req.session_id in _active_sessions else None

    if not session_id:
        session = await _session_service.create_session(
            app_name=_settings.app_name, user_id=user_id_str
        )
        session_id = session.id
        _active_sessions.add(session_id)

    message_text = _build_message(req, user.id)
    parts: list[str] = []
    try:
        async for event in _runner.run_async(
            user_id=user_id_str,
            session_id=session_id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=message_text)]
            ),
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        continue
                    if hasattr(part, "text") and part.text:
                        parts.append(part.text)
    except Exception as e:
        logger.error("Agent error for user %s: %s\n%s", user.id, e, traceback.format_exc())
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            raise HTTPException(
                status_code=503,
                detail=(
                    "The AI service is temporarily unavailable due to quota limits. "
                    "Please try again in a few minutes."
                ),
            )
        raise HTTPException(status_code=500, detail=msg)

    return ChatResponse(
        response="".join(parts) or "Sorry, I cannot answer right now.",
        session_id=session_id,
    )
