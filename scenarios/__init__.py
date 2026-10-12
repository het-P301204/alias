from scenarios.introspection import scenario as introspection_scenario
from scenarios.alias_authorization import scenario as alias_authorization_scenario
from scenarios.batching import scenario as batching_scenario
from scenarios.query_complexity import scenario as query_complexity_scenario
from scenarios.blind_recovery import scenario as blind_recovery_scenario
from scenarios.field_authorization import scenario as field_authorization_scenario

ALL_SCENARIOS = [
    introspection_scenario,
    alias_authorization_scenario,
    batching_scenario,
    query_complexity_scenario,
    blind_recovery_scenario,
    field_authorization_scenario,
]
