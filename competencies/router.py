from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from fastapi import Depends, status, APIRouter
from competencies import service
from models.user import UserRole
from competencies.schemas import CreateCompetenciesRequest, CompetenciesResponse
from auth.dependencies import require_role

router = APIRouter(prefix="/competency", tags=["Competencies"])

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CompetenciesResponse,
    dependencies=[Depends(require_role(UserRole.HR))],
)
async def create_competency(body: CreateCompetenciesRequest, db: AsyncSession = Depends(get_db)):
    competency = await service.create(db, name=body.name)
    return competency

@router.get("", response_model=list[CompetenciesResponse],dependencies=[Depends(require_role(*UserRole))],)
async def get_all_competencies(
    db: AsyncSession = Depends(get_db)
):
    results = await service.get_all_competencies(db)
    return [r for r in results]

@router.get("/{competency_id}", response_model=CompetenciesResponse, dependencies=[Depends(require_role(*UserRole))])
async def get_competency_by_id(
    competency_id: int, db: AsyncSession = Depends(get_db)
):
    result = await service.get_competency_by_id(competency_id, db)
    return result

@router.put("/{competency_id}", response_model=CompetenciesResponse, dependencies=[Depends(require_role(UserRole.HR))])
async def update_competency(competency_id: int, body: CreateCompetenciesRequest, db: AsyncSession = Depends(get_db)):
    name = body.name
    result = await service.update_competency(competency_id, name, db)
    return result

@router.delete("/{competency_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role(UserRole.HR))])
async def delete_competency(competency_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_competency(competency_id, db)
    return {"message": "Competency deleted"}