from typing import TypedDict


class EmployeeRecord(TypedDict):
    id: str
    name: str
    role: str
    department: str
    ssn: str
    salary: float
    email: str


EMPLOYEES: dict[str, EmployeeRecord] = {
    "e1": {
        "id": "e1",
        "name": "Alice",
        "role": "admin",
        "department": "Engineering",
        "ssn": "XXX-XX-1111",  # synthetic — not a real SSN
        "salary": 120000.0,
        "email": "alice@corp.example",
    },
    "e2": {
        "id": "e2",
        "name": "Bob",
        "role": "viewer",
        "department": "Marketing",
        "ssn": "XXX-XX-2222",  # synthetic — not a real SSN
        "salary": 85000.0,
        "email": "bob@corp.example",
    },
    "e3": {
        "id": "e3",
        "name": "Carol",
        "role": "hr",
        "department": "Human Resources",
        "ssn": "XXX-XX-3333",  # synthetic — not a real SSN
        "salary": 95000.0,
        "email": "carol@corp.example",
    },
}

# Roles and which sensitive fields they may access
SENSITIVE_FIELD_ACCESS: dict[str, set[str]] = {
    "admin": {"ssn", "salary"},
    "hr": {"salary"},
    "viewer": set(),
}
