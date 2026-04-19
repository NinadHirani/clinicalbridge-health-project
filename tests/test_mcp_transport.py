"""Smoke test: verify the MCP server responds correctly."""
import httpx
import pytest

BASE = "http://localhost:8080"


@pytest.mark.asyncio
async def test_health():
    """Test health check endpoint."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_agent_card():
    """Test agent card manifest."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE}/agent_card.json")
    assert r.status_code == 200
    data = r.json()
    assert data["protocol"] == "mcp"
    assert data["transport"] == "sse"
    assert len(data["tools"]) == 5
    assert all(tool["name"] for tool in data["tools"])


@pytest.mark.asyncio
async def test_sse_stream():
    """Test SSE endpoint streams MCP protocol events."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE}/sse", timeout=5.0)
    assert r.status_code == 200
    assert "text/event-stream" in r.headers.get("content-type", "")
