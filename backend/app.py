import os
import secrets
from quart import Quart, jsonify
from quart_schema import QuartSchema, Info
from quart_auth import QuartAuth
from quart_redis import RedisHandler
from quart_cors import cors
from api import auth_bp, websockets_bp, health_bp, error_handlers
from data.models import User
from utils.logger import Logger
from version import VERSION


class MyQuart(Quart):
    async def make_response(self, result):
        """
        Overrides the default `make_response` method to handle different types of response data.

        If the `result` parameter is a dictionary or list, it will be automatically converted to a JSON response using `jsonify()`. Otherwise, the default `make_response` method is called.

        This allows the API to return both JSON and other types of responses (e.g. HTML, binary data) without the need for additional handling in the route functions.
        """
        if isinstance(result, (dict, list)):
            result = jsonify(result)
        return await super().make_response(result)


def create_app():
    app = MyQuart(__name__)
    app.secret_key = secrets.token_urlsafe(16)

    QuartSchema(
        app,
        convert_casing=True,
        info=Info(
            title="Quart API Demo by PedanticGeek",
            version=VERSION,
        ),
    )
    app.auth_manager = QuartAuth(
        app,
        attribute_name="username",
        duration=int(os.getenv("AUTH_TOKEN_EXPIRE_DAYS", "30")) * 24 * 60 * 60,
        mode="bearer",
    )
    app.auth_manager.attribute_name = "username"
    app.auth_manager.user_class = User
    app.config["REDIS_URI"] = "redis://" + os.getenv("REDIS_HOSTNAME", "redis")
    app.redis_handler = RedisHandler(app)

    app.logger = Logger(
        app.config["SERVER_NAME"],
        filename="MyQuartApp",
        level=os.getenv("LOG_LEVEL", "INFO"),
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(websockets_bp)

    app.register_error_handler(
        error_handlers.APIException, error_handlers.handle_api_exception
    )
    cors(
        app,
        allow_origin="*",
        allow_methods=["GET", "POST", "PUT", "DELETE"],
    )

    return app
