import strawberry
from typing import Optional

from scenarios.blind_recovery.fixtures import USERS


@strawberry.type
class User:
    id: strawberry.ID
    username: str
    email: str
    role: str


@strawberry.type
class Query:
    @strawberry.field(description="Fetch a user by ID. Hardened: returns null instead of a revealing error.")
    def user(self, id: strawberry.ID) -> Optional[User]:
        record = USERS.get(str(id))
        if not record:
            # DEFENSE: return null — no error message hints at valid IDs or internal state
            return None
        return User(**record)

    @strawberry.field(description="List all users.")
    def users(self) -> list[User]:
        return [User(**u) for u in USERS.values()]


hardened_schema = strawberry.Schema(query=Query)
