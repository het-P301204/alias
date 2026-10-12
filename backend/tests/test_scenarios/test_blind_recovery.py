"""Real assertion tests for the blind-recovery scenario."""
import asyncio

from alias_core.experiments.models import ExperimentConfig, LabMode, ScenarioId
from scenarios.blind_recovery import scenario


def test_metadata_id():
    meta = scenario.get_metadata()
    assert meta.id == ScenarioId.BLIND_RECOVERY


def test_metadata_has_objectives():
    meta = scenario.get_metadata()
    assert len(meta.learning_objectives) >= 2


def test_metadata_category():
    meta = scenario.get_metadata()
    assert meta.category  # non-empty


def test_vulnerable_run_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.BLIND_RECOVERY, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_vulnerable_leaks_schema_hints():
    """Vulnerable mode: at least one error message reveals schema hints."""
    config = ExperimentConfig(scenario_id=ScenarioId.BLIND_RECOVERY, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    hint_evidence = [e for e in result.evidence if e.data.get("reveals_suggestion")]
    assert len(hint_evidence) > 0, "Vulnerable mode must produce at least one revealing error"


def test_vulnerable_has_error_evidence():
    config = ExperimentConfig(scenario_id=ScenarioId.BLIND_RECOVERY, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    error_ev = [e for e in result.evidence if e.type == "error_analysis"]
    assert len(error_ev) > 0


def test_vulnerable_error_message_not_generic():
    config = ExperimentConfig(scenario_id=ScenarioId.BLIND_RECOVERY, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    revealing = [
        e for e in result.evidence
        if e.type == "error_analysis" and e.data.get("reveals_suggestion")
    ]
    assert len(revealing) > 0
    # The error should contain something specific
    msg = revealing[0].data.get("error_message", "")
    assert len(msg) > 10


def test_hardened_run_completes():
    config = ExperimentConfig(scenario_id=ScenarioId.BLIND_RECOVERY, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    assert result.status.value == "completed"


def test_hardened_suppresses_schema_hints():
    """Hardened mode: no error message should reveal schema hints."""
    config = ExperimentConfig(scenario_id=ScenarioId.BLIND_RECOVERY, mode=LabMode.HARDENED)
    result = asyncio.run(scenario.run_experiment(config))
    hint_evidence = [e for e in result.evidence if e.data.get("reveals_suggestion")]
    assert len(hint_evidence) == 0, "Hardened mode must not leak schema hints in error messages"


def test_hardened_verify_defense():
    defense = asyncio.run(scenario.verify_defense(LabMode.HARDENED))
    assert defense.verified is True


def test_vulnerable_verify_defense_shows_flaw():
    defense = asyncio.run(scenario.verify_defense(LabMode.VULNERABLE))
    assert defense.verified is True


def test_result_has_multiple_probes():
    config = ExperimentConfig(scenario_id=ScenarioId.BLIND_RECOVERY, mode=LabMode.VULNERABLE)
    result = asyncio.run(scenario.run_experiment(config))
    probes = {e.data.get("probe") for e in result.evidence if e.type == "error_analysis"}
    # At least 2 distinct probe types
    assert len(probes) >= 2, f"Expected multiple probe types, got {probes}"
