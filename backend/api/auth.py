from quart import Blueprint
from quart_schema import validate_request, validate_response
from quart_auth import login_required, current_user
from version import VERSION
from api import models
from data.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route(f"/api/{VERSION}/login", methods=["POST"])
@validate_request(models.LoginRequest)
@validate_response(models.LoginResponse)
async def login(data: models.LoginRequest):
    return await User.login(data)


@auth_bp.route(f"/api/{VERSION}/logout", methods=["POST"])
@login_required
async def logout():
    return await current_user.logout()


@auth_bp.route(f"/api/{VERSION}/user", methods=["GET"])
@login_required
async def user():
    return await current_user.user_info()


@auth_bp.route(f"/api/{VERSION}/register", methods=["POST"])
@validate_request(models.RegisterRequest)
@validate_response(models.RegisterResponse)
async def register(data: models.RegisterRequest):
    return await User.create_user(data)
