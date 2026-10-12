import strawberry

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, DefenseResult, LabMode, ScenarioMetadata,
)
from alias_core.experiments.models import ScenarioId
from scenarios.field_authorization import runner as _runner


class FieldAuthorizationScenario:
    scenario_id = ScenarioId.FIELD_AUTHORIZATION

    def get_metadata(self) -> ScenarioMetadata:
        return ScenarioMetadata(
            id=ScenarioId.FIELD_AUTHORIZATION,
            title="Field-Level Authorization Bypass",
            description=(
                "Shows how missing per-field authorization checks allow a low-privilege "
                "caller to retrieve sensitive fields (SSN, salary) that are only visible "
                "in the UI for admins, by querying the GraphQL API directly."
            ),
            category="Broken Function Level Authorization",
            difficulty="intermediate",
            learning_objectives=[
                "Understand that UI-level field hiding does not protect GraphQL fields",
                "Reproduce unauthorized field access via a direct API query",
                "Apply per-resolver permission checks for every sensitive field",
            ],
        )

    def get_schema(self, mode: LabMode) -> strawberry.Schema:
        if mode == LabMode.VULNERABLE:
            from scenarios.field_authorization.vulnerable import vulnerable_schema
            return vulnerable_schema
        from scenarios.field_authorization.hardened import hardened_schema
        return hardened_schema

    async def run_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        return await _runner.run_experiment(config)

    async def verify_defense(self, mode: LabMode) -> DefenseResult:
        return await _runner.verify_defense(mode)

    async def reset(self) -> None:
        pass


scenario = FieldAuthorizationScenario()
