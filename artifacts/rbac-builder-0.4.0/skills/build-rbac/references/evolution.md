# Safe evolution and extension

Keep a modular authorization boundary before considering separate services. Application operations depend on capabilities and resource policies, not fixed role labels. Tenant roles are customizable only within a server-owned permission catalog and the administrator's delegated authority.

## Extension contract

Register each module's namespaced permissions, scope types, profile schemas, role templates and policy tests idempotently. New modules and permission codes receive no existing-role grants unless an explicit migration authorizes them. Avoid implicit "all current and future permissions" tenant roles.

Treat permission codes as stable identifiers. A rename, split or retirement needs a compatibility mapping, migration and deprecation plan. Version built-in role templates separately from tenant customizations: do not overwrite a custom role during template upgrades. Distinguish policy/schema versions from cache invalidation counters.

For profile changes, specify old-reader/new-writer compatibility, defaults/backfill, validation timing and rollback limitations. Do not introduce a new required field that immediately locks out all existing users without a planned completion path.

## Change plan and checks

1. Record current policy/schema version and representative allow/deny fixtures.
2. Describe the desired change and expected authorization diff by actor, action, scope and field.
3. Apply expand/backfill/contract migrations as needed; preserve old clients during the transition.
4. Test new and old fixtures. Investigate every unexpected allow, deny and data disclosure.
5. Roll out with explicit policy-version selection where supported; define reconciliation, monitoring and rollback. Do not assume rolling back code reverses migrated data.
6. Remove compatibility paths only after usage and stored data are verified.

For external engines, pin/select supported model versions rather than assuming "latest" is safe. When business data and policy tuples live in different systems, define transactional outbox/reconciliation, stale-state behavior and revocation bounds. Never claim an engine alone solves consistency or query filtering.

## Required extension exercise

When extensibility is in scope, demonstrate a representative change such as a cross-branch support role, one user with multiple profiles, a new module without automatic grants, or a tenant-customized role surviving a template upgrade. Show the changed model/rules and regression results, not just a statement that the architecture is extensible.

## Evidence

OpenFGA provides immutable model versions and model fixtures with positive/negative assertions. These support versioned rollout and policy regression; using OpenFGA is optional.
- https://openfga.dev/docs/getting-started/immutable-models
- https://openfga.dev/docs/modeling/store-file-format
- https://openfga.dev/docs/modeling/migrating/migrating-relations
