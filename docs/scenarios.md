# ALIAS — Scenarios

Each scenario demonstrates one class of GraphQL vulnerability. All run in an isolated lab with synthetic data. Both vulnerable and hardened modes are available; hardened mode applies the defensive control so you can observe the difference.

---

## 1. Schema Introspection

**Scenario ID**: `introspection`  
**Difficulty**: Beginner  
**Category**: Information Disclosure

### What is demonstrated

GraphQL exposes a built-in introspection system that lets any client query the full schema — every type, field, mutation, deprecated item, and directive. In vulnerable mode, introspection is unrestricted. An attacker with any access to the endpoint can run:

```graphql
{ __schema { types { name fields { name type { name } } } } }
```

and receive the complete type map in a single response. This discloses internal field names, business object relationships, and deprecated API surface that was intentionally hidden from the frontend.

### Why it matters

Schema disclosure is typically the first step in a GraphQL attack chain. Knowing exact field names eliminates guesswork for alias-based authorization bypass, blind field recovery, and field-level access testing. Production GraphQL APIs from major companies have been compromised this way.

### Hardened mode

The schema extension `IntrospectionDisabledExtension` intercepts any query that references `__schema`, `__type`, or `__typename` at the root level and returns `null` for all introspection fields. Type names still resolve in valid responses; the schema metadata is simply not disclosed. Hardened mode passes if `types` is empty in the introspection response.

---

## 2. Alias-Based Authorization

**Scenario ID**: `alias-authorization`  
**Difficulty**: Intermediate  
**Category**: Broken Object-Level Authorization (BOLA)

### What is demonstrated

GraphQL's alias feature lets a single query fetch the same field multiple times under different names:

```graphql
{
  me: user(id: "self") { salary }
  victim: user(id: "other-user-id") { salary }
}
```

In a naive implementation, the authorization check fires for the field resolver — but the same resolver handles both aliases. If the check only validates the first alias or validates at the operation level, both aliases are authorized by the check on `me`. The `victim` alias returns restricted data.

### Why it matters

BOLA is consistently the #1 vulnerability in the OWASP API Security Top 10. GraphQL aliases make it trivial to probe multiple object IDs in a single request, bypassing rate limits that count HTTP requests rather than object accesses. Sensitive fields (salary, SSN, medical record) become fully accessible.

### Hardened mode

Field-level authorization is applied per resolver call, using the resolved object's owner ID compared to the requesting user's authenticated identity — not at the operation or query level. Each alias invokes the same per-object check independently. Hardened mode passes if the victim alias returns `null` or an authorization error while the `me` alias succeeds.

---

## 3. Batching & Rate Limits

**Scenario ID**: `batching`  
**Difficulty**: Intermediate  
**Category**: Denial of Service / Brute Force Amplification

### What is demonstrated

GraphQL supports two forms of batching: **HTTP batching** (multiple operations in one POST as a JSON array) and **alias batching** (multiple aliases in one operation). HTTP rate limiters typically count requests, not operations. Vulnerable mode accepts HTTP-batched requests without counting per-operation:

```json
[
  {"query": "mutation { login(user: \"admin\", pass: \"aaa\") { token } }"},
  {"query": "mutation { login(user: \"admin\", pass: \"aab\") { token } }"},
  ...100 more
]
```

One HTTP request becomes 100 login attempts.

### Why it matters

Credential stuffing, OTP brute-forcing, and enumeration attacks are all amplified by batching. The amplification factor equals the batch size. A 10 req/min rate limit becomes 1000 ops/min if each request batches 100 operations.

### Hardened mode

Operation count is extracted before execution. Requests exceeding `MAX_BATCH_OPERATIONS` (default 10) are rejected with HTTP 429 before any operation runs. Hardened mode passes if a batch of 11+ operations returns 429.

---

## 4. Query Depth & Complexity

**Scenario ID**: `query-complexity`  
**Difficulty**: Intermediate  
**Category**: Denial of Service

### What is demonstrated

GraphQL's recursive type system allows deeply nested queries. A schema with `User → friends → [User]` can be queried:

```graphql
{
  user {
    friends {
      friends {
        friends { ... }
      }
    }
  }
}
```

Each level multiplies the number of database lookups. A depth-10 query against a 10-friend-per-user graph requires 10^10 lookups. In vulnerable mode, depth and complexity are unlimited — a single crafted query can exhaust CPU, memory, and DB connections.

### Why it matters

No authentication is required. A single unauthenticated request can denial-of-service a GraphQL API. This is distinct from DDoS — it is a resource exhaustion attack via a single packet.

### Hardened mode

`DepthLimitExtension` rejects queries exceeding `MAX_QUERY_DEPTH` (default 10). `ComplexityLimitExtension` assigns a cost to each field type and rejects queries whose total cost exceeds `MAX_COMPLEXITY` (default 1000). Both checks run before the resolver tree executes. Hardened mode passes if a depth-11 query returns an error without executing.

---

## 5. Blind Schema Recovery

**Scenario ID**: `blind-recovery`  
**Difficulty**: Advanced  
**Category**: Information Disclosure (indirect)

### What is demonstrated

When introspection is disabled but error messages are verbose, field names can still be recovered. Strawberry GraphQL's default validation error for an unknown field is:

```
Cannot query field 'salary' on type 'User'. Did you mean 'name', 'email'?
```

The "Did you mean" suggestion leaks the real field names. By iterating over guesses, an attacker can reconstruct the full schema — without introspection access.

### Why it matters

Disabling introspection provides a false sense of security if error messages are left verbatim. A determined attacker can recover the full schema in O(n log n) queries using binary-search-style probing against the suggestion system.

### Hardened mode

Validation error messages are sanitized before reaching the client. Unknown field errors return a generic message (`"Unknown field."`) without suggestions. Hardened mode passes if the suggestion text does not appear in error responses.

---

## 6. Field-Level Authorization

**Scenario ID**: `field-authorization`  
**Difficulty**: Advanced  
**Category**: Broken Function-Level Authorization

### What is demonstrated

Type-level authorization (checking that the user can access a `User` object) does not imply field-level authorization (checking that the user can read `salary` on that object). In vulnerable mode, any authenticated user who can resolve a `User` can also read every field, including `salary`, `ssn`, and `internalNotes`. Authorization is checked once at object resolution, not per field.

### Why it matters

This pattern is extremely common. ORM-level access control does not protect individual columns. Even if the frontend hides sensitive fields, the API returns them if queried directly.

### Hardened mode

Each sensitive field resolver calls a permission check specific to that field and role combination. A `viewer` role receives `null` (not an error) for `salary`, `ssn`, and `internalNotes`. An `admin` role receives the actual values. Hardened mode passes if the `viewer` role receives `null` for all restricted fields.
