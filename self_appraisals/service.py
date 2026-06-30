

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from self_appraisals import repo
from exceptions import ConflictException, NotFoundException
from models.self_appraisal import SelfAppraisal
from self_appraisals.schemas import SelfAppraisalCreate, SelfAppraisalUpdate


async def create_self_appraisal(
    db: AsyncSession,
    data: SelfAppraisalCreate,
) -> SelfAppraisal:
    existing = await repo.get_by_appraisal_id(db, data.appraisal_id)

    if existing:
        raise ConflictException(
            "Self appraisal already exists for this appraisal_id"
        )

    obj = SelfAppraisal(
        appraisal_id=data.appraisal_id,
        accomplishments=data.accomplishments,
        challenges=data.challenges,
        career_aspirations=data.career_aspirations,
        submitted_at=datetime.now(timezone.utc),
    )

    return await repo.create(db, obj)

async def get_all_self_appraisals(db: AsyncSession):
    return await repo.get_all(db)

async def get_self_appraisal_by_id(
    db: AsyncSession,
    self_appraisal_id: int,
) -> SelfAppraisal:

    obj = await repo.get_by_id(db, self_appraisal_id)

    if not obj:
        raise NotFoundException("Self appraisal not found")
    return obj

async def update_self_appraisal(
    db: AsyncSession,
    self_appraisal_id: int,
    data: SelfAppraisalUpdate,
) -> SelfAppraisal:

    obj = await repo.get_by_id(db, self_appraisal_id)

    if not obj:
        raise NotFoundException("Self appraisal not found")

    if data.accomplishments is not None:
        obj.accomplishments = data.accomplishments

    if data.challenges is not None:
        obj.challenges = data.challenges

    if data.career_aspirations is not None:
        obj.career_aspirations = data.career_aspirations

    # optional audit field (only if exists in Entity base)
    if hasattr(obj, "updated_at"):
        obj.updated_at = datetime.now(timezone.utc)

    return await repo.update(db, obj)

async def delete_self_appraisal(
    db: AsyncSession,
    self_appraisal_id: int,
) -> None:

    obj = await repo.get_by_id(db, self_appraisal_id)
    if not obj:
        raise NotFoundException("Self appraisal not found")
    await repo.delete(db, obj)
