import strawberry
from typing import Optional

from scenarios.batching.fixtures import check_password

_http_request_counter: dict[str, int] = {"count": 0}


@strawberry.type
class AuthResult:
    success: bool
    token: Optional[str] = None
    user_id: Optional[strawberry.ID] = None


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Authenticate a user. Vulnerable: no operation-count limit.")
    def authenticate_user(self, username: str, password: str) -> AuthResult:
        ok = check_password(username, password)
        return AuthResult(
            success=ok,
            token=f"tok_{username}_synthetic" if ok else None,
            user_id=username if ok else None,
        )


@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> str:
        return "ok"


vulnerable_schema = strawberry.Schema(query=Query, mutation=Mutation)
