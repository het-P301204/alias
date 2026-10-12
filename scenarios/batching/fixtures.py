import hashlib
from typing import TypedDict


class DemoAccount(TypedDict):
    username: str
    password_hash: str  # synthetic — not a real credential


def _hash(pw: str) -> str:
    return hashlib.sha256(f"alias_synthetic_salt_{pw}".encode()).hexdigest()


DEMO_ACCOUNTS: dict[str, DemoAccount] = {
    "demo_alice": {"username": "demo_alice", "password_hash": _hash("demo_alice_pw")},
    "demo_bob": {"username": "demo_bob", "password_hash": _hash("demo_bob_pw")},
    "demo_carol": {"username": "demo_carol", "password_hash": _hash("demo_carol_pw")},
    "demo_dave": {"username": "demo_dave", "password_hash": _hash("demo_dave_pw")},
    "demo_eve": {"username": "demo_eve", "password_hash": _hash("demo_eve_pw")},
}

# Correct synthetic passwords (for test fixture only — not real credentials)
DEMO_PASSWORDS: dict[str, str] = {
    "demo_alice": "demo_alice_pw",
    "demo_bob": "demo_bob_pw",
    "demo_carol": "demo_carol_pw",
    "demo_dave": "demo_dave_pw",
    "demo_eve": "demo_eve_pw",
}


def check_password(username: str, password: str) -> bool:
    account = DEMO_ACCOUNTS.get(username)
    if not account:
        return False
    return account["password_hash"] == _hash(password)
