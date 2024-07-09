import pytest
from app import create_app
from quart.testing import QuartClient
from version import VERSION


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app) -> QuartClient:
    return app.test_client()


@pytest.fixture
async def auth_header(client):
    # Create a test user and authenticate
    test_user = {"username": "testuser", "password": "testpassword"}
    await client.post(f"/api/{VERSION}/register", json=test_user)
    response = await client.post(f"/api/{VERSION}/login", json=test_user)
    token = (await response.get_json())["authToken"]
    return ("Authorization", f"Bearer {token}")
