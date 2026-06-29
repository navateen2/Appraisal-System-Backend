"""
Cycles entity — ORM mapped class for table `cycles`.
"""

import enum
from datetime import date
from typing import List
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entity import Entity
from models.user import User
from models.appraisal import Appraisal


class CycleStatus(str, enum.Enum):
    Initiated = "Initiated"
    InProgress = "In Progress"
    Completed = "Completed"


class Cycles(Entity):
    __tablename__ = "cycles"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[CycleStatus] = mapped_column(String(50), nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    creator: Mapped["User"] = relationship("User", back_populates="cycles_created")
    appraisals: Mapped[List["Appraisal"]] = relationship("Appraisal", back_populates="cycle")
