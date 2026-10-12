import strawberry
from alias_core.security.limits import introspection_block_extension
from scenarios.introspection.vulnerable import Query, Mutation

hardened_schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[introspection_block_extension()],
)
