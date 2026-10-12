from pydantic import BaseModel
from typing import Optional, Any
from enum import Enum


class ScenarioId(str, Enum):
    INTROSPECTION = "introspection"
    ALIAS_AUTHORIZATION = "alias-authorization"
    BATCHING = "batching"
    QUERY_COMPLEXITY = "query-complexity"
    BLIND_RECOVERY = "blind-recovery"
    FIELD_AUTHORIZATION = "field-authorization"


class ExperimentStatus(str, Enum):
    READY = "ready"
    VALIDATING = "validating"
    RUNNING = "running"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class LabMode(str, Enum):
    VULNERABLE = "vulnerable"
    HARDENED = "hardened"


class Evidence(BaseModel):
    type: str
    label: str
    data: Any
    timestamp: str


class DefenseResult(BaseModel):
    control_id: str
    verified: bool
    description: str
    details: dict[str, Any] = {}


class ExperimentConfig(BaseModel):
    scenario_id: ScenarioId
    mode: LabMode
    parameters: dict[str, Any] = {}


class ExperimentResult(BaseModel):
    id: str
    scenario_id: ScenarioId
    mode: LabMode
    config: dict[str, Any]
    status: ExperimentStatus
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    input_summary: str = ""
    expected_outcome: str = ""
    actual_outcome: Optional[str] = None
    evidence: list[Evidence] = []
    defensive_control_result: Optional[DefenseResult] = None
    error: Optional[str] = None
    reproducibility_metadata: dict[str, Any] = {}
    is_sample: bool = False


class ScenarioMetadata(BaseModel):
    id: ScenarioId
    title: str
    description: str
    category: str
    difficulty: str  # beginner|intermediate|advanced
    learning_objectives: list[str]
    default_config: dict[str, Any] = {}
