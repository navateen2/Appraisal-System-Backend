import asyncio
import os

# Set DATABASE_URL to a dummy PostgreSQL URL so that module-level create_async_engine
# parsing with pool_size/max_overflow parameters doesn't throw a SQLite pool TypeError.
os.environ["DATABASE_URL"] = "postgresql+asyncpg://localhost/dummy"
os.environ["JWT_SECRET"] = "test_secret_key_placeholder"
os.environ["JWT_SECRET_REFRESH"] = "test_secret_key_refresh_placeholder"
os.environ["JWT_EXPIRY_MINUTES"] = "60"
os.environ["JWT_EXPIRY_REFRESH"] = "30"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["LITELLM_API_KEY"] = "test_key"
os.environ["LITELLM_API_BASE"] = "https://api.openai.com"
os.environ["LITELLM_MODEL"] = "gpt-4"

import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient

# Import connection module to monkeypatch its engine and session maker references
import database.connection

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

# Monkeypatch database connection variables to use SQLite instead of the dummy postgres engine
database.connection.engine = test_engine
database.connection.AsyncSessionLocal = TestSessionLocal

from database.connection import Base, get_db
from main import app
import models  # Ensure all models are registered on Base
from auth.utils import hash_password
from models.user import User, UserRole

# Teach SQLite how to compile/render PostgreSQL JSONB columns
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"
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

from httpx import ASGITransport

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX AsyncClient targeting the FastAPI application."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
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
