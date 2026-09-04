"""Per-call cross-provider fallback for CrewAI agents."""

from __future__ import annotations

import os
import re
import time
from collections import Counter
from typing import Any

from crewai.llms.base_llm import BaseLLM
from crewai.llms.providers.openai.completion import OpenAICompletion
from crewai.utilities.types import LLMMessage
from dotenv import load_dotenv
from pydantic import Field

from stock_picker.model_config import MODEL_FALLBACKS, MODEL_MAX_OUTPUT_TOKENS, MODEL_TIMEOUT_SECONDS, ModelSpec

load_dotenv()


def is_repetitive_response(result: Any) -> bool:
    """Detect long, degenerate model outputs before accepting a provider call."""
    if not isinstance(result, str):
        return False
    words = re.findall(r"[a-z0-9]+", result.lower())
    if len(words) < 120:
        return False
    trigrams = Counter(zip(words, words[1:], words[2:]))
    return bool(trigrams and trigrams.most_common(1)[0][1] >= 12)


def rate_limit_retry_delay(error: Exception) -> float | None:
    """Return a short retry delay only when a free-tier limit can recover quickly."""
    if type(error).__name__ not in {"RateLimitError", "APIStatusError"}:
        return None
    if getattr(error, "status_code", 429) != 429:
        return None
    message = str(error)
    if re.search(r"per[\s_-]*day|requests? per day|daily quota", message, re.IGNORECASE):
        return None
    matches = re.findall(
        r"(?:try again in|retryDelay['\"]?:)\s*['\"]?([0-9.]+)s",
        message,
        re.IGNORECASE,
    )
    requested = float(matches[-1]) if matches else 5.0
    if requested > 10.0:
        return None
    return max(requested + 0.5, 1.0)


class FallbackLLM(BaseLLM):
    """Retry a failed LLM call without restarting completed CrewAI tasks."""

    attempts: list[tuple[ModelSpec, OpenAICompletion]] = Field(exclude=True)
    active_index: int = Field(default=0, exclude=True)

    def call(
        self,
        messages: str | list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        callbacks: list[Any] | None = None,
        available_functions: dict[str, Any] | None = None,
        from_task: Any | None = None,
        from_agent: Any | None = None,
        response_model: type[Any] | None = None,
    ) -> str | Any:
        failures: list[str] = []
        total = len(self.attempts)
        for offset in range(total):
            index = (self.active_index + offset) % total
            spec, llm = self.attempts[index]
            label = f"{spec.label}/{spec.model}"
            print(f"[models] trying {label}", flush=True)
            result = None
            provider_failed = False
            for attempt in range(2):
                try:
                    result = llm.call(
                        messages=messages,
                        tools=tools,
                        callbacks=callbacks,
                        available_functions=available_functions,
                        from_task=from_task,
                        from_agent=from_agent,
                        response_model=response_model,
                    )
                    if is_repetitive_response(result):
                        raise ValueError("degenerate repetitive model response")
                    break
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as error:
                    delay = rate_limit_retry_delay(error) if attempt == 0 else None
                    if delay is not None:
                        print(f"[models] {label} rate limited; retrying in {delay:g}s", flush=True)
                        time.sleep(delay)
                        continue
                    failures.append(f"{label}: {type(error).__name__}")
                    print(f"[models] {label} failed ({type(error).__name__}); trying next", flush=True)
                    provider_failed = True
                    break
            if provider_failed:
                continue
            self.active_index = index
            print(f"[models] completed with {label}", flush=True)
            return result
        raise RuntimeError("All configured models failed for this call: " + "; ".join(failures))

    def supports_function_calling(self) -> bool:
        return all(llm.supports_function_calling() for _, llm in self.attempts)

    def supports_stop_words(self) -> bool:
        return all(llm.supports_stop_words() for _, llm in self.attempts)

    def supports_multimodal(self) -> bool:
        return all(llm.supports_multimodal() for _, llm in self.attempts)

    def get_context_window_size(self) -> int:
        return min(llm.get_context_window_size() for _, llm in self.attempts)


def fallback_llm() -> FallbackLLM:
    """Build the shared quality-first LLM used by every stock-picking agent."""
    attempts: list[tuple[ModelSpec, OpenAICompletion]] = []
    for spec in MODEL_FALLBACKS:
        credential = os.getenv(spec.api_key_env, "").strip()
        if not credential:
            continue
        attempts.append((spec, OpenAICompletion(
            model=spec.model, api_key=credential, base_url=spec.base_url,
            provider="openai", max_retries=0, max_tokens=MODEL_MAX_OUTPUT_TOKENS,
            timeout=MODEL_TIMEOUT_SECONDS, temperature=0.2,
        )))
    if not attempts:
        required = ", ".join(dict.fromkeys(spec.api_key_env for spec in MODEL_FALLBACKS))
        raise RuntimeError(f"Configure at least one provider key in .env: {required}")
    return FallbackLLM(model="quality-first-stock-picker-fallback", attempts=attempts)
