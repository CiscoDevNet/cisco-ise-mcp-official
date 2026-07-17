# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""
Endpoint string guardrails for ISE clients.

These helpers reject obviously dangerous ``endpoint`` arguments before
they get concatenated to a client's ``base_url``. Necessary because
tool-handler arguments may originate (indirectly) from LLM-supplied
inputs, and a successful path-traversal or scheme-injection on
``endpoint`` could redirect requests to unintended destinations.

The checks are intentionally minimal (guardrails, not an allow-list);
allow-listing per client is a GA item.
"""

from typing import Final

_FORBIDDEN_SUBSTRINGS: Final[tuple[str, ...]] = (
    "://",
    "..",
    "\\",
    "\r",
    "\n",
)


def validate_endpoint(endpoint: str) -> str:
    """Validate a relative endpoint path before URL concatenation.

    Returns the input unchanged on success. Raises ``ValueError`` for:
        - empty or non-string input
        - leading ``/`` (would escape the base path)
        - any of the forbidden substrings (scheme injection, traversal,
          backslash, CR/LF header smuggling)
    """
    if not isinstance(endpoint, str) or not endpoint:
        raise ValueError("endpoint must be a non-empty string")
    if endpoint.startswith("/"):
        raise ValueError("endpoint must not start with '/'")
    for bad in _FORBIDDEN_SUBSTRINGS:
        if bad in endpoint:
            raise ValueError(f"endpoint contains forbidden sequence: {bad!r}")
    return endpoint


def assert_url_under_base(url: str, base_url: str) -> None:
    """Defense-in-depth check that the constructed URL stays under ``base_url``."""
    if not url.startswith(base_url):
        raise ValueError("constructed URL escaped base_url")
