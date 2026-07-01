from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from exceptions import NotFoundException, BadRequestException
from summaries import repo
from summaries.schemas import SummaryCreate, SummaryUpdate
from models.appraisal_summary import AppraisalSummary


async def generate_summary(body: SummaryCreate, db: AsyncSession) -> AppraisalSummary:
    existing = await repo.get_by_appraisal_id(body.appraisal_id, db)
    if existing:
        raise BadRequestException(f"Summary already exists for appraisal id {body.appraisal_id}")

    return await repo.create(db, appraisal_id=body.appraisal_id, summary_text=body.summary)


async def get_summary_by_id(summary_id: int, db: AsyncSession) -> AppraisalSummary:
    summary = await repo.get_by_id(summary_id, db)
    if summary is None:
        raise NotFoundException(f"Appraisal summary with id {summary_id} not found")
    return summary


async def get_summary_by_appraisal(appraisal_id: int, db: AsyncSession) -> AppraisalSummary:
    summary = await repo.get_by_appraisal_id(appraisal_id, db)
    if summary is None:
        return None
    return summary


async def update_summary(summary_id: int, body: SummaryUpdate, db: AsyncSession) -> AppraisalSummary:
    summary = await repo.get_by_id(summary_id, db)
    if summary is None:
        raise NotFoundException(f"Appraisal summary with id {summary_id} not found")

    summary.summary = body.summary
    await repo.save_changes(db)
    return summary


async def soft_delete_summary(summary_id: int, db: AsyncSession):
    summary = await repo.get_id(summary_id, db)
    if summary is None:
        raise NotFoundException(f"Appraisal summary with id {summary_id} not found")

    summary.deleted_at = datetime.utcnow()
    await repo.save_changes(db)
