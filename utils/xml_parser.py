# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import defusedxml.ElementTree as ET
from typing import Dict, Any, List, Optional
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
