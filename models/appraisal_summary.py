"""
AppraisalSummary entity — ORM mapped class for table `appraisal_summaries`.
"""

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entity import Entity
from models.appraisal import Appraisal


class AppraisalSummary(Entity):
    __tablename__ = "appraisal_summaries"

    appraisal_id: Mapped[int] = mapped_column(ForeignKey("appraisals.id"), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    appraisal: Mapped["Appraisal"] = relationship("Appraisal", back_populates="summary_report")

    __table_args__ = (UniqueConstraint("appraisal_id", name="uq_appraisal_summary_appraisal"),)
