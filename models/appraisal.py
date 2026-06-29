"""
Appraisal entity — ORM mapped class for table `appraisals`.
"""

import enum
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entity import Entity
from models.associations import employee_lead_recommendations

if TYPE_CHECKING:
    from models.user import User
    from models.cycles import Cycles
    from models.appraisal_lead_assignment import AppraisalLeadAssignment
    from models.self_appraisal import SelfAppraisal
    from models.appraisal_summary import AppraisalSummary


class AppraisalStatus(str, enum.Enum):
    Initiated = "Initiated"
    SelfAppraised = "Self-Appraised"
    InitiateFeedback = "Initiate Feedback"
    FeedbackSubmitted = "Feedback Submitted"
    MeetingDone = "Meeting Done"
    Done = "Done"


class Appraisal(Entity):
    __tablename__ = "appraisals"

    cycle_id: Mapped[int] = mapped_column(ForeignKey("cycles.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[AppraisalStatus] = mapped_column(String(50), nullable=False)
    self_appraisal_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hr_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    cycle: Mapped["Cycles"] = relationship("Cycles", back_populates="appraisals")
    employee: Mapped["User"] = relationship("User", back_populates="appraisals")
    lead_assignments: Mapped[List["AppraisalLeadAssignment"]] = relationship(
        "AppraisalLeadAssignment", back_populates="appraisal"
    )

    self_appraisal: Mapped[Optional["SelfAppraisal"]] = relationship(
        "SelfAppraisal", uselist=False, back_populates="appraisal"
    )
    summary_report: Mapped[Optional["AppraisalSummary"]] = relationship(
        "AppraisalSummary", uselist=False, back_populates="appraisal"
    )

    recommended_leads: Mapped[List["User"]] = relationship(
        "User", secondary=employee_lead_recommendations, back_populates="recommended_appraisals"
    )

    __table_args__ = (UniqueConstraint("cycle_id", "employee_id", name="uq_cycle_employee"),)
