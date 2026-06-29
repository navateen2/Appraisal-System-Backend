"""
AppraisalLeadAssignment entity — ORM mapped class for table `appraisal_lead_assignments`.
"""

import enum
from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entity import Entity
from models.appraisal import Appraisal
from models.user import User
from models.lead_feedback import LeadFeedback


class AssignmentStatus(str, enum.Enum):
    Pending = "Pending"
    Submitted = "Submitted"


class AppraisalLeadAssignment(Entity):
    __tablename__ = "appraisal_lead_assignments"

    appraisal_id: Mapped[int] = mapped_column(ForeignKey("appraisals.id"), nullable=False)
    lead_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[AssignmentStatus] = mapped_column(String(50), nullable=False)

    # Relationships
    appraisal: Mapped["Appraisal"] = relationship("Appraisal", back_populates="lead_assignments")
    lead: Mapped["User"] = relationship("User", foreign_keys=[lead_id], back_populates="assigned_lead_mappings")
    assigner: Mapped["User"] = relationship("User", foreign_keys=[assigned_by], back_populates="given_assignments")
    feedbacks: Mapped[List["LeadFeedback"]] = relationship("LeadFeedback", back_populates="assignment")
