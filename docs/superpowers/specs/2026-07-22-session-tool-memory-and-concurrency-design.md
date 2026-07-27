# Session-Tool Memory & Concurrency Hardening — Design

**Date:** 2026-07-22
**Status:** Approved (design), pending implementation plan
**Scope:** Issues #1 (memory) and #2 (concurrency/backpressure) from the SST test-report feedback.

## Background

SST testing of the ISE MCP server against a 54-node deployment (~1.7M sessions in a
6-hour window) surfaced two distinct failure modes in the four **AuthList-based
session tools** (`active_sessions_search`, `sessions_search_with_advanced_details`,
`sessions_search_with_policy_details`, `sessions_search_with_latency_details`):

- **Run 1 — ghost-task cascade / VM crash.** MCP clients (Cursor) time out at ~21s,
  but the server keeps processing. Concurrent AuthList calls each loaded the full
  session set into memory (4–7 GB each), piling up until the VM's RAM was exhausted
  and it froze for 8–10 minutes.
- **Run 2 — ISE MnT overload (HTTP 502).** Even fully *sequential* AuthList calls,
  issued rapidly (5+ in a row), overwhelmed the ISE Primary MnT node itself. PMNT
  returned HTTP 502 and became unresponsive for ~10 minutes.

Both were confirmed against the source code and against the authoritative Confluence
test report (`SECPOL/2483191889`, "ISE MCP Test Reports").

Root causes (code-verified):

1. **Memory.** `SessionToolHandler._fetch_auth_list_sessions` calls
   `parse_active_session_xml(response.text)`, which does `ET.fromstring()` on the
   entire XML string, producing four full in-memory copies at peak: the raw XML
   string, the ElementTree DOM, the list of dicts, and ~1.7M `ActiveSession`
   Pydantic models. Client-side filtering (`_filter_sessions`) runs only *after*
   all of that exists, so filtering to a handful of matches does not reduce the peak.
2. **Concurrency.** There is no concurrency control anywhere in `mnt_client.py` or
   the handlers — no semaphore, no inter-call gate. Nothing bounds parallel or
   rapid-sequential AuthList downloads.

There is already a proven streaming idiom in this repo: `parse_msg_catalog`
(`utils/xml_parser.py`) uses `ET.iterparse` + `root.clear()` to keep peak memory
proportional to a single subtree rather than the whole document. This design applies
the same idiom to the AuthList path.

## Goals

- Reduce peak memory of AuthList calls from gigabytes to a bounded, small footprint —
  filtered or unfiltered.
- Prevent the ghost-task RAM pile-up under concurrent load.
- Prevent / gracefully ride out ISE MnT overload under rapid sequential load.
- Keep all four session tools' return shapes and filtering results identical.
- Make the concurrency behavior operator-configurable, with conservative defaults
  safe for large deployments.

## Non-goals (explicit follow-ups, not designed here)

- **Issue #3 — log-download redesign.** Product/design decision pending discussion
  with Laxmi (pre-staging requirement, users not knowing which logs to fetch). Noted
  in docs as a follow-up; no code here.
- **Issue #4 — `mac_address` vs `calling_station_id` param rename** on
  `ise_investigate_aaa_failure`. Trivial rename, tracked separately.
- **`ise_deployment_health(deep_diagnostics=true)` node-selection bug** — when only
  1 of N nodes is unhealthy, the tool checks only that node instead of topping up the
  remaining slots (up to 3) with healthy nodes. Plus the broader "no visibility into
  which nodes are targeted / doesn't cover all nodes" concern. Isolated from #1/#2;
  tracked with the #3 log/diagnostics discussion.

---

## Section 1 — Streaming filter-parse for AuthList (memory)

### Current flow (build everything, then filter)

```
_fetch_auth_list_sessions:
    response = await mnt_client.get(endpoint)          # full XML string in memory
    parsed   = parse_active_session_xml(response.text) # DOM + list of 1.7M dicts
    return ActiveSessionList(**parsed).sessions        # 1.7M Pydantic models

search_active_sessions:
    all_sessions = await _fetch_auth_list_sessions(...) # all 1.7M held
    filtered, _  = _filter_sessions(all_sessions, ...)  # discard non-matches AFTER
```

The 4–7 GB peak occurs before `_filter_sessions` ever runs.

### New flow (filter as you parse, retain a bounded sample)

Two observations make this bounded in *all* cases:

1. When a filter is set, we only need the matches.
2. Even with no filter, every session tool returns only a bounded **sample**
   (`limit`, max 20) plus a `total_matching_sessions` **count**. We never need to
   hold more than a small retention cap; the rest are counted and dropped.

**New parser** in `utils/xml_parser.py`:

```python
def iter_filter_active_sessions(byte_stream, predicate, retention_cap) -> tuple[list[dict], int]:
    total_matched = 0
    retained = []                               # never grows past retention_cap
    context = ET.iterparse(byte_stream, events=("end",))
    _, root = next(context)
    for _, elem in context:
        if elem.tag != "activeSession":
            continue
        s = {child.tag: (child.text.strip() if child.text and child.text.strip() else None)
             for child in elem}
        if predicate(s):
            total_matched += 1
            if len(retained) < retention_cap:
                retained.append(s)
        root.clear()                            # free the parsed subtree immediately
    return retained, total_matched
```

Peak memory ≈ `retention_cap` dicts, not 1.7M.

**Predicate builder** — the existing `_filter_sessions` comparisons, packaged as a
callable so they run per-session during the parse:

```python
def _build_session_predicate(username, calling_station_id, nas_ip_address,
                             framed_ip_address, server):
    def predicate(s: dict) -> bool:
        if username and s.get("user_name") != username:
            return False
        if calling_station_id and normalize_mac_address(s.get("calling_station_id") or "") != calling_station_id:
            return False
        if nas_ip_address and s.get("nas_ip_address") != nas_ip_address:
            return False
        if framed_ip_address and s.get("framed_ip_address") != framed_ip_address:
            return False
        if server and s.get("server") != server:
            return False
        return True
    return predicate
```

With no filters set, the predicate returns `True` for all — matching current behavior.

**Streaming client method** on `MNTClient` (e.g. `get_stream`) that yields response
bytes via `client.stream("GET", ...)`, reusing the exact auth / URL / FQDN-discovery
path as `get()`.

**Rewritten fetch** takes normalized filters + a retention cap, returns
`(sessions, total_matched)`:

```python
async def _fetch_auth_list_sessions(self, filters, retention_cap, minutes=1440):
    predicate = _build_session_predicate(**filters)
    async with self.mnt_client.get_stream(endpoint) as byte_stream:
        retained, total = iter_filter_active_sessions(byte_stream, predicate, retention_cap)
    sessions = [ActiveSession(**d) for d in retained]   # models built for the handful only
    return sessions, total
```

### Caller changes

- `search_active_sessions` — `retention_cap = limit`. Uses the returned `total_matched`
  directly as `total_matching_sessions`. The post-parse `_filter_sessions` call is
  removed from this path; its logic now lives in the predicate.
- `search_enriched_active_sessions` — `retention_cap = ENRICHMENT_CAP (100)` when a
  latency filter is active, else `limit`. The **latency filter stays post-enrichment**
  (`_filter_sessions_by_latency`): it needs `response_time_ms` from a *second* per-session
  API call, so it cannot move into the AuthList predicate. Only the five AuthList-level
  filters move into the predicate.

`_filter_sessions` is no longer called on the AuthList path. Return models
(`ActiveSessionSearchResult`, `EnrichedSessionSearchResult`) are unchanged.

---

## Section 2 — Concurrency limiter + adaptive circuit breaker (backpressure)

**Module:** `clients/auth_list_gate.py` — a shared async guard applied *inside*
`_fetch_auth_list_sessions`, so all four session tools inherit it and it cannot be
bypassed by a future tool that calls the fetch.

### Mechanism 1 — Semaphore, reject-immediately

- `asyncio.Semaphore(N)`, default `N = 1`.
- If no slot is free when a call arrives → raise `ISE_BUSY` **immediately**
  (`retry=True`, message: "another large session query is running, retry shortly").
  **No wait.** Given each download is 60–75s, any short queue-wait would end in an
  inevitable rejection anyway, so we skip it and never hang the client.
- The slot is held across the entire download+parse and released in a `finally`, so a
  ghost task (client already disconnected) still releases its slot cleanly. Combined
  with Section 1, a ghost task now costs kilobytes, not gigabytes.
- Addresses the Run-1 parallel pile-up.

### Mechanism 2 — Proactive min-interval floor

SST's RUN2 passed specifically because they inserted a manual delay between AuthList
calls to avoid loading the MnT node with back-to-back large downloads. This mechanism
makes that honorable *and* automatic: a configurable minimum interval between the
*start* of consecutive AuthList downloads.

- Enforced inside the gate: before starting a download, if less than
  `ISE_AUTHLIST_MIN_INTERVAL_S` has elapsed since the previous download started, the
  call **rejects fast** with `ISE_BUSY` (it does not sleep/hang the client — a 60–75s
  download means any wait would blow the ~21s client timeout anyway).
- **Default `0.0` (off).** With the semaphore at 1 and Section 1's prompt memory
  release, the healthy path needs no forced delay; operators on very large MnT nodes
  can raise it (e.g. 5–120s) to proactively space downloads.
- Complements the breaker: the floor *prevents* the first overload proactively; the
  breaker *reacts* to distress once it occurs.

### Mechanism 3 — Adaptive circuit breaker

Catches the Run-2 rapid-sequential MnT overload, which the semaphore cannot (those
calls are sequential, not parallel), and any residual overload the floor doesn't
prevent.

- **Closed (healthy):** cooldown 0 — no latency penalty in the normal case.
- **Opens** on an MnT distress signal observed from the download: HTTP 502 / 503 / 504,
  or connect/read timeout. The open window doubles per consecutive failure —
  `base → 2×base → … → max`, with jitter.
- **While open:** all AuthList calls reject-fast with `ISE_BUSY`. No caller waits.
- **Half-open** after the window expires: exactly one probe call is allowed through.
  - Probe **fails** → re-open for another window (capped at `max`).
  - Probe **succeeds** → reset to closed; normal service resumes.
- **Prolonged outage (> max window):** the breaker never permanently locks out. It
  keeps rejecting fast and allows at most **one probe per `max` window** (e.g. one
  60–75s probe per 300s) until a probe succeeds, then self-heals. No manual
  intervention.
- The breaker is **global** (per-process), not per-slot — MnT distress is a node-level
  condition.

### Interaction with `N > 1`

Raising `ISE_AUTHLIST_MAX_CONCURRENCY` to 2 permits two parallel downloads. This is
only safe *because* Section 1 makes per-download memory small (peak ≈ N × small).
MnT load scales with N; the global breaker remains the backstop against sustained
pressure regardless of N. Default stays at **1** (conservative for large deployments).

### Settings (`clients/settings.py`, env-configurable)

| Setting | Env var | Default |
|---|---|---|
| Max concurrent AuthList downloads | `ISE_AUTHLIST_MAX_CONCURRENCY` | `1` |
| Min interval between AuthList downloads (s) | `ISE_AUTHLIST_MIN_INTERVAL_S` | `0.0` (off) |
| Breaker base backoff (s) | `ISE_AUTHLIST_BACKOFF_BASE_S` | `5.0` |
| Breaker max backoff (s) | `ISE_AUTHLIST_BACKOFF_MAX_S` | `300.0` |

---

## Section 3 — Documentation

Update `MCP_TOOLS_CATALOG.md` and/or `README.md`:

- **Resource profile of the 4 session tools.** Each AuthList call downloads all
  sessions in the window. Document the ISE MnT load and — *after* the Section 1 fix —
  the bounded MCP memory footprint (no longer 4–7 GB). Note that larger `limit` /
  `minutes` raise MnT cost.
- **Backpressure behavior.** `ISE_BUSY` is an expected response under concurrent load
  or MnT distress; clients should retry with their own backoff. Document all four
  env knobs (concurrency, min-interval floor, breaker base/max), including SST's
  recommendation to space large AuthList calls on very large deployments.
- **Guidance.** Prefer narrow filters. `ise_investigate_aaa_failure` is the
  lightweight path for failure lookups (bounded, no full download).
- **Follow-ups.** Note issues #3 (log handling) and #4 (param rename) as tracked
  separately.

---

## Error surface

A new tool error code `ISE_BUSY` (category `EXTERNAL_ERROR`, `retry=True`) is raised by
the gate for both the semaphore-full and breaker-open cases. Existing `ISE_UNREACHABLE`
/ `ISE_API_ERROR` handling in the handlers' `_handle_mnt_errors` is unchanged; the
breaker observes those same underlying `httpx` errors to decide when to open.

## Testing

- **Streaming parser** — unit tests over a synthetic multi-session XML fixture:
  filter match/no-match, retention cap enforced, `total_matched` accurate beyond the
  cap, empty result, malformed XML.
- **Predicate builder** — parity with the old `_filter_sessions` for each of the five
  filters and combinations, including MAC normalization.
- **Gate** — semaphore rejects immediately when full; min-interval floor rejects fast
  when a call arrives too soon after the previous download start (and is a no-op at the
  default 0); breaker opens on 502/timeout, grows/caps the window, rejects while open,
  probes half-open, resets on success.
- **Handler integration** — the four session tools return unchanged shapes; enriched
  latency filter still applied post-enrichment.

## Rollout / risk

- Section 1 must land before any `N > 1` is used.
- Defaults (`N=1`, breaker base 5s / max 300s) are conservative and match the tested
  large-deployment profile.
- No change to tool schemas, parameter names, or result models — client-transparent
  except for the new `ISE_BUSY` retryable error under load.
