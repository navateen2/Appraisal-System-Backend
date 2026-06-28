"""User Repo"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models import User
from models.user import UserRole, UserStatus
from exceptions import ConflictException


async def create(
    db: AsyncSession,
    name: str,
    email: str,
    password_hash: str,
    role: UserRole,
    status: UserStatus,
    age: int | None = None,
) -> User:
    user = User(name=name, email=email, password_hash=password_hash, age=age, role=role)
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(f"Email '{email}' is already in use")
    await db.refresh(user)
    return user


async def get_all_users(db: AsyncSession):
    stmt = select(User).where(User.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result


async def get_filter_users(filter: str, db: AsyncSession):
    stmt = select(User).where(User.deleted_at.is_(None), User.status == UserStatus[filter])
    result = await db.scalars(stmt)
    return result


async def get_user_by_id(user_id: int, db: AsyncSession):
    stmt = select(User).options(selectinload(User.addresses)).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.scalars(stmt)
    user = result.first()
    return user


async def get_user_by_name(user_name: str, db: AsyncSession):
    stmt = select(User).where(User.name == user_name, User.deleted_at.is_(None))
    result = await db.scalars(stmt)
    user = result.first()
    return user


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
    user = await db.scalars(stmt)
    return user.first()


async def update_user(user: User, email: str, db: AsyncSession):
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(f"Email '{email}' is already in use")
    await db.refresh(user)
    return user


async def soft_delete_user(user: User, db: AsyncSession):
    await db.commit()
    return
