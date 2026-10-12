"""Shared test fixtures for the ALIAS test suite."""
import asyncio
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def event_loop():
    """Session-scoped event loop for async tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client():
    """Session-scoped TestClient — triggers lifespan (init_db + registry.discover)."""
    from alias_core.api.main import app
    with TestClient(app) as c:
        yield c
