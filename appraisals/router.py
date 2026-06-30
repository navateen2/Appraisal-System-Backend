"""User Router"""

from sqlalchemy.ext.asyncio import AsyncSession
from appraisals.schemas import AppraisalResponse,AppraisalCreate, AppraisalUpdate
from auth.schemas import TokenPayload
from database import get_db
from fastapi import Depends, status, APIRouter
from . import service
from models.user import UserRole
# from users.schemas import UserCreate, AppraisalResponse, AppraisalResponseId
from auth.dependencies import get_current_user, require_role
# from auth.schemas import TokenPayload
from lead_assignments.router import router as lead_assignment_router

router = APIRouter(prefix="/appraisal", tags=["Appraisals"])

router.include_router(lead_assignment_router)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=AppraisalResponse,
    dependencies=[Depends(require_role(UserRole.HR))],
)
async def create_appraisal(body: AppraisalCreate, db: AsyncSession = Depends(get_db)):
    user = await service.create(
        db,
        cycle_id=body.cycle_id,
        employee_id=body.employee_id,
        idp_text=body.idp_text,
        hr_notes=body.hr_notes
    )
    return user


@router.get("", response_model=list[AppraisalResponse], dependencies=[Depends(require_role(UserRole.HR))])
async def get_all_appraisals(db: AsyncSession = Depends(get_db)):
    results = await service.get_all_appraisals(db)
    return [r for r in results.all()]


# @router.get("/filter/{filter}", response_model=list[AppraisalResponse], dependencies=[Depends(require_role(UserRole.HR))])
# async def get_filter_appraisal(filter: UserStatus | str, db: AsyncSession = Depends(get_db)):
#     results = await service.get_filter_appraisals(filter, db)
#     return [r for r in results.all()]


# @router.get("/search/{user_name}")
# async def get_user_by_name(
#     user_name: str, db: AsyncSession = Depends(get_db), _current_user: TokenPayload = Depends(get_current_user)
# ):
#     result = await service.get_user_by_name(user_name, db)
#     return result


@router.get("/{appraisal_id}", response_model=AppraisalResponse)
async def get_appraisal_by_id(
    appraisal_id: int, db: AsyncSession = Depends(get_db), _current_user: TokenPayload = Depends(get_current_user)
):
    result = await service.get_appraisal_by_id(appraisal_id, db)
    return result


@router.put("/{appraisal_id}", dependencies=[Depends(require_role(UserRole.HR))],response_model=AppraisalResponse)
async def update_appraisal(appraisal_id: int, body: AppraisalUpdate, db: AsyncSession = Depends(get_db)):
    idp_text=body.idp_text
    status_=body.status
    hr_notes=body.hr_notes
    result = await service.update_appraisal(
        appraisal_id=appraisal_id,
        idp_text=idp_text, 
        hr_notes=hr_notes, 
        db=db,
        status=status_
        )
    return result


@router.delete("/{appraisal_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role(UserRole.HR))])
async def soft_delete_Appraisal(appraisal_id: int, db: AsyncSession = Depends(get_db)):
    await service.soft_delete_appraisal(appraisal_id, db)
    return {"message": "appraisal soft deleted"}
