from typing import TypedDict


class UserRecord(TypedDict):
    id: str
    username: str
    email: str
    role: str


USERS: dict[str, UserRecord] = {
    "u1": {"id": "u1", "username": "alice", "email": "alice@example.com", "role": "admin"},
    "u2": {"id": "u2", "username": "bob", "email": "bob@example.com", "role": "viewer"},
    "u3": {"id": "u3", "username": "carol", "email": "carol@example.com", "role": "moderator"},
}

# A non-existent ID used in the attack query to trigger an error
PROBE_ID = "u9999"
