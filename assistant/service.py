import json
from openai import AsyncOpenAI

from config import settings
from .schemas import (
    FeedbackQuestionnaireResponse,
)

client = AsyncOpenAI(
    api_key=settings.litellm_api_key,
    base_url="https://api.groq.com/openai/v1",
)


SYSTEM_PROMPT = """
You are an HR Performance Review Assistant.

Your job is to generate structured guidance for reviewers.

For every competency provided, generate:

- evaluation_focus
- 4 review questions
- scoring criteria for:
    - 9-10
    - 7-8
    - 5-6
    - 3-4
    - 1-2
- 3 example strengths
- 3 example improvement suggestions

Return ONLY valid JSON.

The JSON format MUST be:

{
    "questionnaires":[
        {
            "competency_id":1,
            "competency_name":"Communication",
            "evaluation_focus":"...",
            "questions":[...],
            "score_guide":{
                "9-10":"...",
                "7-8":"...",
                "5-6":"...",
                "3-4":"...",
                "1-2":"..."
            },
            "strength_examples":[...],
            "improvement_examples":[...]
        }
    ]
}

Do not include markdown.
Do not include explanations.
Return JSON only.
"""


async def generate_feedback_questionnaire(
    competencies: list[str],
) -> FeedbackQuestionnaireResponse:
    prompt = _build_prompt(
        competencies=competencies,
    )

    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    content = response.choices[0].message.content

    data = content

    if isinstance(data, list):
        data = data[0]

    return FeedbackQuestionnaireResponse.model_validate_json(data)


def _build_prompt(
    competencies: list[str],
) -> str:

    prompt = """
Generate reviewer guidance for the following competencies.

"""

    for competency in competencies:
        prompt += f"""
Competency Name: {competency}

"""

    return prompt
