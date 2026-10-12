# ALIAS — Defensive Controls

Each scenario's hardened mode applies one or more defensive controls. This document describes each control, how to verify it works, and what a passing result looks like.

---

## 1. Introspection Disabled

**Control ID**: `introspection-disabled`  
**Scenario**: Schema Introspection  
**OWASP**: API9:2023 Improper Inventory Management

### Description

Disable GraphQL introspection at the schema level. The `__schema`, `__type`, and related meta-fields return `null` instead of schema data. Type names in valid query responses still resolve correctly; only the metadata catalog is hidden.

Implementation: a Strawberry schema extension intercepts the execution context before field resolution. If the query's selection set contains any introspection field, the extension substitutes null for that field's result.

### How to verify

Send the standard introspection query to the hardened endpoint:
```graphql
{ __schema { types { name } } }
```

Expected hardened response:
```json
{"data": {"__schema": null}}
```

The platform's `POST /api/defenses/introspection-disabled/verify` runs this check automatically.

### Passing criteria

- `__schema.types` is `null` or an empty array
- No type names are disclosed in the response
- Valid non-introspection queries (e.g. `{ me { name } }`) still work correctly

---

## 2. Per-Object Authorization

**Control ID**: `per-object-authorization`  
**Scenario**: Alias-Based Authorization  
**OWASP**: API1:2023 Broken Object Level Authorization

### Description

Authorization is evaluated inside each field resolver against the resolved object's owner identifier, not at the operation or HTTP level. When the same field is requested via multiple aliases, each alias invokes the same per-object check independently.

```python
# Pseudocode — resolver-level check
def resolve_salary(self, info: Info) -> int | None:
    user_id = self.id
    requesting_user = info.context["user"]
    if user_id != requesting_user.id:
        return None  # silently deny, not an error
    return self.salary
```

### How to verify

Send a query with two aliases targeting different users:
```graphql
{
  me: user(id: "user-1") { salary }
  other: user(id: "user-2") { salary }
}
```

Authenticated as user-1, the hardened response:
```json
{"data": {"me": {"salary": 95000}, "other": {"salary": null}}}
```

### Passing criteria

- The requesting user's own fields resolve normally
- Cross-user alias targets return `null` for protected fields
- No error is raised (the field resolves to `null` silently)

---

## 3. Operation Count Limit

**Control ID**: `batch-operation-limit`  
**Scenario**: Batching & Rate Limits  
**OWASP**: API4:2023 Unrestricted Resource Consumption

### Description

HTTP-batched requests (JSON arrays of GraphQL operations) are counted before execution. If the array length exceeds `MAX_BATCH_OPERATIONS` (default 10), the entire batch is rejected with HTTP 429 before any resolver runs.

This check operates at the transport layer (middleware), not the GraphQL layer, so it cannot be bypassed by query restructuring.

### How to verify

Send an HTTP-batched request with 11 or more operations:
```json
[
  {"query": "{ me { name } }"},
  ... (11 total)
]
```

Expected response: HTTP 429 with body `{"error": "Batch size exceeds limit"}`.

### Passing criteria

- Batches of ≤10 operations succeed
- Batches of 11+ operations return HTTP 429
- The count is per-HTTP-request, not per-session

---

## 4. Query Depth and Complexity Limits

**Control ID**: `query-depth-complexity`  
**Scenario**: Query Depth & Complexity  
**OWASP**: API4:2023 Unrestricted Resource Consumption

### Description

Two Strawberry schema extensions run before the resolver tree executes:

**DepthLimitExtension** — counts the maximum nesting depth of the query's selection set. Queries exceeding `MAX_QUERY_DEPTH` (default 10) are rejected with a GraphQL error; no resolvers run.

**ComplexityLimitExtension** — assigns a cost (default 1 per leaf field, multiplied by list field factors) and rejects queries whose total cost exceeds `MAX_COMPLEXITY` (default 1000).

### How to verify

Send a deeply nested query (depth 11):
```graphql
{ user { friends { friends { friends { friends { friends { friends { friends { friends { friends { friends { name } } } } } } } } } } } }
```

Expected response: GraphQL error, no data.
```json
{"errors": [{"message": "Query depth 11 exceeds maximum 10"}], "data": null}
```

### Passing criteria

- Depth-10 queries succeed
- Depth-11 queries return a GraphQL error without executing
- Complexity-limit queries return a GraphQL error without executing
- The error fires before any database access

---

## 5. Sanitized Validation Errors

**Control ID**: `sanitized-errors`  
**Scenario**: Blind Schema Recovery  
**OWASP**: API9:2023 Improper Inventory Management

### Description

GraphQL's default validation error messages include field-name suggestions derived from the real schema. In hardened mode, all validation error messages are replaced with a generic string before reaching the response serializer. The replacement runs as a response processor in the Strawberry schema extension pipeline.

### How to verify

Query for a field that does not exist on `User`:
```graphql
{ user(id: "1") { doesNotExist } }
```

Vulnerable response:
```json
{"errors": [{"message": "Cannot query field 'doesNotExist' on type 'User'. Did you mean 'salary', 'name'?"}]}
```

Hardened response:
```json
{"errors": [{"message": "Unknown field."}]}
```

### Passing criteria

- Error messages do not include `"Did you mean"` or any field name suggestion
- A generic, non-informative error message is returned instead
- Valid queries still resolve normally

---

## 6. Field-Level Permission Checks

**Control ID**: `field-level-permissions`  
**Scenario**: Field-Level Authorization  
**OWASP**: API5:2023 Broken Function Level Authorization

### Description

Each sensitive field (`salary`, `ssn`, `internalNotes`) has its own resolver that checks the requesting user's role against the field's access policy before returning a value. The check is independent per field — passing object-level authorization does not grant field-level access.

Role access policy:
| Field | viewer | manager | admin |
|-------|--------|---------|-------|
| name, email | ✓ | ✓ | ✓ |
| salary | ✗ (null) | ✓ | ✓ |
| ssn | ✗ (null) | ✗ (null) | ✓ |
| internalNotes | ✗ (null) | ✗ (null) | ✓ |

### How to verify

Send a query requesting all fields as a `viewer`-role user:
```graphql
{ employee(id: "1") { name email salary ssn internalNotes } }
```

Expected hardened response:
```json
{
  "data": {
    "employee": {
      "name": "Alice",
      "email": "alice@example.com",
      "salary": null,
      "ssn": null,
      "internalNotes": null
    }
  }
}
```

### Passing criteria

- `viewer` receives `null` for `salary`, `ssn`, `internalNotes`
- `manager` receives `salary` but `null` for `ssn` and `internalNotes`
- `admin` receives all fields
- No authorization error is raised — restricted fields resolve to `null`
