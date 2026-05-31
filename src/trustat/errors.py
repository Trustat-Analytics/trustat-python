"""Exception hierarchy for the Trustat SDK.

Catch precisely (``except NotFoundError``) or broadly (``except TrustatError``).
Every API error carries the server ``code``, ``message``, ``request_id`` (quote it
in support tickets), HTTP ``status_code``, and any ``extras`` (e.g. quota reason).

    TrustatError                         # base — anything this SDK raises
    └── APIError                         # something went wrong talking to the API
        ├── APIConnectionError           # could not reach / network failure
        │   └── APITimeoutError          # request exceeded the timeout
        └── APIStatusError               # API returned a non-2xx error envelope
            ├── BadRequestError (400)
            │   └── ValidationError (422)
            ├── AuthenticationError (401)
            ├── PermissionDeniedError (403)
            │   └── InsufficientScopeError (403, plan lacks the scope)
            ├── NotFoundError (404)
            ├── InactiveSubscriptionError (412)
            ├── QuotaReachedError (426, .reason in {requests,channels,listing})
            ├── RateLimitError (429, .retry_after seconds)
            ├── ServiceUnavailableError (503)
            ├── GatewayTimeoutError (504)
            └── InternalServerError (500)
"""

from __future__ import annotations

from typing import Any

import httpx

__all__ = [
    "TrustatError",
    "APIError",
    "APIConnectionError",
    "APITimeoutError",
    "APIStatusError",
    "BadRequestError",
    "ValidationError",
    "AuthenticationError",
    "PermissionDeniedError",
    "InsufficientScopeError",
    "NotFoundError",
    "InactiveSubscriptionError",
    "QuotaReachedError",
    "RateLimitError",
    "ServiceUnavailableError",
    "GatewayTimeoutError",
    "InternalServerError",
    "error_from_response",
]


class TrustatError(Exception):
    """Base class for every error raised by the Trustat SDK."""


class APIError(TrustatError):
    """Base for errors arising from an interaction with the API."""

    request_id: str | None

    def __init__(self, message: str, *, request_id: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.request_id = request_id


class APIConnectionError(APIError):
    """The request could not reach the API (DNS, TCP, TLS, or transport error)."""

    def __init__(self, message: str = "Could not connect to Trustat.", *, request_id: str | None = None) -> None:
        super().__init__(message, request_id=request_id)


class APITimeoutError(APIConnectionError):
    """The request exceeded the configured timeout."""

    def __init__(self, message: str = "Request timed out.", *, request_id: str | None = None) -> None:
        super().__init__(message, request_id=request_id)


class APIStatusError(APIError):
    """The API returned a non-2xx response with an error envelope."""

    status_code: int
    code: str | None
    extras: dict[str, Any]
    response: httpx.Response | None

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: str | None = None,
        request_id: str | None = None,
        extras: dict[str, Any] | None = None,
        response: httpx.Response | None = None,
    ) -> None:
        super().__init__(message, request_id=request_id)
        self.status_code = status_code
        self.code = code
        self.extras = dict(extras or {})
        self.response = response

    def __str__(self) -> str:
        rid = f" (request_id={self.request_id})" if self.request_id else ""
        code = f"[{self.code}] " if self.code else ""
        return f"{code}{self.message}{rid}"


class BadRequestError(APIStatusError):
    """400 — malformed request (bad parameter, etc.)."""


class ValidationError(BadRequestError):
    """422 — request failed schema validation. ``extras['details']`` has specifics."""


class AuthenticationError(APIStatusError):
    """401 — missing or invalid API key."""


class PermissionDeniedError(APIStatusError):
    """403 — access denied."""


class InsufficientScopeError(PermissionDeniedError):
    """403 — your plan does not include this feature/scope."""


class NotFoundError(APIStatusError):
    """404 — the requested resource does not exist."""


class InactiveSubscriptionError(APIStatusError):
    """412 — subscription is inactive or unpaid."""


class QuotaReachedError(APIStatusError):
    """426 — monthly quota reached. ``.reason`` in {requests, channels, listing}."""

    @property
    def reason(self) -> str | None:
        return self.extras.get("reason")


class RateLimitError(APIStatusError):
    """429 — rate limit exceeded. ``.retry_after`` is the suggested wait in seconds."""

    @property
    def retry_after(self) -> float | None:
        value = self.extras.get("retry_after")
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None


class ServiceUnavailableError(APIStatusError):
    """503 — an upstream data store is temporarily unavailable (retryable)."""


class GatewayTimeoutError(APIStatusError):
    """504 — the request exceeded the server-side time budget (retryable)."""


class InternalServerError(APIStatusError):
    """500 — an unexpected server error."""


# Server error-code string -> exception class. Mirrors the API's ERROR_CODES.
_CODE_TO_EXC: dict[str, type[APIStatusError]] = {
    "bad_request": BadRequestError,
    "validation_error": ValidationError,
    "not_authenticated": AuthenticationError,
    "forbidden": PermissionDeniedError,
    "insufficient_scope": InsufficientScopeError,
    "not_found": NotFoundError,
    "inactive_subscription": InactiveSubscriptionError,
    "quota_reached": QuotaReachedError,
    "rate_limited": RateLimitError,
    "service_unavailable": ServiceUnavailableError,
    "gateway_timeout": GatewayTimeoutError,
    "internal_server_error": InternalServerError,
}

# Fallback status -> class for responses without a recognized error code.
_STATUS_TO_EXC: dict[int, type[APIStatusError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    412: InactiveSubscriptionError,
    422: ValidationError,
    426: QuotaReachedError,
    429: RateLimitError,
    500: InternalServerError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}


def error_from_response(
    status_code: int,
    body: Any,
    *,
    response: httpx.Response | None = None,
) -> APIStatusError:
    """Build the right ``APIStatusError`` subclass from an error-envelope body.

    Forward-compatible: an unknown ``code`` falls back to the status-code mapping,
    and finally to the generic ``APIStatusError`` so new server codes never crash
    an older SDK.
    """
    err: dict[str, Any] = {}
    if isinstance(body, dict):
        raw = body.get("error")
        if isinstance(raw, dict):
            err = raw
    code = err.get("code")
    message = err.get("message") or f"HTTP {status_code}"
    request_id = err.get("request_id")
    extras = {k: v for k, v in err.items() if k not in ("code", "message", "request_id")}

    cls = _CODE_TO_EXC.get(code) if code else None
    if cls is None:
        cls = _STATUS_TO_EXC.get(status_code, APIStatusError)
    return cls(
        message,
        status_code=status_code,
        code=code,
        request_id=request_id,
        extras=extras,
        response=response,
    )
