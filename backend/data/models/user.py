import os
import json
from typing import Self, Dict, Any

from quart import current_app
from quart_auth import AuthUser
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


from api.error_handlers import APIException
from api import models


PH = PasswordHasher()


class User(AuthUser):
    def __init__(
        self,
        auth_id: str,
    ):
        """
        AuthUser is used by Quart-Auth and takes auth_id:str as identity attribute.
        It is not necessary to mix AuthUser with your User Data model, but for the sake of simplicity, I've joined them here.
        When AuthUser is initiated, it doesn't have properties of the data model class - that's what _resolve method is for.
        """
        super().__init__(auth_id)
        self._resolved = False
        self.username = None
        self.password_hash = None
        self.auth_token = None

    async def _resolve(self) -> Self:
        if not self._resolved:
            data = await self.load_model_from_db(self._auth_id)
            self.from_dict(data)
            self._resolved = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert User object to dictionary excluding AuthUser properties."""
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "auth_token": self.auth_token,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        self.username = data.get("username")
        self.password_hash = data.get("password_hash")
        self.auth_token = data.get("auth_token")

    @classmethod
    async def load_model_from_db(cls, username: str) -> Self:
        """This is a fake method of loading user model from database. Here it simply loads the json file from the database folder"""
        with open(
            os.path.join(os.getcwd(), "data/database/", f"{username}.json"), "r"
        ) as f:
            data = json.load(f)
            return data

    async def save_model_to_db(self) -> None:
        """This is a fake method of loading user model to database. Here it simply saves the json file to the database folder"""
        with open(
            os.path.join(os.getcwd(), "data/database/", f"{self.username}.json"), "w"
        ) as f:
            json.dump(self.to_dict(), f)

    @classmethod
    async def create_user(cls, data: models.RegisterRequest) -> Dict[str, Any]:
        user = cls(auth_id=data.username)
        user.username = data.username
        user.password_hash = PH.hash(data.password)
        await user.save_model_to_db()
        return {"username": user.username}

    @classmethod
    async def login(cls, data: models.LoginRequest) -> Dict[str, Any]:
        try:
            user: User = cls(data.username)
            await user._resolve()
            if user and PH.verify(user.password_hash, data.password):
                token = current_app.auth_manager.dump_token(user.auth_id)
                user.auth_token = token
                await user.save_model_to_db()
                return {"auth_token": token}
        except FileNotFoundError as ex:
            raise APIException("User does not exists", 404) from ex
        except VerifyMismatchError as ex:
            raise APIException("Password do not match", 401) from ex

    async def logout(self) -> None:
        await self._resolve()
        self.auth_token = None
        await self.save_model_to_db()
        return {"username": self.username, "auth_token": None}

    async def user_info(self) -> Dict[str, Any]:
        await self._resolve()
        return {"username": self.username}
