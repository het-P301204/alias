"""Real assertion tests for the batching scenario."""
import asyncio

from alias_core.experiments.models import ExperimentConfig, LabMode, ScenarioId
from scenarios.batching import scenario


def test_metadata_id():
    meta = scenario.get_metadata()
    assert meta.id == ScenarioId.BATCHING


def test_metadata_has_objectives():
    meta = scenario.get_metadata()
    assert len(meta.learning_objectives) >= 2


def test_vulnerable_run_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.BATCHING, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_vulnerable_batch_executes_all():
    """Vulnerable mode: all 5 aliased auth operations execute in 1 HTTP request."""
    config = ExperimentConfig(scenario_id=ScenarioId.BATCHING, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    batch_evidence = [e for e in result.evidence if e.type == "batch_auth_result"]
    assert len(batch_evidence) > 0
    data = batch_evidence[0].data
    assert data.get("rate_limit_triggered") is False
    assert data.get("operations_accepted") == 5


def test_vulnerable_single_http_request():
    config = ExperimentConfig(scenario_id=ScenarioId.BATCHING, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    batch_evidence = [e for e in result.evidence if e.type == "batch_auth_result"]
    assert batch_evidence[0].data.get("http_requests") == 1


def test_hardened_run_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.BATCHING, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_hardened_rate_limit_triggers():
    """Hardened mode: 5-operation batch exceeds the limit of 3, triggering rejection."""
    config = ExperimentConfig(scenario_id=ScenarioId.BATCHING, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    batch_evidence = [e for e in result.evidence if e.type == "batch_auth_result"]
    assert len(batch_evidence) > 0
    data = batch_evidence[0].data
    assert data.get("rate_limit_triggered") is True


def test_hardened_rejects_excess_operations():
    config = ExperimentConfig(scenario_id=ScenarioId.BATCHING, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    batch_evidence = [e for e in result.evidence if e.type == "batch_auth_result"]
    data = batch_evidence[0].data
    assert data.get("rejected") > 0


def test_hardened_verify_defense():
    defense = asyncio.run(scenario.verify_defense(LabMode.HARDENED))
    assert defense.verified is True


def test_vulnerable_verify_defense_shows_flaw():
    defense = asyncio.run(scenario.verify_defense(LabMode.VULNERABLE))
    assert defense.verified is True
