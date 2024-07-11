import asyncio
import json
from quart import Blueprint, websocket, current_app, Websocket
from quart_cors import websocket_cors
from quart_schema import SchemaValidationError
from quart_redis import get_redis
from version import VERSION
from api.error_handlers import APIException
from api.models import WebsocketMessage

websockets_bp = Blueprint("websockets", __name__)


class WebSocketSession:
    def __init__(self, ws: Websocket, token: str):
        self.ws = ws
        self.auth_id = current_app.auth_manager.load_token(token)
        self.redis = get_redis()
        current_app.logger.info(f"WebSocket connection opened for user: {self.auth_id}")

    async def send(self):
        while True:
            try:
                # Pull message from Redis queue
                message = await self.redis.brpop(f"ws:{self.auth_id}")
                if message:
                    await self.ws.send(message[1].decode("utf-8"))
            except Exception as e:
                current_app.logger.error(f"Error in send operation: {str(e)}")

    async def queue(self, message: str):
        try:
            await self.redis.lpush(
                f"ws:{self.auth_id}",
                json.dumps({"payload": {"message": message}}),
            )
        except Exception as e:
            current_app.logger.error(f"Error in queue operation: {str(e)}")

    async def receive(self):
        while True:
            try:
                message: WebsocketMessage = await self.ws.receive_as(WebsocketMessage)
                current_app.logger.info(
                    f"Received message from {self.auth_id}: {message.model_dump(mode='json')}"
                )
                if message.payload.message == "ping":
                    await self.queue("pong")
                elif message.payload.message == "pong":
                    pass
                else:
                    # Here you can add logic to process the received message, I simply push an acknowledgement message back to the client
                    await self.queue(
                        f"Hi {self.auth_id}, I have received your message: {message.payload.message}"
                    )
            except SchemaValidationError:
                await self.queue(
                    f"Sorry, {self.auth_id}, Your message must validate the schema: {WebsocketMessage.model_json_schema()}",
                )
            except Exception as e:
                current_app.logger.error(f"Error in receive operation: {str(e)}")
                break

    async def ping(self):
        while True:
            try:
                await self.queue("ping")
                current_app.logger.debug(f"Sent ping to {self.auth_id}")
            except Exception as e:
                current_app.logger.error(f"Error in ping operation: {str(e)}")
                break
            await asyncio.sleep(60)  # Wait for 60 seconds before next ping

    async def run(self):
        tasks = [
            asyncio.create_task(self.send()),
            asyncio.create_task(self.receive()),
            asyncio.create_task(self.ping()),
        ]
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            current_app.logger.info(f"WebSocket session for {self.auth_id} is closing")
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    def close(self):
        current_app.logger.info(f"WebSocket connection closed for user: {self.auth_id}")


@websockets_bp.websocket(f"/api/{VERSION}/ws")
@websocket_cors(allow_origin="*")
async def ws():
    token = websocket.args.get("token")
    if not token:
        raise APIException("Not authorized", 401)
    session = WebSocketSession(websocket, token)
    try:
        await session.run()
    finally:
        session.close()
