import asyncio
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient

from database.connection import Base, get_db
from main import app
import models  # Ensure all models are registered on Base
from auth.utils import hash_password
from models.user import User, UserRole

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create all tables in the test database once per session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session per test with rollback on completion."""
    async with test_engine.connect() as connection:
        async with connection.begin() as transaction:
            async with TestSessionLocal(bind=connection) as session:
                yield session
                await transaction.rollback()

@pytest.fixture(autouse=True)
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency in the FastAPI app to use the test session."""
    async def _get_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX AsyncClient targeting the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def seed_users(db_session: AsyncSession):
    """Seed an HR user and an Employee user for authentication tests."""
    hr_user = User(
        name="HR Manager",
        email="hr@example.com",
        password_hash=hash_password("hrpassword"),
        role=UserRole.HR
    )
    emp_user = User(
        name="Regular Employee",
        email="employee@example.com",
        password_hash=hash_password("emppassword"),
        role=UserRole.Employee
    )
    db_session.add(hr_user)
    db_session.add(emp_user)
    await db_session.commit()
    await db_session.refresh(hr_user)
    await db_session.refresh(emp_user)
    return {"hr": hr_user, "employee": emp_user}

@pytest.fixture
async def hr_token(client: AsyncClient, seed_users) -> str:
    """Return JWT access token for the HR user."""
    response = await client.post(
        "/auth/login",
        data={"username": "hr@example.com", "password": "hrpassword"}
    )
    return response.json()["access_token"]

@pytest.fixture
async def employee_token(client: AsyncClient, seed_users) -> str:
    """Return JWT access token for the regular employee user."""
    response = await client.post(
        "/auth/login",
        data={"username": "employee@example.com", "password": "emppassword"}
    )
    return response.json()["access_token"]

@pytest.fixture
def hr_headers(hr_token: str) -> dict:
    """Return authorization headers for the HR user."""
    return {"Authorization": f"Bearer {hr_token}"}

@pytest.fixture
def employee_headers(employee_token: str) -> dict:
    """Return authorization headers for the employee user."""
    return {"Authorization": f"Bearer {employee_token}"}
