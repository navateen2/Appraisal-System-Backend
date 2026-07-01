from sqlalchemy import select
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from models.appraisal import Appraisal
from models.cycles import Cycles
from models.user import User
from models.self_appraisal import SelfAppraisal
from models.appraisal_lead_assignment import AppraisalLeadAssignment
from models.lead_feedback import LeadFeedback
from models.competencies import Competencies


async def get_appraisal_summary_data(
    db: AsyncSession,
    appraisal_id: int,
):
    employee = aliased(User)
    lead = aliased(User)

    stmt = (
        select(
            Appraisal.id.label("appraisal_id"),
            Appraisal.cycle_id,
            Cycles.name.label("cycle_name"),
            Appraisal.employee_id,
            employee.name.label("employee_name"),
            Appraisal.hr_notes,
            Appraisal.idp_text,
            SelfAppraisal.id.label("self_appraisal_id"),
            SelfAppraisal.accomplishments,
            SelfAppraisal.challenges,
            SelfAppraisal.career_aspirations,
            AppraisalLeadAssignment.id.label("assignment_id"),
            AppraisalLeadAssignment.lead_id,
            lead.name.label("lead_name"),
            LeadFeedback.id.label("feedback_id"),
            Competencies.name.label("competency_name"),
            LeadFeedback.score,
            LeadFeedback.strengths,
            LeadFeedback.improvements,
        )
        .outerjoin(Cycles, Cycles.id == Appraisal.cycle_id)
        .outerjoin(employee, employee.id == Appraisal.employee_id)
        .outerjoin(
            SelfAppraisal,
            SelfAppraisal.appraisal_id == Appraisal.id,
        )
        .outerjoin(
            AppraisalLeadAssignment,
            AppraisalLeadAssignment.appraisal_id == Appraisal.id,
        )
        .outerjoin(
            lead,
            lead.id == AppraisalLeadAssignment.lead_id,
        )
        .outerjoin(
            LeadFeedback,
            LeadFeedback.mapping_id == AppraisalLeadAssignment.id,
        )
        .outerjoin(
            Competencies,
            Competencies.id == LeadFeedback.competency_id,
        )
        .where(Appraisal.id == appraisal_id)
    )

    result = await db.execute(stmt)

    return result.mappings().all()
