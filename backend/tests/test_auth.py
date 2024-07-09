import pytest
from version import VERSION


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post(
        f"/api/{VERSION}/register",
        json={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = await response.get_json()
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_login(client):
    # First register a user
    await client.post(
        f"/api/{VERSION}/register",
        json={"username": "testuser", "password": "testpassword"},
    )

    # Then try to login
    response = await client.post(
        f"/api/{VERSION}/login",
        json={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = await response.get_json()
    assert "authToken" in data


@pytest.mark.asyncio
async def test_user_info(client, auth_header):
    auth_header = await auth_header
    response = await client.get(f"/api/{VERSION}/user", headers=[auth_header])
    assert response.status_code == 200
    data = await response.get_json()
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_logout(client, auth_header):
    auth_header = await auth_header
    response = await client.post(f"/api/{VERSION}/logout", headers=[auth_header])
    assert response.status_code == 200
    data = await response.get_json()
    assert data["authToken"] is None
