import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User, UserRole
from sqlalchemy import select

@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient, hr_headers, db_session: AsyncSession):
    """Test HR user can successfully create a new user."""
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "securepassword",
        "role": "Employee"
    }
    response = await client.post("/user", json=payload, headers=hr_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane@example.com"
    assert data["role"] == "Employee"

    # Verify user exists in DB
    stmt = select(User).where(User.email == "jane@example.com")
    result = await db_session.scalars(stmt)
    db_user = result.first()
    assert db_user is not None
    assert db_user.name == "Jane Doe"

@pytest.mark.asyncio
async def test_create_user_forbidden(client: AsyncClient, employee_headers):
    """Test regular employee cannot create a user."""
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "securepassword",
        "role": "Employee"
    }
    response = await client.post("/user", json=payload, headers=employee_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_all_users(client: AsyncClient, hr_headers):
    """Test HR user can get all users."""
    response = await client.get("/user", headers=hr_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2

@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient, employee_headers, seed_users):
    """Test retrieving user by ID."""
    emp_user = seed_users["employee"]
    response = await client.get(f"/user/{emp_user.id}", headers=employee_headers)
    assert response.status_code == 200
    assert response.json()["id"] == emp_user.id
    assert response.json()["email"] == emp_user.email

@pytest.mark.asyncio
async def test_get_user_by_name(client: AsyncClient, employee_headers, seed_users):
    """Test searching user by name."""
    emp_user = seed_users["employee"]
    response = await client.get(f"/user/search/{emp_user.name}", headers=employee_headers)
    assert response.status_code == 200
    assert response.json()["id"] == emp_user.id

@pytest.mark.asyncio
async def test_update_user_success(client: AsyncClient, hr_headers, seed_users, db_session: AsyncSession):
    """Test updating user details."""
    emp_user = seed_users["employee"]
    update_payload = {
        "name": "Updated Name",
        "email": "updated@example.com",
        "password": "newpassword",
        "role": "Employee"
    }
    response = await client.put(f"/user/{emp_user.id}", json=update_payload, headers=hr_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["email"] == "updated@example.com"

@pytest.mark.asyncio
async def test_soft_delete_user(client: AsyncClient, hr_headers, seed_users, db_session: AsyncSession):
    """Test soft deleting a user."""
    emp_user = seed_users["employee"]
    response = await client.delete(f"/user/{emp_user.id}", headers=hr_headers)
    assert response.status_code == 204

    # Verify user is soft-deleted
    stmt = select(User).where(User.id == emp_user.id)
    res = await db_session.scalars(stmt)
    db_user = res.first()
    assert db_user.deleted_at is not None
