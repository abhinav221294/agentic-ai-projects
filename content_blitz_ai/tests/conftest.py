import pytest

from fastapi.testclient import TestClient

from backend.src.web_app.api.app import app

client = TestClient(app)


@pytest.fixture
def api_client():
    return client