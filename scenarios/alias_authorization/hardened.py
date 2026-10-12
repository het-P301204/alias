import strawberry
from typing import Optional

from scenarios.alias_authorization.fixtures import ORDERS, USERS
from scenarios.alias_authorization.vulnerable import Order


@strawberry.type
class Query:
    @strawberry.field(description="Fetch an order by ID. Hardened: ownership enforced.")
    def order(self, info: strawberry.types.Info, id: strawberry.ID) -> Optional[Order]:
        ctx = info.context or {}
        caller_id = str(ctx.get("user_id", ""))
        user = USERS.get(caller_id)
        if not user:
            raise PermissionError("Unauthenticated")
        record = ORDERS.get(str(id))
        if not record:
            return None
        # FIX: enforce ownership
        if record["user_id"] != caller_id:
            raise PermissionError(f"Access denied: order {id} does not belong to caller")
        return Order(**record)


hardened_schema = strawberry.Schema(query=Query)
