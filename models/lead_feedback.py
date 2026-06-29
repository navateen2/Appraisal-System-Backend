"""
LeadFeedback entity — ORM mapped class for table `lead_feedbacks`.
"""

from typing import Optional
from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entity import Entity
from models.appraisal_lead_assignment import AppraisalLeadAssignment
from models.competencies import Competencies


class LeadFeedback(Entity):
    __tablename__ = "lead_feedbacks"

    mapping_id: Mapped[int] = mapped_column(ForeignKey("appraisal_lead_assignments.id"), nullable=False)
    competency_id: Mapped[int] = mapped_column(ForeignKey("competencies.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    improvements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    idp_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    assignment: Mapped["AppraisalLeadAssignment"] = relationship("AppraisalLeadAssignment", back_populates="feedbacks")
    competency: Mapped["Competencies"] = relationship("Competencies", back_populates="feedbacks")
