import logging
import os
import warnings

# The Google Gemini SDK prints this warning whenever the ADK runner accesses
# .text on a model response that contains function_call parts (expected during
# tool use). It is benign — suppress it to keep logs clean.
warnings.filterwarnings(
    "ignore",
    message=".*there are non-text parts in the response.*",
)

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from app.api.routes import (  # noqa: E402
    auth,
    babies,
    chat,
    health,
    measurements,
    milestones,
    reference,
    vaccinations,
)
from app.config import get_settings  # noqa: E402
from app.core.db import init_db  # noqa: E402

_FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    logging.getLogger(__name__).info(
        "Starting Baby Health Assistant — model=%s vertexai=%s api_key_set=%s",
        settings.llm_model,
        settings.google_genai_use_vertexai,
        bool(settings.google_api_key),
    )
    init_db()

    application = FastAPI(title="Baby Health Assistant API")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(chat.router)
    application.include_router(babies.router)
    application.include_router(measurements.router)
    application.include_router(measurements.status_router)
    application.include_router(milestones.router)
    application.include_router(milestones.status_router)
    application.include_router(vaccinations.router)
    application.include_router(vaccinations.status_router)
    application.include_router(reference.router)

    _mount_spa(application)

    return application


def _mount_spa(application: FastAPI) -> None:
    """Mount the pre-built React app if the dist folder exists."""
    if not os.path.isdir(_FRONTEND_DIR):
        return

    assets_dir = os.path.join(_FRONTEND_DIR, "assets")
    if os.path.isdir(assets_dir):
        application.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="assets",
        )

    @application.get("/{full_path:path}", include_in_schema=False)
    def serve_spa():
        return FileResponse(os.path.join(_FRONTEND_DIR, "index.html"))


app = create_app()
