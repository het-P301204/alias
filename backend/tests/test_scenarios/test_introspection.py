"""Real assertion tests for the introspection scenario."""
import asyncio
import pytest

from alias_core.experiments.models import ExperimentConfig, LabMode, ScenarioId
from scenarios.introspection import scenario


def test_introspection_metadata_id():
    meta = scenario.get_metadata()
    assert meta.id == ScenarioId.INTROSPECTION


def test_introspection_metadata_has_objectives():
    meta = scenario.get_metadata()
    assert len(meta.learning_objectives) >= 3


def test_introspection_metadata_difficulty():
    meta = scenario.get_metadata()
    assert meta.difficulty in ("beginner", "intermediate", "advanced")


def test_introspection_metadata_category():
    meta = scenario.get_metadata()
    assert meta.category  # non-empty


def test_vulnerable_schema_exists():
    schema = scenario.get_schema(LabMode.VULNERABLE)
    assert schema is not None


def test_hardened_schema_exists():
    schema = scenario.get_schema(LabMode.HARDENED)
    assert schema is not None


def test_vulnerable_run_experiment_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.INTROSPECTION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_vulnerable_exposes_schema():
    config = ExperimentConfig(scenario_id=ScenarioId.INTROSPECTION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert len(result.evidence) > 0
    # Vulnerable mode should produce a schema_dump evidence item
    schema_evidence = [e for e in result.evidence if e.type == "schema_dump"]
    assert len(schema_evidence) > 0


def test_vulnerable_type_count_positive():
    config = ExperimentConfig(scenario_id=ScenarioId.INTROSPECTION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    schema_ev = next(e for e in result.evidence if e.type == "schema_dump")
    assert schema_ev.data["type_count"] > 0


def test_hardened_run_experiment_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.INTROSPECTION, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_hardened_blocks_introspection():
    config = ExperimentConfig(scenario_id=ScenarioId.INTROSPECTION, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    assert len(result.evidence) > 0
    # Hardened mode should produce an introspection_blocked evidence item
    blocked_evidence = [e for e in result.evidence if e.type == "introspection_blocked"]
    assert len(blocked_evidence) > 0


def test_hardened_verify_defense():
    defense = asyncio.run(scenario.verify_defense(LabMode.HARDENED))
    assert defense.verified is True
    assert defense.control_id  # non-empty


def test_vulnerable_verify_defense():
    defense = asyncio.run(scenario.verify_defense(LabMode.VULNERABLE))
    # In vulnerable mode, defense NOT effective — verified=True means the flaw is present
    assert defense.verified is True


def test_result_has_scenario_id():
    config = ExperimentConfig(scenario_id=ScenarioId.INTROSPECTION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.scenario_id == ScenarioId.INTROSPECTION


def test_result_has_duration():
    config = ExperimentConfig(scenario_id=ScenarioId.INTROSPECTION, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.duration_ms is not None
    assert result.duration_ms >= 0
