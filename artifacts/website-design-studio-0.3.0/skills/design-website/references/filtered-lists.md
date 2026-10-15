# Field-filtered lists and tables

Define the data contract before styling controls. For each filter, establish field type, operator, allowed values, null/empty handling and combination logic (AND/OR). Define case/diacritic behavior for text and time zone/inclusive boundaries for date ranges. Distinguish missing value from false, zero or an empty string.

Choose immediate or explicit Apply behavior. Show active conditions, result count when known, individual removal and reset-to-defined-defaults. Maintain draft/applied state separately if Apply is used. Include loading, error/retry, no data and no matches; no matches should offer a useful way to clear conditions.

Filtering, sorting and pagination must describe the same dataset. Client filtering over a server-loaded page is not filtering all records. In server mode, controlled state must drive the request/query key; library manual flags alone do not fetch data. Cancel or ignore stale requests. Define page/cursor reset after condition changes and a stable sort tie-breaker to avoid inconsistent ordering.

When URL persistence is requested, serialize validated supported conditions and support reload plus back/forward. Avoid placing confidential search values in shareable URLs by default. Define how hidden columns, selection across pages and bulk actions behave if those features exist. Frontend filters do not enforce authorization; retain server-side access control.

Use accessible typed controls, explicit labels and a mobile filter panel that preserves draft/applied state. Do not replace all filter types with text inputs. Announce result changes without disruptive focus jumps.

Acceptance: combined filters, zero/false/null values, date boundaries, reset, sort after filter, paging after filter, fast typing with reversed response order, no matches and URL restoration when supported. Use at least one matching record outside the initial server page to detect accidentally page-local filtering. Treat sample-data filtering as a prototype unless the real data path is tested.

Official TanStack Table documentation checked through Context7 on 2026-10-15; this is an implementation option, not a dependency requirement:
- https://tanstack.com/table/latest/docs/guide/column-filtering
- https://tanstack.com/table/latest/docs/guide/pagination
- https://tanstack.com/table/latest/docs/guide/sorting
