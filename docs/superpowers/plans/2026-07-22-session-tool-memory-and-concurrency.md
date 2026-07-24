# Session-Tool Memory & Concurrency Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bound the memory of the four AuthList-based session tools and gate their concurrency so the MCP server no longer crashes under parallel load or overloads the ISE MnT node under rapid sequential load.

**Architecture:** (1) Replace the "download-all → parse-all → filter" AuthList path with a streaming `iterparse` filter that retains only a bounded sample plus a running match count. (2) Wrap every AuthList download in a shared `AuthListGate` — a semaphore (default 1, reject-immediately), a configurable proactive min-interval floor (default 0 = off), and an adaptive circuit breaker that opens on MnT distress (HTTP 502/503/504, timeouts) and self-heals via half-open probes.

**Tech Stack:** Python 3, `asyncio`, `httpx` (async streaming), `defusedxml.ElementTree`, Pydantic v2, `pytest` + `pytest-asyncio`. Run everything via `uv run`.

## Global Constraints

- **Python runner:** all test/lint commands run via `uv run` (e.g. `uv run pytest ...`), never bare `pytest`/`python`.
- **License header:** every new `.py` file starts with the exact three-line header:
  ```
  # Copyright 2026 Cisco Systems, Inc. and its affiliates
  #
  # SPDX-License-Identifier: Apache-2.0
  ```
- **XML parsing:** use `defusedxml.ElementTree` (imported as `ET`), never stdlib `xml.etree` directly — matches existing `utils/xml_parser.py`.
- **Errors:** raise tool errors via `raise_tool_error(ErrorCategory.<X>, "<CODE>", "<msg>", retry=<bool>)` from `models.error_models`. The new backpressure code is `ISE_BUSY`, category `EXTERNAL_ERROR`, `retry=True`.
- **Settings:** new tunables are Pydantic fields on `ISESettings` in `clients/settings.py`, read from env with the documented defaults. Empty-string env values must fall back to the default (add each new numeric field to the existing `_empty_str_to_default` validator list).
- **Defaults (verbatim):** `ISE_AUTHLIST_MAX_CONCURRENCY=1`, `ISE_AUTHLIST_MIN_INTERVAL_S=0.0`, `ISE_AUTHLIST_BACKOFF_BASE_S=5.0`, `ISE_AUTHLIST_BACKOFF_MAX_S=300.0`.
- **No behavior change to return shapes:** `ActiveSessionSearchResult`, `EnrichedSessionSearchResult`, and the policy/latency result models are unchanged. Filtering results must be identical to today's `_filter_sessions`.
- **Spec:** `docs/superpowers/specs/2026-07-22-session-tool-memory-and-concurrency-design.md`.

---

## File Structure

- **Create** `clients/auth_list_gate.py` — `AuthListGate` class (semaphore + min-interval floor + adaptive breaker) and a `guard()` async context manager. One responsibility: admission control for AuthList downloads.
- **Create** `tests/test_auth_list_gate.py` — unit tests for the gate (injected clock, no real time/sleep).
- **Modify** `clients/settings.py` — add four tunable fields + extend `_empty_str_to_default`.
- **Modify** `utils/xml_parser.py` — add `iter_filter_active_sessions(source, predicate, retention_cap)`.
- **Modify** `tools/session_tool_handler.py` — add `_build_session_predicate`, rewrite `_fetch_auth_list_sessions` to stream+filter through the gate, update the two search methods; remove the AuthList use of `_filter_sessions`.
- **Modify** `clients/mnt_client.py` — add `get_stream(endpoint)` async context manager.
- **Modify** `tests/test_session_tools.py` — update `_fetch_auth_list_sessions` tests for the new signature/stream path; add filter-parity tests.
- **Modify** `tests/test_mnt_client.py` — add a `get_stream` test.
- **Modify** `tests/test_settings_log_fields.py` (or nearest settings test) — assert the new defaults.
- **Modify** `README.md` and `MCP_TOOLS_CATALOG.md` — operations/backpressure docs.

Task order is dependency-driven: settings → pure parser/predicate → streaming client → gate → integration → docs. Tasks 1–4 are independent and testable in isolation; Task 5 wires them together.

---

## Task 1: Settings tunables

**Files:**
- Modify: `clients/settings.py`
- Test: `tests/test_settings_log_fields.py`

**Interfaces:**
- Produces: `settings.authlist_max_concurrency: int`, `settings.authlist_min_interval_s: float`, `settings.authlist_backoff_base_s: float`, `settings.authlist_backoff_max_s: float`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_settings_log_fields.py`:

```python
def test_authlist_gate_defaults(monkeypatch):
    # Ensure a clean env so defaults apply.
    for var in (
        "ISE_AUTHLIST_MAX_CONCURRENCY",
        "ISE_AUTHLIST_MIN_INTERVAL_S",
        "ISE_AUTHLIST_BACKOFF_BASE_S",
        "ISE_AUTHLIST_BACKOFF_MAX_S",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("ISE_IP", "192.0.2.1")

    from clients.settings import ISESettings

    s = ISESettings()
    assert s.authlist_max_concurrency == 1
    assert s.authlist_min_interval_s == 0.0
    assert s.authlist_backoff_base_s == 5.0
    assert s.authlist_backoff_max_s == 300.0


def test_authlist_empty_env_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("ISE_IP", "192.0.2.1")
    monkeypatch.setenv("ISE_AUTHLIST_MAX_CONCURRENCY", "")
    monkeypatch.setenv("ISE_AUTHLIST_MIN_INTERVAL_S", "")

    from clients.settings import ISESettings

    s = ISESettings()
    assert s.authlist_max_concurrency == 1
    assert s.authlist_min_interval_s == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_settings_log_fields.py::test_authlist_gate_defaults -v`
Expected: FAIL — `AttributeError: 'ISESettings' object has no attribute 'authlist_max_concurrency'`.

- [ ] **Step 3: Add the fields**

In `clients/settings.py`, after the `pool_timeout_s` field block (around line 71), add:

```python
    # --- AuthList concurrency / backpressure gate --------------------
    # Max full-AuthList downloads allowed to run at once. Default 1
    # serialises the heavy session tools so concurrent calls cannot pile
    # up in memory (the Run-1 crash). Raise only with headroom.
    authlist_max_concurrency: int = Field(
        default=1, ge=1, le=16, validation_alias="ISE_AUTHLIST_MAX_CONCURRENCY"
    )
    # Minimum seconds between the START of consecutive AuthList downloads.
    # Proactively spaces large MnT downloads (SST's manual-delay finding).
    # Default 0.0 = off; a call arriving sooner rejects fast with ISE_BUSY.
    authlist_min_interval_s: float = Field(
        default=0.0, ge=0.0, validation_alias="ISE_AUTHLIST_MIN_INTERVAL_S"
    )
    # Adaptive breaker base backoff (seconds). The open window doubles per
    # consecutive MnT distress signal, starting from this value.
    authlist_backoff_base_s: float = Field(
        default=5.0, gt=0.0, validation_alias="ISE_AUTHLIST_BACKOFF_BASE_S"
    )
    # Adaptive breaker max backoff (seconds); caps the doubling window.
    authlist_backoff_max_s: float = Field(
        default=300.0, gt=0.0, validation_alias="ISE_AUTHLIST_BACKOFF_MAX_S"
    )
```

Then extend the `_empty_str_to_default` validator's field list (around line 55) to include the new numeric fields:

```python
    @field_validator(
        "api_port", "api_username", "api_pwd",
        "ise_admin_session_cookie", "log_cache_ttl_s", "log_cache_dir_prefix",
        "ise_client_cert", "ise_client_key", "ise_client_key_password",
        "ise_ca_bundle",
        "authlist_max_concurrency", "authlist_min_interval_s",
        "authlist_backoff_base_s", "authlist_backoff_max_s",
        mode="before",
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_settings_log_fields.py -v`
Expected: PASS (both new tests).

- [ ] **Step 5: Commit**

```bash
git add clients/settings.py tests/test_settings_log_fields.py
git commit -m "feat(settings): add AuthList concurrency/backpressure tunables"
```

---

## Task 2: Streaming filter-parse + predicate builder

**Files:**
- Modify: `utils/xml_parser.py`
- Modify: `tools/session_tool_handler.py` (add `_build_session_predicate` only; the fetch rewrite is Task 5)
- Test: `tests/test_session_tools.py`

**Interfaces:**
- Produces: `iter_filter_active_sessions(source, predicate: Callable[[dict], bool], retention_cap: int) -> tuple[list[dict], int]` in `utils/xml_parser.py`. `source` is anything `ET.iterparse` accepts (file object or path). Returns `(retained_dicts, total_matched)` where `len(retained_dicts) <= retention_cap` and `total_matched` counts every match regardless of cap.
- Produces: `SessionToolHandler._build_session_predicate(username, calling_station_id, nas_ip_address, framed_ip_address, server) -> Callable[[dict], bool]` (staticmethod). Filter values must already be validated/normalized by the caller.

- [ ] **Step 1: Write the failing tests**

Add a new test class to `tests/test_session_tools.py`:

```python
import io


class TestIterFilterActiveSessions:
    """Streaming, memory-bounded AuthList parse + filter."""

    XML = """<?xml version="1.0"?>
    <activeList noOfActiveSession="3">
        <activeSession>
            <user_name>alice</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:01</calling_station_id>
            <nas_ip_address>10.0.0.1</nas_ip_address>
            <server>ise-1</server>
        </activeSession>
        <activeSession>
            <user_name>bob</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:02</calling_station_id>
            <nas_ip_address>10.0.0.1</nas_ip_address>
            <server>ise-2</server>
        </activeSession>
        <activeSession>
            <user_name>alice</user_name>
            <calling_station_id>AA:BB:CC:DD:EE:03</calling_station_id>
            <nas_ip_address>10.0.0.2</nas_ip_address>
            <server>ise-1</server>
        </activeSession>
    </activeList>"""

    def _src(self):
        return io.BytesIO(self.XML.encode("utf-8"))

    def test_no_filter_retains_up_to_cap_and_counts_all(self):
        from utils.xml_parser import iter_filter_active_sessions

        retained, total = iter_filter_active_sessions(self._src(), lambda s: True, retention_cap=2)
        assert total == 3
        assert len(retained) == 2
        assert retained[0]["user_name"] == "alice"

    def test_predicate_filters_and_counts_matches(self):
        from utils.xml_parser import iter_filter_active_sessions

        pred = lambda s: s.get("user_name") == "alice"
        retained, total = iter_filter_active_sessions(self._src(), pred, retention_cap=10)
        assert total == 2
        assert len(retained) == 2
        assert all(s["user_name"] == "alice" for s in retained)

    def test_cap_zero_counts_but_retains_nothing(self):
        from utils.xml_parser import iter_filter_active_sessions

        retained, total = iter_filter_active_sessions(self._src(), lambda s: True, retention_cap=0)
        assert total == 3
        assert retained == []

    def test_empty_list(self):
        from utils.xml_parser import iter_filter_active_sessions

        src = io.BytesIO(b'<?xml version="1.0"?><activeList noOfActiveSession="0"></activeList>')
        retained, total = iter_filter_active_sessions(src, lambda s: True, retention_cap=5)
        assert total == 0
        assert retained == []

    def test_empty_child_text_becomes_none(self):
        from utils.xml_parser import iter_filter_active_sessions

        src = io.BytesIO(
            b'<?xml version="1.0"?><activeList noOfActiveSession="1">'
            b"<activeSession><user_name>x</user_name><framed_ipv6_address/></activeSession>"
            b"</activeList>"
        )
        retained, total = iter_filter_active_sessions(src, lambda s: True, retention_cap=5)
        assert total == 1
        assert retained[0]["user_name"] == "x"
        assert retained[0]["framed_ipv6_address"] is None


class TestBuildSessionPredicate:
    """Parity between the streaming predicate and legacy _filter_sessions."""

    def _handler(self):
        from unittest.mock import AsyncMock
        from tools.session_tool_handler import SessionToolHandler
        return SessionToolHandler(AsyncMock())

    def test_no_filters_matches_all(self):
        pred = self._handler()._build_session_predicate(None, None, None, None, None)
        assert pred({"user_name": "anyone"}) is True

    def test_username_exact_match(self):
        pred = self._handler()._build_session_predicate("alice", None, None, None, None)
        assert pred({"user_name": "alice"}) is True
        assert pred({"user_name": "alicia"}) is False
        assert pred({"user_name": None}) is False

    def test_mac_normalized_match(self):
        # Predicate receives an already-normalized filter value; session MAC
        # comes raw from XML and must be normalized before comparison.
        pred = self._handler()._build_session_predicate(None, "AA:BB:CC:DD:EE:01", None, None, None)
        assert pred({"calling_station_id": "aa-bb-cc-dd-ee-01"}) is True
        assert pred({"calling_station_id": "AA:BB:CC:DD:EE:99"}) is False

    def test_multiple_filters_are_anded(self):
        pred = self._handler()._build_session_predicate("alice", None, "10.0.0.2", None, "ise-1")
        assert pred({"user_name": "alice", "nas_ip_address": "10.0.0.2", "server": "ise-1"}) is True
        assert pred({"user_name": "alice", "nas_ip_address": "10.0.0.1", "server": "ise-1"}) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_session_tools.py::TestIterFilterActiveSessions tests/test_session_tools.py::TestBuildSessionPredicate -v`
Expected: FAIL — `ImportError`/`AttributeError` (functions not defined).

- [ ] **Step 3: Implement `iter_filter_active_sessions`**

In `utils/xml_parser.py`, add near the top the import and, after `parse_active_session_xml`, the new function:

```python
from typing import Callable, Tuple
```

```python
def iter_filter_active_sessions(
    source,
    predicate: Callable[[Dict[str, Any]], bool],
    retention_cap: int,
) -> Tuple[List[Dict[str, Any]], int]:
    """Stream-parse an ActiveList XML source, filtering as we go.

    Uses ``ET.iterparse`` + ``root.clear()`` (the same idiom as
    ``parse_msg_catalog``) so peak memory is proportional to a single
    ``<activeSession>`` subtree plus the retained sample -- NOT the whole
    document. Applies *predicate* to each session dict; every match
    increments the returned total, but only the first *retention_cap*
    matches are kept in the returned list.

    Args:
        source: Anything ``ET.iterparse`` accepts (file object or path).
        predicate: Called with one session dict; True keeps the session.
        retention_cap: Max sessions to retain in the returned list (>= 0).

    Returns:
        (retained_sessions, total_matched).
    """
    total_matched = 0
    retained: List[Dict[str, Any]] = []
    context = ET.iterparse(source, events=("end",))
    _, root = next(context)
    for _, elem in context:
        if elem.tag != "activeSession":
            continue
        session_data: Dict[str, Any] = {}
        for child in elem:
            value = child.text if child.text and child.text.strip() else None
            session_data[child.tag] = value
        if predicate(session_data):
            total_matched += 1
            if len(retained) < retention_cap:
                retained.append(session_data)
        root.clear()
    logger.debug("Streamed active sessions", total_matched=total_matched, retained=len(retained))
    return retained, total_matched
```

Note: `defusedxml.ElementTree.iterparse` returns the same `(event, elem)` iterator as stdlib and supports `next(context)` to grab the root — confirm the `_, root = next(context)` line works against the installed defusedxml (it mirrors `parse_msg_catalog`, which already relies on this).

- [ ] **Step 4: Implement `_build_session_predicate`**

In `tools/session_tool_handler.py`, add this staticmethod to `SessionToolHandler` (place it just above `_filter_sessions`):

```python
    @staticmethod
    def _build_session_predicate(
        username: Optional[str] = None,
        calling_station_id: Optional[str] = None,
        nas_ip_address: Optional[str] = None,
        framed_ip_address: Optional[str] = None,
        server: Optional[str] = None,
    ):
        """Build a per-session predicate mirroring _filter_sessions.

        Filter values must be pre-validated and normalized by the caller
        (calling_station_id already normalized via validate_mac_address).
        The session's own MAC is normalized here before comparison.
        """
        def predicate(s: dict) -> bool:
            if username and s.get("user_name") != username:
                return False
            if calling_station_id:
                raw = s.get("calling_station_id")
                if not raw or normalize_mac_address(raw) != calling_station_id:
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

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_session_tools.py::TestIterFilterActiveSessions tests/test_session_tools.py::TestBuildSessionPredicate -v`
Expected: PASS (all).

- [ ] **Step 6: Commit**

```bash
git add utils/xml_parser.py tools/session_tool_handler.py tests/test_session_tools.py
git commit -m "feat(sessions): streaming AuthList filter-parse + predicate builder"
```

---

## Task 3: `MNTClient.get_stream`

**Files:**
- Modify: `clients/mnt_client.py`
- Test: `tests/test_mnt_client.py`

**Interfaces:**
- Produces: `MNTClient.get_stream(endpoint: str)` — an `@asynccontextmanager` that yields a live streaming `httpx.Response`. It runs FQDN discovery, validates the endpoint/URL, resolves per-call auth (same as `get()`), opens `client.stream("GET", url, ...)`, calls `response.raise_for_status()` (headers are available before the body is read), then yields the response. Callers read the body via `response.aiter_bytes()`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_mnt_client.py` (follow the file's existing setup for building an `MNTClient` with a mocked async client; mirror whatever fixture the other tests use):

```python
@pytest.mark.asyncio
async def test_get_stream_yields_streaming_response(monkeypatch):
    import contextlib
    from clients.mnt_client import MNTClient

    client = MNTClient()

    # Skip discovery so the test targets streaming only.
    async def _no_discovery():
        client._discovery_succeeded = True
    monkeypatch.setattr(client, "_ensure_mnt_target", _no_discovery)

    chunks = [b"<activeList>", b"</activeList>"]

    class FakeResponse:
        status_code = 200
        def raise_for_status(self):
            return None
        async def aiter_bytes(self):
            for c in chunks:
                yield c

    @contextlib.asynccontextmanager
    async def fake_stream(method, url, **kwargs):
        assert method == "GET"
        yield FakeResponse()

    fake_client = type("C", (), {})()
    fake_client.is_closed = False
    fake_client.stream = fake_stream
    monkeypatch.setattr(client, "_get_client", AsyncMock(return_value=fake_client))
    monkeypatch.setattr(client, "_resolve_per_call_auth", lambda: ({}, "service_account"))

    got = []
    async with client.get_stream("Session/AuthList/x/null") as resp:
        async for c in resp.aiter_bytes():
            got.append(c)
    assert got == chunks
```

(If `tests/test_mnt_client.py` already imports `AsyncMock`/`pytest`, reuse those imports.)

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_mnt_client.py::test_get_stream_yields_streaming_response -v`
Expected: FAIL — `AttributeError: 'MNTClient' object has no attribute 'get_stream'`.

- [ ] **Step 3: Implement `get_stream`**

In `clients/mnt_client.py`, add `from contextlib import asynccontextmanager` to the imports, then add this method to `MNTClient` (just after `get()`):

```python
    @asynccontextmanager
    async def get_stream(self, endpoint: str):
        """Stream a GET from the MNT API without buffering the whole body.

        Mirrors ``get()`` (endpoint validation, one-time FQDN discovery,
        per-call auth selection, URL-under-base assertion) but opens an
        httpx streaming response so the caller can consume the body
        incrementally via ``response.aiter_bytes()``. ``raise_for_status``
        runs on the response headers before yielding, so HTTP errors
        (e.g. 502) surface to the caller/gate before any body is read.
        """
        validate_endpoint(endpoint)
        client = await self._get_client()
        await self._ensure_mnt_target()

        url = f"{self.base_url}{endpoint}"
        assert_url_under_base(url, self.base_url)

        per_call_kwargs, auth_path = self._resolve_per_call_auth()
        logger.info(
            "MNT API GET (stream)",
            url=url,
            auth_path=auth_path,
            mnt_fqdn_pinned=bool(self._mnt_fqdn),
        )
        async with client.stream("GET", url, **per_call_kwargs) as response:
            response.raise_for_status()
            logger.info("MNT API stream response", status_code=response.status_code, url=url)
            yield response
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_mnt_client.py::test_get_stream_yields_streaming_response -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add clients/mnt_client.py tests/test_mnt_client.py
git commit -m "feat(mnt): add get_stream for incremental AuthList downloads"
```

---

## Task 4: `AuthListGate` (semaphore + min-interval + adaptive breaker)

**Files:**
- Create: `clients/auth_list_gate.py`
- Test: `tests/test_auth_list_gate.py`

**Interfaces:**
- Produces: `class AuthListGate` with constructor
  `AuthListGate(max_concurrency, min_interval_s, backoff_base_s, backoff_max_s, *, time_fn=time.monotonic, jitter_fn=None)`
  and `@classmethod from_settings() -> AuthListGate`.
- Produces: `AuthListGate.guard()` — an `@asynccontextmanager`. On entry it admits or raises `ISE_BUSY` (semaphore full, breaker open, or min-interval not elapsed). On exit it records success (resets the breaker) or, for MnT-distress exceptions (`httpx.TimeoutException`, `httpx.ConnectError`, `httpx.HTTPStatusError` with status in {502,503,504}), opens/extends the breaker; the semaphore slot is always released.
- Produces: module singleton `auth_list_gate = AuthListGate.from_settings()`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_auth_list_gate.py`:

```python
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

import httpx
import pytest
from fastmcp.exceptions import ToolError as McpToolError

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


class FakeClock:
    """Deterministic monotonic clock for gate tests."""

    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def advance(self, secs):
        self.t += secs


def _gate(max_concurrency=1, min_interval_s=0.0, base=5.0, mx=300.0, clock=None):
    from clients.auth_list_gate import AuthListGate

    return AuthListGate(
        max_concurrency=max_concurrency,
        min_interval_s=min_interval_s,
        backoff_base_s=base,
        backoff_max_s=mx,
        time_fn=(clock or FakeClock()),
        jitter_fn=lambda: 0.0,
    )


@pytest.mark.asyncio
async def test_second_concurrent_call_rejects_immediately():
    gate = _gate(max_concurrency=1)
    async with gate.guard():
        with pytest.raises(McpToolError) as ei:
            async with gate.guard():
                pass
        assert "ISE_BUSY" in str(ei.value)


@pytest.mark.asyncio
async def test_sequential_calls_after_release_succeed():
    gate = _gate(max_concurrency=1)
    async with gate.guard():
        pass
    async with gate.guard():
        pass  # no error


@pytest.mark.asyncio
async def test_min_interval_floor_rejects_too_soon():
    clock = FakeClock()
    gate = _gate(min_interval_s=10.0, clock=clock)
    async with gate.guard():
        pass
    # Only 3s later -> too soon.
    clock.advance(3.0)
    with pytest.raises(McpToolError) as ei:
        async with gate.guard():
            pass
    assert "ISE_BUSY" in str(ei.value)
    # Past the interval -> allowed.
    clock.advance(10.0)
    async with gate.guard():
        pass


@pytest.mark.asyncio
async def test_breaker_opens_on_502_then_rejects():
    clock = FakeClock()
    gate = _gate(base=5.0, mx=300.0, clock=clock)
    resp = httpx.Response(502, request=httpx.Request("GET", "https://x/y"))
    with pytest.raises(httpx.HTTPStatusError):
        async with gate.guard():
            raise httpx.HTTPStatusError("bad gateway", request=resp.request, response=resp)
    # Breaker open for base (5s) -> immediate call rejects.
    with pytest.raises(McpToolError) as ei:
        async with gate.guard():
            pass
    assert "ISE_BUSY" in str(ei.value)


@pytest.mark.asyncio
async def test_breaker_window_doubles_and_caps():
    clock = FakeClock()
    gate = _gate(base=5.0, mx=8.0, clock=clock)

    async def fail():
        resp = httpx.Response(503, request=httpx.Request("GET", "https://x/y"))
        with pytest.raises(httpx.HTTPStatusError):
            async with gate.guard():
                raise httpx.HTTPStatusError("x", request=resp.request, response=resp)

    await fail()                 # window = 5
    clock.advance(5.0)           # window elapsed -> half-open probe allowed
    await fail()                 # probe failed -> window = min(10, 8) = 8
    clock.advance(7.9)
    with pytest.raises(McpToolError):
        async with gate.guard():
            pass                 # still within 8s window


@pytest.mark.asyncio
async def test_half_open_probe_success_resets_breaker():
    clock = FakeClock()
    gate = _gate(base=5.0, clock=clock)
    resp = httpx.Response(504, request=httpx.Request("GET", "https://x/y"))
    with pytest.raises(httpx.HTTPStatusError):
        async with gate.guard():
            raise httpx.HTTPStatusError("x", request=resp.request, response=resp)
    clock.advance(5.0)           # window elapsed -> probe allowed
    async with gate.guard():
        pass                     # probe succeeds -> reset
    # Breaker fully closed now: another call proceeds with no wait.
    async with gate.guard():
        pass


@pytest.mark.asyncio
async def test_non_distress_exception_does_not_open_breaker():
    gate = _gate()
    with pytest.raises(ValueError):
        async with gate.guard():
            raise ValueError("parse error, not MnT distress")
    # Breaker stayed closed -> next call proceeds.
    async with gate.guard():
        pass
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_auth_list_gate.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'clients.auth_list_gate'`.

- [ ] **Step 3: Implement the gate**

Create `clients/auth_list_gate.py`:

```python
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Admission control for heavy ISE MnT AuthList downloads.

Three layers, all configurable via ``clients.settings.settings``:

1. Semaphore (default 1): caps concurrent AuthList downloads and rejects
   immediately when full -- no queue wait (a 60-75s download makes any
   short wait futile and the MCP client times out at ~21s anyway).
2. Min-interval floor (default 0.0 = off): rejects a call that starts
   sooner than ``min_interval_s`` after the previous download started,
   to proactively space large downloads off the MnT node.
3. Adaptive circuit breaker: opens on MnT distress (HTTP 502/503/504,
   connect/read timeouts) for a window that doubles per consecutive
   failure (base -> ... -> max, plus jitter). While open, calls reject
   fast; after the window one half-open probe is admitted -- success
   resets the breaker, failure re-opens it (capped at max).

All rejections raise ``ISE_BUSY`` (EXTERNAL_ERROR, retry=True).
"""

import asyncio
import random
import time
from contextlib import asynccontextmanager
from typing import Callable, Optional

import httpx

from logger import logger
from clients.settings import settings
from models.error_models import ErrorCategory, raise_tool_error

# HTTP statuses that indicate the MnT node itself is overloaded/unavailable.
_DISTRESS_STATUSES = frozenset({502, 503, 504})


class AuthListGate:
    def __init__(
        self,
        max_concurrency: int,
        min_interval_s: float,
        backoff_base_s: float,
        backoff_max_s: float,
        *,
        time_fn: Callable[[], float] = time.monotonic,
        jitter_fn: Optional[Callable[[], float]] = None,
    ) -> None:
        self._sem = asyncio.Semaphore(max_concurrency)
        self._min_interval_s = min_interval_s
        self._backoff_base_s = backoff_base_s
        self._backoff_max_s = backoff_max_s
        self._time_fn = time_fn
        self._jitter_fn = jitter_fn or (lambda: random.uniform(0.0, backoff_base_s * 0.1))

        # State guarded by ``_lock`` (admission decisions are non-blocking).
        self._lock = asyncio.Lock()
        self._last_start: Optional[float] = None
        self._consecutive_failures = 0
        self._breaker_open_until: Optional[float] = None
        self._probing = False  # a half-open probe is currently in flight

    @classmethod
    def from_settings(cls) -> "AuthListGate":
        return cls(
            max_concurrency=settings.authlist_max_concurrency,
            min_interval_s=settings.authlist_min_interval_s,
            backoff_base_s=settings.authlist_backoff_base_s,
            backoff_max_s=settings.authlist_backoff_max_s,
        )

    def _reject(self, reason: str) -> None:
        logger.warning("AuthList gate rejected call", reason=reason)
        raise_tool_error(
            ErrorCategory.EXTERNAL_ERROR,
            "ISE_BUSY",
            "The ISE session service is busy (another large query is in "
            "progress or the MnT node is under load). Retry shortly.",
            retry=True,
        )

    async def _admit(self) -> None:
        """Decide admission under the state lock; raise ISE_BUSY to reject.

        On success, records the start time and acquires the semaphore slot
        (guaranteed non-blocking because we only acquire when not locked).
        """
        async with self._lock:
            now = self._time_fn()

            # Breaker gate.
            if self._breaker_open_until is not None:
                if now < self._breaker_open_until:
                    if self._probing:
                        self._reject("breaker_open")
                    # Window elapsed: admit exactly one half-open probe.
                    self._probing = True
                elif self._probing:
                    # Another probe is already deciding the breaker's fate.
                    self._reject("breaker_probing")
                else:
                    self._probing = True

            # Min-interval floor.
            if (
                self._min_interval_s > 0.0
                and self._last_start is not None
                and (now - self._last_start) < self._min_interval_s
            ):
                # A probe reservation must be undone before rejecting.
                if self._breaker_open_until is not None:
                    self._probing = False
                self._reject("min_interval")

            # Concurrency slot (non-blocking).
            if self._sem.locked():
                if self._breaker_open_until is not None:
                    self._probing = False
                self._reject("at_capacity")
            await self._sem.acquire()
            self._last_start = now

    async def _record_success(self) -> None:
        async with self._lock:
            self._consecutive_failures = 0
            self._breaker_open_until = None
            self._probing = False

    async def _record_failure(self) -> None:
        async with self._lock:
            self._consecutive_failures += 1
            window = self._backoff_base_s * (2 ** (self._consecutive_failures - 1))
            window = min(window, self._backoff_max_s) + self._jitter_fn()
            self._breaker_open_until = self._time_fn() + window
            self._probing = False
            logger.warning(
                "AuthList breaker opened",
                consecutive_failures=self._consecutive_failures,
                open_for_s=round(window, 2),
            )

    @asynccontextmanager
    async def guard(self):
        await self._admit()
        try:
            yield
        except (httpx.TimeoutException, httpx.ConnectError):
            await self._record_failure()
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code in _DISTRESS_STATUSES:
                await self._record_failure()
            raise
        else:
            await self._record_success()
        finally:
            self._sem.release()


auth_list_gate = AuthListGate.from_settings()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_auth_list_gate.py -v`
Expected: PASS (all seven).

- [ ] **Step 5: Commit**

```bash
git add clients/auth_list_gate.py tests/test_auth_list_gate.py
git commit -m "feat(gate): AuthList semaphore, min-interval floor, adaptive breaker"
```

---

## Task 5: Wire streaming + gate into the session handler

**Files:**
- Modify: `tools/session_tool_handler.py`
- Test: `tests/test_session_tools.py`

**Interfaces:**
- Consumes: `iter_filter_active_sessions` (Task 2), `_build_session_predicate` (Task 2), `MNTClient.get_stream` (Task 3), `auth_list_gate` (Task 4).
- Produces: `SessionToolHandler.__init__(self, mnt_client, gate=None)` — defaults `gate` to the `auth_list_gate` singleton (injectable for tests).
- Produces: `SessionToolHandler._fetch_auth_list_sessions(self, filters: dict, retention_cap: int, minutes: int = 1440) -> Tuple[List[ActiveSession], int]` — streams through the gate and returns `(sessions, total_matched)`. **Signature and return type change** from today's `(minutes) -> List[ActiveSession]`.

- [ ] **Step 1: Update the handler**

In `tools/session_tool_handler.py`:

1. Add imports:
```python
import tempfile
from utils.xml_parser import iter_filter_active_sessions
from clients.auth_list_gate import auth_list_gate
```

2. Update `__init__`:
```python
    def __init__(self, mnt_client: MNTClient, gate=None):
        self.mnt_client = mnt_client
        self.gate = gate if gate is not None else auth_list_gate
```

3. Replace `_fetch_auth_list_sessions` with the streaming, gated, filtering version:
```python
    async def _fetch_auth_list_sessions(
        self,
        filters: dict,
        retention_cap: int,
        minutes: int = 1440,
    ) -> Tuple[List[ActiveSession], int]:
        """Stream authenticated sessions from the past *minutes*, filtering
        during the parse and retaining only up to *retention_cap* matches.

        Returns (sessions, total_matched). Runs inside the AuthList gate so
        concurrency and MnT load are bounded. Callers must validate *minutes*
        and normalize all *filters* values beforehand.
        """
        minutes = validate_minutes(minutes, max_minutes=self.MAX_MINUTES)
        start_time = datetime.now() - timedelta(minutes=minutes)
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        encoded_start_time = quote(start_time_str, safe=":")
        endpoint = f"Session/AuthList/{encoded_start_time}/null"
        predicate = self._build_session_predicate(**filters)

        logger.info("Streaming authenticated sessions via AuthList API", minutes=minutes)
        async with self.gate.guard():
            async with self.mnt_client.get_stream(endpoint) as response:
                with tempfile.SpooledTemporaryFile(max_size=64 * 1024 * 1024) as buf:
                    async for chunk in response.aiter_bytes():
                        buf.write(chunk)
                    buf.seek(0)
                    retained, total_matched = iter_filter_active_sessions(
                        buf, predicate, retention_cap
                    )
        sessions = [ActiveSession(**d) for d in retained]
        logger.info("Streamed authenticated sessions", total_matched=total_matched, retained=len(sessions))
        return sessions, total_matched
```

4. Update `search_active_sessions` — replace the body inside `_handle_mnt_errors` (lines ~165-199) with a single filtered fetch:
```python
        async with self._handle_mnt_errors("searching active sessions"):
            filters = {
                "username": username,
                "calling_station_id": calling_station_id,
                "nas_ip_address": nas_ip_address,
                "framed_ip_address": framed_ip_address,
                "server": server,
            }
            sample_sessions, total_matching_sessions = await self._fetch_auth_list_sessions(
                filters=filters, retention_cap=limit, minutes=minutes,
            )
            search_filters = {"minutes": minutes}
            for key, value in filters.items():
                if value:
                    search_filters[key] = value
            sample_size = len(sample_sessions)
            sampling_note = build_sampling_note(
                sample_size=sample_size,
                total_found=total_matching_sessions,
                resource="session",
            )
            logger.info("Session search complete", total_matching=total_matching_sessions, sample_size=sample_size)
            return ActiveSessionSearchResult(
                search_filters=search_filters,
                total_matching_sessions=total_matching_sessions,
                sample_size=sample_size,
                sample_sessions=sample_sessions,
                sampling_note=sampling_note,
            )
```

5. Update `search_enriched_active_sessions` — replace the fetch+filter block (lines ~287-301) so it streams with the right retention cap and drops the old `_filter_sessions` call:
```python
        async with self._handle_mnt_errors("searching enriched sessions"):
            has_latency_filter = min_latency_ms is not None or max_latency_ms is not None
            cap = self.ENRICHMENT_CAP if has_latency_filter else limit
            filters = {"username": username, "calling_station_id": calling_station_id}
            filtered_sessions, total_sessions_found = await self._fetch_auth_list_sessions(
                filters=filters, retention_cap=cap, minutes=minutes,
            )
            filters_applied = {"minutes": minutes}
            if username:
                filters_applied["username"] = username
            if calling_station_id:
                filters_applied["calling_station_id"] = calling_station_id

            sessions_to_enrich = filtered_sessions[:cap]
            enrichment_results = await asyncio.gather(*[self._enrich_session(s) for s in sessions_to_enrich])
            enriched_sessions = [s for s in enrichment_results if s is not None]

            if has_latency_filter:
                enriched_sessions = self._filter_sessions_by_latency(
                    enriched_sessions, min_latency_ms, max_latency_ms,
                )
                if min_latency_ms is not None:
                    filters_applied["min_latency_ms"] = min_latency_ms
                if max_latency_ms is not None:
                    filters_applied["max_latency_ms"] = max_latency_ms
                total_sessions_found = len(enriched_sessions)

            enriched_sessions = enriched_sessions[:limit]
            return EnrichedSessionSearchResult(
                search_filters=filters_applied,
                total_sessions_found=total_sessions_found,
                actual_sessions_returned=len(enriched_sessions),
                sessions=enriched_sessions,
            )
```

Note: `_filter_sessions` is now unused by the AuthList path. Leave it in place only if other code references it; otherwise delete it and its now-dead `filters_applied` handling. Grep first (Step 3).

Note on the enriched-tool behavior change (document it in the commit): previously, with no latency filter, `total_sessions_found` was the count of *all* filtered sessions but enrichment was capped at `limit`; now with `cap=limit` the streaming `total_matched` still reflects the true total match count (counted beyond the cap), so `total_sessions_found` remains correct while only `cap` sessions are retained for enrichment. This matches prior semantics.

- [ ] **Step 2: Update existing `_fetch_auth_list_sessions` tests**

The `TestFetchAuthListSessions` class mocks `mnt_client.get` and calls `_fetch_auth_list_sessions(minutes=60)`. Rewrite its helper and tests for the streamed, gated, tuple-returning signature. Replace the class body's helper and the four tests with:

```python
    def _make_handler(self, xml_text):
        import contextlib
        from unittest.mock import AsyncMock
        from tools.session_tool_handler import SessionToolHandler

        class FakeResponse:
            def __init__(self, data: bytes):
                self._data = data
            def raise_for_status(self):
                return None
            async def aiter_bytes(self):
                yield self._data

        @contextlib.asynccontextmanager
        async def fake_get_stream(endpoint):
            self._last_endpoint = endpoint
            yield FakeResponse(xml_text.encode("utf-8"))

        mock_client = AsyncMock()
        mock_client.get_stream = fake_get_stream

        # A pass-through gate so tests exercise the handler, not admission.
        import contextlib as _c
        class _PassGate:
            @_c.asynccontextmanager
            async def guard(self):
                yield
        return SessionToolHandler(mock_client, gate=_PassGate()), mock_client

    @pytest.mark.asyncio
    async def test_returns_parsed_sessions(self):
        handler, _ = self._make_handler(self.ACTIVE_LIST_XML)
        sessions, total = await handler._fetch_auth_list_sessions(filters={}, retention_cap=10, minutes=60)
        assert total == 2
        assert len(sessions) == 2
        assert sessions[0].user_name == "alice"
        assert sessions[1].user_name == "bob"

    @pytest.mark.asyncio
    async def test_empty_list_returns_empty(self):
        handler, _ = self._make_handler(self.EMPTY_LIST_XML)
        sessions, total = await handler._fetch_auth_list_sessions(filters={}, retention_cap=10, minutes=60)
        assert sessions == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_session_missing_optional_fields_does_not_raise(self):
        handler, _ = self._make_handler(self.PARTIAL_SESSION_XML)
        sessions, total = await handler._fetch_auth_list_sessions(filters={}, retention_cap=10, minutes=60)
        assert len(sessions) == 1
        assert sessions[0].user_name == "test19"
        assert sessions[0].nas_ip_address is None
        assert sessions[0].calling_station_id is None
        assert sessions[0].framed_ip_address == "10.1.2.3"

    @pytest.mark.asyncio
    async def test_endpoint_uses_authlist_with_null_end_time(self):
        handler, _ = self._make_handler(self.ACTIVE_LIST_XML)
        await handler._fetch_auth_list_sessions(filters={}, retention_cap=10, minutes=60)
        assert self._last_endpoint.startswith("Session/AuthList/")
        assert self._last_endpoint.endswith("/null")

    @pytest.mark.asyncio
    async def test_invalid_minutes_raises_before_io(self):
        handler, _ = self._make_handler(self.ACTIVE_LIST_XML)
        with pytest.raises(McpToolError):
            await handler._fetch_auth_list_sessions(filters={}, retention_cap=10, minutes=0)

    @pytest.mark.asyncio
    async def test_retention_cap_bounds_sample_but_not_total(self):
        handler, _ = self._make_handler(self.ACTIVE_LIST_XML)
        sessions, total = await handler._fetch_auth_list_sessions(filters={}, retention_cap=1, minutes=60)
        assert total == 2
        assert len(sessions) == 1
```

Add `from fastmcp.exceptions import ToolError as McpToolError` to the test file's imports if not already present.

For `TestSessionToolHandlerSearchActiveSessions`, its `_make_handler` mocks `mnt_client.get`; update it to the same `fake_get_stream` + pass-gate pattern (the assertions on results/validation stay the same — `search_active_sessions` still validates inputs and returns `ActiveSessionSearchResult`). Where a test previously asserted `handler.mnt_client.get.assert_not_called()`, change it to assert the stream was never opened (e.g. track a flag in `fake_get_stream` or assert `self._last_endpoint` is unset).

- [ ] **Step 3: Grep for dead references before deleting `_filter_sessions`**

Run: `rtk proxy grep -rn "_filter_sessions\b" tools/ tests/`
If the only remaining hits are the definition and (optionally) the latency helper `_filter_sessions_by_latency` (a different method — keep it), delete `_filter_sessions` and any test that targeted it directly. If other callers exist, leave it.

- [ ] **Step 4: Run the full session + gate + mnt suite**

Run: `uv run pytest tests/test_session_tools.py tests/test_auth_list_gate.py tests/test_mnt_client.py -v`
Expected: PASS. Investigate and fix any test still assuming the old `get`/list-return contract.

- [ ] **Step 5: Run the whole suite (catch cross-module fallout)**

Run: `uv run pytest -q`
Expected: PASS. The policy/latency tools call `search_enriched_active_sessions`, whose external contract is unchanged; if their tests mock `_fetch_auth_list_sessions` or `mnt_client.get`, update those mocks to the new signature/stream path.

- [ ] **Step 6: Commit**

```bash
git add tools/session_tool_handler.py tests/test_session_tools.py
git commit -m "feat(sessions): stream+gate AuthList fetch; bounded memory & concurrency"
```

---

## Task 6: Documentation

**Files:**
- Modify: `README.md`
- Modify: `MCP_TOOLS_CATALOG.md`

**Interfaces:** none (docs only).

- [ ] **Step 1: Add an operations section to `README.md`**

Add a subsection (place it near the existing configuration/env docs) titled "Session tools: resource usage & backpressure" covering:
- The four AuthList tools (`active_sessions_search`, `sessions_search_with_advanced_details`, `sessions_search_with_policy_details`, `sessions_search_with_latency_details`) download all sessions in the requested window from the ISE MnT node. Memory on the MCP server is now bounded (streaming parse; only a small sample is retained) — no longer multi-GB — but MnT still does real work per call, and larger `minutes`/`limit` increase that cost.
- Only one such download runs at a time by default; concurrent or too-rapid calls receive a retryable `ISE_BUSY` error. Clients should back off and retry.
- The four env tunables, as a table, with defaults verbatim:

```markdown
| Env var | Default | Purpose |
| --- | --- | --- |
| `ISE_AUTHLIST_MAX_CONCURRENCY` | `1` | Max concurrent AuthList downloads. |
| `ISE_AUTHLIST_MIN_INTERVAL_S` | `0.0` | Min seconds between download starts (0 = off). Raise to proactively space large downloads on big deployments. |
| `ISE_AUTHLIST_BACKOFF_BASE_S` | `5.0` | Circuit-breaker base backoff after MnT distress (502/503/504/timeout). |
| `ISE_AUTHLIST_BACKOFF_MAX_S` | `300.0` | Circuit-breaker max backoff. |
```
- Guidance: pass narrow filters (username / MAC / NAS IP) to reduce load; use `ise_investigate_aaa_failure` (bounded, no full download) for failure lookups.

- [ ] **Step 2: Note the same in `MCP_TOOLS_CATALOG.md`**

Under each of the four session tools (or in a shared preamble for the session-tool section), add a one-line note: "Heavy MnT call — bounded MCP memory, gated to `ISE_AUTHLIST_MAX_CONCURRENCY` (default 1); may return retryable `ISE_BUSY` under load." Add a short "Backpressure (`ISE_BUSY`)" note listing the four env vars, cross-referencing the README table.

- [ ] **Step 3: Verify env example**

If `.env.example` documents tunables, add the four new vars with their defaults and a one-line comment each. Run `rtk proxy grep -n "TIMEOUT\|ISE_" .env.example` to find the right spot and matching style.

- [ ] **Step 4: Commit**

```bash
git add README.md MCP_TOOLS_CATALOG.md .env.example
git commit -m "docs: session-tool resource usage & AuthList backpressure knobs"
```

---

## Self-Review

**Spec coverage:**
- Section 1 (streaming memory fix) → Tasks 2, 3, 5. ✓
- Section 2 mechanism 1 (semaphore, reject-immediately) → Task 4 (`_admit` capacity check) + Task 5 (wired via `guard()`). ✓
- Section 2 mechanism 2 (min-interval floor, default 0) → Tasks 1, 4. ✓
- Section 2 mechanism 3 (adaptive breaker) → Task 4. ✓
- Settings (4 env vars, defaults) → Task 1. ✓
- `ISE_BUSY` error surface → Task 4. ✓
- Section 3 (docs) → Task 6. ✓
- Return shapes unchanged → Task 5 keeps `ActiveSessionSearchResult` / `EnrichedSessionSearchResult`. ✓
- Out-of-scope items (#3 logs, #4 rename, deployment_health bug) → not implemented here, tracked in spec. ✓

**Type consistency:**
- `_fetch_auth_list_sessions` returns `Tuple[List[ActiveSession], int]` in both its definition (Task 5) and all callers/tests (Task 5). ✓
- `iter_filter_active_sessions(source, predicate, retention_cap) -> (list, int)` used identically in Tasks 2 and 5. ✓
- `_build_session_predicate(username, calling_station_id, nas_ip_address, framed_ip_address, server)` defined in Task 2, called with `**filters` where `filters` keys match those names in Task 5. Note: `search_enriched_active_sessions` passes only `username`/`calling_station_id`; the other three default to `None`. ✓
- `AuthListGate.guard()` / `from_settings()` / `auth_list_gate` singleton names match across Tasks 4 and 5. ✓

**Placeholder scan:** no TBD/TODO; every code step shows complete code. ✓

**Known follow-up for the implementer:** confirm `defusedxml.ElementTree.iterparse` accepts a file object and supports `next(context)` for the root (Task 2 Step 3) — it mirrors the working `parse_msg_catalog`, but verify against the installed version before relying on it.
