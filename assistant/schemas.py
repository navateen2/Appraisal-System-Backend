from pydantic import BaseModel


class FeedbackQuestionnaireRequest(BaseModel):
    competencies: list[str]


class CompetencyQuestionnaire(BaseModel):
    competency_name: str

    evaluation_focus: str

    questions: list[str]

    score_guide: dict[str, str]

    strength_examples: list[str]

    improvement_examples: list[str]


class FeedbackQuestionnaireResponse(BaseModel):
    questionnaires: list[CompetencyQuestionnaire]
