import asyncio
from quart import Blueprint, websocket, current_app, Websocket
from quart_auth import login_required, current_user
from quart_schema import SchemaValidationError
from quart_redis import get_redis
from version import VERSION
from api.models import WebsocketMessage


websockets_bp = Blueprint("websockets", __name__)


class WebSocketSession:
    def __init__(self, ws: Websocket, auth_id: str):
        self.ws = ws
        self.auth_id = auth_id
        self.logger = current_app.logger
        self.redis = get_redis()

    async def send(self):
        while True:
            try:
                # Pull message from Redis queue
                message = await self.redis.lpop(f"ws:{self.auth_id}")
                if message:
                    await self.ws.send(message.decode("utf-8"))
            except Exception as e:
                self.logger.error(f"Error in send operation: {str(e)}")
            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting

    async def receive(self):
        while True:
            try:
                message: WebsocketMessage = await self.ws.receive_as(WebsocketMessage)
                self.logger.info(
                    f"Received message from {self.auth_id}: {message.model_dump()}"
                )
                # Here you can add logic to process the received message, I simply push an acknowledgement message back to the client
                await self.redis.rpush(
                    f"ws:{self.auth_id}",
                    f"Hi {self.auth_id}, I have received your message: {message.model_dump(mode='json')}",
                )
            except SchemaValidationError:
                await self.redis.rpush(
                    f"ws:{self.auth_id}",
                    f"Sorry, {self.auth_id}, Your message must validate the schema: {WebsocketMessage.model_json_schema()}",
                )
            except Exception as e:
                self.logger.error(f"Error in receive operation: {str(e)}")
                break

    async def ping(self):
        while True:
            try:
                await self.ws.send("ping")
                self.logger.debug(f"Sent ping to {self.auth_id}")
            except Exception as e:
                self.logger.error(f"Error in ping operation: {str(e)}")
                break
            await asyncio.sleep(60)  # Wait for 60 seconds before next ping

    async def run(self):
        send_task = asyncio.create_task(self.send())
        receive_task = asyncio.create_task(self.receive())
        ping_task = asyncio.create_task(self.ping())

        try:
            await asyncio.gather(send_task, receive_task, ping_task)
        except asyncio.CancelledError:
            self.logger.info(f"WebSocket session for {self.auth_id} is closing")
        finally:
            send_task.cancel()
            receive_task.cancel()
            ping_task.cancel()


@websockets_bp.websocket(f"/api/{VERSION}/ws")
@login_required
async def ws():
    session = WebSocketSession(websocket, current_user._auth_id)
    current_app.logger.info(
        f"WebSocket connection opened for user: {current_user._auth_id}"
    )

    try:
        await session.run()
    finally:
        current_app.logger.info(
            f"WebSocket connection closed for user: {current_user._auth_id}"
        )


@websockets_bp.before_websocket
async def before_websocket():
    current_app.logger.info(
        f"Preparing WebSocket connection for user: {current_user._auth_id}"
    )
