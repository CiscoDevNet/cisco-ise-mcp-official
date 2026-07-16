# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Pure helper for flattening an ISE condition tree to a human-readable string.

Lives in ``utils`` (not ``services``) so it can be safely imported by both
``tools/`` and ``services/`` without creating an import cycle.
"""

from typing import Optional


_AND_CONDITION_TYPES = {"ConditionAndBlock", "LibraryConditionAndBlock"}
_OR_CONDITION_TYPES = {"ConditionOrBlock", "LibraryConditionOrBlock"}
_BLOCK_CONDITION_TYPES = _AND_CONDITION_TYPES | _OR_CONDITION_TYPES
_ATTRIBUTE_CONDITION_TYPES = {"ConditionAttributes", "LibraryConditionAttributes"}
_REFERENCE_CONDITION_TYPES = {"ConditionReference"}


def condition_to_summary(
    condition: Optional[dict], *, _nested: bool = False
) -> Optional[str]:
    """Walk an ISE condition tree and return a human-readable summary string.

    Returns None when *condition* is None or empty.
    """
    if not condition:
        return None

    condition_type = condition.get("conditionType", "")
    is_negate = condition.get("isNegate", False)

    if condition_type in _ATTRIBUTE_CONDITION_TYPES:
        dictionary = condition.get("dictionaryName", "")
        attribute = condition.get("attributeName", "")
        operator = condition.get("operator", "")
        value = condition.get("attributeValue", "")
        dict_value = condition.get("dictionaryValue", "")
        display_value = f"{dict_value}:{value}" if dict_value else value
        text = f"{dictionary}:{attribute} {operator} {display_value}"

    elif condition_type in _REFERENCE_CONDITION_TYPES:
        text = condition.get("name") or condition.get("id", "unknown")

    elif condition_type in _BLOCK_CONDITION_TYPES:
        joiner = " AND " if condition_type in _AND_CONDITION_TYPES else " OR "
        children = condition.get("children") or []
        parts = [
            condition_to_summary(child, _nested=True)
            for child in children
        ]
        parts = [p for p in parts if p]
        if not parts:
            return None
        text = joiner.join(parts)
        if _nested and len(parts) > 1:
            text = f"({text})"
        if is_negate:
            return f"NOT ({text})"
        return text

    elif condition_type == "TimeAndDateCondition":
        text = "TimeAndDate condition"

    else:
        text = condition.get("name") or f"unknown condition ({condition_type})"

    if is_negate:
        text = f"NOT {text}"
    return text
