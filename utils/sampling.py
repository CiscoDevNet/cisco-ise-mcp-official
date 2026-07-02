# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

"""Pure helper for building a plain-language sampling note.

Tool results often return a bounded SAMPLE of a larger matching set, capped by
a request limit to fit the SLM context window. This helper produces a single
plain-language sentence ONLY when the returned list is actually truncated, so
the answer-generation SLM does not misread a capped list as the exhaustive set.

When the list is empty or complete there is nothing to disclose, so the helper
returns ``None`` and callers can omit the note from their serialized result.

The function is generic across tools: it takes the counts and a resource noun,
and never references any specific result-model field name.
"""

from typing import Optional


def build_sampling_note(
    sample_size: int, total_found: int, resource: str = "result"
) -> Optional[str]:
    """Build a plain-language note describing a truncated result list.

    Args:
        sample_size: Number of items actually included in the returned list.
        total_found: Total number of items matching the query in the backend.
        resource: Singular noun for the item type (e.g. "session"). Pluralized
            naively by appending "s".

    Returns:
        A single sentence stating the concrete N-of-M counts when the list is a
        truncated sample, or ``None`` when the list is empty or complete (i.e.
        nothing about sampling needs to be disclosed).
    """
    if sample_size <= 0 or sample_size >= total_found:
        return None
    plural = f"{resource}s"
    return (
        f"This is a SAMPLE of {sample_size} out of {total_found} matching "
        f"{plural}, capped by the result limit. Treat it as a representative "
        "example, not an exhaustive list."
    )
