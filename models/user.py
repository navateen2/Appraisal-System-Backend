"""
User entity — ORM mapped class for table `users`.
"""

import enum
from datetime import date
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.entity import Entity
from models.associations import employee_lead_recommendations

if TYPE_CHECKING:
    from models.cycles import Cycles
    from models.appraisal import Appraisal
    from models.appraisal_lead_assignment import AppraisalLeadAssignment
    from models.audit import Audit


class UserRole(str, enum.Enum):
    HR = "HR"
    Employee = "Employee"


class User(Entity):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(50), nullable=False)
    joined_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    cycles_created: Mapped[List["Cycles"]] = relationship("Cycles", back_populates="creator")
    appraisals: Mapped[List["Appraisal"]] = relationship("Appraisal", back_populates="employee")
    assigned_lead_mappings: Mapped[List["AppraisalLeadAssignment"]] = relationship(
        "AppraisalLeadAssignment", foreign_keys="[AppraisalLeadAssignment.lead_id]", back_populates="lead"
    )
    given_assignments: Mapped[List["AppraisalLeadAssignment"]] = relationship(
        "AppraisalLeadAssignment", foreign_keys="[AppraisalLeadAssignment.assigned_by]", back_populates="assigner"
    )
    audits: Mapped[List["Audit"]] = relationship("Audit", back_populates="user")

    recommended_appraisals: Mapped[List["Appraisal"]] = relationship(
        "Appraisal", secondary=employee_lead_recommendations, back_populates="recommended_leads"
    )
