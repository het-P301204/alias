from typing import TypedDict


class UserRecord(TypedDict):
    id: str
    name: str
    role: str


class OrderRecord(TypedDict):
    id: str
    user_id: str
    total: float
    status: str


USERS: dict[str, UserRecord] = {
    "1": {"id": "1", "name": "Alice", "role": "customer"},
    "2": {"id": "2", "name": "Bob", "role": "customer"},
    "3": {"id": "3", "name": "Carol", "role": "admin"},
}

ORDERS: dict[str, OrderRecord] = {
    "1": {"id": "1", "user_id": "1", "total": 99.99, "status": "COMPLETE"},
    "2": {"id": "2", "user_id": "1", "total": 149.50, "status": "PENDING"},
    "3": {"id": "3", "user_id": "2", "total": 75.00, "status": "COMPLETE"},
}


def reset_fixtures() -> None:
    pass  # dicts are module constants; identity stable across resets
