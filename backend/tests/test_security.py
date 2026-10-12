"""Security boundary tests for the ALIAS API."""


def test_cors_does_not_echo_evil_origin(client):
    r = client.get("/api/health", headers={"Origin": "https://evil.com"})
    assert r.headers.get("access-control-allow-origin") != "https://evil.com"


def test_cors_allows_known_dev_origin(client):
    r = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
    acao = r.headers.get("access-control-allow-origin")
    assert acao == "http://localhost:5173", f"Expected localhost:5173, got {acao!r}"


def test_invalid_scenario_id_rejected_422(client):
    r = client.post(
        "/api/experiments",
        json={"scenario_id": "nonexistent-scenario", "mode": "vulnerable", "parameters": {}},
    )
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"


def test_invalid_mode_rejected_422(client):
    r = client.post(
        "/api/experiments",
        json={"scenario_id": "introspection", "mode": "attack", "parameters": {}},
    )
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"


def test_missing_scenario_id_rejected_422(client):
    r = client.post(
        "/api/experiments",
        json={"mode": "vulnerable", "parameters": {}},
    )
    assert r.status_code == 422


def test_missing_mode_rejected_422(client):
    r = client.post(
        "/api/experiments",
        json={"scenario_id": "introspection", "parameters": {}},
    )
    assert r.status_code == 422


def test_empty_body_rejected(client):
    r = client.post("/api/experiments", json={})
    assert r.status_code == 422


def test_invalid_report_format_rejected(client):
    r = client.get("/api/reports/some-id?format=xml")
    assert r.status_code == 422


def test_health_endpoint_not_requiring_auth(client):
    r = client.get("/api/health")
    assert r.status_code == 200


def test_experiments_not_accepting_html_injection(client):
    r = client.post(
        "/api/experiments",
        json={
            "scenario_id": "introspection",
            "mode": "vulnerable",
            "parameters": {"note": "<script>alert('xss')</script>"},
        },
    )
    # Either accepted (and stored safely) or rejected — not a server error
    assert r.status_code in (200, 400, 422)
