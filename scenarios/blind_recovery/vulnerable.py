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
    @strawberry.field(description="Fetch a user by ID. Vulnerable: verbose error messages leak schema hints.")
    def user(self, id: strawberry.ID) -> Optional[User]:
        record = USERS.get(str(id))
        if not record:
            # VULNERABILITY: verbose error reveals the id tried and internal structure
            raise Exception(
                f"User '{id}' not found in USERS dict — "
                f"valid ids are: {list(USERS.keys())}"
            )
        return User(**record)

    @strawberry.field(description="List all users.")
    def users(self) -> list[User]:
        return [User(**u) for u in USERS.values()]


vulnerable_schema = strawberry.Schema(query=Query)
