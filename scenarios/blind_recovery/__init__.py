import strawberry

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, DefenseResult, LabMode, ScenarioMetadata,
)
from alias_core.experiments.models import ScenarioId
from scenarios.blind_recovery import runner as _runner


class BlindRecoveryScenario:
    scenario_id = ScenarioId.BLIND_RECOVERY

    def get_metadata(self) -> ScenarioMetadata:
        return ScenarioMetadata(
            id=ScenarioId.BLIND_RECOVERY,
            title="Error-Message Schema Recovery",
            description=(
                "Shows how verbose GraphQL error messages — including 'Did you mean …' "
                "suggestions and internal diagnostic details — let an attacker enumerate "
                "valid field names and entity IDs without credentials."
            ),
            category="Information Disclosure",
            difficulty="beginner",
            learning_objectives=[
                "Understand how validation errors reveal valid field names",
                "Trace how runtime errors expose internal identifiers",
                "Sanitize error messages in production to prevent schema enumeration",
            ],
        )

    def get_schema(self, mode: LabMode) -> strawberry.Schema:
        if mode == LabMode.VULNERABLE:
            from scenarios.blind_recovery.vulnerable import vulnerable_schema
            return vulnerable_schema
        from scenarios.blind_recovery.hardened import hardened_schema
        return hardened_schema

    async def run_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        return await _runner.run_experiment(config)

    async def verify_defense(self, mode: LabMode) -> DefenseResult:
        return await _runner.verify_defense(mode)

    async def reset(self) -> None:
        pass


scenario = BlindRecoveryScenario()
