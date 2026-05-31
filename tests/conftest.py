from __future__ import annotations

import httpx
import pytest

from trustat import AsyncTrustat, Trustat

BASE = "http://test.local"


def ok(response: object) -> dict:
    """A success envelope."""
    return {"status": "ok", "response": response}


def err(code: str, message: str = "boom", *, request_id: str = "req_abc", **extra: object) -> dict:
    """An error envelope."""
    return {"status": "error", "error": {"code": code, "message": message, "request_id": request_id, **extra}}


def page_body(item_key: str, items: list, *, next_cursor: str | None = None, total: int | None = None) -> dict:
    body: dict = {item_key: items, "limit": len(items)}
    if next_cursor is not None:
        body["next_cursor"] = next_cursor
    if total is not None:
        body["total"] = total
    return body


@pytest.fixture
def client() -> Trustat:
    c = Trustat(api_key="tk_test", base_url=BASE, max_retries=2)
    try:
        yield c
    finally:
        c.close()


@pytest.fixture
async def aclient() -> AsyncTrustat:
    c = AsyncTrustat(api_key="tk_test", base_url=BASE, max_retries=2)
    try:
        yield c
    finally:
        await c.close()


def resp(status: int, body: object, **headers: str) -> httpx.Response:
    return httpx.Response(status, json=body, headers=headers)
