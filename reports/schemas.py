from pydantic import BaseModel


class CompetencyScoreReportRow(BaseModel):
    employee_id: int
    employee_name: str

    competency_id: int
    competency_name: str

    score: int | None
