"""Real assertion tests for the field-authorization scenario."""
import asyncio

from alias_core.experiments.models import ExperimentConfig, LabMode, ScenarioId
from scenarios.field_authorization import scenario


def test_metadata_id():
    meta = scenario.get_metadata()
    assert meta.id == ScenarioId.FIELD_AUTHORIZATION


def test_metadata_has_objectives():
    meta = scenario.get_metadata()
    assert len(meta.learning_objectives) >= 2


def test_metadata_category():
    meta = scenario.get_metadata()
    assert meta.category  # non-empty


def test_vulnerable_run_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.FIELD_AUTHORIZATION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_vulnerable_exposes_ssn():
    """Vulnerable mode: SSN is returned to a viewer-role caller."""
    config = ExperimentConfig(scenario_id=ScenarioId.FIELD_AUTHORIZATION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    ssn_evidence = [e for e in result.evidence if e.data.get("field") == "ssn"]
    assert len(ssn_evidence) > 0, "Must have SSN field evidence"
    assert ssn_evidence[0].data.get("vulnerable_flaw") is True, "SSN must be exposed in vulnerable mode"


def test_vulnerable_exposes_salary():
    config = ExperimentConfig(scenario_id=ScenarioId.FIELD_AUTHORIZATION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    salary_evidence = [e for e in result.evidence if e.data.get("field") == "salary"]
    assert len(salary_evidence) > 0
    assert salary_evidence[0].data.get("actual_access") is True


def test_vulnerable_ssn_has_value():
    config = ExperimentConfig(scenario_id=ScenarioId.FIELD_AUTHORIZATION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    ssn_ev = next(e for e in result.evidence if e.data.get("field") == "ssn")
    assert ssn_ev.data.get("ssn_value") is not None


def test_hardened_run_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.FIELD_AUTHORIZATION, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_hardened_hides_ssn():
    """Hardened mode: SSN is null (not returned) for a viewer-role caller."""
    config = ExperimentConfig(scenario_id=ScenarioId.FIELD_AUTHORIZATION, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    ssn_evidence = [e for e in result.evidence if e.data.get("field") == "ssn"]
    assert len(ssn_evidence) > 0, "Must have SSN field evidence"
    assert ssn_evidence[0].data.get("actual_access") is False, "SSN must be hidden in hardened mode"


def test_hardened_hides_salary():
    config = ExperimentConfig(scenario_id=ScenarioId.FIELD_AUTHORIZATION, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    salary_ev = [e for e in result.evidence if e.data.get("field") == "salary"]
    assert len(salary_ev) > 0
    assert salary_ev[0].data.get("actual_access") is False


def test_hardened_ssn_value_is_none():
    config = ExperimentConfig(scenario_id=ScenarioId.FIELD_AUTHORIZATION, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    ssn_ev = next(e for e in result.evidence if e.data.get("field") == "ssn")
    assert ssn_ev.data.get("ssn_value") is None


def test_hardened_verify_defense():
    defense = asyncio.run(scenario.verify_defense(LabMode.HARDENED))
    assert defense.verified is True


def test_vulnerable_verify_defense_shows_flaw():
    defense = asyncio.run(scenario.verify_defense(LabMode.VULNERABLE))
    assert defense.verified is True  # flaw confirmed


def test_result_has_evidence_for_multiple_fields():
    config = ExperimentConfig(scenario_id=ScenarioId.FIELD_AUTHORIZATION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    fields = {e.data.get("field") for e in result.evidence if e.type == "field_access"}
    assert "ssn" in fields
    assert "salary" in fields
