import os
import warnings

# The Google Gemini SDK prints this warning whenever the ADK runner accesses
# .text on a model response that contains function_call parts (expected during
# tool use). It is benign — suppress it to keep logs clean.
warnings.filterwarnings(
    "ignore",
    message=".*there are non-text parts in the response.*",
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import chat, health
from app.config import get_settings

_FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(title="G6PD Health Assistant API")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health.router)
    application.include_router(chat.router)

    _mount_spa(application)

    return application


def _mount_spa(application: FastAPI) -> None:
    """Mount the pre-built React app if the dist folder exists."""
    if not os.path.isdir(_FRONTEND_DIR):
        return

    assets_dir = os.path.join(_FRONTEND_DIR, "assets")
    if os.path.isdir(assets_dir):
        application.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @application.get("/{full_path:path}", include_in_schema=False)
    def serve_spa():
        return FileResponse(os.path.join(_FRONTEND_DIR, "index.html"))


app = create_app()
