import json
from typing import Any, Callable

import httpx
from fastmcp.exceptions import ToolError as McpToolError

from clients.client_factory import ClientFactory, ClientName
from logger import logger
from models.error_models import ErrorCategory, raise_tool_error


class BaseToolHandler:
    def __init__(self, client_name: ClientName, client_factory: ClientFactory):
        self.client_factory = client_factory
        self.client_name = client_name

    @property
    def client(self) -> object:
        return self.client_factory.get_client(self.client_name)

    async def execute_api_call(self, api_function: Callable, operation_name: str, **kwargs) -> Any:
        """
            Generic method to execute API calls with consistent error handling and logging.

            Args:
                api_function: The async API function to call
                operation_name: Name of the operation for logging
                **kwargs: Arguments to pass to the API function

            Returns:
                Any: Parsed response on success

            Raises:
                McpToolError: On any API call failure (propagated as isError=True by FastMCP)
        """
        response = None
        try:
            logger.info("Executing API call", operation=operation_name)
            response = await api_function(client=self.client, **kwargs)
            if response is None:
                logger.error("API call returned None", operation=operation_name)
                raise_tool_error(
                    ErrorCategory.EXTERNAL_ERROR,
                    "ISE_INVALID_RESPONSE",
                    f"ISE API returned no response object for {operation_name}.",
                    retry=False,
                )
            status_code = response.status_code
            if status_code >= 400:
                body = response.content.decode("utf-8", errors="replace")[:500]
                logger.error("API call returned error", operation=operation_name, status_code=status_code, body=body)
                raise_tool_error(
                    ErrorCategory.EXTERNAL_ERROR, "ISE_API_ERROR",
                    f"ISE API returned HTTP {status_code} for {operation_name}.",
                    retry=status_code >= 500,
                )
            logger.debug("API call successful", operation=operation_name, status_code=status_code)
            parsed_response: Any = json.loads(response.content)
            logger.debug("API response parsed", operation=operation_name)
            return parsed_response
        except McpToolError:
            raise
        except (json.JSONDecodeError, ValueError, TypeError):
            if response is None:
                logger.error("API call failed: no response available to parse", operation=operation_name)
                raise_tool_error(
                    ErrorCategory.EXTERNAL_ERROR,
                    "ISE_INVALID_RESPONSE",
                    f"ISE API returned no parseable response for {operation_name}.",
                    retry=False,
                )
            raw_body = response.content.decode("utf-8", errors="replace")[:500]
            logger.error("API call returned non-JSON body", operation=operation_name, status_code=response.status_code, body=raw_body)
            raise_tool_error(
                ErrorCategory.EXTERNAL_ERROR,
                "ISE_INVALID_RESPONSE",
                f"ISE API returned a non-JSON or empty response for {operation_name} "
                f"(HTTP {response.status_code}).",
                retry=False,
            )
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            logger.exception("ISE API unreachable", operation=operation_name, error=str(e))
            raise_tool_error(
                ErrorCategory.EXTERNAL_ERROR, "ISE_UNREACHABLE",
                f"The ISE API is unreachable or timed out during {operation_name}. Try again later.",
                retry=True,
            )
        except Exception as e:
            logger.exception("Unexpected error in API call", operation=operation_name, error=str(e))
            raise_tool_error(
                ErrorCategory.EXTERNAL_ERROR, "ISE_API_ERROR",
                f"Error in {operation_name}.",
            )
