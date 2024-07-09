from typing import Dict, Any, Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    auth_token: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class RegisterResponse(BaseModel):
    username: str


class WebsocketMessage(BaseModel):
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any] | None]
