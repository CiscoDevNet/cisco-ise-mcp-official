# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

from models.error_models import ErrorCategory, raise_tool_error
from utils.input_validators import validate_limit

_EXPIRY_DAYS_MIN = 1
_EXPIRY_DAYS_MAX = 365

_CERT_LIMIT_MAX = 100

_VALID_STATUS_FILTERS = ("all", "enabled", "disabled")


def validate_expiry_days(value: int) -> int:
    """Validate that expiry_days is within [1, 365].

    Returns the value unchanged on success.
    Raises a CLIENT_ERROR ToolError when out of range.
    """
    if value < _EXPIRY_DAYS_MIN or value > _EXPIRY_DAYS_MAX:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_EXPIRY_DAYS",
            f"expiry_days must be between {_EXPIRY_DAYS_MIN} and {_EXPIRY_DAYS_MAX}, got {value}. "
            "Example: expiry_days=90 to find certs expiring within the next 90 days.",
        )
    return value


def validate_cert_limit(value: int) -> int:
    """Validate that the certificate result limit is within [1, 100].

    Thin wrapper around :func:`utils.input_validators.validate_limit` that
    pins the upper bound to the certificate-specific maximum so behaviour
    (error code ``INVALID_LIMIT`` and message format) stays consistent
    across all tools.
    """
    return validate_limit(value, max_limit=_CERT_LIMIT_MAX)


def validate_cert_status_filter(value: str) -> Literal["all", "enabled", "disabled"]:
    """Validate that status_filter is one of 'all', 'enabled', or 'disabled'.

    Returns the validated string on success.
    Raises a CLIENT_ERROR ToolError on invalid values.
    """
    normalised = value.strip().lower()
    if normalised not in _VALID_STATUS_FILTERS:
        raise_tool_error(
            ErrorCategory.CLIENT_ERROR,
            "INVALID_STATUS_FILTER",
            f"status_filter must be one of {_VALID_STATUS_FILTERS}, got '{value}'. "
            "Use 'enabled' to focus on operationally active certificates.",
        )
    return normalised  # type: ignore[return-value]
