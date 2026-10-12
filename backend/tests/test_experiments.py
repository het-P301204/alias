"""Tests for /api/experiments endpoints."""
import time


def test_list_experiments_returns_200(client):
    r = client.get("/api/experiments")
    assert r.status_code == 200


def test_list_experiments_has_data_wrapper(client):
    r = client.get("/api/experiments")
    body = r.json()
    assert "data" in body
    assert "items" in body["data"]
    assert "total" in body["data"]


def test_list_experiments_has_seeded_samples(client):
    r = client.get("/api/experiments")
    total = r.json()["data"]["total"]
    assert total >= 3, "Expected at least 3 seeded sample experiments"


def test_create_experiment_introspection_vulnerable(client):
    r = client.post(
        "/api/experiments",
        json={"scenario_id": "introspection", "mode": "vulnerable", "parameters": {}},
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["status"] in ("ready", "running", "completed", "validating", "analyzing")
    assert data["scenario_id"] == "introspection"
    assert data["mode"] == "vulnerable"


def test_create_experiment_returns_id(client):
    r = client.post(
        "/api/experiments",
        json={"scenario_id": "batching", "mode": "hardened", "parameters": {}},
    )
    assert r.status_code == 200
    assert "id" in r.json()["data"]
    exp_id = r.json()["data"]["id"]
    assert len(exp_id) == 36  # UUID format


def test_experiment_has_required_fields(client):
    r = client.post(
        "/api/experiments",
        json={"scenario_id": "introspection", "mode": "hardened", "parameters": {}},
    )
    assert r.status_code == 200
    data = r.json()["data"]
    for field in ("id", "scenario_id", "mode", "status", "started_at"):
        assert field in data, f"Missing required field: {field!r}"


def test_get_experiment_by_id(client):
    # Create first
    r = client.post(
        "/api/experiments",
        json={"scenario_id": "alias-authorization", "mode": "vulnerable", "parameters": {}},
    )
    assert r.status_code == 200
    exp_id = r.json()["data"]["id"]

    # Retrieve by ID
    r2 = client.get(f"/api/experiments/{exp_id}")
    assert r2.status_code == 200
    assert r2.json()["data"]["id"] == exp_id
    assert r2.json()["data"]["scenario_id"] == "alias-authorization"


def test_get_nonexistent_experiment_returns_404(client):
    r = client.get("/api/experiments/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_cancel_experiment_endpoint(client):
    r = client.post(
        "/api/experiments",
        json={"scenario_id": "introspection", "mode": "vulnerable", "parameters": {}},
    )
    exp_id = r.json()["data"]["id"]

    r2 = client.post(f"/api/experiments/{exp_id}/cancel")
    assert r2.status_code == 200
    assert "cancelled" in r2.json()["data"]


def test_experiment_timeout_field_present(client):
    r = client.post(
        "/api/experiments",
        json={"scenario_id": "introspection", "mode": "vulnerable", "parameters": {}},
    )
    assert r.status_code == 200
    data = r.json()["data"]
    # started_at must be present; timeout status is possible
    assert data.get("started_at") is not None


def test_multiple_experiments_can_be_submitted(client):
    for _ in range(3):
        r = client.post(
            "/api/experiments",
            json={"scenario_id": "introspection", "mode": "vulnerable", "parameters": {}},
        )
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"


def test_filter_experiments_by_scenario_id(client):
    r = client.get("/api/experiments?scenario_id=introspection")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    for item in items:
        assert item["scenario_id"] == "introspection"


def test_pagination_limit_respected(client):
    r = client.get("/api/experiments?limit=2")
    assert r.status_code == 200
    assert len(r.json()["data"]["items"]) <= 2
