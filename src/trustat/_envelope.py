"""Unwrap the Trustat response envelope, or raise the mapped error.

Success: ``{"status": "ok", "response": <payload>}`` -> returns ``<payload>``.
Error:   ``{"status": "error", "error": {"code", "message", "request_id", ...}}``
         -> raises the mapped ``APIStatusError`` subclass.
"""

from __future__ import annotations

from typing import Any

import httpx

from .errors import error_from_response


def parse_envelope(response: httpx.Response) -> Any:
    """Return the inner payload on success; raise an ``APIStatusError`` on error."""
    body: Any
    try:
        body = response.json()
    except Exception:
        body = None

    if response.is_success and isinstance(body, dict) and body.get("status") == "ok":
        return body.get("response")

    # Non-2xx, or a 2xx without the expected ok envelope -> raise the mapped error.
    raise error_from_response(response.status_code, body, response=response)
