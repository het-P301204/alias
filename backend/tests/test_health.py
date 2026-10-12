"""Tests for GET /api/health."""


def test_health_returns_200(client):
    r = client.get("/api/health")
    assert r.status_code == 200


def test_health_response_has_data_wrapper(client):
    r = client.get("/api/health")
    body = r.json()
    assert "data" in body
    assert body["error"] is None


def test_health_status_ok(client):
    r = client.get("/api/health")
    assert r.json()["data"]["status"] == "ok"


def test_health_shows_version(client):
    r = client.get("/api/health")
    assert "version" in r.json()["data"]
    assert r.json()["data"]["version"]  # non-empty


def test_health_shows_scenarios_loaded(client):
    r = client.get("/api/health")
    count = r.json()["data"]["scenarios_loaded"]
    assert count == 6, f"Expected 6 scenarios, got {count}"


def test_health_has_timestamp(client):
    r = client.get("/api/health")
    ts = r.json()["data"].get("timestamp")
    assert ts is not None
    assert "T" in ts  # ISO-8601 format


def test_health_db_ok(client):
    r = client.get("/api/health")
    assert r.json()["data"]["db_ok"] is True
