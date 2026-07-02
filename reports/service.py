from sqlalchemy.ext.asyncio import AsyncSession

from . import repo


async def get_cycle_competency_scores(
    db: AsyncSession,
    cycle_id: int,
):
    return await repo.get_cycle_competency_scores(
        db=db,
        cycle_id=cycle_id,
    )
