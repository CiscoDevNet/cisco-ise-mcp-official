# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import defusedxml.ElementTree as ET
from typing import Dict, Any, List, Optional, Callable, Tuple
from logger import logger


def parse_active_session_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse the ActiveList XML response from ISE MNT API into a Python dictionary.
    
    Expected XML format:
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <activeList noOfActiveSession="1">
        <activeSession>
            <user_name>thomas</user_name>
            <calling_station_id>BA:4B:FB:77:B8:BF</calling_station_id>
            <nas_ip_address>10.80.60.150</nas_ip_address>
            <server>ise</server>
            <framed_ip_address>10.251.204.55</framed_ip_address>
            <framed_ipv6_address/>
            <audit_session_id>0A50963200000000C2E7E7E5</audit_session_id>
            <acct_session_id>00000001</acct_session_id>
            <nas_ipv6_address/>
        </activeSession>
    </activeList>
    
    Args:
        xml_string: The XML response string from the MNT API
        
    Returns:
        Dictionary with 'noOfActiveSession' and 'sessions' list
        
    Raises:
        ET.ParseError: If the XML is malformed
        ValueError: If the XML structure is unexpected
    """
    try:
        root = ET.fromstring(xml_string)
        
        # Validate root element
        if root.tag != "activeList":
            raise ValueError(f"Expected root element 'activeList', got '{root.tag}'")
        
        # Get the count of active sessions from attribute
        no_of_sessions = root.get("noOfActiveSession", "0")
        
        # Parse each activeSession element
        sessions = []
        for session_elem in root.findall("activeSession"):
            session_data = {}
            
            # Extract all child elements
            for child in session_elem:
                # Get text content, use None if empty
                value = child.text if child.text and child.text.strip() else None
                session_data[child.tag] = value
            
            sessions.append(session_data)
        
        result = {
            "noOfActiveSession": int(no_of_sessions),
            "sessions": sessions
        }
        
        logger.debug("Parsed active sessions from XML", count=len(sessions))
        return result
        
    except ET.ParseError as e:
        logger.error("Failed to parse XML", error=str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error parsing active session XML", error=str(e))
        raise


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
    context = ET.iterparse(source, events=("start", "end"))
    _, root = next(context)
    for event, elem in context:
        if event != "end" or elem.tag != "activeSession":
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


def _local_tag(elem) -> str:
    """Return an element's tag with any XML namespace prefix stripped."""
    tag = elem.tag
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _find_local(parent, name: str):
    """Find a direct child by local tag name, ignoring any namespace.

    ``Element.find(name)`` misses namespaced children, and the MnT responses we
    parse here are inconsistent about declaring one.
    """
    for child in parent:
        if _local_tag(child) == name:
            return child
    return None


def parse_session_count_xml(xml_string: str) -> int:
    """Parse a ``<sessionCount>`` response from the MnT session-count APIs.

    Shared by ``Session/ActiveCount``, ``Session/PostureCount`` and
    ``Session/ProfilerCount``, all of which return::

        <sessionCount>
            <count>5</count>
        </sessionCount>

    Raises:
        ET.ParseError: If the XML is malformed.
        ValueError: If the root element is not ``sessionCount``, ``<count>`` is
            missing/blank, or its text is not an integer.
    """
    try:
        root = ET.fromstring(xml_string)
        root_tag = _local_tag(root)
        if root_tag != "sessionCount":
            raise ValueError(f"Expected root element 'sessionCount', got '{root_tag}'")
        count_elem = _find_local(root, "count")
        if count_elem is None or not (count_elem.text and count_elem.text.strip()):
            raise ValueError("Missing <count> element in sessionCount response")
        return int(count_elem.text.strip())
    except ET.ParseError as e:
        logger.error("Failed to parse sessionCount XML", error=str(e))
        raise
    except (ValueError, TypeError) as e:
        logger.error("Unexpected value in sessionCount XML", error=str(e))
        raise


def parse_mnt_error_body(xml_string: str) -> Optional[str]:
    """Extract ``<internal-error-info>`` from an MnT REST error response body.

    ISE returns a structured body alongside HTTP 500::

        <mnt-rest-result>
          <http-code>500</http-code>
          <internal-error-info>Session data is not available for 4.4.4.1.</internal-error-info>
          ...
        </mnt-rest-result>

    That text is the only place ISE says WHY the call failed -- "no such
    session" and a genuine backend fault are both HTTP 500 -- so callers use it
    both to build a useful error message and to tell the two apart.

    Returns the text when present, else ``None`` (including for malformed or
    unrecognised bodies) so callers can fall back to a generic message. Parsing
    an error body must never itself raise and mask the original HTTP error.
    """
    try:
        root = ET.fromstring(xml_string)
        if _local_tag(root) != "mnt-rest-result":
            return None
        elem = _find_local(root, "internal-error-info")
        if elem is not None and elem.text and elem.text.strip():
            return elem.text.strip()
    except Exception:  # noqa: BLE001 -- see docstring
        logger.debug("MnT error body was not a parseable mnt-rest-result")
    return None


# ISE reports "this identifier has no session" as HTTP 500 with this phrase in
# <internal-error-info>, not as a 404 or an empty document. Matching on message
# text is fragile, but it is the only signal ISE gives, and the distinction
# matters: an absent session is a normal empty result, while every other 500 is
# a fault that must not be reported as "nothing found".
_NO_SESSION_MARKER = "is not available"


def mnt_error_is_missing_session(body: Optional[str]) -> bool:
    """True when an MnT error body means "no session for this identifier"."""
    detail = parse_mnt_error_body(body) if body else None
    return bool(detail) and _NO_SESSION_MARKER in detail


# Fields of a <sessionParameters> body that map onto ActiveSession, as
# {ActiveSession field: sessionParameters element}. Identity apart from
# ``server``, which MnT calls ``acs_server`` in this response shape.
_SESSION_PARAMS_TO_ACTIVE_SESSION = {
    "user_name": "user_name",
    "calling_station_id": "calling_station_id",
    "nas_ip_address": "nas_ip_address",
    "framed_ip_address": "framed_ip_address",
    "audit_session_id": "audit_session_id",
    "acct_session_id": "acct_session_id",
    "nas_ipv6_address": "nas_ipv6_address",
    "server": "acs_server",
}


def parse_session_detail_as_active_session(xml_string: str) -> Dict[str, Any]:
    """Parse a ``<sessionParameters>`` body into an ActiveSession-shaped dict.

    The single-identifier MnT endpoints (``Session/MACAddress``,
    ``Session/UserName``, ``Session/IPAddress``, ``Session/EndPointIPAddress``)
    return the much richer ``<sessionParameters>`` document rather than
    ``<activeList>``. This projects it down to the ActiveSession fields so a
    direct lookup and an AuthList scan can return the same result shape.

    Returns a dict suitable for ``ActiveSession(**result)``.

    Raises:
        ET.ParseError: If the XML is malformed.
        ValueError: If the root element is not ``sessionParameters``.
    """
    try:
        root = ET.fromstring(xml_string)
        root_tag = _local_tag(root)
        if root_tag != "sessionParameters":
            raise ValueError(f"Expected root element 'sessionParameters', got '{root_tag}'")

        raw: Dict[str, Any] = {}
        for child in root:
            text = child.text
            raw[_local_tag(child)] = text.strip() if text and text.strip() else None

        return {
            field: raw.get(source)
            for field, source in _SESSION_PARAMS_TO_ACTIVE_SESSION.items()
        }
    except ET.ParseError as e:
        logger.error("Failed to parse sessionParameters XML", error=str(e))
        raise
    except ValueError as e:
        logger.error("Unexpected sessionParameters XML structure", error=str(e))
        raise


# Keys to extract from other_attr_string (":!:" delimited Key=Value pairs)
_OTHER_ATTR_KEYS = frozenset({
    "AuthenticationStatus",
    "IdentityPolicyMatchedRule",
    "Protocol",
    "ISEPolicySetName",
    "AuthorizationPolicyMatchedRule",
    "StepLatency",
})

# Map XML/key names to SessionDetail field names (snake_case)
_OTHER_ATTR_FIELD_MAP = {
    "AuthenticationStatus": "authentication_status",
    "IdentityPolicyMatchedRule": "identity_policy_matched_rule",
    "Protocol": "protocol",
    "ISEPolicySetName": "ise_policy_set_name",
    "AuthorizationPolicyMatchedRule": "authorization_policy_matched_rule",
    "StepLatency": "steps_latencies",
}


def _parse_steps_latencies(raw: Optional[str]) -> Optional[List[Dict[str, int]]]:
    """Parse a StepLatency value string into a list of step-index/latency dicts.

    The raw format is ``1=0;2=0;3=1;...`` where each token is
    ``<index>=<latency_ms>``.  The index maps directly to the
    execution_steps array position (e.g. index 1 -> execution_steps[1]).
    Entries are sorted by index.

    Each returned dict has ``step_index`` (int) and ``latency_ms`` (int),
    ready for construction of ``StepLatency`` model instances.

    Returns None if *raw* is empty or malformed.
    """
    if not raw or not raw.strip():
        return None
    try:
        pairs: List[tuple[int, int]] = []
        for token in raw.split(";"):
            token = token.strip()
            if not token:
                continue
            pos_str, _, lat_str = token.partition("=")
            pairs.append((int(pos_str), int(lat_str)))
        if not pairs:
            return None
        pairs.sort(key=lambda p: p[0])
        return [{"step_index": pos, "latency_ms": lat} for pos, lat in pairs]
    except (ValueError, TypeError):
        logger.debug("Failed to parse StepLatency value", raw=raw)
        return None


def _parse_other_attr_string(other_attr_string: Optional[str]) -> Dict[str, Any]:
    """Extract required key-value pairs from other_attr_string (:!: delimited).

    Handles the special ``StepLatency`` key whose value is parsed into a
    list of ``{step_index, latency_ms}`` dicts via ``_parse_steps_latencies``.
    """
    result: Dict[str, Any] = {
        "authentication_status": None,
        "identity_policy_matched_rule": None,
        "protocol": None,
        "ise_policy_set_name": None,
        "authorization_policy_matched_rule": None,
        "steps_latencies": None,
    }
    if not other_attr_string or not other_attr_string.strip():
        return result
    delimiter: str = ":!:"
    for part in other_attr_string.split(delimiter):
        part = part.strip()
        if "=" not in part:
            continue
        key, _, value = part.partition("=")
        key = key.strip()
        if key in _OTHER_ATTR_KEYS:
            field_name = _OTHER_ATTR_FIELD_MAP[key]
            result[field_name] = value.strip() if value else None

    if isinstance(result.get("steps_latencies"), str):
        result["steps_latencies"] = _parse_steps_latencies(result["steps_latencies"])

    return result


def parse_session_detail_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse the sessionParameters XML response from ISE MNT Last Session by Attributes API.

    Extracts 16 direct child elements and 6 key-value pairs from other_attr_string.
    Derives authentication_result ("Passed"/"Failed") from raw <passed>/<failed> XML elements.
    Empty elements become None.

    Args:
        xml_string: The XML response string from the MNT API (e.g. Session/UserName/...).

    Returns:
        Dictionary suitable for SessionDetail model:

        From direct XML child elements (15 + 1 derived):
            authentication_result, user_name, nas_ip_address, calling_station_id,
            identity_group, network_device_name, acs_server, authentication_method,
            authentication_protocol, framed_ip_address, auth_acs_timestamp,
            posture_status, selected_azn_profiles, identity_store, response_time,
            execution_steps.

        From other_attr_string key-value pairs (6):
            authentication_status, identity_policy_matched_rule, protocol,
            ise_policy_set_name, authorization_policy_matched_rule, steps_latencies.

        execution_steps is parsed from a comma-separated XML text value into a
        List[str] of step-code strings.  steps_latencies is parsed from the
        StepLatency value in other_attr_string into a List[Dict] of
        {step_index, latency_ms} entries.  Both fields are excluded from
        SessionDetail serialization (internal use for latency context resolution).

    Raises:
        ET.ParseError: If the XML is malformed
        ValueError: If the XML structure is unexpected
    """
    try:
        root = ET.fromstring(xml_string)
        root_tag = root.tag.split("}", 1)[-1] if "}" in root.tag else root.tag
        if root_tag != "sessionParameters":
            raise ValueError(f"Expected root element 'sessionParameters', got '{root.tag}'")

        data: Dict[str, Any] = {}

        for child in root:
            tag = child.tag
            if "}" in tag:
                tag = tag.split("}", 1)[1]
            text = child.text if child.text and child.text.strip() else None
            data[tag] = text

        other_attr = data.pop("other_attr_string", None)
        parsed_other = _parse_other_attr_string(other_attr)
        data.update(parsed_other)

        raw_passed = data.pop("passed", None)
        raw_failed = data.pop("failed", None)
        if raw_passed == "1":
            data["authentication_result"] = "Passed"
        elif raw_failed == "1":
            data["authentication_result"] = "Failed"
        else:
            data["authentication_result"] = None

        if "response_time" in data and data["response_time"] is not None:
            try:
                data["response_time"] = int(data["response_time"])
            except (TypeError, ValueError):
                data["response_time"] = None

        if data.get("posture_status") == "":
            data["posture_status"] = None

        raw_steps = data.get("execution_steps")
        if raw_steps and isinstance(raw_steps, str) and raw_steps.strip():
            data["execution_steps"] = [s.strip() for s in raw_steps.split(",") if s.strip()]
        else:
            data["execution_steps"] = None

        result = {k: v for k, v in data.items() if k in (
            "authentication_result", "user_name", "nas_ip_address", "calling_station_id",
            "identity_group", "network_device_name", "acs_server", "authentication_method",
            "authentication_protocol", "framed_ip_address", "auth_acs_timestamp",
            "posture_status", "selected_azn_profiles", "identity_store", "response_time",
            "authentication_status", "identity_policy_matched_rule", "protocol",
            "ise_policy_set_name", "authorization_policy_matched_rule",
            "execution_steps", "steps_latencies",
            "failure_reason", "response",
        )}
        logger.debug("Parsed sessionParameters XML for Last Session API")
        return result

    except ET.ParseError as e:
        logger.error("Failed to parse session detail XML", error=str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error parsing session detail XML", error=str(e))
        raise

def parse_auth_status_xml(xml_string: str) -> List[Dict[str, Any]]:
    """Parse the AuthStatus XML response from ISE MNT API into a list of auth-status dicts.

    Expected XML format:
    <authStatusOutputList>
        <authStatusList key="...">
            <authStatusElements>
                <passed xsi:type="xs:boolean" ...>false</passed>
                <failed xsi:type="xs:boolean" ...>true</failed>
                <user_name>testUser</user_name>
                ...
            </authStatusElements>
        </authStatusList>
    </authStatusOutputList>

    The ``<failed>`` and ``<passed>`` XML elements are xs:boolean strings
    ("true"/"false") and are converted to Python bools.  An
    ``authentication_result`` field ("Passed"/"Failed") is derived from them.
    The ``execution_steps`` comma-separated string is split into List[str].

    Args:
        xml_string: Raw XML response from the AuthStatus MNT API.

    Returns:
        List of dicts, one per ``<authStatusElements>``.  Each dict maps
        element tag names to their text values (or None for empty elements).

    Raises:
        ET.ParseError: If the XML is malformed.
        ValueError: If the root element is not ``authStatusOutputList``.
    """
    try:
        root = ET.fromstring(xml_string)

        root_tag = root.tag.split("}", 1)[-1] if "}" in root.tag else root.tag
        if root_tag != "authStatusOutputList":
            raise ValueError(f"Expected root element 'authStatusOutputList', got '{root.tag}'")

        results: List[Dict[str, Any]] = []

        for status_list in root.findall("authStatusList"):
            for elem_group in status_list.findall("authStatusElements"):
                data: Dict[str, Any] = {}

                for child in elem_group:
                    tag = child.tag.split("}", 1)[-1] if "}" in child.tag else child.tag

                    if len(child) > 0:
                        continue

                    text = child.text if child.text and child.text.strip() else None
                    data[tag] = text

                raw_passed = data.pop("passed", None)
                raw_failed = data.pop("failed", None)
                passed_bool = raw_passed is not None and raw_passed.lower() == "true"
                failed_bool = raw_failed is not None and raw_failed.lower() == "true"
                data["passed"] = passed_bool
                data["failed"] = failed_bool

                if passed_bool:
                    data["authentication_result"] = "Passed"
                elif failed_bool:
                    data["authentication_result"] = "Failed"
                else:
                    data["authentication_result"] = None

                raw_steps = data.get("execution_steps")
                if raw_steps and isinstance(raw_steps, str) and raw_steps.strip():
                    data["execution_steps"] = [s.strip() for s in raw_steps.split(",") if s.strip()]
                else:
                    data["execution_steps"] = None

                results.append(data)

        logger.debug("Parsed auth status elements from XML", count=len(results))
        return results

    except ET.ParseError as e:
        logger.error("Failed to parse auth status XML", error=str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error parsing auth status XML", error=str(e))
        raise


def parse_failure_reasons_xml(xml_string: str) -> Dict[str, Dict[str, Optional[str]]]:
    """Parse the FailureReasons XML response from ISE MNT API.

    Expected XML format:
    <failureReasonList>
        <failureReason id="22040">
            <code>22040 Wrong password</code>
            <cause>The user provided an incorrect password.</cause>
            <resolution>Verify the user credentials and try again.</resolution>
        </failureReason>
    </failureReasonList>

    Args:
        xml_string: Raw XML response from the FailureReasons MNT API.

    Returns:
        Dict keyed by failure reason id (e.g. "22040").  Each value is a dict
        with keys ``code``, ``cause``, ``resolution`` (values may be None).

    Raises:
        ET.ParseError: If the XML is malformed.
        ValueError: If the root element is not ``failureReasonList``.
    """
    try:
        root = ET.fromstring(xml_string)

        root_tag = root.tag.split("}", 1)[-1] if "}" in root.tag else root.tag
        if root_tag != "failureReasonList":
            raise ValueError(f"Expected root element 'failureReasonList', got '{root.tag}'")

        catalog: Dict[str, Dict[str, Optional[str]]] = {}

        for reason_elem in root:
            tag = reason_elem.tag.split("}", 1)[-1] if "}" in reason_elem.tag else reason_elem.tag
            if tag != "failureReason":
                continue

            reason_id = reason_elem.get("id")
            if not reason_id:
                continue

            fields: Dict[str, Optional[str]] = {"code": None, "cause": None, "resolution": None}
            for child in reason_elem:
                child_tag = child.tag.split("}", 1)[-1] if "}" in child.tag else child.tag
                if child_tag in fields:
                    fields[child_tag] = child.text.strip() if child.text else None

            catalog[reason_id] = fields

        logger.debug("Parsed failure reasons catalog", count=len(catalog))
        return catalog

    except ET.ParseError as e:
        logger.error("Failed to parse failure reasons XML", error=str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error parsing failure reasons XML", error=str(e))
        raise


def parse_msg_catalog(xml_path: str) -> Dict[str, str]:
    """Parse msg_cat.xml into a code-to-text lookup dict.

    Streams the file with iterparse and clears processed subtrees from the
    root element so that peak memory stays proportional to a single
    ``<message>`` subtree rather than the entire document.

    Args:
        xml_path: Filesystem path to the message catalog XML file.

    Returns:
        Dict mapping message code (str) to its English text (str).
        Returns an empty dict if the file is missing or unparseable.
    """
    catalog: Dict[str, str] = {}
    try:
        context = ET.iterparse(xml_path, events=("start", "end"))
        _, root = next(context)
        for event, elem in context:
            if event != "end" or elem.tag != "message":
                continue
            code = elem.get("code")
            if code:
                text_elem = elem.find("text")
                if text_elem is not None and text_elem.text:
                    catalog[code] = text_elem.text.strip()
            root.clear()
    except FileNotFoundError:
        logger.warning("Message catalog file not found", path=xml_path)
    except ET.ParseError as e:
        logger.warning("Failed to parse message catalog XML", error=str(e))
    except Exception as e:
        logger.warning("Unexpected error loading message catalog", error=str(e))

    logger.info("Loaded message catalog", count=len(catalog), path=xml_path)
    return catalog


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
