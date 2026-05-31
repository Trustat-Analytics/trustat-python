from __future__ import annotations

import respx
from conftest import BASE, page_body, resp


@respx.mock
def test_cursor_auto_pagination(client):
    # two pages then stop (next_cursor null)
    respx.get(f"{BASE}/public/v1/channels/search").mock(
        side_effect=[
            resp(200, {"status": "ok", "response": page_body("channels", [{"channel_id": 1}, {"channel_id": 2}], next_cursor="c1", total=5)}),
            resp(200, {"status": "ok", "response": page_body("channels", [{"channel_id": 3}, {"channel_id": 4}], next_cursor="c2", total=5)}),
            resp(200, {"status": "ok", "response": page_body("channels", [{"channel_id": 5}], next_cursor=None, total=5)}),
        ]
    )
    ids = [c.channel_id for c in client.channels.search(q="x", limit=2)]
    assert ids == [1, 2, 3, 4, 5]


@respx.mock
def test_cursor_first_page_metadata(client):
    respx.get(f"{BASE}/public/v1/channels/search").mock(
        return_value=resp(
            200,
            {"status": "ok", "response": page_body("channels", [{"channel_id": 1}], next_cursor="c1", total=99)},
            **{"ratelimit-remaining": "42", "ratelimit-limit": "100", "x-quota-requests": "7/5000"},
        )
    )
    page = client.channels.search(q="x", limit=1)
    assert page.total == 99
    assert page.next_cursor == "c1"
    assert page.rate_limit.remaining == 42 and page.rate_limit.limit == 100
    assert page.quota.requests == (7, 5000) and page.quota.requests_remaining == 4993


@respx.mock
def test_offset_pagination_stops_on_short_page(client):
    respx.get(f"{BASE}/public/v1/channels/durov/mentions").mock(
        side_effect=[
            resp(200, {"status": "ok", "response": page_body("mentions", [{"mention_id": "a"}, {"mention_id": "b"}])}),
            resp(200, {"status": "ok", "response": page_body("mentions", [{"mention_id": "c"}])}),  # short -> stop
        ]
    )
    ids = [m.mention_id for m in client.channels.mentions("durov", limit=2)]
    assert ids == ["a", "b", "c"]


@respx.mock
def test_does_not_use_total_to_bound_loop(client):
    # total lies (says 100) but only one short page exists -> loop must stop on the data
    respx.get(f"{BASE}/public/v1/posts/search").mock(
        return_value=resp(200, {"status": "ok", "response": page_body("posts", [{"message_id": 1}], next_cursor=None, total=100)})
    )
    items = list(client.posts.search(q="x", limit=20))
    assert len(items) == 1


@respx.mock
def test_iter_pages(client):
    respx.get(f"{BASE}/public/v1/channels/search").mock(
        side_effect=[
            resp(200, {"status": "ok", "response": page_body("channels", [{"channel_id": 1}], next_cursor="c1")}),
            resp(200, {"status": "ok", "response": page_body("channels", [{"channel_id": 2}], next_cursor=None)}),
        ]
    )
    pages = list(client.channels.search(q="x", limit=1).iter_pages())
    assert len(pages) == 2 and [len(p) for p in pages] == [1, 1]
