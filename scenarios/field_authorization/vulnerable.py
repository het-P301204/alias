import strawberry
from typing import Optional

from scenarios.field_authorization.fixtures import EMPLOYEES


@strawberry.type
class Employee:
    id: strawberry.ID
    name: str
    role: str
    department: str
    email: str
    ssn: str        # VULNERABILITY: exposed to any authenticated caller
    salary: float   # VULNERABILITY: exposed to any authenticated caller


@strawberry.type
class Query:
    @strawberry.field(description="Fetch employee by ID. Vulnerable: all fields returned regardless of caller role.")
    def employee(self, id: strawberry.ID) -> Optional[Employee]:
        record = EMPLOYEES.get(str(id))
        if not record:
            return None
        return Employee(
            id=record["id"],
            name=record["name"],
            role=record["role"],
            department=record["department"],
            email=record["email"],
            ssn=record["ssn"],
            salary=record["salary"],
        )

    @strawberry.field(description="List all employees.")
    def employees(self) -> list[Employee]:
        return [
            Employee(
                id=r["id"],
                name=r["name"],
                role=r["role"],
                department=r["department"],
                email=r["email"],
                ssn=r["ssn"],
                salary=r["salary"],
            )
            for r in EMPLOYEES.values()
        ]


vulnerable_schema = strawberry.Schema(query=Query)
