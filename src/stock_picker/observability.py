"""Optional Phoenix tracing for CrewAI runs."""

import logging
import os


logger = logging.getLogger(__name__)


def configure_observability() -> None:
    """Configure tracing only when a Phoenix collector was explicitly set."""
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
    if not endpoint:
        return
    try:
        from phoenix.otel import register
        from openinference.instrumentation.crewai import CrewAIInstrumentor

        tracer_provider = register(project_name="stock-picker", endpoint=endpoint)
        CrewAIInstrumentor().instrument(skip_dep_check=True, tracer_provider=tracer_provider)
    except Exception:
        logger.warning("Phoenix tracing is unavailable; continuing without it.", exc_info=True)
