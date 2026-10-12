import strawberry
from typing import Optional

from scenarios.field_authorization.fixtures import EMPLOYEES, SENSITIVE_FIELD_ACCESS


@strawberry.type
class Employee:
    id: strawberry.ID
    name: str
    role: str
    department: str
    email: str
    ssn: Optional[str] = None      # FIX: null for unauthorized callers
    salary: Optional[float] = None  # FIX: null for unauthorized callers


@strawberry.type
class Query:
    @strawberry.field(description="Fetch employee by ID. Hardened: sensitive fields gated by caller role.")
    def employee(self, info: strawberry.types.Info, id: strawberry.ID) -> Optional[Employee]:
        ctx = info.context or {}
        caller_role = str(ctx.get("role", "viewer"))
        allowed = SENSITIVE_FIELD_ACCESS.get(caller_role, set())

        record = EMPLOYEES.get(str(id))
        if not record:
            return None

        return Employee(
            id=record["id"],
            name=record["name"],
            role=record["role"],
            department=record["department"],
            email=record["email"],
            ssn=record["ssn"] if "ssn" in allowed else None,
            salary=record["salary"] if "salary" in allowed else None,
        )

    @strawberry.field(description="List all employees (non-sensitive fields only).")
    def employees(self, info: strawberry.types.Info) -> list[Employee]:
        ctx = info.context or {}
        caller_role = str(ctx.get("role", "viewer"))
        allowed = SENSITIVE_FIELD_ACCESS.get(caller_role, set())

        return [
            Employee(
                id=r["id"],
                name=r["name"],
                role=r["role"],
                department=r["department"],
                email=r["email"],
                ssn=r["ssn"] if "ssn" in allowed else None,
                salary=r["salary"] if "salary" in allowed else None,
            )
            for r in EMPLOYEES.values()
        ]


hardened_schema = strawberry.Schema(query=Query)
