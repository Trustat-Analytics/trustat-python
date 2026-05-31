from __future__ import annotations

import httpx
import pytest
import respx
from conftest import BASE, err, ok, resp

import trustat
from trustat import (
    AuthenticationError,
    NotFoundError,
    QuotaReachedError,
    RateLimitError,
    Trustat,
    TrustatError,
)


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv("TRUSTAT_API_KEY", raising=False)
    with pytest.raises(TrustatError):
        Trustat(base_url=BASE)


def test_api_key_from_env(monkeypatch):
    monkeypatch.setenv("TRUSTAT_API_KEY", "tk_env")
    c = Trustat(base_url=BASE)
    assert c.api_key == "tk_env"
    c.close()


def test_repr_redacts_key():
    c = Trustat(api_key="tk_supersecretvalue", base_url=BASE)
    text = repr(c)
    assert "supersecretvalue" not in text
    assert "tk_sup" in text  # short prefix kept
    c.close()


@respx.mock
def test_auth_bearer_default(client):
    route = respx.get(f"{BASE}/public/v1/channels/777").mock(return_value=resp(200, ok({"channel_id": 777})))
    client.channels.get("777")
    assert route.calls.last.request.headers["authorization"] == "Bearer tk_test"


@respx.mock
def test_auth_x_api_key_option():
    c = Trustat(api_key="tk_test", base_url=BASE, auth_header="x-api-key")
    route = respx.get(f"{BASE}/public/v1/channels/777").mock(return_value=resp(200, ok({"channel_id": 777})))
    c.channels.get("777")
    req = route.calls.last.request
    assert req.headers["x-api-key"] == "tk_test"
    assert "authorization" not in req.headers
    c.close()


@respx.mock
def test_envelope_unwrapped_to_model(client):
    respx.get(f"{BASE}/public/v1/channels/777").mock(
        return_value=resp(200, ok({"channel_id": 777, "title": "Demo", "source": "telegram"}))
    )
    ch = client.channels.get("777")
    assert ch.channel_id == 777 and ch.title == "Demo"


@respx.mock
@pytest.mark.parametrize(
    "code,status,exc",
    [
        ("not_authenticated", 401, AuthenticationError),
        ("not_found", 404, NotFoundError),
        ("rate_limited", 429, RateLimitError),
        ("quota_reached", 426, QuotaReachedError),
    ],
)
def test_error_mapping(client, code, status, exc):
    respx.get(f"{BASE}/public/v1/channels/x").mock(return_value=resp(status, err(code)))
    with pytest.raises(exc) as ei:
        client.channels.get("x")
    assert ei.value.code == code
    assert ei.value.request_id == "req_abc"
    assert ei.value.status_code == status


@respx.mock
def test_quota_reason_and_retry_after(client):
    respx.get(f"{BASE}/public/v1/channels/x").mock(return_value=resp(426, err("quota_reached", reason="channels")))
    with pytest.raises(QuotaReachedError) as ei:
        client.channels.get("x")
    assert ei.value.reason == "channels"


@respx.mock
def test_unknown_code_falls_back(client):
    # forward-compat: a status with an unrecognized code still raises a typed status error
    respx.get(f"{BASE}/public/v1/channels/x").mock(return_value=resp(418, err("teapot_brewing")))
    with pytest.raises(trustat.errors.APIStatusError) as ei:
        client.channels.get("x")
    assert ei.value.status_code == 418 and ei.value.code == "teapot_brewing"
