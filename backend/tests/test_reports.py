"""Tests for /api/reports and the reporting.generator module."""
import json
import uuid


# Seeded sample IDs (deterministic, created in init_db._seed_sample_experiments)
_SAMPLE_INTROSPECTION = str(uuid.uuid5(uuid.NAMESPACE_DNS, "alias-sample-introspection"))
_SAMPLE_QUERY_COMPLEXITY = str(uuid.uuid5(uuid.NAMESPACE_DNS, "alias-sample-query-complexity"))
_SAMPLE_FIELD_AUTHORIZATION = str(uuid.uuid5(uuid.NAMESPACE_DNS, "alias-sample-field-authorization"))


# ---------------------------------------------------------------------------
# HTTP report endpoint
# ---------------------------------------------------------------------------

def test_json_report_endpoint_returns_200(client):
    r = client.get(f"/api/reports/{_SAMPLE_INTROSPECTION}?format=json")
    assert r.status_code == 200


def test_json_report_content_type(client):
    r = client.get(f"/api/reports/{_SAMPLE_INTROSPECTION}?format=json")
    assert "application/json" in r.headers.get("content-type", "")


def test_json_report_has_required_keys(client):
    r = client.get(f"/api/reports/{_SAMPLE_INTROSPECTION}?format=json")
    body = r.json()
    for key in ("report_format", "generated_at", "scenario", "mode", "evidence"):
        assert key in body, f"Missing key: {key!r}"


def test_csv_report_endpoint_returns_200(client):
    r = client.get(f"/api/reports/{_SAMPLE_INTROSPECTION}?format=csv")
    assert r.status_code == 200


def test_csv_report_content_type(client):
    r = client.get(f"/api/reports/{_SAMPLE_INTROSPECTION}?format=csv")
    assert "csv" in r.headers.get("content-type", "").lower()


def test_csv_report_has_header_row(client):
    r = client.get(f"/api/reports/{_SAMPLE_INTROSPECTION}?format=csv")
    assert "Field" in r.text and "Value" in r.text


def test_html_report_endpoint_returns_200(client):
    r = client.get(f"/api/reports/{_SAMPLE_INTROSPECTION}?format=html")
    assert r.status_code == 200


def test_html_report_is_valid_html(client):
    r = client.get(f"/api/reports/{_SAMPLE_INTROSPECTION}?format=html")
    text = r.text
    assert text.strip().startswith("<!DOCTYPE html") or "<html" in text


def test_html_report_contains_scenario_id(client):
    r = client.get(f"/api/reports/{_SAMPLE_INTROSPECTION}?format=html")
    assert "introspection" in r.text


def test_report_404_for_missing_experiment(client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    r = client.get(f"/api/reports/{fake_id}?format=json")
    assert r.status_code == 404


def test_report_default_format_is_json(client):
    r = client.get(f"/api/reports/{_SAMPLE_INTROSPECTION}")
    assert r.status_code == 200
    r.json()  # must be valid JSON


# ---------------------------------------------------------------------------
# generator module (unit-level)
# ---------------------------------------------------------------------------

def _make_result():
    """Build a minimal ExperimentResult using the seeded introspection sample via DB."""
    import asyncio
    from alias_core.database.init_db import get_db
    from alias_core.database.queries import get_experiment

    async def _fetch():
        async with get_db() as db:
            return await get_experiment(db, _SAMPLE_INTROSPECTION)

    return asyncio.run(_fetch())


def test_generate_json_returns_string():
    from alias_core.reporting.generator import generate_json
    result = _make_result()
    if result is None:
        pytest.skip("Sample experiment not in DB")
    out = generate_json(result)
    assert isinstance(out, str)
    parsed = json.loads(out)
    assert "report_type" in parsed
    assert "executive_summary" in parsed
    assert "evidence" in parsed
    assert "remediation" in parsed


def test_generate_json_disclaimer_present():
    from alias_core.reporting.generator import generate_json, DISCLAIMER
    result = _make_result()
    if result is None:
        pytest.skip("Sample experiment not in DB")
    out = generate_json(result)
    assert DISCLAIMER[:30] in out


def test_generate_csv_returns_string():
    from alias_core.reporting.generator import generate_csv
    result = _make_result()
    if result is None:
        pytest.skip("Sample experiment not in DB")
    out = generate_csv(result)
    assert isinstance(out, str)
    assert len(out) > 0


def test_generate_csv_has_evidence_rows():
    from alias_core.reporting.generator import generate_csv
    result = _make_result()
    if result is None:
        pytest.skip("Sample experiment not in DB")
    out = generate_csv(result)
    lines = [l for l in out.splitlines() if l.strip()]
    # At least header + 1 data row
    assert len(lines) >= 2


def test_generate_html_returns_string():
    from alias_core.reporting.generator import generate_html
    result = _make_result()
    if result is None:
        pytest.skip("Sample experiment not in DB")
    out = generate_html(result)
    assert isinstance(out, str)
    assert "<!DOCTYPE html" in out


def test_generate_html_contains_experiment_id():
    from alias_core.reporting.generator import generate_html
    result = _make_result()
    if result is None:
        pytest.skip("Sample experiment not in DB")
    out = generate_html(result)
    assert result.id in out


def test_generate_html_contains_remediation():
    from alias_core.reporting.generator import generate_html
    result = _make_result()
    if result is None:
        pytest.skip("Sample experiment not in DB")
    out = generate_html(result)
    assert "Remediation" in out


def test_remediation_text_for_all_scenarios():
    from alias_core.reporting.generator import _get_remediation
    from alias_core.experiments.models import ScenarioId
    for sid in ScenarioId:
        text = _get_remediation(sid.value)
        assert len(text) > 10, f"Empty remediation for {sid.value}"


import pytest
