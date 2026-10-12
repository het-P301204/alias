import strawberry
from strawberry.extensions import SchemaExtension

from scenarios.query_complexity.vulnerable import Query

MAX_DEPTH = 5
MAX_COMPLEXITY = 100


def _count_depth(doc: str) -> int:
    """Simple brace-counting depth estimator."""
    max_d = cur = 0
    for ch in doc:
        if ch == "{":
            cur += 1
            max_d = max(max_d, cur)
        elif ch == "}":
            cur -= 1
    return max_d


class MaxDepthExtension(SchemaExtension):
    def on_executing(self):
        doc = self.execution_context.query or ""
        depth = _count_depth(doc)
        if depth > MAX_DEPTH:
            raise ValueError(
                f"Query depth {depth} exceeds maximum allowed depth of {MAX_DEPTH}"
            )
        yield


class MaxComplexityExtension(SchemaExtension):
    LIST_FIELDS = {"users", "posts", "friends", "comments"}
    COSTS = {"User": 1, "Post": 2, "Comment": 1}
    LIST_MULTIPLIER = 3

    def _estimate(self, doc: str) -> int:
        tokens = doc.replace("{", " { ").replace("}", " } ").split()
        cost = 0
        for tok in tokens:
            cost += self.COSTS.get(tok.capitalize(), 0)
            if tok in self.LIST_FIELDS:
                cost += self.LIST_MULTIPLIER
        return cost

    def on_executing(self):
        doc = self.execution_context.query or ""
        complexity = self._estimate(doc)
        if complexity > MAX_COMPLEXITY:
            raise ValueError(
                f"Query complexity {complexity} exceeds maximum allowed complexity of {MAX_COMPLEXITY}"
            )
        yield


hardened_schema = strawberry.Schema(
    query=Query,
    extensions=[MaxDepthExtension, MaxComplexityExtension],
)
