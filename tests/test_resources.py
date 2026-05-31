from __future__ import annotations

import respx
from conftest import BASE, ok, resp


@respx.mock
def test_path_and_query_serialization(client):
    route = respx.get(f"{BASE}/public/v1/channels/catalog").mock(
        return_value=resp(200, ok({"channels": [], "total": 0}))
    )
    client.channels.catalog(verified=True, category_ids=[10, 20], limit=5, language=None)
    req = route.calls.last.request
    params = dict(req.url.params)
    assert params["verified"] == "true"  # bool serialized
    assert params["category_ids"] == "10,20"  # list -> csv
    assert params["limit"] == "5"
    assert "language" not in params  # None dropped


@respx.mock
def test_channel_path_is_encoded(client):
    # an @username / +hash must be URL-encoded into the path
    route = respx.get(url__regex=rf"{BASE}/public/v1/channels/.+").mock(return_value=resp(200, ok({"channel_id": 1})))
    client.channels.get("@durov")
    assert "%40durov" in str(route.calls.last.request.url)


@respx.mock
def test_dictionaries_return_list(client):
    respx.get(f"{BASE}/public/v1/dictionaries/categories").mock(
        return_value=resp(200, ok({"categories": [{"id": 1, "name": "News"}, {"id": 2, "name": "Tech"}]}))
    )
    cats = client.dictionaries.categories()
    assert [c.name for c in cats] == ["News", "Tech"]


@respx.mock
def test_lookup_is_callable(client):
    route = respx.get(f"{BASE}/public/v1/lookup").mock(
        return_value=resp(200, ok({"results": [{"type": "channel", "source": "telegram", "channel_id": 1}]}))
    )
    res = client.lookup("durov")  # callable sugar
    assert res.results[0].channel_id == 1
    assert dict(route.calls.last.request.url.params)["ref"] == "durov"


@respx.mock
def test_usage_info(client):
    respx.get(f"{BASE}/public/v1/usage/info").mock(
        return_value=resp(200, ok({"plan": "pro", "spent_requests": "10/3000000"}))
    )
    assert client.usage.info().spent_requests == "10/3000000"


@respx.mock
def test_system_endpoints_at_root(client):
    respx.get(f"{BASE}/health").mock(return_value=resp(200, ok({"status": "ok"})))
    respx.get(f"{BASE}/version").mock(return_value=resp(200, ok({"version": "1.0.0"})))
    assert client.system.health().status == "ok"
    assert client.system.version().version == "1.0.0"
