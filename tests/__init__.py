"""Offline tests: ignore local credentials and disable provider telemetry."""
import os

os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"
