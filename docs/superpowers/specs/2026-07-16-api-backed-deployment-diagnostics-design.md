# API-backed deployment diagnostics

**Date:** 2026-07-16
**Updated:** 2026-07-23 — streaming read of the API response; `deep_diagnostics`
flag kept (renamed `diagnostics`) for gating rather than removed.
**Status:** Approved (design)
**Tool affected:** `ise_deployment_health` (`DeploymentToolHandler` + `DeploymentDiagnosticsResolver`)

## Problem

Today, deep deployment diagnostics are produced by downloading each node's
`iseLocalStore` log (capped at 3 nodes, unhealthy prioritized), extracting a zip,
and parsing `System-Stats: ISE Utilization` lines for CPU / memory / disk over a
60-minute window (`SystemStatsParser`). This is:

- **Heavy** — one authenticated log download + zip extraction per sampled node.
- **Incomplete** — capped at 3 nodes; a large deployment is only partially covered.
- **Gated** — exposed behind a `deep_diagnostics=True` flag precisely because it
  is slow, requiring callers to opt in only on problem-signaling wording.

ISE exposes a single MNT dashboard endpoint that returns process health plus
CPU / memory / latency time series for **all** nodes in one call:

```
GET https://<mnt>:<port>/admin/API/mnt/dashboard/getSystemSummaryDetails
```

One API call replaces the entire log-download path (one authenticated download +
zip extraction *per node*). It is far lighter, but not free: in a large
deployment the 60-minute series across every node can be a sizable XML payload.
So the diagnostics stay **gated behind an opt-in flag** (renamed from
`deep_diagnostics` to `diagnostics`), and when they do run the response is read
with a **streaming, memory-bounded parse** rather than buffered whole.

## Goals

1. Replace log-download-based system stats with the `getSystemSummaryDetails`
   API for the `ise_deployment_health` diagnostics.
2. Add **process health** (per-node process up/down/disabled) derived from the
   API, mapped to the admin-guide "Process Down" concept.
3. **Keep the opt-in gating flag, renamed `deep_diagnostics` → `diagnostics`.**
   Diagnostics run only when `diagnostics=True`; the base summary is always
   returned regardless. The API response can be large in big deployments, so
   the call stays opt-in.
4. Read the `getSystemSummaryDetails` response with a **streaming, memory-bounded
   parse** (the AuthList pattern: `get_stream` → spooled temp file → `iterparse`
   with `root.clear()`, run off the event loop via `asyncio.to_thread`), so a
   large payload cannot spike memory or stall the event loop.
5. Degrade gracefully: an API failure must not fail the base health summary.

## Non-goals

- Changing how the base `DeploymentHealthSummary` verdict is computed (it stays
  driven by the Deployment OpenAPI node status). Process-down faults surface as
  **diagnostics observations**, not as inputs to `summary.verdict`.
- Disk utilization. The API does not report per-mount disk %, so it is dropped.
- The 24-hour time series. Only the 60-minute window is aggregated (matches the
  existing `system_stats` output shape).

## API response shape

`<dashboardResult>` contains three repeated element groups:

- `lstProcessStatuses` (one per node) — per-process numeric status codes plus a
  top-level `<status>` and `<server>`. Example fields: `applicationServer`,
  `database`, `databaseListener`, `alertManager`, `logCollector`,
  `logProcessor`, `sessionDatabase`, `ipepService`, `profilerDb`, `sxpEngine`,
  `deviceAdmin`, `xgridJabberd`, `xgridPubsub`, `xgridCm`, `xgridController`,
  `certificateAuthority`, `identityMapping`, `aDConnector`.
- `lstSystemStatus60Min` (many per node) — `server`, `timestamp`,
  `cpuUtilization`, `memoryUtilization`, `latency` at ~5-minute cadence.
- `lstSystemStatus24Hr` (many per node) — same fields, hourly. **Unused.**

### Process status codes

Confirmed by correlating a real API sample (vm218 @ 08:30) against the node's
`70001 NOTICE System-Stats: ISE Process Health` log line (@ 09:12):

| Code | Meaning        | Fault? | Evidence |
|------|----------------|--------|----------|
| `1`  | running        | no     | applicationServer/database/… = `1`, log says `running` |
| `2`  | disabled       | no     | sxpEngine=`2`, identityMapping=`2`; log says `SXP Engine Service=disabled`, `PassiveID …=disabled` |
| `-1` | not applicable | no     | alertManager/logCollector/xgrid* = `-1`; not present in log |
| `0`  | not running    | **yes**| admin-guide "Process Down": one of the Cisco ISE processes is not running |

Only code `0` (and any future stuck/initializing value observed as non-running)
counts as a fault. `2` (disabled) and `-1` (N/A) are reported but not counted
against health. Unrecognized codes are surfaced as `unknown:<n>` and treated as
non-fault (reported, not counted).

### Top-level `<status>` field

The per-node `<status>` element reads `Failed` in the sample even though every
process is `running` or `disabled`. It is therefore **unreliable as a verdict**.
It is surfaced verbatim as `reported_status` (informational — the "not used for
the verdict" framing lives in this spec and the field description, not in the
response payload) and does **not** drive any health conclusion.

## Design

### Data flow

```
DeploymentToolHandler.get_deployment_health(hostnames=None, diagnostics=False)
  → nodes  (Deployment OpenAPI, possibly hostname-filtered)      [unchanged]
  → if diagnostics:                                              [gated, opt-in]
      DeploymentDiagnosticsResolver.resolve(nodes, scoped)
       ├─ observations: node-status + PAN redundancy             [unchanged]
       └─ system_stats:
            async with mnt_gate.guard():                      # shared MnT admission control
              async with mnt_client.get_stream("dashboard/getSystemSummaryDetails") as resp:
                  spool resp.aiter_bytes() → SpooledTemporaryFile
                  parsed = await asyncio.to_thread(iter_parse_system_summary, buf)
            → SystemSummaryParser.build(parsed)  # services/… (new)
            → filter to hostnames present in `nodes`
```

### New components

1. **`iter_parse_system_summary(source)`** in `utils/xml_parser.py`
   - **Streaming** parse of `<dashboardResult>` via `ET.iterparse(source,
     events=("start","end"))` + `root.clear()` after each processed top-level
     child — the same memory-bounded idiom as `parse_msg_catalog` and
     `iter_filter_active_sessions`. Peak memory is proportional to one repeated
     element subtree, not the whole document.
   - `source` is anything `iterparse` accepts (the spooled temp-file object).
   - On `end` of `lstProcessStatuses` → extract child dict, append to
     `process_statuses`. On `end` of `lstSystemStatus60Min` → extract, append to
     `status_60min`. **`lstSystemStatus24Hr` is skipped entirely** (never
     materialized). `root.clear()` after each so the parsed subtree is freed.
   - Returns raw dicts: `{"process_statuses": [...], "status_60min": [...]}`
     — the exact shape `SystemSummaryParser.build` consumes.
   - Root-tag validation (`dashboardResult`, checked on the first `start`
     event); raises `ValueError` on wrong root, `ET.ParseError` on malformed
     XML — consistent with the other parsers.
   - Wrapped by the shared `MntGate` (see "Gate generalization" below):
     `getSystemSummaryDetails` is another heavy read against the same MnT node,
     so it shares the semaphore / min-interval floor / circuit breaker that
     protect that node from AuthList downloads.

2. **`services/system_summary_parser.py`** — `SystemSummaryParser`
   - Pure / no I/O. Maps process codes → states, builds the fault list,
     aggregates the 60-min CPU/mem/latency series per node to
     min/max/avg/latest (reuses the `_aggregate` shape).
   - `_PROCESS_CODE_MAP = {1: "running", 2: "disabled", -1: "not_applicable", 0: "down"}`.
   - Keyed by `<server>` (short hostname).

3. **Resolver wiring** (`DeploymentDiagnosticsResolver`)
   - Constructor takes the `mnt_client` (injected, like other MNT consumers).
     Drops the `SystemStatsParser` / `log_service` dependency.
   - Also takes the shared `mnt_gate` (injected, defaults to the `mnt_gate`
     singleton — same DI shape `SessionToolHandler` uses).
   - `resolve()` wraps the fetch in `async with self.gate.guard():`, streams the
     API via `mnt_client.get_stream(...)`, spools the body into a
     `SpooledTemporaryFile`, runs `iter_parse_system_summary` under
     `asyncio.to_thread` (the parse is synchronous/CPU-bound and may read a
     spilled temp file), builds `system_stats` via `SystemSummaryParser`, and
     filters rows to hostnames present in the handler's `nodes` list (respects
     the caller's hostname filter).
   - **A gate rejection is treated as a degrade, not a failure.** Diagnostics is
     opt-in enrichment on top of the base summary, so an `ISE_BUSY` from the gate
     folds into the same graceful `system_stats = {"status": "unavailable",
     "reason": <generic>}` block used for API/parse errors — the base summary
     still returns. The resolver never re-raises `ISE_BUSY`; the tool does not
     fail because the MnT node was under load.
   - Adds one observation per node with a non-empty `processes_down` list, e.g.
     `"vm218: process(es) not running: database (admin-guide: Process Down)"`.
   - `resolve()` is only reached when the handler was called with
     `diagnostics=True` (gating lives in the handler, not the resolver).

### Response shape (`DeploymentDiagnostics.system_stats`)

```json
{
  "source": "getSystemSummaryDetails",
  "duration_minutes": 60,
  "nodes": {
    "vm218": {
      "reported_status": "Failed",
      "processes_down": [],
      "processes": { "applicationServer": "running", "sxpEngine": "disabled", "...": "..." },
      "cpu_percent":    {"min": 3,  "max": 4,  "avg": 3.5, "latest": 3},
      "memory_percent": {"min": 57, "max": 57, "avg": 57,  "latest": 57},
      "latency":        {"min": 0,  "max": 0,  "avg": 0,   "latest": 0}
    }
  }
}
```

On any diagnostics-path failure,
`system_stats = {"status": "unavailable", "reason": "<reason>"}` — a distinct
retry-oriented reason for a gate rejection, one generic reason for everything
else (see **Error handling**; full detail logged server-side only).
`system_stats` remains `Optional[dict[str, Any]]` on the model — **no model
change required**.

### Removals

- **`SystemStatsParser` class** (`services/system_stats_parser.py`) and its test
  `tests/test_system_stats_parser.py` — removed. **The module is NOT deleted**:
  its `_parse_ts` helper is reused by `services/certificate_log_scanner.py`, so
  `_parse_ts` (and the timestamp regex/format it needs) stays.
- **`iseLocalStore` log fetch** and the 3-node sampling cap in the resolver —
  removed. `diagnostics=True` runs the new API path only; it never returns to
  log downloads. The flag is purely a gate, not a log-vs-API switch.

### Renamed / kept

- **`deep_diagnostics` parameter → `diagnostics`** on `get_deployment_health`.
  Same opt-in semantics (default `False`; base summary always returned), just a
  cleaner name. The tool description keeps opt-in language but replaces the
  "heavy log download" rationale with "the API response can be large in big
  deployments." When `diagnostics=False`, `diagnostics` is `None` in the result,
  exactly as today. The `DeploymentDiagnostics` model docstring (and the
  `system_stats` field description that says "log-derived") are updated to
  reference `diagnostics=True` and the API source — a docstring change only, not
  a schema change.
- **`deep-diagnostics-gating` memory** — **kept and updated**, not deleted. The
  flag still exists, so gating guidance stays relevant. Update it to reference
  `diagnostics=true` (not `deep_diagnostics`) and to reflect the lighter,
  single-API-call cost profile: still opt-in on problem-signaling wording, but
  the cost is one (possibly large) API call rather than per-node log downloads.

### Gate generalization (`AuthListGate` → `MntGate`)

`getSystemSummaryDetails` is another heavy read against the same MnT node as
AuthList. Its admission-control mechanics — semaphore, min-interval floor,
adaptive circuit breaker on 502/503/504 + timeouts — are already fully generic;
nothing in the logic is AuthList-specific. Rather than add a parallel gate, the
existing gate is renamed and shared by both consumers (one semaphore protects
the node across all heavy reads). **No back-compat env aliases** — this is a new,
pre-release surface, so the env vars are renamed outright.

Rename surface (clean break, no aliases):

- `clients/auth_list_gate.py` → `clients/mnt_gate.py`; class `AuthListGate` →
  `MntGate`; module singleton `auth_list_gate` → `mnt_gate`.
- Settings (`clients/settings.py`): `authlist_max_concurrency` →
  `mnt_gate_max_concurrency`, `authlist_min_interval_s` →
  `mnt_gate_min_interval_s`, `authlist_backoff_base_s` →
  `mnt_gate_backoff_base_s`, `authlist_backoff_max_s` → `mnt_gate_backoff_max_s`.
- Env var names: `ISE_AUTHLIST_MAX_CONCURRENCY` → `ISE_MNT_GATE_MAX_CONCURRENCY`,
  `ISE_AUTHLIST_MIN_INTERVAL_S` → `ISE_MNT_GATE_MIN_INTERVAL_S`,
  `ISE_AUTHLIST_BACKOFF_BASE_S` → `ISE_MNT_GATE_BACKOFF_BASE_S`,
  `ISE_AUTHLIST_BACKOFF_MAX_S` → `ISE_MNT_GATE_BACKOFF_MAX_S`. Update
  `.env.example` and the `README.md` env table.
- Consumers: `SessionToolHandler` imports/`gate=` default → `mnt_gate`;
  `DeploymentDiagnosticsResolver` gains the same `gate=mnt_gate` injection.
- The `ISE_BUSY` rejection copy ("The ISE session service is busy…") is
  generalized to "the ISE MnT node" since it now covers deployment diagnostics
  too.
- Tests: `tests/test_auth_list_gate.py` → `tests/test_mnt_gate.py` (class/
  singleton/settings references updated); `tests/test_settings_log_fields.py`
  and `tests/test_session_tools.py` env-var and attribute references updated.
- Docs: the `MCP_TOOLS_CATALOG.md` backpressure paragraph and the four
  "Heavy MnT call — gated to `ISE_AUTHLIST_MAX_CONCURRENCY`" lines are updated to
  the new env-var names; the `ise_deployment_health` section notes that
  `diagnostics=true` is a gated heavy MnT call subject to the same backpressure.

The behavioral contract of the gate is otherwise unchanged; this is a
rename-plus-second-consumer, not a logic change.

### Kept as-is

- `log_service` (still used by `certificate_diagnostics_resolver` and `server.py`).
- `services/system_stats_parser.py` module file (for `_parse_ts`).
- The resolver's observation logic for node status and PAN redundancy (the
  `scoped` handling for deployment-wide HA claims is unchanged).

## Documentation updates

Both the in-code tool description and the tools catalog carry `deep_diagnostics`
opt-in guidance and describe the old log-derived `system_stats` shape. Both must
be updated as first-class deliverables of this feature. The flag is **renamed,
not removed** — it stays opt-in — and the `system_stats` shape/source changes.

### Tool description — `server.py` (`ise_deployment_health`)

- **Rename the `deep_diagnostics` parameter to `diagnostics`** in the signature
  and its `Annotated[...]` description block (default `False`). Update the
  description to replace the "heavy per-node log download" rationale with
  "API-backed process health + CPU/memory/latency; opt-in because the API
  response can be large in big deployments and the call is gated for MnT-node
  backpressure."
- Rename the `deep_diagnostics=deep_diagnostics` argument to
  `diagnostics=diagnostics` in the `get_deployment_health(...)` call.
- Update the docstring's `Returns:` section: `diagnostics` is present **only when
  `diagnostics=True`** (process health + CPU/memory/latency per node, API-sourced,
  not log-derived), else `None`. Note `system_stats` may be an `unavailable`
  block on gate rejection or API/parse failure. Keep the existing topology /
  HA / node-status description intact.

### Catalog — `MCP_TOOLS_CATALOG.md` (`ise_deployment_health` section)

- **Intro line (~795):** change "with optional log-derived per-node system
  statistics" to opt-in, API-sourced process health + CPU/memory/latency
  (`diagnostics=true`).
- **Opt-in paragraph (~801):** keep, but rewrite — rename `deep_diagnostics` →
  `diagnostics`, drop the "heavy log download" framing, and state it is a gated
  heavy MnT call (may return an `unavailable` block / `ISE_BUSY`-style degrade
  under load).
- **Parameter table (~823):** rename the `deep_diagnostics` row to `diagnostics`
  (default `false`); update its description. `hostnames` unchanged.
- **`diagnostics` / `system_stats` return shape (~846–848):** rewrite to the new
  shape — present only when `diagnostics=true`; `system_stats` has
  `source: "getSystemSummaryDetails"`, `duration_minutes`, and `nodes` keyed by
  hostname, each node either `{reported_status, processes_down, processes,
  cpu_percent, memory_percent, latency}` (each metric a `{min, max, avg, latest}`
  object) or `{status: "unavailable", reason}`. Drop `disk_percent`, `anchor`,
  `sample_count`, `window`.
- **"Use when" bullet (~856):** rename the `(with deep_diagnostics=true)`
  qualifier to `(with diagnostics=true)`.
- **Best-practices bullet (~868):** rewrite the "keep `deep_diagnostics=false`"
  line to reference `diagnostics` and the new (lighter, but still gated) cost
  profile — set `diagnostics=true` on problem-signaling wording.
- **Quick-reference row (~987):** rename the `(deep_diagnostics=true)` qualifier
  to `(diagnostics=true)` in the "Investigate why a node is disconnected / not
  syncing" row.
- **Backpressure references:** update the `ISE_AUTHLIST_*` env-var names to the
  new `ISE_MNT_GATE_*` names wherever they appear (the backpressure paragraph and
  the four "Heavy MnT call" lines), and note that `ise_deployment_health` with
  `diagnostics=true` is now also gated by the shared MnT gate.
- Optionally add "Which ISE processes are down on a node?" to the
  "Questions this tool answers" list, since process health is returned when
  `diagnostics=true`.

## Error handling

Every diagnostics-path failure degrades to
`system_stats = {"status": "unavailable", "reason": <reason>}` and the base
summary still returns. There are exactly **two** reason strings (module-level
constants, never interpolated from exception text, so no status code / URL /
host can leak):

- **Gate rejection** (`ISE_BUSY` — semaphore full, min-interval, breaker open):
  a distinct, retry-oriented reason, e.g.
  `"diagnostics skipped: the ISE MnT node is busy or under load; retry shortly"`.
  The gate rejection is caught inside `resolve()` and mapped to this reason — it
  is **not** re-raised as `ISE_BUSY` (diagnostics degrade, they don't fail the
  tool).
- **Everything else** (unreachable, timeout, HTTP/auth error, malformed XML /
  wrong root / parse error, no usable rows): one generic reason, e.g.
  `"diagnostics unavailable; no system-summary data could be retrieved"`.

| Failure | Behavior |
|---------|----------|
| Gate rejection (`ISE_BUSY`) | Caught, mapped to the busy reason. Base summary still returns. |
| Auth / HTTP / unreachable / timeout | Catch, log full detail server-side, generic reason. Base summary still returns. |
| Malformed XML / wrong root / no rows | Same graceful degradation, generic reason. |
| Node in API but not in `nodes` list | Excluded (scope respects the hostname filter). |
| Node in `nodes` but absent from API | No stats entry for it; not an error. |

Full detail (status code, URL, host) is logged server-side only — mirrors the
current per-node isolation posture.

## Testing (TDD — tests first)

- **`tests/test_system_summary_parser.py`**
  - Code → state mapping for all of `1 / 2 / -1 / 0` and an unknown code.
  - `processes_down` contains only code-`0` fields.
  - 60-min aggregation (min/max/avg/latest); empty/missing series handled.
  - `reported_status` surfaced verbatim (e.g. `"Failed"`).
  - Correlation fixture built from the real captured XML.
- **`utils/xml_parser.py` tests** for `iter_parse_system_summary` — streaming
  parse over a file-like source, malformed XML (`ET.ParseError`), wrong root
  (`ValueError`), missing lists, and confirmation that `lstSystemStatus24Hr` is
  skipped.
- **Resolver tests** (`tests/test_deployment_diagnostics_resolver.py`, updated)
  - Hostname filtering (only `nodes` rows reported).
  - Graceful degradation on API/parse error → `unavailable` block with the
    **generic** reason, base summary intact.
  - **Gate rejection** (`ISE_BUSY` from an injected gate) → `unavailable` block
    with the **busy/retry** reason; the tool does **not** raise, base summary
    intact.
  - Fetch is wrapped in the injected gate's `guard()` (assert the gate is
    entered).
  - Observation generated for a node with a down process.
- **Handler test** — `diagnostics=False` (default) → `diagnostics is None`, no
  API call; `diagnostics=True` → resolver invoked, diagnostics present.
- **Gate tests** — `tests/test_auth_list_gate.py` → `tests/test_mnt_gate.py`,
  updated for `MntGate` / `mnt_gate` / `mnt_gate_*` settings. Behavior assertions
  unchanged (rename only).
- **Settings tests** — `tests/test_settings_log_fields.py` updated for the
  `ISE_MNT_GATE_*` env vars and `mnt_gate_*` attributes.
- **Session-tool tests** — `tests/test_session_tools.py` references to
  `AuthListGate` / `auth_list_gate` / `ISE_AUTHLIST_*` updated to the new names.
- **Docs check** — `test_server.py` and any catalog-consistency test updated so
  no test references `deep_diagnostics`, `disk_percent`, `anchor`/`sample_count`,
  or the old `ISE_AUTHLIST_*` names for this tool; the catalog references
  `diagnostics` and `ISE_MNT_GATE_*`.

## Open questions

None. Process-code semantics, `<status>` handling, window choice, scope, and
failure behavior are all resolved. The 2026-07-23 amendments are decided:
streaming read (not buffered), `deep_diagnostics` renamed to `diagnostics` and
**kept** as an opt-in gate (default `False`), the gate generalized to a shared
`MntGate` (env vars renamed to `ISE_MNT_GATE_*`, no back-compat aliases), and a
gate rejection **degrades** to an `unavailable` `system_stats` block with a
distinct retry-oriented reason rather than failing the tool.
