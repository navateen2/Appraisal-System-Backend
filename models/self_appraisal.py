"""
SelfAppraisal entity — ORM mapped class for table `self_appraisals`.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entity import Entity
from models.appraisal import Appraisal


class SelfAppraisal(Entity):
    __tablename__ = "self_appraisals"

    appraisal_id: Mapped[int] = mapped_column(ForeignKey("appraisals.id"), nullable=False)
    accomplishments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    challenges: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    career_aspirations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    appraisal: Mapped["Appraisal"] = relationship("Appraisal", back_populates="self_appraisal")

    __table_args__ = (UniqueConstraint("appraisal_id", name="uq_self_appraisal_appraisal"),)
