# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

"""Shared base model for ISE MCP tool results.

Tools return these models directly so FastMCP can advertise an ``outputSchema``
and populate the MCP ``structuredContent`` channel (LLM-friendly), while still
mirroring a JSON text block for backward-compatible clients.

FastMCP builds structured content via ``pydantic_core.to_jsonable_python``,
which serializes every field including ``None``. Previously tools called
``model_dump_json(exclude_none=True)`` themselves, so absent optional fields
were dropped from the wire payload -- a contract several field descriptions
rely on (e.g. sampling_note is "Absent when all results are returned"). This
base restores that behavior via a model serializer that strips ``None`` values
recursively, so the structured payload matches the previous string output while
the JSON Schema still lists all properties.
"""

from pydantic import BaseModel, model_serializer
from pydantic.functional_serializers import SerializerFunctionWrapHandler


class IseResultModel(BaseModel):
    """Base for tool-result models: omit ``None`` fields from serialized output.

    The serializer intentionally carries NO return annotation. Annotating it
    (e.g. ``-> dict``) makes Pydantic derive the model's serialization-mode JSON
    Schema from that annotation, collapsing it to a bare ``{"type": "object"}``
    and destroying the ``outputSchema`` FastMCP advertises for the tool. Leaving
    it unannotated preserves the full per-field schema while still dropping
    ``None`` values from the emitted payload.
    """

    @model_serializer(mode="wrap")
    def _drop_none(self, handler: SerializerFunctionWrapHandler):
        return {key: value for key, value in handler(self).items() if value is not None}
