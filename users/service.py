"""User Service"""

from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from models.user import UserRole, UserStatus
from datetime import datetime, timedelta, timezone

from exceptions import NotFoundException, BadRequestException
from auth.utils import hash_password
from users import repo


async def create(
    db: AsyncSession,
    name: str,
    email: str,
    password: str,
    role: UserRole,
    status: UserStatus,
    age: int | None = None,
) -> User:
    user = await repo.create(
        db, name=name, email=email, password_hash=hash_password(password), age=age, role=role, status=status
    )
    return user


async def get_all_users(db: AsyncSession):
    return await repo.get_all_users(db)


async def get_filter_users(filter: UserStatus | str, db: AsyncSession):
    if filter != "All":
        return await repo.get_filter_users(filter, db)
    return await repo.get_all_users(db)


async def get_user_by_name(user_name: str, db: AsyncSession):
    user = await repo.get_user_by_name(user_name, db)
    if user is None:
        raise NotFoundException("Users not found")
    return user


async def get_user_by_id(user_id: int, db: AsyncSession):
    user = await repo.get_user_by_id(user_id, db)
    if user is None:
        raise NotFoundException(f"User with id: {user_id} not found")
    return user


async def update_user(user_id: int, name: str, email: str, status: str, age: int | None, db: AsyncSession):
    user = await repo.get_user_by_id(user_id, db)
    if user is None:
        raise NotFoundException(f"User with id {user_id} not found")
    if not isinstance(name, str) or not name.strip():
        raise BadRequestException("name must be a non-empty string")
    if not isinstance(email, str) or not email.strip():
        raise BadRequestException("email must be a non-empty string")
    print(status)
    if not isinstance(status, str) or not status.strip():
        raise BadRequestException("status must be a non-empty string")

    probation_period = datetime.now(timezone.utc) - timedelta(days=30)
    user.name = name.strip()
    user.email = email.strip()
    if user.created_at <= probation_period and status != "INACTIVE":
        user.status = status
    else:
        user.status = status
        raise BadRequestException("Probation period is not over")

    result = await repo.update_user(user, email, db)
    return result


async def soft_delete_user(user_id: int, db: AsyncSession):
    user = await repo.get_user_by_id(user_id, db)
    if user is None:
        raise NotFoundException(f"User with id:{user_id} not found")
    user.deleted_at = datetime.now()
    await repo.soft_delete_user(user, db)
    return
