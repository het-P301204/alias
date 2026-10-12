import strawberry
from typing import Optional

from scenarios.alias_authorization.fixtures import ORDERS, USERS


@strawberry.type
class Order:
    id: strawberry.ID
    user_id: strawberry.ID
    total: float
    status: str


@strawberry.type
class Query:
    @strawberry.field(description="Fetch an order by ID. Vulnerable: no ownership check.")
    def order(self, info: strawberry.types.Info, id: strawberry.ID) -> Optional[Order]:
        ctx = info.context or {}
        caller_id = str(ctx.get("user_id", ""))
        user = USERS.get(caller_id)
        if not user:
            raise PermissionError("Unauthenticated")
        # VULNERABILITY: returns order regardless of whether it belongs to caller
        record = ORDERS.get(str(id))
        if not record:
            return None
        return Order(**record)


vulnerable_schema = strawberry.Schema(query=Query)
