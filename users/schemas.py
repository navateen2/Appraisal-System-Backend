from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
from models.user import UserRole, UserStatus


class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1)
    email: EmailStr
    role: UserRole
    status: UserStatus
    age: int | None = Field(ge=0, le=150)
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    status: UserStatus
    role: str
    age: int | None = None


class UserResponseId(UserResponse):
    created_at: datetime
    updated_at: datetime
