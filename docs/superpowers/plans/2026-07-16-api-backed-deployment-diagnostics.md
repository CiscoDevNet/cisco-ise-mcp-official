# API-backed Deployment Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the log-download deep diagnostics in `ise_deployment_health` with a single `getSystemSummaryDetails` MnT API call (per-node process health + CPU/memory/latency for all nodes), read via a streaming memory-bounded parse; keep the diagnostics behind an opt-in flag renamed `deep_diagnostics` → `diagnostics`; and share one MnT admission-control gate (`AuthListGate` → `MntGate`) across AuthList and the summary call.

**Architecture:** `AuthListGate` is renamed to the endpoint-agnostic `MntGate` (settings/env renamed to `ISE_MNT_GATE_*`, no back-compat aliases) and shared by both consumers. A streaming parser `iter_parse_system_summary` turns the `<dashboardResult>` document into raw dicts via `ET.iterparse` + `root.clear()`. A pure service `SystemSummaryParser` maps process-status codes to states and aggregates the 60-minute series per node. `DeploymentDiagnosticsResolver` streams the endpoint through the injected `mnt_client` under the shared `mnt_gate`, filters rows to the handler's node list, and degrades gracefully: a gate rejection folds into an `unavailable` block with a distinct retry-oriented reason, every other failure into one generic reason. The handler and tool keep the opt-in flag, renamed `diagnostics`.

**Tech Stack:** Python 3.12, `uv` for running tests, `pytest` + `pytest-asyncio`, `defusedxml` for XML parsing, `httpx` (MnT client, streaming), Pydantic v2 settings/models.

## Global Constraints

- Run all tests with `uv run pytest ...` (never bare `pytest`/`python`).
- Every new/edited source file starts with the repo's standard header (copy verbatim):
  ```python
  # Copyright 2026 Cisco Systems, Inc. and its affiliates
  #
  # SPDX-License-Identifier: Apache-2.0
  ```
- MnT process-status code semantics (verbatim): `1`=running, `2`=disabled, `-1`=not_applicable, `0`=down (the only fault). Unknown codes → `"unknown:<n>"` (non-fault, reported not counted).
- The top-level `<status>` element is surfaced verbatim as `reported_status` and never drives any verdict.
- Diagnostics are **opt-in**: they run only when `diagnostics=True`. The base health summary is always returned regardless, and a diagnostics-path failure must never fail the tool.
- Exactly two `unavailable` reason strings (module-level constants, never interpolated from exception text): a **busy/retry** reason for a gate rejection, a **generic** reason for every other failure. No status codes / URLs / hosts in responses; full detail goes to the server log.
- `system_stats` stays `Optional[dict[str, Any]]` on `DeploymentDiagnostics` — no model schema change.
- Endpoint passed to the MnT client is relative: `"dashboard/getSystemSummaryDetails"` (client base URL is already `…/admin/API/mnt/`).
- Reading the summary response uses the streaming AuthList pattern: `mnt_client.get_stream(...)` → `SpooledTemporaryFile(max_size=64 * 1024 * 1024)` → `asyncio.to_thread(iter_parse_system_summary, buf)`.
- The summary fetch runs inside the shared gate: `async with self._gate.guard():`.

---

### Task 1: Rename `AuthListGate` → `MntGate` (shared MnT admission gate)

One mechanical rename across the gate module, settings, singleton, the session-tool consumer, tests, `.env.example`, and README. No behavior change — this generalizes the gate so Task 4 can share it. **No back-compat env aliases** (pre-release; env vars renamed outright).

**Files:**
- Rename: `clients/auth_list_gate.py` → `clients/mnt_gate.py`
- Modify: `clients/settings.py` (validator list + four Field defs, ~lines 60-99)
- Modify: `tools/session_tool_handler.py` (import ~line 15, gate default ~line 48, comment ~line 109)
- Rename+modify test: `tests/test_auth_list_gate.py` → `tests/test_mnt_gate.py`
- Modify: `tests/test_settings_log_fields.py` (~lines 40-73)
- Modify: `tests/test_session_tools.py` (gate references ~lines 306-336)
- Modify: `.env.example` (~lines 28-31)
- Modify: `README.md` (env table ~lines 326-329)

**Interfaces:**
- Consumes: nothing new.
- Produces: `clients/mnt_gate.py` exporting `class MntGate` (same constructor/`from_settings`/`guard()` as before) and singleton `mnt_gate`. Settings attributes `mnt_gate_max_concurrency`, `mnt_gate_min_interval_s`, `mnt_gate_backoff_base_s`, `mnt_gate_backoff_max_s`, sourced from env `ISE_MNT_GATE_MAX_CONCURRENCY`, `ISE_MNT_GATE_MIN_INTERVAL_S`, `ISE_MNT_GATE_BACKOFF_BASE_S`, `ISE_MNT_GATE_BACKOFF_MAX_S`.

- [ ] **Step 1: Move the gate module and rename its symbols**

Run: `git mv clients/auth_list_gate.py clients/mnt_gate.py`

In `clients/mnt_gate.py`:
- Change the module docstring first line from `"""Admission control for heavy ISE MnT AuthList downloads.` to `"""Admission control for heavy ISE MnT reads (AuthList downloads, dashboard summary).`
- Rename `class AuthListGate:` → `class MntGate:`.
- In `from_settings`, change the return annotation `-> "AuthListGate":` → `-> "MntGate":` and update the four settings reads:

```python
    @classmethod
    def from_settings(cls) -> "MntGate":
        return cls(
            max_concurrency=settings.mnt_gate_max_concurrency,
            min_interval_s=settings.mnt_gate_min_interval_s,
            backoff_base_s=settings.mnt_gate_backoff_base_s,
            backoff_max_s=settings.mnt_gate_backoff_max_s,
        )
```

- In `_reject`, generalize the copy from `"The ISE session service is busy ..."` to:

```python
        raise_tool_error(
            ErrorCategory.EXTERNAL_ERROR,
            "ISE_BUSY",
            "The ISE MnT node is busy (another large query is in progress or "
            "the node is under load). Retry shortly.",
            retry=True,
        )
```

- Rename the module-level singleton at the bottom:

```python
mnt_gate = MntGate.from_settings()
```

- [ ] **Step 2: Rename the settings fields**

In `clients/settings.py`, update the `@field_validator(...)` name list (~lines 60-61), replacing the four `authlist_*` names:

```python
        "mnt_gate_max_concurrency", "mnt_gate_min_interval_s",
        "mnt_gate_backoff_base_s", "mnt_gate_backoff_max_s",
```

Then rename the four Field definitions (~lines 82-99) — keep the comments, change names and `validation_alias`:

```python
    mnt_gate_max_concurrency: int = Field(
        default=1, ge=1, le=16, validation_alias="ISE_MNT_GATE_MAX_CONCURRENCY"
    )
    mnt_gate_min_interval_s: float = Field(
        default=0.0, ge=0.0, validation_alias="ISE_MNT_GATE_MIN_INTERVAL_S"
    )
    mnt_gate_backoff_base_s: float = Field(
        default=5.0, gt=0.0, validation_alias="ISE_MNT_GATE_BACKOFF_BASE_S"
    )
    mnt_gate_backoff_max_s: float = Field(
        default=300.0, gt=0.0, validation_alias="ISE_MNT_GATE_BACKOFF_MAX_S"
    )
```

- [ ] **Step 3: Update the session-tool consumer**

In `tools/session_tool_handler.py`:
- Line ~15: `from clients.auth_list_gate import auth_list_gate` → `from clients.mnt_gate import mnt_gate`
- Line ~45 docstring: `gate: Optional AuthListGate for concurrency control (defaults to singleton)` → `gate: Optional MntGate for concurrency control (defaults to singleton)`
- Line ~48: `self.gate = gate if gate is not None else auth_list_gate` → `self.gate = gate if gate is not None else mnt_gate`
- Line ~109 comment: `# -- essential once ISE_AUTHLIST_MAX_CONCURRENCY > 1, where` → `# -- essential once ISE_MNT_GATE_MAX_CONCURRENCY > 1, where`

- [ ] **Step 4: Rename and update the gate test file**

Run: `git mv tests/test_auth_list_gate.py tests/test_mnt_gate.py`

In `tests/test_mnt_gate.py`, update the import + constructor in `_gate` (~lines 30-40):

```python
def _gate(max_concurrency=1, min_interval_s=0.0, base=5.0, mx=300.0, clock=None):
    from clients.mnt_gate import MntGate

    return MntGate(
        max_concurrency=max_concurrency,
        min_interval_s=min_interval_s,
        backoff_base_s=base,
        backoff_max_s=mx,
        time_fn=(clock or FakeClock()),
        jitter_fn=lambda: 0.0,
    )
```

- [ ] **Step 5: Update the settings tests**

In `tests/test_settings_log_fields.py`, rename the two test functions and their env vars / attributes (~lines 40-73):

```python
def test_mnt_gate_defaults(monkeypatch):
    # Ensure a clean env so defaults apply.
    for var in (
        "ISE_MNT_GATE_MAX_CONCURRENCY",
        "ISE_MNT_GATE_MIN_INTERVAL_S",
        "ISE_MNT_GATE_BACKOFF_BASE_S",
        "ISE_MNT_GATE_BACKOFF_MAX_S",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("ISE_IP", "192.0.2.1")

    from clients.settings import ISESettings

    s = ISESettings()
    assert s.mnt_gate_max_concurrency == 1
    assert s.mnt_gate_min_interval_s == 0.0
    assert s.mnt_gate_backoff_base_s == 5.0
    assert s.mnt_gate_backoff_max_s == 300.0


def test_mnt_gate_empty_env_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("ISE_IP", "192.0.2.1")
    monkeypatch.setenv("ISE_MNT_GATE_MAX_CONCURRENCY", "")
    monkeypatch.setenv("ISE_MNT_GATE_MIN_INTERVAL_S", "")
    monkeypatch.setenv("ISE_MNT_GATE_BACKOFF_BASE_S", "")
    monkeypatch.setenv("ISE_MNT_GATE_BACKOFF_MAX_S", "")

    from clients.settings import ISESettings

    s = ISESettings()
    assert s.mnt_gate_max_concurrency == 1
    assert s.mnt_gate_min_interval_s == 0.0
    assert s.mnt_gate_backoff_base_s == 5.0
    assert s.mnt_gate_backoff_max_s == 300.0
```

- [ ] **Step 6: Update session-tool test references**

In `tests/test_session_tools.py`, update the gate references (~lines 306-336). Replace `from clients.auth_list_gate import AuthListGate` with `from clients.mnt_gate import MntGate`, and the constructor `gate = AuthListGate(` with `gate = MntGate(`. Update the class docstring at ~line 310 (`this wires a real AuthListGate so the distress signal from get_stream's`) to say `MntGate`.

Run to find any remaining literal references:
`uv run python -c "import pathlib,re; p=pathlib.Path('tests/test_session_tools.py'); print([i+1 for i,l in enumerate(p.read_text().splitlines()) if re.search('AuthListGate|auth_list_gate|ISE_AUTHLIST', l)])"`
Expected: `[]` after the edits. Rename any stragglers (e.g. the `test_endpoint_uses_authlist_*` / `authlist` method names may stay as descriptive test names — only symbol/env references must change).

- [ ] **Step 7: Update `.env.example` and README env table**

In `.env.example` (~lines 28-31), replace:

```
ISE_MNT_GATE_MAX_CONCURRENCY=1    # Max concurrent heavy MnT reads (AuthList, summary)
ISE_MNT_GATE_MIN_INTERVAL_S=0.0   # Min seconds between heavy MnT read starts (0 = off)
ISE_MNT_GATE_BACKOFF_BASE_S=5.0   # Circuit-breaker base backoff after MnT distress
ISE_MNT_GATE_BACKOFF_MAX_S=300.0  # Circuit-breaker max backoff
```

In `README.md` (~lines 326-329), replace the four rows:

```
| `ISE_MNT_GATE_MAX_CONCURRENCY` | `1` | Max concurrent heavy MnT reads (AuthList downloads and deployment-diagnostics summary). |
| `ISE_MNT_GATE_MIN_INTERVAL_S` | `0.0` | Min seconds between heavy MnT read starts (0 = off). Raise to proactively space large reads on big deployments. |
| `ISE_MNT_GATE_BACKOFF_BASE_S` | `5.0` | Circuit-breaker base backoff after MnT distress (502/503/504/timeout). |
| `ISE_MNT_GATE_BACKOFF_MAX_S` | `300.0` | Circuit-breaker max backoff. |
```

- [ ] **Step 8: Run the affected suites**

Run: `uv run pytest tests/test_mnt_gate.py tests/test_settings_log_fields.py tests/test_session_tools.py -v`
Expected: PASS (rename only; behavior unchanged).

- [ ] **Step 9: Commit**

```bash
git add clients/mnt_gate.py clients/settings.py tools/session_tool_handler.py \
  tests/test_mnt_gate.py tests/test_settings_log_fields.py tests/test_session_tools.py \
  .env.example README.md
git commit -m "refactor(gate): rename AuthListGate -> shared MntGate; ISE_MNT_GATE_* env"
```

---

### Task 2: `iter_parse_system_summary` streaming XML parser

**Files:**
- Modify: `utils/xml_parser.py` (append new function; module already imports `defusedxml.ElementTree as ET`, `logger`, and typing names)
- Test: `tests/test_xml_parser_system_summary.py` (create)

**Interfaces:**
- Consumes: nothing (leaf). Takes a file-like `source` (anything `ET.iterparse` accepts).
- Produces: `iter_parse_system_summary(source) -> Dict[str, Any]` returning
  `{"process_statuses": list[dict], "status_60min": list[dict]}`. Each
  `process_statuses` dict maps every child tag → its text (empty → None), e.g.
  `{"server": "vm218", "status": "Failed", "applicationServer": "1", ...}`.
  Each `status_60min` dict has `server`, `timestamp`, `cpuUtilization`,
  `memoryUtilization`, `latency` (str values). `<lstSystemStatus24Hr>` is
  skipped. Raises `ValueError` on wrong root tag,
  `defusedxml.ElementTree.ParseError` on malformed XML.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_xml_parser_system_summary.py`:

```python
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import io
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from utils.xml_parser import iter_parse_system_summary

_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<dashboardResult>
  <lstProcessStatuses>
    <timestamp>2026-07-16 08:30:51.488</timestamp>
    <server>vm218</server>
    <applicationServer>1</applicationServer>
    <database>1</database>
    <alertManager>-1</alertManager>
    <sxpEngine>2</sxpEngine>
    <status>Failed</status>
    <message/>
  </lstProcessStatuses>
  <lstSystemStatus60Min>
    <server>vm218</server>
    <timestamp>2026-07-16 07:38:00</timestamp>
    <cpuUtilization>4</cpuUtilization>
    <memoryUtilization>57</memoryUtilization>
    <latency>0</latency>
  </lstSystemStatus60Min>
  <lstSystemStatus24Hr>
    <server>vm218</server>
    <timestamp>2026-07-15 08:00:00</timestamp>
    <cpuUtilization>4</cpuUtilization>
    <memoryUtilization>55</memoryUtilization>
    <latency>0</latency>
  </lstSystemStatus24Hr>
</dashboardResult>
"""


def _src():
    return io.BytesIO(_XML)


def test_parses_process_statuses_and_60min():
    result = iter_parse_system_summary(_src())
    assert len(result["process_statuses"]) == 1
    ps = result["process_statuses"][0]
    assert ps["server"] == "vm218"
    assert ps["applicationServer"] == "1"
    assert ps["sxpEngine"] == "2"
    assert ps["status"] == "Failed"
    assert len(result["status_60min"]) == 1
    row = result["status_60min"][0]
    assert row["server"] == "vm218"
    assert row["cpuUtilization"] == "4"
    assert row["latency"] == "0"


def test_ignores_24hr_series():
    result = iter_parse_system_summary(_src())
    assert "status_24hr" not in result
    # 24hr rows must not leak into the 60-min list.
    assert len(result["status_60min"]) == 1


def test_empty_element_becomes_none():
    result = iter_parse_system_summary(_src())
    assert result["process_statuses"][0]["message"] is None


def test_wrong_root_raises_value_error():
    with pytest.raises(ValueError):
        iter_parse_system_summary(io.BytesIO(b"<notDashboard></notDashboard>"))


def test_malformed_xml_raises_parse_error():
    import defusedxml.ElementTree as ET
    with pytest.raises(ET.ParseError):
        iter_parse_system_summary(io.BytesIO(b"<dashboardResult><unclosed>"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_xml_parser_system_summary.py -v`
Expected: FAIL with `ImportError: cannot import name 'iter_parse_system_summary'`

- [ ] **Step 3: Write minimal implementation**

Append to `utils/xml_parser.py`:

```python
def iter_parse_system_summary(source) -> Dict[str, Any]:
    """Stream-parse the getSystemSummaryDetails dashboard XML from the MnT API.

    Uses ``ET.iterparse`` + ``root.clear()`` (the same memory-bounded idiom as
    ``parse_msg_catalog`` / ``iter_filter_active_sessions``) so peak memory is
    proportional to one repeated element subtree, not the whole document.

    Returns a dict with two lists:
      - ``process_statuses``: one dict per ``<lstProcessStatuses>`` node,
        mapping each child tag to its text (empty elements -> None).
      - ``status_60min``: one dict per ``<lstSystemStatus60Min>`` sample,
        with server/timestamp/cpuUtilization/memoryUtilization/latency.

    The ``<lstSystemStatus24Hr>`` series is intentionally skipped (its subtree
    is cleared but never materialized).

    Args:
        source: Anything ``ET.iterparse`` accepts (file object or path).

    Raises:
        ET.ParseError: If the XML is malformed.
        ValueError: If the root element is not ``dashboardResult``.
    """
    def _local(tag: str) -> str:
        return tag.split("}", 1)[-1] if "}" in tag else tag

    def _row(elem) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for child in elem:
            text = child.text if child.text and child.text.strip() else None
            data[_local(child.tag)] = text
        return data

    process_statuses: List[Dict[str, Any]] = []
    status_60min: List[Dict[str, Any]] = []
    try:
        context = ET.iterparse(source, events=("start", "end"))
        _, root = next(context)  # first event is 'start' on the root element
        if _local(root.tag) != "dashboardResult":
            raise ValueError(
                f"Expected root element 'dashboardResult', got '{root.tag}'"
            )
        for event, elem in context:
            if event != "end":
                continue
            tag = _local(elem.tag)
            if tag == "lstProcessStatuses":
                process_statuses.append(_row(elem))
                root.clear()
            elif tag == "lstSystemStatus60Min":
                status_60min.append(_row(elem))
                root.clear()
            elif tag == "lstSystemStatus24Hr":
                root.clear()  # unused; free the subtree immediately
    except ET.ParseError as e:
        logger.error("Failed to parse system summary XML", error=str(e))
        raise
    except ValueError:
        raise
    except Exception as e:
        logger.error("Unexpected error parsing system summary XML", error=str(e))
        raise

    logger.debug(
        "Streamed system summary XML",
        process_nodes=len(process_statuses),
        samples_60min=len(status_60min),
    )
    return {"process_statuses": process_statuses, "status_60min": status_60min}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_xml_parser_system_summary.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add utils/xml_parser.py tests/test_xml_parser_system_summary.py
git commit -m "feat: streaming parse of getSystemSummaryDetails dashboard XML"
```

---

### Task 3: `SystemSummaryParser` service

**Files:**
- Create: `services/system_summary_parser.py`
- Test: `tests/test_system_summary_parser.py`

**Interfaces:**
- Consumes: the dict shape from `iter_parse_system_summary` (Task 2):
  `{"process_statuses": [...], "status_60min": [...]}`.
- Produces: `SystemSummaryParser().build(parsed: dict) -> dict` keyed by server
  hostname. Each value:
  `{"reported_status": str|None, "processes_down": list[str],
    "processes": dict[str, str], "cpu_percent": dict|None,
    "memory_percent": dict|None, "latency": dict|None}`. Each metric dict is
  `{"min": float, "max": float, "avg": float, "latest": float}`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_system_summary_parser.py`:

```python
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from services.system_summary_parser import SystemSummaryParser


def _parsed():
    return {
        "process_statuses": [
            {
                "server": "vm218",
                "status": "Failed",
                "message": None,
                "timestamp": "2026-07-16 08:30:51.488",
                "applicationServer": "1",
                "database": "0",
                "sxpEngine": "2",
                "alertManager": "-1",
                "identityMapping": "7",
            },
        ],
        "status_60min": [
            {"server": "vm218", "timestamp": "2026-07-16 07:38:00",
             "cpuUtilization": "4", "memoryUtilization": "57", "latency": "0"},
            {"server": "vm218", "timestamp": "2026-07-16 07:43:00",
             "cpuUtilization": "3", "memoryUtilization": "57", "latency": "2"},
        ],
    }


def test_process_code_mapping():
    out = SystemSummaryParser().build(_parsed())
    procs = out["vm218"]["processes"]
    assert procs["applicationServer"] == "running"   # 1
    assert procs["database"] == "down"               # 0
    assert procs["sxpEngine"] == "disabled"          # 2
    assert procs["alertManager"] == "not_applicable" # -1
    assert procs["identityMapping"] == "unknown:7"   # unknown


def test_non_process_fields_excluded_from_processes():
    out = SystemSummaryParser().build(_parsed())
    procs = out["vm218"]["processes"]
    for skipped in ("server", "status", "message", "timestamp"):
        assert skipped not in procs


def test_processes_down_lists_only_code_zero():
    out = SystemSummaryParser().build(_parsed())
    assert out["vm218"]["processes_down"] == ["database"]


def test_reported_status_surfaced_verbatim():
    out = SystemSummaryParser().build(_parsed())
    assert out["vm218"]["reported_status"] == "Failed"


def test_metric_aggregation():
    out = SystemSummaryParser().build(_parsed())
    cpu = out["vm218"]["cpu_percent"]
    assert cpu == {"min": 3.0, "max": 4.0, "avg": 3.5, "latest": 3.0}
    lat = out["vm218"]["latency"]
    assert lat["latest"] == 2.0  # latest by timestamp order


def test_missing_series_yields_none_metrics():
    parsed = {"process_statuses": _parsed()["process_statuses"], "status_60min": []}
    out = SystemSummaryParser().build(parsed)
    assert out["vm218"]["cpu_percent"] is None
    assert out["vm218"]["memory_percent"] is None
    assert out["vm218"]["latency"] is None


def test_node_with_only_series_still_appears():
    parsed = {
        "process_statuses": [],
        "status_60min": [
            {"server": "vm9", "timestamp": "2026-07-16 07:38:00",
             "cpuUtilization": "5", "memoryUtilization": "60", "latency": "1"},
        ],
    }
    out = SystemSummaryParser().build(parsed)
    assert "vm9" in out
    assert out["vm9"]["processes"] == {}
    assert out["vm9"]["cpu_percent"]["latest"] == 5.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_system_summary_parser.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'services.system_summary_parser'`

- [ ] **Step 3: Write minimal implementation**

Create `services/system_summary_parser.py`:

```python
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Map ISE getSystemSummaryDetails dashboard data into per-node health.

Pure and testable: no I/O. Consumes the dict produced by
``utils.xml_parser.iter_parse_system_summary`` and returns a per-node summary of
process states (running / disabled / not_applicable / down / unknown), the list
of processes that are down (code 0 only), the ISE-reported top-level status
verbatim, and min/max/avg/latest aggregates of the 60-minute
CPU / memory / latency series.

Process-status code semantics (confirmed against the ``70001 System-Stats: ISE
Process Health`` log line): 1=running, 2=disabled, -1=not_applicable, 0=down
(the only fault). Unknown codes are surfaced as ``unknown:<n>`` and are not
faults.
"""

from typing import Any, Dict, List

# Elements of <lstProcessStatuses> that are NOT process codes.
_NON_PROCESS_FIELDS = frozenset({"server", "timestamp", "status", "message"})

_CODE_MAP = {
    "1": "running",
    "2": "disabled",
    "-1": "not_applicable",
    "0": "down",
}

_METRIC_FIELDS = (
    ("cpu_percent", "cpuUtilization"),
    ("memory_percent", "memoryUtilization"),
    ("latency", "latency"),
)


def _aggregate(values: List[float]) -> Dict[str, float]:
    return {
        "min": min(values),
        "max": max(values),
        "avg": round(sum(values) / len(values), 2),
        "latest": values[-1],
    }


def _blank_node() -> Dict[str, Any]:
    return {
        "reported_status": None,
        "processes_down": [],
        "processes": {},
        "cpu_percent": None,
        "memory_percent": None,
        "latency": None,
    }


class SystemSummaryParser:
    def build(self, parsed: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Build a per-node summary keyed by server hostname."""
        nodes: Dict[str, Dict[str, Any]] = {}

        for row in parsed.get("process_statuses", []):
            server = row.get("server")
            if not server:
                continue
            processes: Dict[str, str] = {}
            processes_down: List[str] = []
            for field, value in row.items():
                if field in _NON_PROCESS_FIELDS:
                    continue
                state = _CODE_MAP.get(value, f"unknown:{value}")
                processes[field] = state
                if state == "down":
                    processes_down.append(field)
            node = _blank_node()
            node["reported_status"] = row.get("status")
            node["processes_down"] = processes_down
            node["processes"] = processes
            nodes[server] = node

        # Aggregate the 60-min series per server (ordered by timestamp so
        # ``latest`` is the most recent sample).
        series: Dict[str, List[dict]] = {}
        for sample in parsed.get("status_60min", []):
            server = sample.get("server")
            if not server:
                continue
            series.setdefault(server, []).append(sample)

        for server, samples in series.items():
            samples.sort(key=lambda s: s.get("timestamp") or "")
            node = nodes.setdefault(server, _blank_node())
            for out_key, src_key in _METRIC_FIELDS:
                values: List[float] = []
                for s in samples:
                    raw = s.get(src_key)
                    if raw is None:
                        continue
                    try:
                        values.append(float(raw))
                    except (TypeError, ValueError):
                        continue
                if values:
                    node[out_key] = _aggregate(values)

        return nodes
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_system_summary_parser.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add services/system_summary_parser.py tests/test_system_summary_parser.py
git commit -m "feat: SystemSummaryParser maps process codes and aggregates stats"
```

---

### Task 4: Rewrite `DeploymentDiagnosticsResolver` (streaming read, shared gate, graceful degrade)

**Files:**
- Modify: `services/deployment_diagnostics_resolver.py` (full rewrite of the stats path)
- Test: `tests/test_deployment_diagnostics_resolver.py` (replace entirely)

**Interfaces:**
- Consumes: `iter_parse_system_summary` (Task 2), `SystemSummaryParser` (Task 3),
  the shared `mnt_gate` singleton (Task 1), and an injected `mnt_client` exposing
  `get_stream(endpoint) -> async context manager` yielding an httpx streaming
  response with `aiter_bytes()`.
- Produces: `DeploymentDiagnosticsResolver(mnt_client, gate=None)` and
  `async resolve(nodes, scoped=False) -> DeploymentDiagnostics`. `system_stats`
  is `None` when there are no nodes; else
  `{"source": "getSystemSummaryDetails", "duration_minutes": 60, "nodes": {...}}`
  (keyed by the caller's node hostnames), OR
  `{"status": "unavailable", "reason": <busy-or-generic>}` on failure.

- [ ] **Step 1: Write the failing tests**

Replace the entire contents of `tests/test_deployment_diagnostics_resolver.py` with:

```python
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

pytest_plugins = ("pytest_asyncio",)


def _node(hostname, roles, node_status="Connected", fqdn=None):
    from models.deployment_models import DeploymentNodeSummary
    return DeploymentNodeSummary(
        hostname=hostname, fqdn=fqdn, ip_address=None,
        roles=roles, services=[], node_status=node_status,
    )


_SUMMARY_XML = b"""<?xml version="1.0"?>
<dashboardResult>
  <lstProcessStatuses>
    <server>vm218</server><status>Failed</status>
    <applicationServer>1</applicationServer><database>0</database>
  </lstProcessStatuses>
  <lstProcessStatuses>
    <server>vm219</server><status>Failed</status>
    <applicationServer>1</applicationServer><database>1</database>
  </lstProcessStatuses>
  <lstSystemStatus60Min>
    <server>vm218</server><timestamp>2026-07-16 07:38:00</timestamp>
    <cpuUtilization>4</cpuUtilization><memoryUtilization>57</memoryUtilization><latency>0</latency>
  </lstSystemStatus60Min>
</dashboardResult>
"""


class _FakeStreamResponse:
    def __init__(self, body: bytes, chunk: int = 32):
        self._body = body
        self._chunk = chunk

    async def aiter_bytes(self):
        for i in range(0, len(self._body), self._chunk):
            yield self._body[i:i + self._chunk]


def _mnt_streaming(body: bytes):
    """MnT client whose get_stream yields a fake streaming response."""
    mnt = MagicMock()

    @asynccontextmanager
    async def _get_stream(endpoint):
        yield _FakeStreamResponse(body)

    mnt.get_stream = _get_stream
    return mnt


def _mnt_stream_raising(exc):
    mnt = MagicMock()

    @asynccontextmanager
    async def _get_stream(endpoint):
        raise exc
        yield  # pragma: no cover

    mnt.get_stream = _get_stream
    return mnt


class _RejectingGate:
    """A gate whose guard() rejects immediately with ISE_BUSY."""

    def guard(self):
        return self

    async def __aenter__(self):
        from models.error_models import ErrorCategory, raise_tool_error
        raise_tool_error(
            ErrorCategory.EXTERNAL_ERROR, "ISE_BUSY",
            "The ISE MnT node is busy. Retry shortly.", retry=True,
        )

    async def __aexit__(self, *exc):
        return False


class _PassGate:
    """A gate whose guard() always admits."""

    def guard(self):
        return self

    async def __aenter__(self):
        return None

    async def __aexit__(self, *exc):
        return False


def _resolver(mnt, gate=None):
    from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver
    return DeploymentDiagnosticsResolver(mnt, gate=gate or _PassGate())


class TestObservations:
    @pytest.mark.asyncio
    async def test_observes_unhealthy_nodes(self):
        nodes = [_node("vm218", ["PrimaryAdmin"]), _node("vm220", [], node_status="NotInSync")]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        joined = " ".join(result.observations)
        assert "vm220" in joined and "NotInSync" in joined

    @pytest.mark.asyncio
    async def test_observes_missing_pan_redundancy(self):
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        joined = " ".join(result.observations).lower()
        assert "redundancy" in joined or "secondaryadmin" in joined.replace(" ", "")

    @pytest.mark.asyncio
    async def test_standalone_has_no_missing_pan_observation(self):
        nodes = [_node("vm1", ["Standalone"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        joined = " ".join(result.observations)
        assert "No PrimaryAdmin" not in joined and "redundancy" not in joined

    @pytest.mark.asyncio
    async def test_scoped_suppresses_pan_redundancy_observation(self):
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes, scoped=True)
        joined = " ".join(result.observations).lower()
        assert "redundancy" not in joined
        assert "no primaryadmin" not in joined

    @pytest.mark.asyncio
    async def test_scoped_still_reports_per_node_unhealthy(self):
        nodes = [_node("vm220", ["PrimaryAdmin"], node_status="NotInSync")]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes, scoped=True)
        joined = " ".join(result.observations)
        assert "vm220" in joined and "NotInSync" in joined


class TestSystemStats:
    @pytest.mark.asyncio
    async def test_stats_keyed_by_nodes_in_list(self):
        nodes = [_node("vm218", ["PrimaryAdmin"]), _node("vm219", ["SecondaryAdmin"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        assert result.system_stats["source"] == "getSystemSummaryDetails"
        assert result.system_stats["duration_minutes"] == 60
        assert set(result.system_stats["nodes"].keys()) == {"vm218", "vm219"}
        assert result.system_stats["nodes"]["vm218"]["processes_down"] == ["database"]
        assert result.system_stats["nodes"]["vm218"]["cpu_percent"]["latest"] == 4.0

    @pytest.mark.asyncio
    async def test_api_row_not_in_node_list_is_excluded(self):
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        assert set(result.system_stats["nodes"].keys()) == {"vm218"}

    @pytest.mark.asyncio
    async def test_down_process_generates_observation(self):
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve(nodes)
        joined = " ".join(result.observations)
        assert "vm218" in joined
        assert "database" in joined.lower() and "not running" in joined.lower()

    @pytest.mark.asyncio
    async def test_no_nodes_leaves_system_stats_none(self):
        result = await _resolver(_mnt_streaming(_SUMMARY_XML)).resolve([])
        assert result.system_stats is None

    @pytest.mark.asyncio
    async def test_api_failure_degrades_with_generic_reason(self):
        import httpx
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        mnt = _mnt_stream_raising(httpx.ConnectError("boom to 10.0.0.1"))
        result = await _resolver(mnt).resolve(nodes)
        assert result.system_stats["status"] == "unavailable"
        reason = result.system_stats["reason"]
        assert "10.0.0.1" not in reason and "boom" not in reason.lower()
        # Base observations still run despite the API failure.
        joined = " ".join(result.observations).lower()
        assert "redundancy" in joined or "secondaryadmin" in joined.replace(" ", "")

    @pytest.mark.asyncio
    async def test_malformed_xml_degrades_with_generic_reason(self):
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        result = await _resolver(_mnt_streaming(b"<dashboardResult><nope>")).resolve(nodes)
        assert result.system_stats["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_gate_rejection_degrades_with_busy_reason(self):
        # A busy gate must NOT fail the tool; it degrades to an unavailable
        # block with a distinct retry-oriented reason.
        nodes = [_node("vm218", ["PrimaryAdmin"])]
        resolver = _resolver(_mnt_streaming(_SUMMARY_XML), gate=_RejectingGate())
        result = await resolver.resolve(nodes)
        assert result.system_stats["status"] == "unavailable"
        reason = result.system_stats["reason"].lower()
        assert "busy" in reason or "retry" in reason
        # Distinct from the generic reason.
        from services.deployment_diagnostics_resolver import (
            _BUSY_REASON, _GENERIC_REASON,
        )
        assert result.system_stats["reason"] == _BUSY_REASON
        assert _BUSY_REASON != _GENERIC_REASON
        # Base observations still present.
        assert " ".join(result.observations)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_deployment_diagnostics_resolver.py -v`
Expected: FAIL — `DeploymentDiagnosticsResolver` currently takes no `mnt_client`/`gate`, has no `_BUSY_REASON`/`_GENERIC_REASON`, and returns the old log-based shape.

- [ ] **Step 3: Write minimal implementation**

Replace the entire contents of `services/deployment_diagnostics_resolver.py` with:

```python
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Derive deployment diagnostics from the node list and the MnT dashboard API.

Produces human-readable observations derived from node status and roles, plus
per-node system statistics (process health and CPU/memory/latency) fetched in a
single call to the MnT ``getSystemSummaryDetails`` endpoint. The call covers all
nodes at once; results are filtered to the hostnames in the caller's node list.

The response is read with a streaming, memory-bounded parse (the AuthList
pattern: ``get_stream`` -> spooled temp file -> ``iterparse`` off the event loop)
and the fetch runs inside the shared ``mnt_gate`` so it shares MnT-node
backpressure with the session tools.

Diagnostics degrade gracefully: a gate rejection folds into an ``unavailable``
system_stats block with a distinct retry-oriented reason, and any other failure
(auth / HTTP / parse) into one generic reason. The base observations still run,
and the tool never fails because diagnostics could not be produced.
"""

import asyncio
import tempfile

from fastmcp.exceptions import ToolError as McpToolError

from logger import logger
from clients.mnt_gate import mnt_gate
from models.deployment_models import DeploymentDiagnostics, DeploymentNodeSummary
from services.system_summary_parser import SystemSummaryParser
from utils.xml_parser import iter_parse_system_summary

_CONNECTED = "Connected"
_SUMMARY_ENDPOINT = "dashboard/getSystemSummaryDetails"
_SPOOL_MAX_BYTES = 64 * 1024 * 1024

_BUSY_REASON = (
    "diagnostics skipped: the ISE MnT node is busy or under load; retry shortly"
)
_GENERIC_REASON = (
    "diagnostics unavailable; no system-summary data could be retrieved"
)


class DeploymentDiagnosticsResolver:
    def __init__(self, mnt_client, gate=None) -> None:
        self._mnt_client = mnt_client
        self._gate = gate if gate is not None else mnt_gate
        self._parser = SystemSummaryParser()

    async def _fetch_and_parse(self) -> dict:
        """Stream + parse the summary XML. Raises on gate/API/parse failure."""
        async with self._gate.guard():
            async with self._mnt_client.get_stream(_SUMMARY_ENDPOINT) as response:
                with tempfile.SpooledTemporaryFile(max_size=_SPOOL_MAX_BYTES) as buf:
                    async for chunk in response.aiter_bytes():
                        buf.write(chunk)
                    buf.seek(0)
                    # iterparse is synchronous/CPU-bound and may read a
                    # spilled-to-disk temp file; run it off the event loop.
                    return await asyncio.to_thread(iter_parse_system_summary, buf)

    async def _system_stats(
        self, nodes: list[DeploymentNodeSummary]
    ) -> tuple[dict, list[str]]:
        """Fetch + parse system summary. Never raises.

        Returns ``(system_stats, extra_observations)``. On a gate rejection the
        block carries the busy/retry reason; on any other failure the generic
        reason.
        """
        try:
            parsed = await self._fetch_and_parse()
            per_node = self._parser.build(parsed)
        except McpToolError as exc:
            # Gate rejection (ISE_BUSY) -> degrade, do NOT re-raise.
            logger.info("Deployment diagnostics gated (MnT busy)", error=str(exc))
            return ({"status": "unavailable", "reason": _BUSY_REASON}, [])
        except Exception as exc:  # auth / HTTP / parse — isolate, log full detail
            logger.info(
                "Deployment diagnostics: system summary unavailable",
                error=str(exc),
            )
            return ({"status": "unavailable", "reason": _GENERIC_REASON}, [])

        wanted = {n.hostname for n in nodes}
        scoped_nodes = {h: v for h, v in per_node.items() if h in wanted}

        observations: list[str] = []
        for hostname, data in scoped_nodes.items():
            down = data.get("processes_down") or []
            if down:
                observations.append(
                    f"{hostname}: process(es) not running: {', '.join(down)} "
                    "(admin-guide: Process Down)."
                )

        return (
            {
                "source": "getSystemSummaryDetails",
                "duration_minutes": 60,
                "nodes": scoped_nodes,
            },
            observations,
        )

    async def resolve(
        self, nodes: list[DeploymentNodeSummary], scoped: bool = False
    ) -> DeploymentDiagnostics:
        """Derive diagnostics for ``nodes``.

        Args:
            nodes: The node list to diagnose.
            scoped: True when the caller filtered to specific hostnames.
                Deployment-wide HA claims (missing Primary/Secondary PAN) are
                omitted for a filtered slice; per-node observations and
                system_stats are still produced.
        """
        observations: list[str] = []

        for node in nodes:
            if node.node_status != _CONNECTED:
                observations.append(
                    f"{node.hostname}: nodeStatus={node.node_status or 'Unknown'} "
                    "(not Connected)"
                )

        if not scoped:
            has_primary = any("PrimaryAdmin" in n.roles for n in nodes)
            has_secondary = any("SecondaryAdmin" in n.roles for n in nodes)
            has_standalone = any("Standalone" in n.roles for n in nodes)
            if not (has_primary or has_standalone):
                observations.append(
                    "No PrimaryAdmin (Primary PAN) node present in the deployment."
                )
            elif has_primary and not has_secondary:
                observations.append(
                    "No SecondaryAdmin (Secondary PAN) node present — no PAN redundancy."
                )

        system_stats = None
        if nodes:
            system_stats, stats_observations = await self._system_stats(nodes)
            observations.extend(stats_observations)

        return DeploymentDiagnostics(
            observations=observations, system_stats=system_stats
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_deployment_diagnostics_resolver.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Commit**

```bash
git add services/deployment_diagnostics_resolver.py tests/test_deployment_diagnostics_resolver.py
git commit -m "feat: stream getSystemSummaryDetails under shared MnT gate; degrade on busy/failure"
```

---

### Task 5: Handler — rename `deep_diagnostics` → `diagnostics` (keep opt-in)

**Files:**
- Modify: `tools/deployment_tool_handler.py`
- Modify: `models/deployment_models.py` (docstrings only, ~lines 202-227)
- Test: `tests/test_deployment_tool_handler.py`

**Interfaces:**
- Consumes: `DeploymentDiagnosticsResolver(mnt_client, gate=None)` (Task 4).
- Produces: `get_deployment_health(hostnames: list[str] | None = None, diagnostics: bool = False) -> DeploymentHealthResult`.
  `result.diagnostics` is populated only when `diagnostics=True`, else `None`.
  No model schema change — only stale docstrings referencing the old flag name
  and log source are corrected.

- [ ] **Step 1: Update the failing tests**

In `tests/test_deployment_tool_handler.py`, replace `_make_handler` so the
resolver receives a streaming mock MnT client (the resolver no longer uses
`log_service`), and use a pass-through gate to avoid singleton coupling:

```python
def _make_handler():
    from contextlib import asynccontextmanager
    from tools.deployment_tool_handler import DeploymentToolHandler
    from services.deployment_diagnostics_resolver import DeploymentDiagnosticsResolver

    mock_factory = MagicMock()
    mock_factory.get_client.return_value = MagicMock()

    body = (
        b'<?xml version="1.0"?><dashboardResult>'
        b'<lstProcessStatuses><server>vm218</server><status>Failed</status>'
        b'<applicationServer>1</applicationServer></lstProcessStatuses>'
        b'</dashboardResult>'
    )

    class _Resp:
        async def aiter_bytes(self):
            yield body

    mnt = MagicMock()

    @asynccontextmanager
    async def _get_stream(endpoint):
        yield _Resp()

    mnt.get_stream = _get_stream

    class _PassGate:
        def guard(self):
            return self

        async def __aenter__(self):
            return None

        async def __aexit__(self, *exc):
            return False

    resolver = DeploymentDiagnosticsResolver(mnt, gate=_PassGate())
    return DeploymentToolHandler(mock_factory, resolver)
```

In `test_all_nodes_no_filter`, the default call must NOT run diagnostics, so keep:

```python
        assert result.diagnostics is None
```

Replace the whole `test_deep_diagnostics_attaches_diagnostics` test with:

```python
    @pytest.mark.asyncio
    async def test_diagnostics_flag_attaches_diagnostics(self):
        handler = _make_handler()
        with patch.object(handler, "execute_api_call", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {"response": [
                _raw_node("vm220", [], status="NotInSync"),
            ]}
            result = await handler.get_deployment_health(diagnostics=True)

        assert result.diagnostics is not None
        assert any("vm220" in o for o in result.diagnostics.observations)

    @pytest.mark.asyncio
    async def test_diagnostics_default_off(self):
        handler = _make_handler()
        with patch.object(handler, "execute_api_call", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = {"response": [_raw_node("vm218", ["PrimaryAdmin"])]}
            result = await handler.get_deployment_health()
        assert result.diagnostics is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_deployment_tool_handler.py -v`
Expected: FAIL — `get_deployment_health` still names the param `deep_diagnostics`; `diagnostics=True` raises `TypeError`.

- [ ] **Step 3: Update the implementation**

In `tools/deployment_tool_handler.py`, rename the parameter and its docstring,
and update the log field + call. Replace the signature:

```python
    async def get_deployment_health(
        self,
        hostnames: list[str] | None = None,
        deep_diagnostics: bool = False,
    ) -> DeploymentHealthResult:
        """Fetch deployed nodes and compute a derived health assessment.

        Args:
            hostnames: Exact node hostnames to filter on (OR-combined).
                None/empty returns all nodes.
            deep_diagnostics: When True, attach deeper diagnostics via the
                DeploymentDiagnosticsResolver.

        Returns:
            DeploymentHealthResult with nodes, summary, and optional diagnostics.
        """
```

with:

```python
    async def get_deployment_health(
        self,
        hostnames: list[str] | None = None,
        diagnostics: bool = False,
    ) -> DeploymentHealthResult:
        """Fetch deployed nodes and compute a derived health assessment.

        Args:
            hostnames: Exact node hostnames to filter on (OR-combined).
                None/empty returns all nodes.
            diagnostics: When True, attach API-backed diagnostics (process
                health + CPU/memory/latency from getSystemSummaryDetails) via
                the DeploymentDiagnosticsResolver. Opt-in because the response
                can be large in big deployments and the call is gated for MnT
                backpressure.

        Returns:
            DeploymentHealthResult with nodes, summary, and optional diagnostics.
        """
```

Replace the log call:

```python
        logger.info(
            "Fetching deployment nodes",
            hostname_count=len(hostnames) if hostnames else 0,
            deep_diagnostics=deep_diagnostics,
        )
```

with:

```python
        logger.info(
            "Fetching deployment nodes",
            hostname_count=len(hostnames) if hostnames else 0,
            diagnostics=diagnostics,
        )
```

Replace the conditional diagnostics block:

```python
        diagnostics = None
        if deep_diagnostics:
            diagnostics = await self.diagnostics_resolver.resolve(
                nodes, scoped=bool(hostnames)
            )
```

with:

```python
        diagnostics_result = None
        if diagnostics:
            diagnostics_result = await self.diagnostics_resolver.resolve(
                nodes, scoped=bool(hostnames)
            )
```

And update the return to use the renamed local:

```python
        return DeploymentHealthResult(
            nodes=nodes, summary=summary, diagnostics=diagnostics_result
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_deployment_tool_handler.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Correct the stale model docstrings**

In `models/deployment_models.py`, the `DeploymentDiagnostics` docstring and the
`system_stats` / `diagnostics` field descriptions still reference the old
`deep_diagnostics` flag and a "log-derived" source. The schema does NOT change;
fix only the copy.

Replace the `DeploymentDiagnostics` class docstring (~lines 202-208):

```python
class DeploymentDiagnostics(IseResultModel):
    """Deeper diagnostics, populated only when deep_diagnostics=True.

    Today this carries derived observations. The next feature adds
    log-backed system statistics via the `system_stats` field without
    changing this model's consumers.
    """
```

with:

```python
class DeploymentDiagnostics(IseResultModel):
    """API-backed diagnostics, populated only when diagnostics=True.

    Carries derived observations plus per-node system statistics sourced from
    the MnT getSystemSummaryDetails API (process health and CPU/memory/latency).
    """
```

Replace the `system_stats` field description (~lines 214-217):

```python
    system_stats: Optional[dict[str, Any]] = Field(
        None,
        description="Log-derived per-node system statistics (added by a later feature)",
    )
```

with:

```python
    system_stats: Optional[dict[str, Any]] = Field(
        None,
        description="Per-node system statistics from the MnT "
        "getSystemSummaryDetails API, or an {status: 'unavailable', reason} "
        "block when the call is gated or fails",
    )
```

Replace the `DeploymentHealthResult.diagnostics` field description (~lines 225-227):

```python
    diagnostics: Optional[DeploymentDiagnostics] = Field(
        None, description="Deep diagnostics; present only when deep_diagnostics=True"
    )
```

with:

```python
    diagnostics: Optional[DeploymentDiagnostics] = Field(
        None, description="Diagnostics; present only when diagnostics=True"
    )
```

- [ ] **Step 6: Re-run to confirm nothing broke**

Run: `uv run pytest tests/test_deployment_tool_handler.py -v`
Expected: PASS (docstring-only change).

- [ ] **Step 7: Commit**

```bash
git add tools/deployment_tool_handler.py models/deployment_models.py tests/test_deployment_tool_handler.py
git commit -m "feat: rename deep_diagnostics -> diagnostics on the deployment handler"
```

---

### Task 6: `server.py` — wire `mnt_client` into the resolver; rename tool param

**Files:**
- Modify: `server.py` (resolver construction line ~108; tool param + docstring + call ~lines 321-355)
- Test: `tests/test_server.py` (deployment tool tests)

**Interfaces:**
- Consumes: `mnt_client` singleton (imported line 13), `get_deployment_health(hostnames=None, diagnostics=False)` (Task 5).
- Produces: `ise_deployment_health(hostnames=None, diagnostics=False)` tool.

- [ ] **Step 1: Update the failing tests**

In `tests/test_server.py`, find the deployment tool tests. Update the call/assert
that use `deep_diagnostics`:

Replace:

```python
            result = await ise_deployment_health(hostnames=["vm218"], deep_diagnostics=True)

        mock_handler.get_deployment_health.assert_called_once()
        kw = mock_handler.get_deployment_health.call_args[1]
        assert kw["hostnames"] == ["vm218"]
        assert kw["deep_diagnostics"] is True
```

with:

```python
            result = await ise_deployment_health(hostnames=["vm218"], diagnostics=True)

        mock_handler.get_deployment_health.assert_called_once()
        kw = mock_handler.get_deployment_health.call_args[1]
        assert kw["hostnames"] == ["vm218"]
        assert kw["diagnostics"] is True
```

In the default-params test, replace:

```python
        kw = mock_handler.get_deployment_health.call_args[1]
        assert kw["hostnames"] is None
        assert kw["deep_diagnostics"] is False
```

with:

```python
        kw = mock_handler.get_deployment_health.call_args[1]
        assert kw["hostnames"] is None
        assert kw["diagnostics"] is False
```

(If exact surrounding lines differ, locate them with:
`uv run python -c "import pathlib,re; p=pathlib.Path('tests/test_server.py'); [print(i+1, l.rstrip()) for i,l in enumerate(p.read_text().splitlines()) if 'deep_diagnostics' in l]"`)

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_server.py -k deployment -v`
Expected: FAIL — the tool still declares `deep_diagnostics`; passing `diagnostics=` errors or the renamed assertions mismatch.

- [ ] **Step 3: Update the implementation**

In `server.py`, wire the MnT client into the resolver (line ~108):

```python
deployment_diagnostics_resolver = DeploymentDiagnosticsResolver()
```

becomes:

```python
deployment_diagnostics_resolver = DeploymentDiagnosticsResolver(mnt_client)
```

In the `ise_deployment_health` tool (~lines 321-329), rename the parameter block:

```python
    deep_diagnostics: Annotated[
        bool,
        "Default false. When true, also gather deeper per-node diagnostic data "
        "(log-derived system stats: CPU, memory, process health, replication "
        "indicators). Heavier and slower — set true ONLY when the user's wording "
        "signals a problem or asks to investigate/diagnose (e.g. 'down', "
        "'not syncing', 'out of sync', 'registration failed', 'overloaded'). "
        "Keep false for general status, topology, readiness, or HA questions.",
    ] = False,
) -> DeploymentHealthResult:
```

with:

```python
    diagnostics: Annotated[
        bool,
        "Default false. When true, attach API-backed per-node diagnostics "
        "(process health + CPU/memory/latency from the MnT "
        "getSystemSummaryDetails API). Opt-in: the response can be large in big "
        "deployments and the call is gated for MnT-node backpressure. Set true "
        "ONLY when the user's wording signals a problem or asks to "
        "investigate/diagnose (e.g. 'down', 'not syncing', 'out of sync', "
        "'registration failed', 'overloaded'). Keep false for general status, "
        "topology, readiness, or HA questions.",
    ] = False,
) -> DeploymentHealthResult:
```

Extend the docstring `Returns:` block. After the `summary:` bullet lines (ending
`with hostnames set the scope is "filtered" and they are null.`), insert:

```python
    - diagnostics: Present only when diagnostics=true — per-node process health
      (from the MnT getSystemSummaryDetails API) plus CPU/memory/latency and
      derived observations. Nodes with a process reporting "down" are flagged.
      On MnT-node load or an API/parse failure, system_stats degrades to an
      {status: "unavailable", reason} block; the base summary is unaffected.
```

Update the call at the bottom of the tool:

```python
    result: DeploymentHealthResult = await deployment_tool_handler.get_deployment_health(
        hostnames=hostnames,
        deep_diagnostics=deep_diagnostics,
    )
```

becomes:

```python
    result: DeploymentHealthResult = await deployment_tool_handler.get_deployment_health(
        hostnames=hostnames,
        diagnostics=diagnostics,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_server.py -k deployment -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add server.py tests/test_server.py
git commit -m "feat: wire MnT client into resolver; rename deep_diagnostics tool param to diagnostics"
```

---

### Task 7: Remove the obsolete `SystemStatsParser` class (keep `_parse_ts`)

**Files:**
- Modify: `services/system_stats_parser.py` (remove `SystemStatsParser` + utilization helpers; keep `_parse_ts`, `_TS_RE`, `_TS_FMT`)
- Delete: `tests/test_system_stats_parser.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `services/system_stats_parser.py` still exports `_parse_ts` (used by `services/certificate_log_scanner.py`).

- [ ] **Step 1: Verify what still imports from the module**

Run: `uv run python -c "import pathlib,re; [print(f'{p}:{i+1}: {l.strip()}') for p in pathlib.Path('.').rglob('*.py') if '.venv' not in str(p) and '__pycache__' not in str(p) for i,l in enumerate(p.read_text().splitlines()) if re.search('system_stats_parser|SystemStatsParser', l)]"`
Expected: after Tasks 3-4, the only non-test import is
`services/certificate_log_scanner.py: from services.system_stats_parser import _parse_ts`
(plus this task's own file). If anything else still imports `SystemStatsParser`, stop and reconcile before deleting.

- [ ] **Step 2: Delete the obsolete test file**

Run: `git rm tests/test_system_stats_parser.py`

- [ ] **Step 3: Trim the module to just the timestamp helper**

Replace the entire contents of `services/system_stats_parser.py` with:

```python
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Timestamp parsing for ISE log lines.

Formerly also hosted ``SystemStatsParser`` (log-derived CPU/memory/disk stats),
replaced by the MnT ``getSystemSummaryDetails`` API path. The ``_parse_ts``
helper and its regex/format remain because ``services.certificate_log_scanner``
reuses them for ISE log timestamp parsing.
"""

import re
from datetime import datetime
from typing import Optional

# Leading timestamp: "2026-07-01 00:02:37.362 +00:00"
_TS_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} [+-]\d{2}:\d{2})"
)
_TS_FMT = "%Y-%m-%d %H:%M:%S.%f %z"


def _parse_ts(line: str) -> Optional[datetime]:
    m = _TS_RE.match(line)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), _TS_FMT)
    except ValueError:
        return None
```

- [ ] **Step 4: Run the affected suite to confirm nothing broke**

Run: `uv run pytest tests/test_certificate_log_scanner.py -v`
Expected: PASS (the `_parse_ts` reuse still works)

- [ ] **Step 5: Commit**

```bash
git add services/system_stats_parser.py
git commit -m "refactor: drop obsolete SystemStatsParser, keep _parse_ts helper"
```

---

### Task 8: Update `MCP_TOOLS_CATALOG.md`

**Files:**
- Modify: `MCP_TOOLS_CATALOG.md` (`ise_deployment_health` section ~795-869; quick-reference row ~987; backpressure lines ~22, 28, 173, 284, 452)

**Interfaces:** documentation only. No code.

- [ ] **Step 1: Update the section intro**

Locate the `ise_deployment_health` intro (~795). Replace the trailing clause
"with optional log-derived per-node system statistics." so the sentence ends:
"…, with opt-in API-sourced per-node process health and CPU/memory/latency (`diagnostics=true`)."

- [ ] **Step 2: Rewrite the opt-in paragraph (keep it, don't delete)**

Replace the opt-in paragraph (~801) with:

```markdown
Set `diagnostics=true` only when the user's wording signals a problem or explicitly asks to investigate/diagnose (e.g. "down", "broken", "not syncing", "out of sync", "registration failed", "overloaded", "investigate", "diagnose"). Diagnostics fetch per-node process health and CPU/memory/latency from the MnT `getSystemSummaryDetails` API — one call, but the response can be large in big deployments, and it is gated for MnT-node backpressure (may return an `{status: "unavailable"}` block under load). For general status, topology, readiness, HA, or plain "is it healthy?" questions, keep it false.
```

- [ ] **Step 3: Add a process-health question and rename the parameter row**

In "Questions this tool answers", add after the "down/disconnected" bullet:

```markdown
- "Which ISE processes are down on a node?" (with `diagnostics=true`)
```

In the parameter table (~820-823), replace the `deep_diagnostics` row:

```markdown
| `deep_diagnostics` | boolean         | No       | false   | When true, also gather log-derived per-node system statistics (CPU, memory, disk, replication/process indicators). Set true only when wording signals a problem or asks to investigate/diagnose. |
```

with:

```markdown
| `diagnostics` | boolean         | No       | false   | When true, attach API-backed per-node diagnostics (process health + CPU/memory/latency from the MnT `getSystemSummaryDetails` API). Opt-in: the response can be large and the call is gated for MnT backpressure. Set true only when wording signals a problem or asks to investigate/diagnose. |
```

- [ ] **Step 4: Rewrite the diagnostics return shape**

Replace the `diagnostics` bullet block (~846-848):

```markdown
- `diagnostics`: Present only when `deep_diagnostics=true`, otherwise omitted:
  - `observations`: Human-readable derived observations about node health (including replication/process signals)
  - `system_stats`: Log-derived per-node system statistics: top-level `anchor`, `duration_minutes`, and `nodes` (keyed by hostname). Each node is either `{status: "ok", window: {start, end}, sample_count, cpu_percent, memory_percent, disk_percent}` (each metric a `{min, max, avg, latest}` object) or `{status: "unavailable", reason}`.
```

with:

```markdown
- `diagnostics`: Present only when `diagnostics=true`, otherwise omitted:
  - `observations`: Human-readable derived observations about node health (node status, PAN redundancy, and any processes reporting "down").
  - `system_stats`: Per-node system statistics from the MnT `getSystemSummaryDetails` API: top-level `source` (`"getSystemSummaryDetails"`), `duration_minutes` (60), and `nodes` (keyed by hostname). Each node has `reported_status` (the ISE-reported summary status, informational), `processes_down` (process names reporting not-running), `processes` (map of process name → `running` / `disabled` / `not_applicable` / `down` / `unknown:<n>`), and `cpu_percent` / `memory_percent` / `latency` (each a `{min, max, avg, latest}` object, or null when no samples). If the MnT node is busy or the call/parse fails, `system_stats` is `{status: "unavailable", reason}` instead (the base summary is unaffected).
```

- [ ] **Step 5: Update "Use when" and "Best practices"**

Replace the "Use when" bullet (~856):

```markdown
- Investigating replication or node-status problems (with `deep_diagnostics=true`)
```

with:

```markdown
- Investigating replication or node-status problems, or which processes are down on a node (with `diagnostics=true`)
```

Replace the best-practices bullet (~868):

```markdown
- Keep `deep_diagnostics=false` for status/readiness checks; enable it only when a problem is signaled
```

with:

```markdown
- Keep `diagnostics=false` for status/readiness checks; enable it only when a problem is signaled (it is a gated heavy MnT call)
```

- [ ] **Step 6: Fix the quick-reference row**

Replace (~987):

```markdown
| "Investigate why a node is disconnected / not syncing"  | `ise_deployment_health` (deep_diagnostics=true) |
```

with:

```markdown
| "Investigate why a node is disconnected / not syncing"  | `ise_deployment_health` (diagnostics=true) |
```

- [ ] **Step 7: Update the backpressure env-var references**

Replace the `ISE_AUTHLIST_*` names with `ISE_MNT_GATE_*` wherever they appear
(the backpressure paragraph ~22 and the four "Heavy MnT call — gated to
`ISE_AUTHLIST_MAX_CONCURRENCY`" lines ~28, 173, 284, 452). In the backpressure
paragraph, generalize the tunable names to `ISE_MNT_GATE_MAX_CONCURRENCY`,
`ISE_MNT_GATE_MIN_INTERVAL_S`, `ISE_MNT_GATE_BACKOFF_BASE_S`,
`ISE_MNT_GATE_BACKOFF_MAX_S`, and each "Heavy MnT call" line reads
`gated to `ISE_MNT_GATE_MAX_CONCURRENCY` (default 1)`.

- [ ] **Step 8: Verify no stray references remain**

Run: `uv run python -c "import pathlib,re; p=pathlib.Path('MCP_TOOLS_CATALOG.md'); [print(i+1, l.rstrip()) for i,l in enumerate(p.read_text().splitlines()) if re.search('deep_diagnostics|disk_percent|log-derived|ISE_AUTHLIST', l)]"`
Expected: no output.

- [ ] **Step 9: Commit**

```bash
git add MCP_TOOLS_CATALOG.md
git commit -m "docs: update deployment-health catalog for API-backed diagnostics + MnT gate"
```

---

### Task 9: Update the `deep-diagnostics-gating` memory (keep + adapt)

**Files:**
- Modify: `/Users/ronadsou/.claude/projects/-Users-ronadsou-Projects-ISE-opensource-cisco-ise-mcp-official/memory/deep-diagnostics-gating.md`
- Modify: `/Users/ronadsou/.claude/projects/-Users-ronadsou-Projects-ISE-opensource-cisco-ise-mcp-official/memory/MEMORY.md` (pointer line)

**Interfaces:** memory only. Not part of the git repo; no commit.

- [ ] **Step 1: Rewrite the memory body**

Replace the body of `deep-diagnostics-gating.md` (keep the frontmatter, but you
may update `description`) so it references the renamed flag and lighter cost:

```markdown
---
name: deep-diagnostics-gating
description: Only set ise_deployment_health diagnostics=true when user wording signals a problem
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9e621c80-99c5-46fe-966a-01d5afe35f8e
---

When calling the `ise_deployment_health` MCP tool, set `diagnostics=true` ONLY when the user's wording signals something is wrong or asks to investigate/diagnose (e.g. "down", "broken", "why is X failing", "not syncing", "out of sync", "registration failed", "investigate", "diagnose"). For general "is it healthy?", status, topology, readiness, or HA questions, keep it `false`.

**Why:** Diagnostics are opt-in. The flag was renamed from `deep_diagnostics` to `diagnostics`, and the data now comes from one MnT `getSystemSummaryDetails` API call (not per-node log downloads) — lighter, but the response can be large in big deployments and the call is gated for MnT-node backpressure, so it still shouldn't run on plain health checks. I over-triggered the old flag on a general-health request; the user flagged it.

**How to apply:** Default `diagnostics=false`; opt in only on problem-signaling phrasing.
```

- [ ] **Step 2: Update the MEMORY.md pointer**

In `MEMORY.md`, replace the line:

```markdown
- [Deep diagnostics gating](deep-diagnostics-gating.md) — ise_deployment_health deep_diagnostics=true only on problem-signaling wording
```

with:

```markdown
- [Deep diagnostics gating](deep-diagnostics-gating.md) — ise_deployment_health diagnostics=true only on problem-signaling wording
```

- [ ] **Step 3: Update the API-backed feature memory pointer (optional)**

The `api-backed-diagnostics-feature` memory says diagnostics replace the log path
and are "not yet executed." Once this plan is implemented, update its status line
(or leave for the finishing step). No action required for correctness now.

---

### Task 10: Full suite green

**Files:** none (verification).

- [ ] **Step 1: Run the entire test suite**

Run: `uv run pytest -q`
Expected: PASS (no failures, no errors). Investigate and fix any regressions before considering the feature complete.

- [ ] **Step 2: Confirm no lingering old-name references in code**

Run: `uv run python -c "import pathlib,re; [print(f'{p}:{i+1}: {l.strip()}') for p in pathlib.Path('.').rglob('*.py') if '.venv' not in str(p) and '__pycache__' not in str(p) for i,l in enumerate(p.read_text().splitlines()) if re.search('deep_diagnostics|AuthListGate|auth_list_gate|ISE_AUTHLIST|authlist_(max|min|backoff)', l)]"`
Expected: no output. (Descriptive test method names containing the word "authlist" are acceptable; symbol/env references are not.)
