from strawberry.extensions import SchemaExtension
from strawberry.types import ExecutionContext
from graphql import GraphQLError

MAX_QUERY_DEPTH = 10
MAX_COMPLEXITY = 1000
MAX_BATCH_OPERATIONS = 10
MAX_RESPONSE_SIZE = 1_048_576  # 1MB
MAX_CONCURRENT_EXPERIMENTS = 3
EXPERIMENT_TIMEOUT_SECONDS = 30


def _measure_depth(node, depth: int = 0) -> int:
    """Recursively measure the maximum selection depth of a query AST node."""
    from graphql.language import ast as gql_ast

    if not hasattr(node, "selection_set") or node.selection_set is None:
        return depth
    child_depths = [
        _measure_depth(sel, depth + 1)
        for sel in node.selection_set.selections
    ]
    return max(child_depths) if child_depths else depth


class DepthLimitExtension(SchemaExtension):
    """Strawberry extension that rejects queries exceeding MAX_QUERY_DEPTH."""

    def __init__(self, *, max_depth: int = MAX_QUERY_DEPTH, execution_context: ExecutionContext):
        self.max_depth = max_depth
        super().__init__(execution_context=execution_context)

    def on_executing_start(self) -> None:
        doc = self.execution_context.graphql_document
        if doc is None:
            return
        for definition in doc.definitions:
            depth = _measure_depth(definition)
            if depth > self.max_depth:
                raise GraphQLError(
                    f"Query depth {depth} exceeds maximum allowed depth {self.max_depth}."
                )


def _estimate_complexity(node, complexity: int = 0) -> int:
    """Simple field-count complexity estimator."""
    from graphql.language import ast as gql_ast

    if not hasattr(node, "selection_set") or node.selection_set is None:
        return complexity + 1
    total = complexity + 1
    if node.selection_set:
        for sel in node.selection_set.selections:
            total += _estimate_complexity(sel, 0)
    return total


class ComplexityLimitExtension(SchemaExtension):
    """Strawberry extension that rejects queries exceeding MAX_COMPLEXITY."""

    def __init__(self, *, max_complexity: int = MAX_COMPLEXITY, execution_context: ExecutionContext):
        self.max_complexity = max_complexity
        super().__init__(execution_context=execution_context)

    def on_executing_start(self) -> None:
        doc = self.execution_context.graphql_document
        if doc is None:
            return
        for definition in doc.definitions:
            cost = _estimate_complexity(definition)
            if cost > self.max_complexity:
                raise GraphQLError(
                    f"Query complexity {cost} exceeds maximum allowed complexity {self.max_complexity}."
                )


def depth_limit_extension(max_depth: int = MAX_QUERY_DEPTH):
    """Return a DepthLimitExtension class bound to the given limit."""
    class _BoundDepthLimit(DepthLimitExtension):
        def __init__(self, *, execution_context: ExecutionContext):
            super().__init__(max_depth=max_depth, execution_context=execution_context)
    return _BoundDepthLimit


def complexity_limit_extension(max_complexity: int = MAX_COMPLEXITY):
    """Return a ComplexityLimitExtension class bound to the given limit."""
    class _BoundComplexityLimit(ComplexityLimitExtension):
        def __init__(self, *, execution_context: ExecutionContext):
            super().__init__(max_complexity=max_complexity, execution_context=execution_context)
    return _BoundComplexityLimit
