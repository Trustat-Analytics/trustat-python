from __future__ import annotations

import pytest
import respx

from conftest import BASE, ok, page_body, resp
from trustat import NotFoundError


@respx.mock
async def test_async_get(aclient):
    respx.get(f"{BASE}/public/v1/channels/777").mock(return_value=resp(200, ok({"channel_id": 777})))
    ch = await aclient.channels.get("777")
    assert ch.channel_id == 777


@respx.mock
async def test_async_awaited_page(aclient):
    respx.get(f"{BASE}/public/v1/channels/search").mock(
        return_value=resp(
            200, {"status": "ok", "response": page_body("channels", [{"channel_id": 1}], next_cursor=None, total=1)}
        )
    )
    page = await aclient.channels.search(q="x", limit=5)
    assert len(page) == 1 and page.total == 1


@respx.mock
async def test_async_auto_paginate_without_await(aclient):
    respx.get(f"{BASE}/public/v1/channels/search").mock(
        side_effect=[
            resp(200, {"status": "ok", "response": page_body("channels", [{"channel_id": 1}], next_cursor="c1")}),
            resp(200, {"status": "ok", "response": page_body("channels", [{"channel_id": 2}], next_cursor=None)}),
        ]
    )
    ids = [ch.channel_id async for ch in aclient.channels.search(q="x", limit=1)]
    assert ids == [1, 2]


@respx.mock
async def test_async_iter_pages(aclient):
    respx.get(f"{BASE}/public/v1/channels/search").mock(
        side_effect=[
            resp(200, {"status": "ok", "response": page_body("channels", [{"channel_id": 1}], next_cursor="c1")}),
            resp(200, {"status": "ok", "response": page_body("channels", [{"channel_id": 2}], next_cursor=None)}),
        ]
    )
    pages = [p async for p in aclient.channels.search(q="x", limit=1).iter_pages()]
    assert len(pages) == 2


@respx.mock
async def test_async_error_mapping(aclient):
    respx.get(f"{BASE}/public/v1/posts/1_2").mock(
        return_value=resp(404, {"status": "error", "error": {"code": "not_found", "message": "x", "request_id": "r"}})
    )
    with pytest.raises(NotFoundError):
        await aclient.posts.get("1_2")
