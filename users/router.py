"""User Router"""

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from fastapi import Depends, status, APIRouter
from users import service
from models.user import UserRole
from users.schemas import UserCreate, UserResponse, UserResponseId
from auth.dependencies import get_current_user, require_role
from auth.schemas import TokenPayload

router = APIRouter(prefix="/user", tags=["Users"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    dependencies=[Depends(require_role(UserRole.HR))],
)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await service.create(
        db,
        name=body.name,
        email=body.email,
        password=body.password,
        role=body.role,
    )
    return user


@router.get("", response_model=list[UserResponse], dependencies=[Depends(require_role(UserRole.HR))])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    results = await service.get_all_users(db)
    return [r for r in results.all()]


# @router.get("/filter/{filter}", response_model=list[UserResponse], dependencies=[Depends(require_role(UserRole.HR))])
# async def get_filter_users(filter: UserStatus | str, db: AsyncSession = Depends(get_db)):
#     results = await service.get_filter_users(filter, db)
#     return [r for r in results.all()]


@router.get("/search/{user_name}", response_model=UserResponseId)
async def get_user_by_name(
    user_name: str, db: AsyncSession = Depends(get_db), _current_user: TokenPayload = Depends(get_current_user)
):
    result = await service.get_user_by_name(user_name, db)
    return result


@router.get("/{user_id}", response_model=UserResponseId)
async def get_user_by_id(
    user_id: int, db: AsyncSession = Depends(get_db), _current_user: TokenPayload = Depends(get_current_user)
):
    result = await service.get_user_by_id(user_id, db)
    return result


@router.put("/{user_id}", dependencies=[Depends(require_role(UserRole.HR))])
async def update_user(user_id: int, body: UserCreate, db: AsyncSession = Depends(get_db)):
    name = body.name
    email = body.email
    result = await service.update_user(user_id, name, email, db)
    return result


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role(UserRole.HR))])
async def soft_delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    await service.soft_delete_user(user_id, db)
    return {"message": "User soft deleted"}
