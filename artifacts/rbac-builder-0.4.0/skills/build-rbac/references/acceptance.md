# Application acceptance

Build tests from a scope-aware matrix using representative actors and real endpoint/data-access paths. Include an allowed control so a system that denies everything cannot pass. Mark irrelevant cases with a reason; do not build optional infrastructure just to run a checklist.

| Boundary | Expected evidence |
| --- | --- |
| Anonymous, suspended, missing grant, unknown action | Denied on protected operation |
| Active authorized actor in valid scope | Allowed with intended result |
| Same role in another tenant/branch or another owner's object | Denied without leakage |
| List/search/count/export/nested relations | Same scope semantics, correct pagination/counts |
| Forged tenant/owner/role/entitlement/profile attribute | Rejected or safely server-derived |
| Private fields and administrative fields | Separate authorized reads and writes, including exports |
| Role editing or delegation exceeds administrator authority | Denied, including indirect escalation |
| Last recoverable administrator removed concurrently | Recovery invariant preserved |
| Role/membership/relationship/entitlement revoked | Documented bound across sessions/workers |
| Invitation replay, expired grant, rejoining tenant | No unintended authority restored |
| Branch transfer and overlapping domain profiles | Correct independent permissions and historical ownership |
| Custom/bulk/file/job operations | Same boundaries as ordinary endpoints |
| Cache/policy dependency unavailable or stale | Fail closed or equivalent authoritative fallback |
| Privileged write and audit rollback/retry | Consistent state; idempotent durable events |
| New module/template/policy/profile schema upgrade | Only expected permission diff; customizations preserved |

Use isolated databases and installed framework-compatible clients. Test state changes and concurrent cases when relevant, not merely mocked permission helpers. Verify schema constraints, migration/backfill on representative data and rollback limitations. A UI test cannot substitute for direct API tests.

If UI changes, verify scope selection, field visibility, permission refresh after revocation, accessible errors and existing locale/design conventions. Do not add themes or translations unrelated to the task.

Report executed commands and results separately from suggested tests and blocked checks. A checklist is not an executed test suite.
