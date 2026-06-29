"""
Shared association tables for explicit many-to-many relationships.
"""

from sqlalchemy import Table, Column, Integer, ForeignKey
from models.entity import Entity

employee_lead_recommendations = Table(
    "employee_lead_recommendations",
    Entity.metadata,
    Column("appraisal_id", Integer, ForeignKey("appraisals.id", ondelete="CASCADE"), primary_key=True),
    Column("recommended_lead_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)
