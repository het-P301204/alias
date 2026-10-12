"""Real assertion tests for the alias-authorization scenario."""
import asyncio

from alias_core.experiments.models import ExperimentConfig, LabMode, ScenarioId
from scenarios.alias_authorization import scenario


def test_metadata_id():
    meta = scenario.get_metadata()
    assert meta.id == ScenarioId.ALIAS_AUTHORIZATION


def test_metadata_has_objectives():
    meta = scenario.get_metadata()
    assert len(meta.learning_objectives) >= 2


def test_metadata_category():
    meta = scenario.get_metadata()
    assert meta.category  # non-empty


def test_vulnerable_run_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.ALIAS_AUTHORIZATION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_vulnerable_allows_unauthorized_access():
    config = ExperimentConfig(scenario_id=ScenarioId.ALIAS_AUTHORIZATION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"
    # The IDOR flaw: Bob's order (unauthorized) is returned when authenticated as Alice
    unauthorized_evidence = [
        e for e in result.evidence
        if e.data.get("authorized") is False and e.data.get("actually_returned") is True
    ]
    assert len(unauthorized_evidence) > 0, "Vulnerable mode must expose IDOR flaw"


def test_vulnerable_alice_own_order_accessible():
    config = ExperimentConfig(scenario_id=ScenarioId.ALIAS_AUTHORIZATION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    alice_evidence = [e for e in result.evidence if e.data.get("authorized") is True]
    assert len(alice_evidence) > 0, "Alice's own order should be accessible"
    assert alice_evidence[0].data.get("actually_returned") is True


def test_hardened_run_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.ALIAS_AUTHORIZATION, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_hardened_denies_unauthorized_access():
    config = ExperimentConfig(scenario_id=ScenarioId.ALIAS_AUTHORIZATION, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    # In hardened mode, no evidence should show unauthorized=False AND returned=True
    unauthorized_evidence = [
        e for e in result.evidence
        if e.data.get("authorized") is False and e.data.get("actually_returned") is True
    ]
    assert len(unauthorized_evidence) == 0, "Hardened mode must block cross-user access"


def test_hardened_verify_defense():
    defense = asyncio.run(scenario.verify_defense(LabMode.HARDENED))
    assert defense.verified is True


def test_vulnerable_verify_defense_shows_flaw():
    defense = asyncio.run(scenario.verify_defense(LabMode.VULNERABLE))
    # In vulnerable mode: the flaw is present → verified=True (flaw confirmed)
    assert defense.verified is True


def test_result_has_evidence():
    config = ExperimentConfig(scenario_id=ScenarioId.ALIAS_AUTHORIZATION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert len(result.evidence) >= 2  # at least Alice's order and Bob's order
