import sys
from unittest.mock import MagicMock

# Pre-mock Google ADK and agent modules before create_app() is imported.
# chat.py instantiates InMemorySessionService() and Runner(agent=root_agent)
# at module load time — those must be mocked or they attempt network calls.
for _mod in [
    "google.adk",
    "google.adk.runners",
    "google.adk.sessions",
    "google.genai",
    "google.genai.types",
]:
    sys.modules.setdefault(_mod, MagicMock())

sys.modules.setdefault("app.agent.agent", MagicMock())

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api.app import create_app  # noqa: E402
from app.core.db import get_session  # noqa: E402


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient with production app wired to the test in-memory DB."""
    app = create_app()
    app.dependency_overrides[get_session] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
