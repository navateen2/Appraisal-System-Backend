import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seed_users):
    """Test successful login returns access and refresh tokens."""
    response = await client.post(
        "/auth/login",
        data={"username": "hr@example.com", "password": "hrpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_failure(client: AsyncClient, seed_users):
    """Test login failure with invalid password."""
    response = await client.post(
        "/auth/login",
        data={"username": "hr@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_token_refresh_success(client: AsyncClient, seed_users):
    """Test token refresh with a valid refresh token."""
    # First login to get a refresh token
    login_resp = await client.post(
        "/auth/login",
        data={"username": "hr@example.com", "password": "hrpassword"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    # Refresh the token
    refresh_resp = await client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_token_refresh_failure(client: AsyncClient, seed_users):
    """Test token refresh with an invalid refresh token."""
    refresh_resp = await client.post(
        "/auth/refresh",
        json={"refresh_token": "invalidtokenvalue"}
    )
    assert refresh_resp.status_code == 401
