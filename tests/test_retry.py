from __future__ import annotations

import httpx
import pytest
import respx

from conftest import BASE, err, ok, resp
from trustat import NotFoundError, RateLimitError, Trustat


@respx.mock
def test_retries_429_then_succeeds(client):
    route = respx.get(f"{BASE}/public/v1/channels/x").mock(
        side_effect=[
            resp(429, err("rate_limited"), **{"retry-after": "0"}),
            resp(200, ok({"channel_id": 1})),
        ]
    )
    ch = client.channels.get("x")
    assert ch.channel_id == 1
    assert route.call_count == 2


@respx.mock
def test_retries_500_then_succeeds(client):
    route = respx.get(f"{BASE}/public/v1/channels/x").mock(
        side_effect=[resp(503, err("service_unavailable")), resp(200, ok({"channel_id": 2}))]
    )
    assert client.channels.get("x").channel_id == 2
    assert route.call_count == 2


@respx.mock
def test_gives_up_after_max_retries():
    c = Trustat(api_key="tk_test", base_url=BASE, max_retries=1)
    route = respx.get(f"{BASE}/public/v1/channels/x").mock(
        return_value=resp(429, err("rate_limited"), **{"retry-after": "0"})
    )
    with pytest.raises(RateLimitError):
        c.channels.get("x")
    assert route.call_count == 2  # initial + 1 retry
    c.close()


@respx.mock
def test_retries_connection_error(client):
    route = respx.get(f"{BASE}/public/v1/channels/x").mock(
        side_effect=[httpx.ConnectError("boom"), resp(200, ok({"channel_id": 3}))]
    )
    assert client.channels.get("x").channel_id == 3
    assert route.call_count == 2


@respx.mock
def test_does_not_retry_404(client):
    route = respx.get(f"{BASE}/public/v1/channels/x").mock(return_value=resp(404, err("not_found")))
    with pytest.raises(NotFoundError):
        client.channels.get("x")
    assert route.call_count == 1  # 404 is terminal
