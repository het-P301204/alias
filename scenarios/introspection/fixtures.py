import strawberry
from enum import Enum
from typing import Optional
import typing


@strawberry.enum
class UserRole(Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    CUSTOMER = "CUSTOMER"


@strawberry.type
class User:
    id: strawberry.ID
    email: str
    name: str
    role: str
    created_at: str
    password_hash: Optional[str] = strawberry.field(
        description="[DEPRECATED] Raw hash stored for legacy compat",
        deprecation_reason="Use auth service instead",
        default=None,
    )
    last_login_ip: Optional[str] = None
    internal_notes: Optional[str] = None


@strawberry.type
class OrderItem:
    product_id: strawberry.ID
    quantity: int
    unit_price: float


@strawberry.type
class Order:
    id: strawberry.ID
    user_id: strawberry.ID
    total: float
    status: str
    items: typing.List[OrderItem]


@strawberry.type
class Product:
    id: strawberry.ID
    name: str
    price: float
    cost: float = strawberry.field(description="Internal cost — not for clients")
    internal_sku: str = strawberry.field(description="Warehouse SKU")


@strawberry.type
class Config:
    maintenance_mode: bool
    debug_enabled: bool
    admin_email_override: Optional[str] = None


SEED_USERS = [
    {"id": "1", "email": "alice@asterion.io", "name": "Alice", "role": "CUSTOMER", "created_at": "2024-01-01", "last_login_ip": "10.0.0.1", "internal_notes": None},
    {"id": "2", "email": "bob@asterion.io", "name": "Bob", "role": "STAFF", "created_at": "2024-01-02", "last_login_ip": "10.0.0.2", "internal_notes": "Legacy account"},
    {"id": "3", "email": "carol@asterion.io", "name": "Carol", "role": "ADMIN", "created_at": "2023-12-01", "last_login_ip": "10.0.0.3", "internal_notes": "Primary admin"},
]

SEED_PRODUCTS = [
    {"id": "p1", "name": "Widget Pro", "price": 49.99, "cost": 12.50, "internal_sku": "WP-001"},
    {"id": "p2", "name": "Gadget Plus", "price": 89.99, "cost": 24.00, "internal_sku": "GP-002"},
]

SEED_CONFIG = {"maintenance_mode": False, "debug_enabled": True, "admin_email_override": "ops@asterion.io"}
