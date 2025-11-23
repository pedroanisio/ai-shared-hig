"""Shared pytest fixtures and configuration."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from universal_corpus.database import Base, get_db
from universal_corpus.api import app


# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test_patterns.db"


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    return engine


@pytest.fixture(scope="session")
def TestSessionLocal(test_engine):
    """Create a test session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session(test_engine, TestSessionLocal):
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override the database dependency for testing."""
    def _override():
        try:
            yield db_session
        finally:
            pass
    return _override


@pytest.fixture(scope="function")
def client(override_get_db):
    """Create a test client with overridden database."""
    from fastapi.testclient import TestClient
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

