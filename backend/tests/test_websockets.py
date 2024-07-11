import asyncio
import pytest
import json
from version import VERSION
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_redis(mocker):
    mock_redis = MagicMock()
    mock_redis.brpop = AsyncMock(
        return_value=(
            "ws:testuser",
            '{"payload": {"message": "Hi testuser, I have received your message: Hello, WebSocket!"}}'.encode(
                "utf-8"
            ),
        )
    )
    mock_redis.lpush = AsyncMock(return_value="ws:testuser")

    # Mock the get_redis function
    mocker.patch("api.websockets.get_redis", return_value=mock_redis)

    return mock_redis


@pytest.mark.asyncio
async def test_websocket_connection(client, auth_header, mock_redis):
    async with client.websocket(
        path=f"api/{VERSION}/ws",
        query_string={"token": auth_header[1].split()[1]},
        headers={"Origin": "localhost"},
    ) as websocket:
        msg = json.dumps(
            {
                "payload": {"message": "Hello, WebSocket!"},
                "metadata": {"type": "greeting"},
            }
        )
        await websocket.send(msg)
        res = await websocket.receive()
    mock_redis.brpop.assert_called_with("ws:testuser")
    mock_redis.lpush.assert_called_with(
        "ws:testuser", '{"payload": {"message": "ping"}}'
    )
    assert (
        res
        == '{"payload": {"message": "Hi testuser, I have received your message: Hello, WebSocket!"}}'
    )
