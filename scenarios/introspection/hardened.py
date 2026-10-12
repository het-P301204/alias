import strawberry
from strawberry.extensions import SchemaExtension

from scenarios.introspection.vulnerable import Query, Mutation


class IntrospectionExtension(SchemaExtension):
    """Rejects __schema and __type introspection queries."""

    def on_executing(self):
        request = self.execution_context
        doc = request.query or ""
        if "__schema" in doc or "__type" in doc:
            raise PermissionError("GraphQL introspection is disabled on this endpoint.")
        yield


hardened_schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[IntrospectionExtension],
)
