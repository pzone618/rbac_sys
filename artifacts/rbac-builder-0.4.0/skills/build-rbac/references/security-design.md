# Authorization contract and enforcement

## Decision model

An authenticated request is allowed only when the subject is active, the action is known, and an applicable grant satisfies all policy requirements for that action: tenant membership, grant scope, resource ownership/relationships, trusted attributes and optional service entitlement. Otherwise deny. Explicitly supported public routes have a separate documented policy.

A Role groups capabilities; a RoleAssignment binds a subject to a role and scope, optionally with start/end time. Distinguish tenant, branch, team, own and platform scopes. Enforce tenant-aware uniqueness and referential integrity. Do not infer ownership from a role or a permission suffix.

Prefer allow-only grants with default deny. Add explicit deny, inheritance, separation of duties, approval or temporary delegation only when required; then define precedence, cycle detection, time semantics and conflict tests. Background service identities need explicit capabilities and scope, not implicit platform administration.

## Trusted enforcement

- Derive subject and tenant context from validated authentication and membership. A client tenant selector is a request to validate, never proof of membership.
- Centralize decisions; cover nested serializers, lists/search/counts/aggregates, files, exports, bulk calls, alternate APIs and jobs.
- Use the same policy semantics for object checks and collection filtering. Filter before pagination/counting; do not fetch a page then discard forbidden rows.
- Protect owner, tenant, role, membership, entitlement and security-relevant attributes on both input and output. Validate cross-object references server-side.
- Fail closed on missing policy context, unknown actions or policy-engine failure. Use an authoritative database fallback only when it preserves the same semantics.
- Choose consistent 401/403/404 behavior without revealing inaccessible objects. Return stable public reason codes; detailed decision explanations require separate authorization.
- Prevent check/write races on privileged writes with an explicit transaction, locking/version check or equivalent invariant. Declare transaction ownership.
- Jobs must revalidate at execution or follow an explicit approved snapshot/delegation policy. Never blindly replay client privileges.

## Administrative boundaries

Granting requires both administrative permission and delegated authority over the target permission, tenant, scope and duration. Role editing must not indirectly grant powers the editor could not directly assign. Having a permission does not automatically mean being allowed to delegate it. Prevent self-escalation and unintended loss of the last recoverable administrator, including concurrent changes. Bootstrap without default passwords; document recovery.

## Revocation and audit

Define the maximum revocation delay for roles, memberships, relationships, entitlements and sessions. Short token TTL is eventual revocation. Use authoritative checks or versioned invalidation for immediate requirements; cover workers and replicas. Cache keys must isolate app/environment/tenant/subject and relevant policy versions. Handle outages without granting access; do not rely on Pub/Sub alone for durable invalidation.

Record actor, optional impersonator, target, tenant/scope, action, outcome, timestamp, correlation ID and redacted changes. Couple successful privileged writes and audit in the same transaction or durable outbox; define audit failure policy. Persist denied attempts outside rolled-back business transactions where required. Restrict audit reading/export and prevent ordinary editing/deletion. Keep secrets and unnecessary profile data out of logs.
