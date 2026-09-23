"""Safe, user-facing failure handling for the public demo."""

from __future__ import annotations

import re
import uuid

_QUOTA_MARKERS = ("429", "quota", "rate limit", "rate_limit", "resource exhausted", "too many requests", "requests per day", "tokens per")

def is_quota_error(error: BaseException) -> bool:
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if getattr(current, "status_code", None) == 429 or type(current).__name__ in {"RateLimitError", "TooManyRequestsError"}:
            return True
        if any(marker in str(current).lower() for marker in _QUOTA_MARKERS):
            return True
        current = current.__cause__ or current.__context__
    return False

def public_error_message(error: BaseException, language: str, action: str) -> str:
    spanish = language != "English"
    if is_quota_error(error):
        return "La cuota gratuita del modelo está agotada temporalmente. Probá nuevamente más tarde." if spanish else "The model's free quota is temporarily exhausted. Please try again later."
    return f"El servicio no está disponible en este momento y no pude completar {action}. Probá nuevamente más tarde." if spanish else f"The service is currently unavailable, so I couldn't complete {action}. Please try again later."

def log_failure(event: str, error: BaseException) -> None:
    safe_event = re.sub(r"[^a-z0-9_.-]", "_", event.lower())[:64]
    safe_type = re.sub(r"[^A-Za-z0-9_.-]", "_", type(error).__name__)[:64]
    print(f"[failure] event={safe_event} type={safe_type} incident={uuid.uuid4().hex[:12]}", flush=True)
