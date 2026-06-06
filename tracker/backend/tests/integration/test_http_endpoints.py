"""Integration tests for HTTP endpoints with real Redis."""
import pytest

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_home_endpoint_returns_ip(live_http_client):
    response = await live_http_client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint(live_http_client):
    response = await live_http_client.get("/health")
    assert response.status_code in (200, 503)
    data = await response.get_json()
    assert "status" in data
    assert "redis" in data


@pytest.mark.asyncio
async def test_announce_without_params(live_http_client):
    response = await live_http_client.get("/announce")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_announce_valid(live_http_client):
    response = await live_http_client.get(
        "/announce",
        query_string={
            "info_hash": "a" * 40,
            "peer_id": "-testpeer00000",
            "port": "6881",
            "left": "1000",
            "numwant": "50",
        },
    )
    assert response.status_code == 200
    # Response should be bencoded
    data = await response.get_data()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_scrape_valid(live_http_client):
    response = await live_http_client.get(
        "/scrape",
        query_string={"info_hash": "b" * 40},
    )
    assert response.status_code == 200
    data = await response.get_data()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_scrape_missing_info_hash(live_http_client):
    response = await live_http_client.get("/scrape")
    assert response.status_code == 200  # Returns home page


@pytest.mark.asyncio
async def test_api_endpoint(live_http_client):
    response = await live_http_client.get("/api")
    assert response.status_code == 200
    data = await response.get_json()
    assert "quart_version" in data
    assert "redis_version" in data
    assert "python_version" in data


@pytest.mark.asyncio
async def test_geo_api_endpoint(live_http_client):
    response = await live_http_client.get("/api/geo")
    assert response.status_code == 200
    data = await response.get_json()
    assert "provider" in data
    assert data["provider"] == "IPLocate.io"


@pytest.mark.asyncio
async def test_tracker_data_endpoint(live_http_client):
    response = await live_http_client.get("/api/tracker_data")
    assert response.status_code == 200
    data = await response.get_json()
    assert "swarms" in data
    assert "total_peers" in data
    assert "total_swarms" in data
