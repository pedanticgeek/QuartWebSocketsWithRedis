import pytest
import json
from version import VERSION
from unittest.mock import AsyncMock


@pytest.fixture
def mock_redis(mocker):
    mock_redis = AsyncMock()
    mock_redis.lpop.return_value = None
    mock_redis.rpush.return_value = "ws:testuser"

    # Mock the get_redis function
    mocker.patch("api.websockets.get_redis", return_value=mock_redis)

    return mock_redis


@pytest.mark.asyncio
async def test_websocket_connection(client, auth_header, mock_redis):
    auth_header = await auth_header
    async with client.websocket(
        f"/api/{VERSION}/ws", headers=[auth_header]
    ) as websocket:
        msg = json.dumps(
            {
                "payload": {"message": "Hello, WebSocket!"},
                "metadata": {"type": "greeting"},
            }
        )
        await websocket.send(msg)
    mock_redis.lpop.assert_called_with("ws:testuser")
    mock_redis.rpush.assert_called_with(
        "ws:testuser",
        "Hi testuser, I have received your message: " + msg.replace('"', "'"),
    )


@pytest.mark.asyncio
async def test_websocket_ping(client, auth_header, mock_redis):
    auth_header = await auth_header
    async with client.websocket(
        f"/api/{VERSION}/ws", headers=[auth_header]
    ) as websocket:
        await websocket.send("abc")
        ping = await websocket.receive()
        assert ping == "ping"
