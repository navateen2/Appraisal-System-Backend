"""
Competencies entity — ORM mapped class for table `competencies`.
"""

from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entity import Entity
from models.lead_feedback import LeadFeedback


class Competencies(Entity):
    __tablename__ = "competencies"

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    feedbacks: Mapped[List["LeadFeedback"]] = relationship("LeadFeedback", back_populates="competency")
