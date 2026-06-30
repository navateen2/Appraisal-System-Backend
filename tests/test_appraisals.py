import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.appraisal import Appraisal
from sqlalchemy import select

@pytest.mark.asyncio
async def test_appraisal_lifecycle(client: AsyncClient, hr_headers, seed_users, db_session: AsyncSession):
    """Test full appraisal lifecycle: create, retrieve, update, and soft delete."""
    # 1. Create a cycle first
    cycle_resp = await client.post("/cycles", json={
        "name": "Appraisal Test Cycle",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-30T00:00:00"
    }, headers=hr_headers)
    assert cycle_resp.status_code == 201
    cycle_id = cycle_resp.json()["id"]
    emp_user = seed_users["employee"]

    # 2. Create appraisal
    appraisal_payload = {
        "cycle_id": cycle_id,
        "employee_id": emp_user.id,
        "status": "Initiated",
        "idp_text": "Need to learn FastAPI.",
        "hr_notes": "First appraisal"
    }
    create_resp = await client.post("/appraisal", json=appraisal_payload, headers=hr_headers)
    assert create_resp.status_code == 201
    appraisal_id = create_resp.json()["id"]

    # 3. Retrieve appraisal
    get_resp = await client.get(f"/appraisal/{appraisal_id}", headers=hr_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["idp_text"] == "Need to learn FastAPI."

    # 4. Update appraisal
    update_payload = {
        "idp_text": "Need to learn FastAPI and Advanced SQL.",
        "hr_notes": "Updated notes",
        "status": "Initiated"
    }
    update_resp = await client.put(f"/appraisal/{appraisal_id}", json=update_payload, headers=hr_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["idp_text"] == "Need to learn FastAPI and Advanced SQL."

    # 5. Soft Delete appraisal (using corrected path param)
    delete_resp = await client.delete(f"/appraisal/{appraisal_id}", headers=hr_headers)
    assert delete_resp.status_code == 204

    # Verify soft deleted in DB
    stmt = select(Appraisal).where(Appraisal.id == appraisal_id)
    result = await db_session.scalars(stmt)
    db_appraisal = result.first()
    assert db_appraisal is not None
    assert db_appraisal.deleted_at is not None
