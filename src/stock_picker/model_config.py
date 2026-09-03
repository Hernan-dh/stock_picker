"""Version-controlled runtime model order for the stock-picking crew."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    label: str
    model: str
    api_key_env: str
    base_url: str


MODEL_FALLBACKS = (
    ModelSpec("Gemini", "gemini-3.7-flash", "GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/"),
    ModelSpec("Gemini", "gemini-3.6-flash", "GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/"),
    ModelSpec("Groq", "openai/gpt-oss-120b", "GROQ_API_KEY", "https://api.groq.com/openai/v1"),
    ModelSpec("OpenRouter", "nvidia/nemotron-3-super-120b-a12b:free", "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
)

MODEL_TIMEOUT_SECONDS = 90
MODEL_MAX_OUTPUT_TOKENS = 16_384
