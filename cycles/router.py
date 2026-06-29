from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, HTTPException
from database import get_db
from models.user import UserRole
from auth.dependencies import require_role, get_current_user
from auth.schemas import TokenPayload
from cycles import service
from cycles.schemas import (
    CycleCreate,
    CycleUpdate,
    CycleStatusUpdate,
    CycleResponse,
    AssignmentParam,
    BulkAssignmentResponse,
)
from models.cycles import CycleStatus

router = APIRouter(prefix="/cycles", tags=["Appraisal Cycles"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CycleResponse,
    dependencies=[Depends(require_role(UserRole.HR))],
)
async def create_new_cycle(
    body: CycleCreate, db: AsyncSession = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)
):
    return await service.create_cycle(db, body, current_user.id)


@router.get("", response_model=list[CycleResponse], dependencies=[Depends(require_role(UserRole.HR))])
async def get_cycles(status: CycleStatus | None = None, db: AsyncSession = Depends(get_db)):
    return await service.get_all_cycles(db, status_filter=status)


@router.get("/{cycle_id}", response_model=CycleResponse, dependencies=[Depends(require_role(UserRole.HR))])
async def get_cycle(cycle_id: int, db: AsyncSession = Depends(get_db)):
    cycle = await service.get_cycle_by_id(db, cycle_id)
    if not cycle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
    return cycle


@router.put("/{cycle_id}", response_model=CycleResponse, dependencies=[Depends(require_role(UserRole.HR))])
async def update_existing_cycle(cycle_id: int, body: CycleUpdate, db: AsyncSession = Depends(get_db)):
    cycle = await service.update_cycle(db, cycle_id, body)
    if not cycle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
    return cycle


@router.patch("/{cycle_id}/status", response_model=CycleResponse, dependencies=[Depends(require_role(UserRole.HR))])
async def update_status(cycle_id: int, body: CycleStatusUpdate, db: AsyncSession = Depends(get_db)):
    return await service.update_cycle_status(db, cycle_id, body)


@router.delete("/{cycle_id}", dependencies=[Depends(require_role(UserRole.HR))])
async def delete_cycle(cycle_id: int, db: AsyncSession = Depends(get_db)):
    success = await service.soft_delete_cycle(db, cycle_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cycle not found")
    return {"message": "Cycle soft-deleted successfully"}


@router.post(
    "/{cycle_id}/assignments", response_model=BulkAssignmentResponse, dependencies=[Depends(require_role(UserRole.HR))]
)
async def manage_cycle_assignments(cycle_id: int, body: AssignmentParam, db: AsyncSession = Depends(get_db)):
    return await service.assign_employees_to_cycle(db, cycle_id, body.employee_ids)


@router.delete("/{cycle_id}/assignments/{employee_id}", dependencies=[Depends(require_role(UserRole.HR))])
async def remove_single_assignment(cycle_id: int, employee_id: int, db: AsyncSession = Depends(get_db)):
    success = await service.remove_employee_assignment(db, cycle_id, employee_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment target record not found")
    return {"message": "Employee assignment track removed successfully from cycle"}
