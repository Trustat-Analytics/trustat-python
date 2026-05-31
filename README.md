# Trustat Python SDK

[![PyPI](https://img.shields.io/pypi/v/trustat.svg)](https://pypi.org/project/trustat/)
[![Python](https://img.shields.io/pypi/pyversions/trustat.svg)](https://pypi.org/project/trustat/)
[![CI](https://github.com/Trustat-Analytics/trustat-python/actions/workflows/ci.yml/badge.svg)](https://github.com/Trustat-Analytics/trustat-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

The Python SDK for the [Trustat API](https://trustat.me) — analytics for Telegram & MAX
channels: profiles, statistics, subscriber/views dynamics, mentions, forwards, posts and
edit history, and the Telegram Ads database.

Typed (Pydantic v2), sync **and** async, with automatic pagination, retries, and a clean
error hierarchy.

## Install

```bash
pip install trustat
```

Requires Python 3.10+.

## Quickstart

```python
from trustat import Trustat

client = Trustat(api_key="tk_...")          # or set TRUSTAT_API_KEY

channel = client.channels.get("durov")       # id, username, @username, or +hash
print(channel.title, channel.participants)

stat = client.channels.stat("durov")
print(stat.er_day, stat.quality_score)

# auto-paginating: iterate the whole result set, pages fetched lazily
for post in client.posts.search(q="bitcoin", limit=50):
    print(post.message_id, post.views)
```

The client holds a pooled connection — reuse one instance, and close it when done
(or use it as a context manager):

```python
with Trustat(api_key="tk_...") as client:
    ...
```

## Authentication

Pass `api_key=` or set the `TRUSTAT_API_KEY` environment variable. The key is sent as
`Authorization: Bearer <key>` by default; pass `auth_header="x-api-key"` to use the
`X-API-Key` header instead. Override the host with `base_url=` or `TRUSTAT_BASE_URL`.

## Async

Every method has an async twin on `AsyncTrustat` — identical signatures, just `await`:

```python
import asyncio
from trustat import AsyncTrustat

async def main():
    async with AsyncTrustat(api_key="tk_...") as client:
        channel = await client.channels.get("durov")

        # auto-paginate without awaiting first:
        async for ch in client.channels.search(q="news"):
            print(ch.title)

asyncio.run(main())
```

## Pagination

List methods (`search`, `catalog`, channel `posts`/`mentions`/`forwards`/`ads`, `ads.search`,
`ads.by_advertiser`) return a **page** you can iterate directly — it transparently fetches
subsequent pages:

```python
page = client.channels.search(q="news", limit=50)
print(page.total)            # approximate match count (informational)
print(page.next_cursor)      # the cursor for the next page
print(page.rate_limit.remaining, page.quota.requests_remaining)

for ch in page:              # iterates EVERY result across all pages, lazily
    ...

for one_page in page.iter_pages():   # or iterate page-by-page
    print(len(one_page))
```

Never use `page.total` to bound a loop — it is approximate. Iterating until exhaustion is
correct. (Mentions and forwards are depth-capped server-side at ~10k results; iterate within
a date window for deeper history.)

## Errors

```python
from trustat import NotFoundError, RateLimitError, QuotaReachedError, TrustatError

try:
    client.channels.get("does-not-exist")
except NotFoundError as e:
    print(e.code, e.request_id)        # "not_found", "req_..."
except RateLimitError as e:
    print("retry after", e.retry_after)
except QuotaReachedError as e:
    print("quota:", e.reason)          # "requests" | "channels" | "listing"
except TrustatError:
    ...                                 # base class — catches everything
```

The SDK automatically retries transient failures (429, 5xx, connection/timeout errors) with
exponential backoff + jitter, honoring `Retry-After` / `RateLimit-Reset`. Configure with
`max_retries=` and `timeout=`.

## Resources

| Namespace | Highlights |
|---|---|
| `client.channels` | `get`, `stat`, `batch`, `subscribers`, `views`, `reach`, `mentions`, `forwards`, `posts`, `ads`, `catalog`, `search` |
| `client.posts` | `search`, `get`, `history`, `stat` |
| `client.ads` | `search`, `get`, `facets`, `timeline`, `by_advertiser` |
| `client.lookup` | resolve any id / link / `@username` → canonical ids (`client.lookup("durov")`) |
| `client.dictionaries` | `categories`, `countries`, `languages` |
| `client.usage` | `info` — your current quota consumption |
| `client.system` | `health`, `version` |

## Configuration

```python
Trustat(
    api_key=None,            # or TRUSTAT_API_KEY
    base_url=None,           # or TRUSTAT_BASE_URL
    auth_header="authorization",  # or "x-api-key"
    timeout=None,            # httpx.Timeout or seconds
    max_retries=2,
    default_headers=None,
    default_query=None,
    http_client=None,        # inject your own httpx.Client (proxies, transport, ...)
)
```

## License

MIT
