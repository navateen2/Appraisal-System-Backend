"""Appraisal Service"""

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import TokenPayload
from models.appraisal import Appraisal, AppraisalStatus
from models.appraisal_lead_assignment import AssignmentStatus
from models.user import UserRole
from .schemas import AppraisalResponse
from datetime import datetime

from exceptions import ForbiddenException, NotFoundException, BadRequestException
from . import repo


async def create(
    db: AsyncSession,
    cycle_id: int,
    employee_id: int,
) -> AppraisalResponse:
    user = await repo.create(db, cycle_id, employee_id)
    return user


async def get_all_appraisals(db: AsyncSession, status: str | None):
    return await repo.get_all_appraisals(db, status)


# async def get_filter_appraisals(filter: str, db: AsyncSession):
#     if filter != "All":
#         return await repo.get_filter_users(filter, db)
#     return await repo.get_all_users(db)


# async def get_user_by_name(user_name: str, db: AsyncSession):
#     user = await repo.get_user_by_name(user_name, db)
#     if user is None:
#         raise NotFoundException("Users not found")
#     return user


async def get_appraisal_by_id(appraisal_id: int, db: AsyncSession):
    appraisal = await repo.get_appraisal_by_id(appraisal_id, db)
    if appraisal is None:
        raise NotFoundException(f"Appraisal with id: {appraisal_id} not found")
    return appraisal


async def soft_delete_appraisal(appraisal_id: int, db: AsyncSession):
    appraisal = await repo.get_appraisal_by_id(appraisal_id, db)
    if appraisal is None:
        raise NotFoundException(f"Appraisal with id:{appraisal_id} not found")
    if appraisal.status != AppraisalStatus.Initiated:
        raise BadRequestException("Appraisal in progress")
    appraisal.deleted_at = datetime.now()
    await repo.soft_delete_appraisal(appraisal, db)
    return


async def create_or_update_idp(db: AsyncSession, appraisal_id: int, idp_text: str) -> Appraisal:
    appraisal = await repo.get_appraisal_by_id(db, appraisal_id)
    if not appraisal:
        raise NotFoundException(f"Appraisal with ID {appraisal_id} not found.")

    if appraisal.status != AppraisalStatus.FeedbackSubmitted:
        raise BadRequestException(f"IDP updates allowed only when status is '{AppraisalStatus.FeedbackSubmitted}'")

    return await repo.update_appraisal_idp(db, appraisal, idp_text=idp_text)


async def create_or_update_meeting_notes(db: AsyncSession, appraisal_id: int, meeting_notes: str) -> Appraisal:

    appraisal = await repo.get_appraisal_by_id(db, appraisal_id)
    if not appraisal:
        raise NotFoundException(f"Appraisal with ID {appraisal_id} not found.")

    allowed_statuses = [AppraisalStatus.FeedbackSubmitted, AppraisalStatus.MeetingDone]
    if appraisal.status not in allowed_statuses:
        raise BadRequestException(
            "Meeting notes operations are allowed only when status is 'Feedback Submitted' or 'Meeting Done'."
        )

    return await repo.update_appraisal_hr_notes(db, appraisal, hr_notes=meeting_notes)


async def get_idp_text(db: AsyncSession, appraisal_id: int) -> Appraisal:
    appraisal = await repo.get_appraisal_by_id(db, appraisal_id)
    if not appraisal:
        raise NotFoundException(f"Appraisal with ID {appraisal_id} not found.")
    return appraisal


async def get_meeting_notes(db: AsyncSession, appraisal_id: int) -> Appraisal:
    appraisal = await repo.get_appraisal_by_id(db, appraisal_id)
    if not appraisal:
        raise NotFoundException(f"Appraisal with ID {appraisal_id} not found.")
    return appraisal


async def get_filtered_employee_history(db: AsyncSession, employee_id: int) -> List[dict]:
    appraisals = await repo.get_employee_appraisal_history(db, employee_id)
    processed_history = []

    for app in appraisals:
        final_idp = None
        final_notes = None
        if app.status == AppraisalStatus.MeetingDone:
            final_idp = app.idp_text
        elif app.status == AppraisalStatus.Done:
            final_idp = app.idp_text
            final_notes = app.hr_notes

        processed_history.append(
            {
                "id": app.id,
                "employee_id": app.employee_id,
                "status": app.status,
                "idp_text": final_idp,
                "meeting_notes": final_notes,
                "created_at": app.created_at,
                "cycle_details": {
                    "cycle_id": app.cycle.id,
                    "cycle_name": app.cycle.name,
                    "start_date": app.cycle.start_date,
                    "end_date": app.cycle.end_date,
                    "cycle_status": app.cycle.status,
                },
            }
        )

    return processed_history


async def transition_appraisal_status(
    db: AsyncSession, appraisal_id: int, target_status: AppraisalStatus, current_user: TokenPayload
) -> Appraisal:
    appraisal = await repo.get_detailed_appraisal_by_id(db, appraisal_id)
    if not appraisal:
        raise NotFoundException(f"Appraisal with ID {appraisal_id} not found.")

    current_status = appraisal.status

    if target_status == AppraisalStatus.SelfAppraised:
        if current_status != AppraisalStatus.Initiated:
            raise BadRequestException("Can only transition to 'Self-Appraised' from 'Initiated' state.")
        if not appraisal.self_appraisal or appraisal.self_appraisal.submitted_at is None:
            raise BadRequestException("Cannot transition; self appraisal has not been submitted yet.")

    elif target_status == AppraisalStatus.InitiateFeedback:
        if current_user.role != UserRole.HR:
            raise ForbiddenException("Access Denied: Only HR can initiate the feedback cycle.")
        if current_status != AppraisalStatus.SelfAppraised:
            raise BadRequestException("Can only transition to 'Initiate Feedback' from 'Self-Appraised' state.")
        if not appraisal.lead_assignments or len(appraisal.lead_assignments) < 1:
            raise BadRequestException("At least one Appraisal Lead Assignment must be mapped to initiate feedback.")

    elif target_status == AppraisalStatus.FeedbackSubmitted:
        if current_status != AppraisalStatus.InitiateFeedback:
            raise BadRequestException("Can only transition to 'Feedback Submitted' from 'Initiate Feedback' state.")

        if not appraisal.lead_assignments:
            raise BadRequestException("No lead assignments found for this appraisal.")

        has_pending = any(a.status != AssignmentStatus.Submitted for a in appraisal.lead_assignments)
        if has_pending:
            raise BadRequestException("All related lead assignments must be marked as 'Submitted'.")

    elif target_status == AppraisalStatus.MeetingDone:
        if current_user.role != UserRole.HR:
            raise ForbiddenException("Access Denied: Only HR can mark the meeting state as complete.")
        if current_status != AppraisalStatus.FeedbackSubmitted:
            raise BadRequestException("Can only transition to 'Meeting Done' from 'Feedback Submitted' state.")

    elif target_status == AppraisalStatus.Done:
        if current_user.role != UserRole.HR:
            raise ForbiddenException("Access Denied: Only HR can finalize the appraisal.")
        if current_status != AppraisalStatus.MeetingDone:
            raise BadRequestException("Can only transition to 'Done' from 'Meeting Done' state.")

    else:
        raise BadRequestException(f"Unsupported workflow state target: {target_status}")

    return await repo.update_appraisal_status(db, appraisal, target_status)
