from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from config import settings
from generate_summary import repo


SYSTEM_PROMPT = """
You are an expert HR appraisal assistant.

Your task is to summarize an employee appraisal into a professional,
objective performance review.

Use ONLY the information provided.

Your summary should contain the following sections:

1. Overall Performance
2. Key Accomplishments
3. Strengths
4. Areas for Improvement
5. Feedback Themes
6. Career Aspirations
7. Overall Assessment

Do not invent information.
If a section has no information, mention that it was not provided.
"""


async def generate_appraisal_summary(
    db: AsyncSession,
    appraisal_id: int,
) -> str:
    appraisal_data = await repo.get_appraisal_summary_data(
        db=db,
        appraisal_id=appraisal_id,
    )

    if appraisal_data is None:
        return None

    prompt = _build_prompt(appraisal_data)

    summary = await _generate_ai_summary(prompt)

    return summary


def _build_prompt(rows: list[dict]) -> str:
    first = rows[0]

    prompt = f"""
Employee: {first["employee_name"]}
Cycle: {first["cycle_name"]}

HR Notes:
{first["hr_notes"] or "Not provided"}

IDP:
{first["idp_text"] or "Not provided"}

Self Appraisal

Accomplishments:
{first["accomplishments"] or "Not provided"}

Challenges:
{first["challenges"] or "Not provided"}

Career Aspirations:
{first["career_aspirations"] or "Not provided"}

Lead Feedback
"""

    for row in rows:
        prompt += f"""

Lead: {row["lead_name"] or "Not provided"}

Competency:
{row["competency_name"] or "Not provided"}

Score:
{row["score"] or "Not provided"}

Strengths:
{row["strengths"] or "Not provided"}

Areas for Improvement:
{row["improvements"] or "Not provided"}
"""

    prompt += """

Generate a concise professional appraisal summary.

Use these headings exactly:

Overall Performance

Key Accomplishments

Strengths

Areas for Improvement

Feedback Themes

Career Aspirations

Overall Assessment
"""

    return prompt


client = AsyncOpenAI(
    api_key=settings.litellm_api_key,
    base_url="https://api.groq.com/openai/v1",
)


async def _generate_ai_summary(prompt: str) -> str:
    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.3,
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

    return response.choices[0].message.content.strip()
