"""
Appraisal lead reccomendation entity — ORM mapped class for table `appraisal_lead_reccoemendation`.
"""

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entity import Entity
from models.appraisal import Appraisal


class ALR(Entity):
    __tablename__ = "ALR"

    appraisal_id: Mapped[int] = mapped_column(ForeignKey("appraisals.id"), nullable=False)
    reccomended_lead_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    appraisal: Mapped["Appraisal"] = relationship("Appraisal", back_populates="summary_report")

    __table_args__ = (UniqueConstraint("appraisal_id", name="uq_appraisal_summary_appraisal"),)
