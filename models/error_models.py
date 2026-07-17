# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# SPDX-License-Identifier: Apache-2.0

import json
from enum import Enum

from pydantic import BaseModel, Field
from fastmcp.exceptions import ToolError as McpToolError


class ErrorCategory(str, Enum):
    CLIENT_ERROR = "client_error"
    SERVER_ERROR = "server_error"
    EXTERNAL_ERROR = "external_error"


class ToolErrorDetail(BaseModel):
    """Structured error payload embedded in MCP isError responses."""

    error_category: ErrorCategory = Field(..., description="Whether the error is due to client input, server, or an external dependency")
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description safe for the agent/user")
    retry: bool = Field(False, description="Whether the caller should retry the request")


def is_error_response(data: dict) -> bool:
    """Check whether a parsed JSON dict represents a ToolErrorDetail."""
    return "error_category" in data or "error_code" in data


def raise_tool_error(
    category: ErrorCategory,
    code: str,
    message: str,
    *,
    retry: bool = False,
) -> None:
    """Raise a FastMCP ToolError so the MCP response carries isError=True.

    The exception message is a JSON string preserving the structured
    error_category / error_code / message / retry schema.
    """
    payload = json.dumps(
        ToolErrorDetail(
            error_category=category,
            error_code=code,
            message=message,
            retry=retry,
        ).model_dump(mode="json"),
    )
    raise McpToolError(payload)
