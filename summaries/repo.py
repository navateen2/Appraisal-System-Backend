from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.appraisal_summary import AppraisalSummary


async def create(db: AsyncSession, appraisal_id: int, summary_text: str) -> AppraisalSummary:
    summary = AppraisalSummary(appraisal_id=appraisal_id, summary=summary_text)
    db.add(summary)
    await db.commit()
    await db.refresh(summary)
    return summary


async def get_by_id(summary_id: int, db: AsyncSession) -> AppraisalSummary | None:
    stmt = select(AppraisalSummary).where(AppraisalSummary.id == summary_id, AppraisalSummary.deleted_at.is_(None))
    result = await db.scalars(stmt)
    return result.first()


async def get_by_appraisal_id(appraisal_id: int, db: AsyncSession) -> AppraisalSummary | None:
    stmt = select(AppraisalSummary).where(
        AppraisalSummary.appraisal_id == appraisal_id, AppraisalSummary.deleted_at.is_(None)
    )
    result = await db.scalars(stmt)
    return result.first()


async def save_changes(db: AsyncSession):
    await db.commit()
