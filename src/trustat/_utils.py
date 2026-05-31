"""Small internal helpers: query serialization, user-agent, secret redaction."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

from ._version import __version__


def quote_path(value: Any) -> str:
    """URL-encode a path segment (so ``@username``, ``+hash``, ids, etc. are safe).

    ``safe=""`` also encodes ``/`` so an identifier can never inject extra path
    segments; FastAPI decodes it back before resolving.
    """
    return quote(str(value), safe="")


def serialize_query(params: Mapping[str, Any] | None) -> dict[str, Any]:
    """Turn a params mapping into httpx-ready query values.

    - ``None`` values are dropped (so callers pass only what they set).
    - ``bool`` becomes ``"true"``/``"false"`` (FastAPI's expected form).
    - lists/tuples become comma-joined strings (the API splits CSV params).
    """
    out: dict[str, Any] = {}
    if not params:
        return out
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            out[key] = "true" if value else "false"
        elif isinstance(value, (list, tuple, set)):
            items = [str(v) for v in value if v is not None]
            if items:
                out[key] = ",".join(items)
        else:
            out[key] = value
    return out


def user_agent() -> str:
    return f"trustat-python/{__version__}"


def redact_key(api_key: str | None) -> str:
    """Mask an API key for safe display in reprs/logs (keeps a short prefix)."""
    if not api_key:
        return "None"
    if len(api_key) <= 8:
        return "***"
    return f"{api_key[:6]}...{api_key[-2:]}"
