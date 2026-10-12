from typing import Generator
import strawberry
from strawberry.extensions import SchemaExtension
from graphql import GraphQLError

from scenarios.batching.vulnerable import Query, Mutation

MAX_AUTH_OPS = 3


class OperationLimitExtension(SchemaExtension):
    """Reject batches with too many auth operations (counted by field aliases)."""

    def on_validate(self) -> Generator:
        query = self.execution_context.query or ""
        count = query.count("authenticateUser")
        if count > MAX_AUTH_OPS:
            if self.execution_context.pre_execution_errors is None:
                self.execution_context.pre_execution_errors = []
            self.execution_context.pre_execution_errors.append(
                GraphQLError(
                    f"Batch limit exceeded: {count} auth operations in one request "
                    f"(max {MAX_AUTH_OPS})"
                )
            )
        yield


hardened_schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[OperationLimitExtension],
)
