from typing import Generator, Any
from strawberry.extensions import SchemaExtension
from graphql import GraphQLError

MAX_QUERY_DEPTH = 10
MAX_COMPLEXITY = 1000
MAX_BATCH_OPERATIONS = 10
MAX_RESPONSE_SIZE = 1_048_576  # 1MB
MAX_CONCURRENT_EXPERIMENTS = 3
EXPERIMENT_TIMEOUT_SECONDS = 30


def _measure_depth(node: Any, depth: int = 0) -> int:
    if not hasattr(node, "selection_set") or node.selection_set is None:
        return depth
    child_depths = [_measure_depth(sel, depth + 1) for sel in node.selection_set.selections]
    return max(child_depths) if child_depths else depth


def _estimate_complexity(node: Any) -> int:
    if not hasattr(node, "selection_set") or node.selection_set is None:
        return 1
    total = 1
    for sel in node.selection_set.selections:
        total += _estimate_complexity(sel)
    return total


def _block(ctx: Any, msg: str) -> None:
    if ctx.pre_execution_errors is None:
        ctx.pre_execution_errors = []
    ctx.pre_execution_errors.append(GraphQLError(msg))


def depth_limit_extension(max_depth: int = MAX_QUERY_DEPTH) -> type:
    class _DepthLimit(SchemaExtension):
        def on_validate(self) -> Generator:
            doc = self.execution_context.graphql_document
            if doc is not None:
                for definition in doc.definitions:
                    d = _measure_depth(definition)
                    if d > max_depth:
                        _block(
                            self.execution_context,
                            f"Query depth {d} exceeds maximum allowed depth {max_depth}.",
                        )
            yield

    _DepthLimit.__name__ = f"DepthLimit_{max_depth}"
    _DepthLimit.__qualname__ = f"DepthLimit_{max_depth}"
    return _DepthLimit


def complexity_limit_extension(max_complexity: int = MAX_COMPLEXITY) -> type:
    class _ComplexityLimit(SchemaExtension):
        def on_validate(self) -> Generator:
            doc = self.execution_context.graphql_document
            if doc is not None:
                for definition in doc.definitions:
                    cost = _estimate_complexity(definition)
                    if cost > max_complexity:
                        _block(
                            self.execution_context,
                            f"Query complexity {cost} exceeds maximum allowed complexity {max_complexity}.",
                        )
            yield

    _ComplexityLimit.__name__ = f"ComplexityLimit_{max_complexity}"
    _ComplexityLimit.__qualname__ = f"ComplexityLimit_{max_complexity}"
    return _ComplexityLimit


def operation_limit_extension(max_ops: int = MAX_BATCH_OPERATIONS) -> type:
    class _OperationLimit(SchemaExtension):
        def on_validate(self) -> Generator:
            doc = self.execution_context.graphql_document
            if doc is not None and len(doc.definitions) > max_ops:
                _block(
                    self.execution_context,
                    f"Operation count {len(doc.definitions)} exceeds limit {max_ops}.",
                )
            yield

    _OperationLimit.__name__ = f"OperationLimit_{max_ops}"
    _OperationLimit.__qualname__ = f"OperationLimit_{max_ops}"
    return _OperationLimit


def introspection_block_extension() -> type:
    """Block __schema and __type introspection queries."""
    class _BlockIntrospection(SchemaExtension):
        def on_validate(self) -> Generator:
            query = self.execution_context.query or ""
            if "__schema" in query or "__type" in query:
                _block(
                    self.execution_context,
                    "GraphQL introspection is disabled on this endpoint.",
                )
            yield

    return _BlockIntrospection
