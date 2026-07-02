from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.appraisal import Appraisal
from models.appraisal_lead_assignment import AppraisalLeadAssignment
from models.competencies import Competencies
from models.lead_feedback import LeadFeedback
from models.user import User


async def get_cycle_competency_scores(
    db: AsyncSession,
    cycle_id: int,
):
    stmt = (
        select(
            User.id.label("employee_id"),
            User.name.label("employee_name"),
            Competencies.id.label("competency_id"),
            Competencies.name.label("competency_name"),
            LeadFeedback.score.label("score"),
        )
        .join(Appraisal, Appraisal.employee_id == User.id)
        .join(
            AppraisalLeadAssignment,
            AppraisalLeadAssignment.appraisal_id == Appraisal.id,
        )
        .join(
            LeadFeedback,
            LeadFeedback.mapping_id == AppraisalLeadAssignment.id,
        )
        .join(
            Competencies,
            Competencies.id == LeadFeedback.competency_id,
        )
        .where(Appraisal.cycle_id == cycle_id)
        .order_by(User.name, Competencies.name)
    )

    result = await db.execute(stmt)

    return result.mappings().all()
