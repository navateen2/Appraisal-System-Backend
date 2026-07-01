from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
from models.user import UserRole


class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1)
    email: EmailStr
    role: UserRole
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    role: str
    created_at: datetime


class UserResponseId(UserResponse):
    created_at: datetime
    updated_at: datetime
