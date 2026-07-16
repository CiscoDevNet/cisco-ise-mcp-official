# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import ipaddress
import re
from typing import Optional

from models.error_models import ErrorCategory, raise_tool_error


_HOSTNAME_RE = re.compile(r"^[a-zA-Z][\w\-]*$")


def normalize_mac_address(mac: str) -> str:
    """Normalize a MAC address to uppercase colon-separated format (XX:XX:XX:XX:XX:XX).

    Handles colon, dash, dot (Cisco), and bare formats.
    Returns the original string uppercased if the cleaned length is not 12 hex chars.
    """
    clean = mac.upper().replace(":", "").replace("-", "").replace(".", "")
    if len(clean) != 12:
        return mac.upper()
    return ":".join(clean[i : i + 2] for i in range(0, 12, 2))


def _is_valid_mac(mac: str) -> bool:
    clean = re.sub(r"[:\-.]", "", mac.strip())
    return len(clean) == 12 and all(c in "0123456789abcdefABCDEF" for c in clean)


def validate_mac_address(value: str) -> str:
    """Validate and normalize a MAC address.

    Returns the normalized MAC (XX:XX:XX:XX:XX:XX) on success.
    Raises a CLIENT_ERROR ToolError on invalid format.
    """
    value = value.strip()
    if not _is_valid_mac(value):
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_MAC_ADDRESS",
            f"'{value}' is not a valid MAC address. "
            "Expected formats: XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXX.XXXX.XXXX, or XXXXXXXXXXXX.",
        )
    return normalize_mac_address(value)


def validate_ip_address(value: str) -> str:
    """Validate an IP address (v4 or v6).

    Returns the stripped string on success.
    Raises a CLIENT_ERROR ToolError on invalid format.
    """
    value = value.strip()
    try:
        ipaddress.ip_address(value)
    except ValueError:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_IP_ADDRESS",
            f"'{value}' is not a valid IP address.",
        )
    return value


def validate_hostname(value: str) -> str:
    """Validate an ISE node hostname.

    Matches the deployment API's contract: must start with a letter,
    contain only word chars/hyphens, length 1-64. Rejecting other input
    also guards against filter-string injection (dots, ampersands, etc.).

    Returns the stripped hostname on success.
    Raises a CLIENT_ERROR ToolError on invalid format.
    """
    value = value.strip()
    if not value or len(value) > 64 or not _HOSTNAME_RE.match(value):
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_HOSTNAME",
            f"'{value}' is not a valid ISE node hostname. "
            "Expected 1-64 characters, starting with a letter and containing "
            "only letters, digits, underscores, or hyphens (no dots or FQDNs).",
        )
    return value


def validate_minutes(value: int, *, max_minutes: int) -> int:
    """Validate that *minutes* is within [1, max_minutes].

    Returns the value unchanged on success.
    Raises a CLIENT_ERROR ToolError when out of range, with a user-ready
    message. The sub-1-minute case is called out explicitly because the
    common trigger is a user asking for a "last N seconds" window, which the
    routing LLM floors to 0; the message tells the user the smallest
    supported window so they can retry.
    """
    if value < 1:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_MINUTES",
            "The smallest supported lookback window is 1 minute. "
            "Please retry with a window of at least 1 minute (for example, 'in the last 1 minute').",
        )
    if value > max_minutes:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_MINUTES",
            f"The largest supported lookback window is {max_minutes} minutes "
            f"({max_minutes // 60} hours). Please retry with a smaller window (got {value} minutes).",
        )
    return value


def validate_limit(value: int, *, max_limit: int) -> int:
    """Validate that *limit* is within [1, max_limit].

    Returns the value unchanged on success.
    Raises a CLIENT_ERROR ToolError when out of range.
    """
    if value < 1 or value > max_limit:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_LIMIT",
            f"limit must be between 1 and {max_limit}, got {value}.",
        )
    return value


_MAX_USERNAME_LENGTH = 256


def validate_username(value: str) -> str:
    """Validate and sanitize a username string.

    Strips whitespace, rejects empty strings, control characters, and
    values exceeding 256 characters.

    Returns the stripped username on success.
    Raises a CLIENT_ERROR ToolError on invalid input.
    """
    value = value.strip()
    if not value:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_USERNAME",
            "Username must not be empty.",
        )
    if len(value) > _MAX_USERNAME_LENGTH:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_USERNAME",
            f"Username exceeds maximum length of {_MAX_USERNAME_LENGTH} characters.",
        )
    if any(c < '\x20' and c not in ('\t',) for c in value):
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_USERNAME",
            "Username contains invalid control characters.",
        )
    return value


# ---------------------------------------------------------------------------
# Policy tool validators
# ---------------------------------------------------------------------------

# Mirrors the OpenAPI policy-set name pattern from api_specs/policy-bundled.yaml
# (PolicySet.name): alphanumerics, underscore, hyphen, period, parentheses, space.
_POLICY_SET_NAME_PATTERN = re.compile(r"^[\w\-\.\(\)\ ]+$")
_MAX_POLICY_SET_NAME_LENGTH = 256
_MAX_NAME_SUBSTRING_LENGTH = 256

# Allowed characters for substring filters: alphanumerics, underscore, hyphen,
# period, parentheses, space, colon, slash, plus, comma, ampersand. Wide enough
# to cover ISE-generated names (e.g. "AD:abc.com", "Default Network Access")
# while excluding URL/control characters and quote injection vectors.
_NAME_SUBSTRING_PATTERN = re.compile(r"^[\w\-\.\(\)\ :/+,&]+$")

_VALID_POLICY_SET_STATES = ("all", "enabled", "disabled", "monitor")
_VALID_RULE_STATES = ("all", "enabled", "disabled")
_VALID_CONDITION_SCOPES = ("all", "policyset", "authentication", "authorization")


def validate_policy_set_name(value: str) -> str:
    """Validate a Cisco ISE policy-set name (exact-match lookup).

    Mirrors the OpenAPI pattern ``^[\\w\\-\\.\\(\\)\\ ]+$`` from
    ``api_specs/policy-bundled.yaml``. Strips outer whitespace; rejects
    empty values and values exceeding 256 characters.

    Returns the stripped name on success.
    Raises a CLIENT_ERROR ToolError on invalid input.
    """
    value = value.strip()
    if not value:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_POLICY_SET_NAME",
            "policy_set_name must not be empty.",
        )
    if len(value) > _MAX_POLICY_SET_NAME_LENGTH:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_POLICY_SET_NAME",
            f"policy_set_name exceeds maximum length of {_MAX_POLICY_SET_NAME_LENGTH} characters.",
        )
    if not _POLICY_SET_NAME_PATTERN.match(value):
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_POLICY_SET_NAME",
            (
                f"'{value}' is not a valid policy-set name. "
                "Allowed characters: letters, digits, underscore, hyphen, period, parentheses, space."
            ),
        )
    return value


def validate_name_substring(value: str, *, field_name: str = "name_substring") -> str:
    """Validate a substring-search filter value.

    Wider character set than ``validate_policy_set_name`` because substring
    search is used against rule names, profile names, library condition
    names, identity store names, etc., which may contain characters like
    ``:`` (e.g. ``AD:corp.example.com``), ``/`` and ``+``.

    Returns the stripped value on success.
    Raises a CLIENT_ERROR ToolError on invalid input.
    """
    value = value.strip()
    if not value:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_NAME_SUBSTRING",
            f"{field_name} must not be empty.",
        )
    if len(value) > _MAX_NAME_SUBSTRING_LENGTH:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_NAME_SUBSTRING",
            f"{field_name} exceeds maximum length of {_MAX_NAME_SUBSTRING_LENGTH} characters.",
        )
    if not _NAME_SUBSTRING_PATTERN.match(value):
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_NAME_SUBSTRING",
            (
                f"'{value}' is not a valid {field_name}. "
                "Allowed characters: letters, digits, underscore, hyphen, period, parentheses, space, colon, slash, plus, comma, ampersand."
            ),
        )
    return value


def validate_policy_set_state_filter(value: str) -> str:
    """Validate the policy-set ``state_filter`` enum.

    Returns the lowercased value on success.
    Raises a CLIENT_ERROR ToolError on invalid input.
    """
    normalized = (value or "").strip().lower()
    if normalized not in _VALID_POLICY_SET_STATES:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_STATE_FILTER",
            f"state_filter must be one of {list(_VALID_POLICY_SET_STATES)}, got '{value}'.",
        )
    return normalized


def validate_rule_state_filter(value: str) -> str:
    """Validate the rule ``state_filter`` enum.

    Returns the lowercased value on success.
    Raises a CLIENT_ERROR ToolError on invalid input.
    """
    normalized = (value or "").strip().lower()
    if normalized not in _VALID_RULE_STATES:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_STATE_FILTER",
            f"state_filter must be one of {list(_VALID_RULE_STATES)}, got '{value}'.",
        )
    return normalized


def validate_condition_scope_filter(value: str) -> str:
    """Validate the library-condition ``scope_filter`` enum.

    Returns the lowercased value on success.
    Raises a CLIENT_ERROR ToolError on invalid input.
    """
    normalized = (value or "").strip().lower()
    if normalized not in _VALID_CONDITION_SCOPES:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_SCOPE_FILTER",
            f"scope_filter must be one of {list(_VALID_CONDITION_SCOPES)}, got '{value}'.",
        )
    return normalized


def validate_min_hit_counts(value: Optional[int]) -> Optional[int]:
    """Validate that ``min_hit_counts``, when provided, is a non-negative integer.

    Returns the value unchanged on success.
    Raises a CLIENT_ERROR ToolError when negative.
    """
    if value is None:
        return None
    if value < 0:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_MIN_HIT_COUNTS",
            f"min_hit_counts must be a non-negative integer, got {value}.",
        )
    return value


def validate_max_hit_counts(value: Optional[int]) -> Optional[int]:
    """Validate that ``max_hit_counts``, when provided, is a non-negative integer.

    Returns the value unchanged on success.
    Raises a CLIENT_ERROR ToolError when negative.
    """
    if value is None:
        return None
    if value < 0:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_MAX_HIT_COUNTS",
            f"max_hit_counts must be a non-negative integer, got {value}.",
        )
    return value


def validate_hit_counts_range(
    min_hit_counts: Optional[int],
    max_hit_counts: Optional[int],
) -> None:
    """Ensure ``min_hit_counts`` does not exceed ``max_hit_counts`` when both set.

    Assumes both values have already been validated as non-negative.
    Raises a CLIENT_ERROR ToolError when ``min_hit_counts > max_hit_counts``.
    """
    if (
        min_hit_counts is not None
        and max_hit_counts is not None
        and min_hit_counts > max_hit_counts
    ):
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_HIT_COUNT_RANGE",
            (
                f"min_hit_counts ({min_hit_counts}) must be <= max_hit_counts "
                f"({max_hit_counts})."
            ),
        )


def validate_latency_range(
    min_latency_ms: Optional[int],
    max_latency_ms: Optional[int],
) -> None:
    """Validate that latency filter bounds are non-negative and consistent.

    Raises a CLIENT_ERROR ToolError on invalid values.
    """
    if min_latency_ms is not None and min_latency_ms < 0:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_MIN_LATENCY",
            "min_latency_ms must be a non-negative integer.",
        )
    if max_latency_ms is not None and max_latency_ms < 0:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_MAX_LATENCY",
            "max_latency_ms must be a non-negative integer.",
        )
    if (
        min_latency_ms is not None and
        max_latency_ms is not None and
        min_latency_ms > max_latency_ms
    ):
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_LATENCY_RANGE",
            f"min_latency_ms ({min_latency_ms}) must be <= max_latency_ms ({max_latency_ms}).",
        )
