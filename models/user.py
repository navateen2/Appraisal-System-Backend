"""
Employee entity — ORM mapped class for table `users`.
"""

import enum
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.entity import Entity


class UserRole(str, enum.Enum):
    UI = ("UI",)
    UX = ("UX",)
    DEVELOPER = "DEVOLOPER"
    HR = "HR"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PROBATION = "PROBATION"


class User(Entity):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
