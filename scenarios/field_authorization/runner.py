import time
import uuid
from datetime import datetime, timezone

from alias_core.experiments.models import (
    ExperimentConfig, ExperimentResult, ExperimentStatus,
    Evidence, DefenseResult, LabMode,
)
from alias_core.experiments.models import ScenarioId

# Query as a viewer — should be denied SSN and salary in hardened mode
VIEWER_QUERY = '{ employee(id: "e1") { id name ssn salary } }'
VIEWER_CTX = {"user_id": "e2", "role": "viewer"}


def _get_schema(mode: LabMode):
    if mode == LabMode.VULNERABLE:
        from scenarios.field_authorization.vulnerable import vulnerable_schema
        return vulnerable_schema
    from scenarios.field_authorization.hardened import hardened_schema
    return hardened_schema


async def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    schema = _get_schema(config.mode)
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.monotonic()

    result = schema.execute_sync(VIEWER_QUERY, context_value=VIEWER_CTX)

    duration_ms = int((time.monotonic() - t0) * 1000)
    completed = datetime.now(timezone.utc).isoformat()

    data = result.data or {}
    emp = data.get("employee") or {}
    ssn_val = emp.get("ssn") if isinstance(emp, dict) else None
    salary_val = emp.get("salary") if isinstance(emp, dict) else None

    ssn_accessed = ssn_val is not None
    salary_accessed = salary_val is not None

    evidence: list[Evidence] = []

    evidence.append(Evidence(
        type="field_access",
        label="SSN Field Access (viewer role requesting admin's record)",
        data={
            "field": "ssn",
            "caller_role": "viewer",
            "target_employee": "e1",
            "ssn_value": ssn_val,
            "actual_access": ssn_accessed,
            "vulnerable_flaw": ssn_accessed,
        },
        timestamp=completed,
    ))

    evidence.append(Evidence(
        type="field_access",
        label="Salary Field Access (viewer role requesting admin's record)",
        data={
            "field": "salary",
            "caller_role": "viewer",
            "target_employee": "e1",
            "salary_value": salary_val,
            "actual_access": salary_accessed,
            "vulnerable_flaw": salary_accessed,
        },
        timestamp=completed,
    ))

    any_unauthorized = ssn_accessed or salary_accessed

    if config.mode == LabMode.VULNERABLE:
        actual_outcome = (
            "Sensitive fields (SSN, salary) returned to viewer role — missing field-level checks"
            if any_unauthorized else "Fields unexpectedly blocked (unexpected in vulnerable mode)"
        )
    else:
        actual_outcome = (
            "Sensitive fields (SSN, salary) redacted for viewer role — field-level authorization active"
            if not any_unauthorized else "Defense failed — sensitive fields still accessible"
        )

    return ExperimentResult(
        id=str(uuid.uuid4()),
        scenario_id=ScenarioId.FIELD_AUTHORIZATION,
        mode=config.mode,
        config=config.parameters,
        status=ExperimentStatus.COMPLETED,
        started_at=started,
        completed_at=completed,
        duration_ms=duration_ms,
        input_summary="Viewer-role caller requesting SSN and salary of employee e1",
        expected_outcome=(
            "SSN and salary returned to viewer (no field-level auth)"
            if config.mode == LabMode.VULNERABLE
            else "SSN and salary null for viewer — field-level auth enforced"
        ),
        actual_outcome=actual_outcome,
        evidence=evidence,
        is_sample=True,
    )


async def verify_defense(mode: LabMode) -> DefenseResult:
    schema = _get_schema(mode)
    result = schema.execute_sync(VIEWER_QUERY, context_value=VIEWER_CTX)
    data = result.data or {}
    emp = data.get("employee") or {}
    ssn_val = emp.get("ssn") if isinstance(emp, dict) else None
    ssn_blocked = ssn_val is None

    if mode == LabMode.HARDENED:
        verified = ssn_blocked
    else:
        verified = not ssn_blocked

    return DefenseResult(
        control_id="field-authorization-check",
        verified=verified,
        description="SSN field inaccessible to viewer-role callers in hardened mode",
        details={
            "caller_role": "viewer",
            "ssn_value": ssn_val,
            "ssn_blocked": ssn_blocked,
        },
    )
