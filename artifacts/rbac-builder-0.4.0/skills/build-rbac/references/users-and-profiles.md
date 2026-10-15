# Users, profiles and lifecycle

## Separate responsibilities

| Concept | Responsibility |
| --- | --- |
| User | Stable application identity, account state and provider linkage |
| ExternalIdentity | Unique trusted issuer/provider + subject link to User |
| Profile | Domain data such as student, customer or employee; multiple may coexist |
| Membership | Participation and status in a tenant/organization |
| RoleAssignment | Capability bundle within a validated scope and validity interval |
| Relationship | Ownership, teaching assignment, team participation or resource sharing |
| Entitlement | Service eligibility such as enrollment or subscription; separate from staff authority |

Map to an existing provider/framework rather than duplicating its identity store. Do not identify users by mutable email alone or automatically merge accounts based on an unverified matching email. Account linking/merging requires proof, conflict handling and traceable reassignment.

## Field contract

For every profile field define: type, owner/system of record, sensitivity, view/edit audiences, validation, required stage, verification status, audit/redaction rules and schema evolution. Use separate self-service and administrative input/output schemas; reject unknown/protected fields or document safe omission.

Examples:
- display_name: user editable with bounds; no authority.
- employee_number: HR/admin managed within organization.
- teacher_verification: trusted workflow managed; never self-certified.
- subscription_status: entitlement/billing managed; not an ordinary profile field.

Keep security-relevant attributes server-controlled and validate their source. Attribute read permission and write permission are distinct. Apply field visibility to details, lists, nested relations and exports. Do not solve all extensions with an untyped JSON blob or arbitrary EAV schema: use typed domain tables for important relationships and constraints; allow bounded, validated metadata only where justified.

Sensitive contact changes need provider-supported verification and appropriate reauthentication. Define deletion/anonymization, retention and historical ownership behavior according to actual requirements; never invent legal periods. Keep provider and application updates consistent with retries/reconciliation where a single transaction is impossible.

## Lifecycle contract

Select actual states and transitions rather than imposing every state:
- Account: pending verification, active, suspended, closed.
- Membership: invited, active, suspended, ended.
- Grant: scheduled, active, expired, revoked.
- Domain profile and entitlement: independent domain states.

For every transition specify actor, permission, prerequisites, state mutation, affected grants/relationships/sessions, audit, retry/idempotency and recovery. Invitations need scoped purpose, expiry, single-use redemption and validated recipient; no unintended grant before acceptance.

Leaving one tenant ends that membership's authority, not the global user or unrelated profiles. Rejoining must not silently reactivate old grants. A branch transfer must explicitly end, preserve or replace prior assignments. Suspension must follow documented access and session revocation semantics. Account closure must not destroy necessary business/audit references.

Implement provider-supported recovery/MFA/session management as required; do not rebuild identity-provider features by default.

## Evidence

Keycloak demonstrates governed attributes with separate view/edit permissions, conditional requirements, validation and managed-attribute policy. Adapt the principle without requiring Keycloak or copying its user/admin profile categories as application business roles.
- https://github.com/keycloak/keycloak/blob/main/docs/documentation/server_admin/topics/users/user-profile.adoc
