import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_health_check_endpoint():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["version"] == "0.1.0"
        assert "endpoints" in data


@pytest.mark.asyncio
async def test_process_time_header():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert "X-Process-Time" in response.headers


@pytest.mark.asyncio
async def test_cors_headers_present():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


@pytest.mark.asyncio
async def test_cors_denies_unknown_origin():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://evil.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        cors_origin = response.headers.get("access-control-allow-origin", "")
        assert cors_origin != "http://evil.com"


@pytest.mark.asyncio
async def test_rate_limiter_allows_normal_requests():
    from app import rate_limiter

    ip = "192.168.1.1"
    for _ in range(10):
        assert rate_limiter.is_limited(ip) is False


@pytest.mark.asyncio
async def test_root_endpoint_returns_correct_structure():
    from app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        data = response.json()
        assert "/health" in data["endpoints"]
        assert "/chat" in data["endpoints"]
