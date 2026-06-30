import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.audit import Audit, AuditAction
from sqlalchemy import select

@pytest.mark.asyncio
async def test_audit_logging_on_mutation(client: AsyncClient, hr_headers, db_session: AsyncSession, seed_users):
    """Test that mutating operations write corresponding logs to the audits table."""
    # 1. Create a competency (triggers INSERT listener)
    payload = {"name": "Communication Skills"}
    create_resp = await client.post("/competency", json=payload, headers=hr_headers)
    assert create_resp.status_code == 201
    competency_id = create_resp.json()["id"]

    # Verify INSERT audit log exists
    stmt = (
        select(Audit)
        .where(Audit.table_name == "competencies", Audit.action == AuditAction.INSERT)
    )
    result = await db_session.scalars(stmt)
    insert_audit = result.first()
    assert insert_audit is not None
    assert insert_audit.user_id == seed_users["hr"].id
    assert insert_audit.record_id == competency_id

    # 2. Update competency (triggers UPDATE listener)
    update_payload = {"name": "Advanced Communication Skills"}
    update_resp = await client.put(f"/competency/{competency_id}", json=update_payload, headers=hr_headers)
    assert update_resp.status_code == 200

    # Verify UPDATE audit log exists
    stmt_up = (
        select(Audit)
        .where(Audit.table_name == "competencies", Audit.action == AuditAction.UPDATE)
    )
    result_up = await db_session.scalars(stmt_up)
    update_audit = result_up.first()
    assert update_audit is not None
    assert update_audit.user_id == seed_users["hr"].id
    assert update_audit.record_id == competency_id
    # Assert differential changes
    assert "name" in update_audit.changed_fields
    assert update_audit.changed_fields["name"][0] == "Communication Skills"
    assert update_audit.changed_fields["name"][1] == "Advanced Communication Skills"
