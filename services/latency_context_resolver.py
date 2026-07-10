# Copyright (c) 2025 Cisco Systems, Inc. All Rights Reserved

from typing import Dict, List, Optional

from fastmcp.exceptions import ToolError as McpToolError

from logger import logger
from models.error_models import ErrorCategory, raise_tool_error
from models.session_models import (
    EnrichedSessionSearchResult,
    ExecutionStep,
    LatencyEnrichedSessionSearchResult,
    SessionDetail,
    SessionWithLatencyContext,
)


class LatencyContextResolver:
    """Maps execution step codes to human-readable message texts.

    Receives a pre-parsed message catalog dict (code -> text) at init time
    and performs pure in-memory lookups with no additional API calls.
    """

    def __init__(self, msg_catalog: Dict[str, str]):
        self._msg_catalog = msg_catalog

    def _resolve_steps(self, session: SessionDetail) -> Optional[List[ExecutionStep]]:
        """Resolve the parsed execution_steps list into ExecutionStep objects.

        When ``session.steps_latencies`` is available, a dict keyed by
        step_index (which maps directly to the execution_steps array index)
        is built for O(1) latency lookup per step.
        """
        steps_codes: Optional[List[str]] = session.execution_steps
        if not steps_codes:
            return None

        latency_by_index: Dict[int, int] = {}
        if session.steps_latencies:
            latency_by_index = {sl.step_index: sl.latency_ms for sl in session.steps_latencies}

        steps: List[ExecutionStep] = []
        for idx, code in enumerate(steps_codes):
            latency: Optional[int] = latency_by_index.get(idx)
            steps.append(ExecutionStep(
                code=code,
                text=self._msg_catalog.get(code),
                latency_ms=latency,
            ))
        return steps if steps else None

    def enrich_sessions_with_latency_context(
        self, enriched_result: EnrichedSessionSearchResult
    ) -> LatencyEnrichedSessionSearchResult:
        """Resolve execution steps for each session in an enriched search result.

        Args:
            enriched_result: The enriched session search result from
                ``SessionToolHandler.search_enriched_active_sessions``.

        Returns:
            LatencyEnrichedSessionSearchResult with each session paired with
            its resolved execution steps.
        """
        try:
            results: List[SessionWithLatencyContext] = []

            for session in enriched_result.sessions:
                resolved_steps: Optional[List[ExecutionStep]] = self._resolve_steps(session)

                if resolved_steps is None:
                    results.append(SessionWithLatencyContext(
                        session=session,
                        execution_steps=None,
                        latency_context_note="No execution steps found in session data",
                    ))
                    continue

                unresolved: int = sum(1 for s in resolved_steps if s.text is None)
                note: Optional[str] = None
                if unresolved:
                    logger.debug("Unresolved execution steps", user_name=session.user_name, unresolved=unresolved, total=len(resolved_steps))
                    note = f"{unresolved} of {len(resolved_steps)} step code(s) could not be resolved from the message catalog"

                results.append(SessionWithLatencyContext(
                    session=session,
                    execution_steps=resolved_steps,
                    latency_context_note=note,
                ))

            return LatencyEnrichedSessionSearchResult(
                search_filters=enriched_result.search_filters,
                total_sessions_found=enriched_result.total_sessions_found,
                actual_sessions_returned=len(results),
                sessions=results,
            )
        except McpToolError:
            raise
        except Exception as e:
            logger.exception("Error enriching sessions with latency context", error=str(e))
            raise_tool_error(
                ErrorCategory.SERVER_ERROR, "LATENCY_ENRICHMENT_ERROR",
                "An unexpected error occurred while resolving execution steps for sessions.",
            )
