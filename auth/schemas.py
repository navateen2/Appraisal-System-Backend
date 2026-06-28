from pydantic import BaseModel
from models.user import UserRole


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenPayload(BaseModel):
    id: int
    email: str
    role: UserRole


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str | None = "bearer"
