import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.cycles import Cycles, CycleStatus
from sqlalchemy import select

@pytest.mark.asyncio
async def test_create_cycle_success(client: AsyncClient, hr_headers, db_session: AsyncSession):
    """Test HR user can create an appraisal cycle."""
    payload = {
        "name": "Mid Year 2026",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-30T00:00:00"
    }
    response = await client.post("/cycles", json=payload, headers=hr_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Mid Year 2026"
    assert data["status"] == "Initiated"

    # Verify cycle exists in DB
    stmt = select(Cycles).where(Cycles.name == "Mid Year 2026")
    result = await db_session.scalars(stmt)
    db_cycle = result.first()
    assert db_cycle is not None

@pytest.mark.asyncio
async def test_get_cycles(client: AsyncClient, hr_headers, seed_users):
    """Test retrieving appraisal cycles."""
    # First create a cycle
    payload = {
        "name": "Year End 2026",
        "start_date": "2026-12-01T00:00:00",
        "end_date": "2026-12-31T00:00:00"
    }
    await client.post("/cycles", json=payload, headers=hr_headers)

    response = await client.get("/cycles", headers=hr_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

@pytest.mark.asyncio
async def test_update_cycle_details(client: AsyncClient, hr_headers):
    """Test updating cycle details."""
    # Create cycle
    create_resp = await client.post("/cycles", json={
        "name": "Q1 2026",
        "start_date": "2026-01-01T00:00:00",
        "end_date": "2026-03-31T00:00:00"
    }, headers=hr_headers)
    cycle_id = create_resp.json()["id"]

    # Update it
    update_payload = {
        "name": "Q1 2026 Rev",
        "start_date": "2026-01-01T00:00:00",
        "end_date": "2026-04-15T00:00:00"
    }
    update_resp = await client.put(f"/cycles/{cycle_id}", json=update_payload, headers=hr_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Q1 2026 Rev"

@pytest.mark.asyncio
async def test_manage_cycle_assignments(client: AsyncClient, hr_headers, seed_users):
    """Test assigning employees to a cycle and removing the assignment."""
    # Create cycle
    create_resp = await client.post("/cycles", json={
        "name": "Q2 2026",
        "start_date": "2026-04-01T00:00:00",
        "end_date": "2026-06-30T00:00:00"
    }, headers=hr_headers)
    cycle_id = create_resp.json()["id"]
    emp_user = seed_users["employee"]

    # Assign employee
    assign_payload = {"employee_ids": [emp_user.id]}
    assign_resp = await client.post(f"/cycles/{cycle_id}/assignments", json=assign_payload, headers=hr_headers)
    assert assign_resp.status_code == 200
    data = assign_resp.json()
    assert len(data["successfully_assigned"]) == 1
    assert data["successfully_assigned"][0]["employee_id"] == emp_user.id

    # Remove assignment
    remove_resp = await client.delete(f"/cycles/{cycle_id}/assignments/{emp_user.id}", headers=hr_headers)
    assert remove_resp.status_code == 200
    assert "removed successfully" in remove_resp.json()["message"]
