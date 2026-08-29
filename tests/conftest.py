import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import Base, get_db
from app.main import create_app


TEST_SETTINGS = Settings(
    api_secret_key="test-secret",
    ollama_host="http://ollama.invalid",
    ollama_model="test-model",
    ollama_api_key="test-key",
    allowed_models=frozenset({"test-model"}),
)


@pytest.fixture
def app():
    return create_app(TEST_SETTINGS)


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session(app):
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is not configured")

    test_engine = create_engine(database_url)
    try:
        connection = test_engine.connect()
    except OperationalError as exc:
        pytest.skip(f"Disposable PostgreSQL database is unavailable: {exc}")

    transaction = connection.begin()
    Base.metadata.create_all(bind=connection)
    session = Session(bind=connection)

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session
    finally:
        app.dependency_overrides.clear()
        session.close()
        transaction.rollback()
        connection.close()
        test_engine.dispose()
