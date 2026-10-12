import uuid
from datetime import datetime, timezone

import strawberry

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, DefenseResult, LabMode, ScenarioMetadata,
)
from alias_core.experiments.models import ScenarioId
from scenarios.introspection import runner as _runner


class IntrospectionScenario:
    scenario_id = ScenarioId.INTROSPECTION

    def get_metadata(self) -> ScenarioMetadata:
        return ScenarioMetadata(
            id=ScenarioId.INTROSPECTION,
            title="GraphQL Introspection Disclosure",
            description=(
                "Demonstrates how unrestricted GraphQL introspection exposes the full "
                "schema — types, fields, mutations, deprecated fields — enabling attackers "
                "to map the API without credentials."
            ),
            category="Information Disclosure",
            difficulty="beginner",
            learning_objectives=[
                "Understand what GraphQL introspection reveals",
                "Execute a __schema query and parse results",
                "Implement and verify an IntrospectionExtension defense",
            ],
        )

    def get_schema(self, mode: LabMode) -> strawberry.Schema:
        if mode == LabMode.VULNERABLE:
            from scenarios.introspection.vulnerable import vulnerable_schema
            return vulnerable_schema
        from scenarios.introspection.hardened import hardened_schema
        return hardened_schema

    async def run_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        return await _runner.run_experiment(config)

    async def verify_defense(self, mode: LabMode) -> DefenseResult:
        return await _runner.verify_defense(mode)

    async def reset(self) -> None:
        pass  # fixtures are module-level constants; nothing to restore


scenario = IntrospectionScenario()
