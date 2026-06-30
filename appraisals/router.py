"""User Router"""

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from appraisals.schemas import AppraisalResponse,AppraisalCreate, EmployeeHistoryResponse, UpdateStatusRequest, UpdateStatusResponse
from appraisals.schemas import (
    IDPCreateUpdate, 
    IDPResponse, 
    MeetingNotesCreateUpdate, 
    MeetingNotesResponse,
    MeetingNotesGetResponse
)
from auth.schemas import TokenPayload
from database import get_db
from fastapi import Depends, status, APIRouter

from exceptions import ForbiddenException
from models.appraisal import AppraisalStatus
from . import service
from models.user import UserRole
# from users.schemas import UserCreate
from auth.dependencies import get_current_user, require_role
# from auth.schemas import TokenPayload

router = APIRouter(prefix="/appraisal", tags=["Appraisals"])

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
    )
    return user


@router.get("", response_model=list[AppraisalResponse], dependencies=[Depends(require_role(UserRole.HR,UserRole.Employee))])
async def get_all_appraisals(status: AppraisalStatus | None = None, db: AsyncSession = Depends(get_db)):
    results = await service.get_all_appraisals(db, status)
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


@router.get("/{appraisal_id}", response_model=AppraisalResponse, dependencies=[Depends(require_role(UserRole.HR, UserRole.Employee))])
async def get_appraisal_by_id(
    appraisal_id: int, db: AsyncSession = Depends(get_db)
):
    result = await service.get_appraisal_by_id(appraisal_id, db)
    return result

@router.delete("/{appraisal_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role(UserRole.HR))])
async def soft_delete_Appraisal(appraisal_id: int, db: AsyncSession = Depends(get_db)):
    await service.soft_delete_appraisal(appraisal_id, db)
    return {"message": "appraisal soft deleted"}

@router.post("/{appraisal_id}/idp", response_model=IDPResponse, dependencies=[Depends(require_role(UserRole.Employee))])
async def create_idp_text(appraisal_id: int, body: IDPCreateUpdate, db: AsyncSession = Depends(get_db)):
    updated_appraisal = await service.create_or_update_idp(db, appraisal_id, body.idp_text)
    return updated_appraisal

@router.put("/{appraisal_id}/idp", response_model=IDPResponse, dependencies=[Depends(require_role(UserRole.Employee))])
async def update_idp_text(appraisal_id: int, body: IDPCreateUpdate, db: AsyncSession = Depends(get_db)):
    updated_appraisal = await service.create_or_update_idp(db, appraisal_id, body.idp_text)
    return updated_appraisal

@router.post("/{appraisal_id}/meeting-notes", response_model=MeetingNotesResponse, dependencies=[Depends(require_role(UserRole.HR))])
async def create_meeting_notes(appraisal_id: int, body: MeetingNotesCreateUpdate, db: AsyncSession = Depends(get_db)):
    updated_appraisal = await service.create_or_update_meeting_notes(db, appraisal_id, body.meeting_notes)
    return {
        "message": "Meeting Notes Created Successfully",
        "meeting_notes": updated_appraisal.hr_notes,
        "updated_at": updated_appraisal.updated_at
    }

@router.put("/{appraisal_id}/meeting-notes", response_model=MeetingNotesResponse, dependencies=[Depends(require_role(UserRole.HR))])
async def update_meeting_notes(appraisal_id: int, body: MeetingNotesCreateUpdate, db: AsyncSession = Depends(get_db)):
    updated_appraisal = await service.create_or_update_meeting_notes(db, appraisal_id, body.meeting_notes)
    return {
        "message": "Meeting Notes Updated Successfully",
        "meeting_notes": updated_appraisal.hr_notes,
        "updated_at": updated_appraisal.updated_at
    }

@router.get(
    "/{appraisal_id}/idp", 
    response_model=IDPResponse, 
    dependencies=[Depends(require_role(UserRole.HR, UserRole.Employee))]
)
async def get_appraisal_idp(appraisal_id: int, db: AsyncSession = Depends(get_db)):
    appraisal = await service.get_idp_text(db, appraisal_id)
    return appraisal 

@router.get(
    "/{appraisal_id}/meeting-notes", 
    response_model=MeetingNotesGetResponse, 
    dependencies=[Depends(require_role(UserRole.HR, UserRole.Employee))]
)
async def get_appraisal_meeting_notes(appraisal_id: int, db: AsyncSession = Depends(get_db)):
    appraisal = await service.get_meeting_notes(db, appraisal_id)
    return {
        "meeting_notes": appraisal.hr_notes,
        "updated_at": appraisal.updated_at
    }

@router.get("/{user_id}/appraisals", response_model=List[EmployeeHistoryResponse])
async def get_user_appraisals_history(
    user_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise ForbiddenException("Access Denied: You cannot view appraisal histories belonging to other accounts."
        )
        
    return await service.get_filtered_employee_history(db, user_id)

@router.put(
    "/{appraisal_id}/status", 
    response_model=UpdateStatusResponse, 
    dependencies=[Depends(require_role(UserRole.HR, UserRole.Employee))]
)
async def update_appraisal_status(
    appraisal_id: int,
    payload: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    updated_appraisal = await service.transition_appraisal_status(
        db=db, 
        appraisal_id=appraisal_id, 
        target_status=payload.status,
        current_user=current_user
    )
    
    return UpdateStatusResponse(
        message="Appraisal status updated successfully",
        master_status=updated_appraisal.status
    )