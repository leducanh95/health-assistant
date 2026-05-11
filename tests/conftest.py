import os

# Set env vars before any app module is imported.
# get_settings() is @lru_cache'd at module level in security.py and db.py,
# so these must exist before the first import of any app.* module.
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("WHO_DATA_PATH", "data/who")
os.environ.setdefault("GOOGLE_API_KEY", "fake-key-for-tests")

import pytest  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.db import Base  # noqa: E402


@pytest.fixture(scope="function")
def db_session():
    """Fresh in-memory SQLite DB per test, rolled back on teardown."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, autoflush=False, expire_on_commit=False)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()
    engine.dispose()
