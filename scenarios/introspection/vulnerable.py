import strawberry
import typing
from typing import Optional

from scenarios.introspection.fixtures import (
    User, Product, Order, OrderItem, Config,
    SEED_USERS, SEED_PRODUCTS, SEED_CONFIG,
)


def _make_user(d: dict) -> User:
    return User(
        id=d["id"], email=d["email"], name=d["name"], role=d["role"],
        created_at=d["created_at"], password_hash="$2b$12$XXXX_SYNTHETIC_HASH",
        last_login_ip=d["last_login_ip"], internal_notes=d.get("internal_notes"),
    )


@strawberry.type
class Query:
    @strawberry.field(description="List users (paginated)")
    def users(self, limit: int = 10) -> typing.List[User]:
        return [_make_user(u) for u in SEED_USERS[:limit]]

    @strawberry.field(description="Get user by ID")
    def user(self, id: strawberry.ID) -> Optional[User]:
        match = next((u for u in SEED_USERS if u["id"] == str(id)), None)
        return _make_user(match) if match else None

    @strawberry.field(description="List admin users only")
    def admin_users(self) -> typing.List[User]:
        return [_make_user(u) for u in SEED_USERS if u["role"] == "ADMIN"]

    @strawberry.field(description="Current authenticated user")
    def current_user(self, info: strawberry.types.Info) -> Optional[User]:
        uid = (info.context or {}).get("user_id")
        match = next((u for u in SEED_USERS if u["id"] == str(uid)), None)
        return _make_user(match) if match else None

    @strawberry.field(description="List products")
    def products(self) -> typing.List[Product]:
        return [Product(**p) for p in SEED_PRODUCTS]

    @strawberry.field(description="Orders for a user")
    def orders(self, user_id: Optional[strawberry.ID] = None) -> typing.List[Order]:
        return [Order(id="o1", user_id="1", total=99.99, status="COMPLETE", items=[
            OrderItem(product_id="p1", quantity=2, unit_price=49.99)
        ])]

    @strawberry.field(description="System configuration")
    def config(self) -> Config:
        return Config(**SEED_CONFIG)


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Create a new user")
    def create_user(self, email: str, name: str, role: str = "CUSTOMER") -> User:
        return User(id="new", email=email, name=name, role=role, created_at="2026-01-01")

    @strawberry.mutation(description="Update user details")
    def update_user(self, id: strawberry.ID, name: Optional[str] = None) -> Optional[User]:
        match = next((u for u in SEED_USERS if u["id"] == str(id)), None)
        if not match:
            return None
        d = dict(match)
        if name:
            d["name"] = name
        return _make_user(d)

    @strawberry.mutation(description="Delete user account")
    def delete_user(self, id: strawberry.ID) -> bool:
        return True

    @strawberry.mutation(description="Trigger password reset email")
    def reset_password(self, email: str) -> bool:
        return True

    @strawberry.mutation(description="Create a new product")
    def create_product(self, name: str, price: float, cost: float, internal_sku: str) -> Product:
        return Product(id="new_p", name=name, price=price, cost=cost, internal_sku=internal_sku)


# Vulnerable: introspection fully enabled (default strawberry behavior)
vulnerable_schema = strawberry.Schema(query=Query, mutation=Mutation)
