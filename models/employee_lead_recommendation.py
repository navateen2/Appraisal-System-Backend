"""
Employee lead recomendation entity — ORM mapped class for table `EmployeeLeadRecommendations`.
"""

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entity import Entity
from models.appraisal import Appraisal


class ELR(Entity):
    __tablename__ = "EmployeeLeadRecomendations"

    appraisal_id: Mapped[int] = mapped_column(ForeignKey("appraisals.id"), nullable=False)
    recommended_lead_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    appraisal: Mapped["Appraisal"] = relationship("Appraisal", back_populates="summary_report")

    __table_args__ = (UniqueConstraint("appraisal_id", name="uq_appraisal_summary_appraisal"),)
