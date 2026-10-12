import strawberry

from alias_core.security.limits import depth_limit_extension
from scenarios.query_complexity.vulnerable import Query

# Hardened: depth limit of 4 — rejects queries with depth > 4 (e.g. depth-5 nested queries)
hardened_schema = strawberry.Schema(
    query=Query,
    extensions=[depth_limit_extension(max_depth=4)],
)
