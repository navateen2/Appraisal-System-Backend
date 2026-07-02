from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from auth.schemas import TokenPayload
from config import settings
from generate_summary import repo
from summaries.service import get_summary_by_appraisal
from summaries.router import generate_appraisal_summary as store_in_db
from summaries.schemas import SummaryCreate


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
No prose or markdown only plain text
"""


async def generate_appraisal_summary(db: AsyncSession, appraisal_id: int, current_user: TokenPayload) -> str:
    appraisal_summary = await get_summary_by_appraisal(appraisal_id=appraisal_id, db=db)
    if appraisal_summary is not None:
        return appraisal_summary.summary

    appraisal_data = await repo.get_appraisal_summary_data(
        db=db,
        appraisal_id=appraisal_id,
    )

    if appraisal_data is None:
        return None

    prompt = _build_prompt(appraisal_data)

    summary = await _generate_ai_summary(prompt)

    await store_in_db(db=db, body=SummaryCreate(appraisal_id=appraisal_id, summary=summary), current_user=current_user)

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


async def get_cycle_appraisal_summaries(
    db: AsyncSession,
    cycle_id: int,
):
    return await repo.get_cycle_appraisal_summaries(
        db=db,
        cycle_id=cycle_id,
    )

async def get_appraisal_summary_details(
    db: AsyncSession,
    appraisal_id: int,
):
    rows = await repo.get_appraisal_summary_data(
        db=db,
        appraisal_id=appraisal_id,
    )

    if not rows:
        return None

    first = rows[0]

    leads = {}

    for row in rows:
        assignment_id = row["assignment_id"]

        if assignment_id not in leads:
            leads[assignment_id] = {
                "assignment_id": assignment_id,
                "lead_id": row["lead_id"],
                "lead_name": row["lead_name"],
                "feedback": [],
            }

        if row["competency_name"] is not None:
            leads[assignment_id]["feedback"].append(
                {
                    "competency_name": row["competency_name"],
                    "score": row["score"],
                    "strengths": row["strengths"],
                    "improvements": row["improvements"],
                }
            )

    return {
        "appraisal_id": first["appraisal_id"],
        "cycle_id": first["cycle_id"],
        "cycle_name": first["cycle_name"],
        "employee_id": first["employee_id"],
        "employee_name": first["employee_name"],
        "hr_notes": first["hr_notes"],
        "idp_text": first["idp_text"],
        "self_appraisal_id": first["self_appraisal_id"],
        "accomplishments": first["accomplishments"],
        "challenges": first["challenges"],
        "career_aspirations": first["career_aspirations"],
        "lead_feedback": list(leads.values()),
    }