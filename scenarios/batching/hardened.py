import strawberry
from strawberry.extensions import SchemaExtension

from scenarios.batching.vulnerable import Query, Mutation, AuthResult

MAX_AUTH_OPS = 3


class OperationLimitExtension(SchemaExtension):
    """Reject batched requests that exceed MAX_AUTH_OPS auth operations."""

    def on_executing(self):
        doc = self.execution_context.query or ""
        count = doc.count("authenticateUser")
        if count > MAX_AUTH_OPS:
            raise PermissionError(
                f"Batch limit exceeded: {count} auth operations in one request "
                f"(max {MAX_AUTH_OPS})"
            )
        yield


hardened_schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[OperationLimitExtension],
)
