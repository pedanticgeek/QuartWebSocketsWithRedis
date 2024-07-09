import pytest
from data.models import User
from api.error_handlers import APIException
from api.models import RegisterRequest, LoginRequest


@pytest.mark.asyncio
async def test_create_user():
    user_data = RegisterRequest(username="testuser", password="testpassword")
    result = await User.create_user(user_data)
    assert result["username"] == "testuser"


@pytest.mark.asyncio
async def test_login_user(app):
    user_data = LoginRequest(username="testuser", password="testpassword")
    async with app.app_context():
        result = await User.login(user_data)
        assert "auth_token" in result


@pytest.mark.asyncio
async def test_login_negative(app):
    async with app.app_context():
        with pytest.raises(APIException, match="Password do not match"):
            user_data = LoginRequest(username="testuser", password="wrongpassword")
            await User.login(user_data)
        with pytest.raises(APIException, match="User does not exists"):
            user_data = LoginRequest(username="wronguser", password="wrongpassword")
            await User.login(user_data)


@pytest.mark.asyncio
async def test_user_info():
    user = User("testuser")
    user.username = "testuser"
    await user.save_model_to_db()
    info = await user.user_info()
    assert info["username"] == "testuser"


@pytest.mark.asyncio
async def test_logout():
    user = User("testuser")
    user.username = "testuser"
    user.auth_token = "sometoken"
    await user.save_model_to_db()
    result = await user.logout()
    assert result["auth_token"] is None
