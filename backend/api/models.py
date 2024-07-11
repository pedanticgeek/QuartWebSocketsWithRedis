from typing import Dict, Any, Optional
from pydantic import BaseModel, Extra


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


class WebsocketPaylod(BaseModel, extra="allow"):
    message: str


class WebsocketMessage(BaseModel):
    payload: WebsocketPaylod
    metadata: Optional[Dict[str, Any] | None]
