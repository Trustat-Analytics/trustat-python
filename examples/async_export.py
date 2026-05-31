"""Async export: stream a large result set, watching rate-limit/quota burn-down."""

import asyncio

from trustat import AsyncTrustat


async def main() -> None:
    async with AsyncTrustat() as client:
        total_seen = 0

        # Iterate page-by-page so we can watch the rate-limit/quota headers as we go.
        async for page in client.posts.search(q="bitcoin", sort="date", limit=100).iter_pages():
            for post in page.items:
                total_seen += 1
                # ... write `post` to your sink (CSV, DB, queue) ...

            rl = page.rate_limit
            print(f"page: +{len(page)} (total {total_seen}/~{page.total}) "
                  f"rate_remaining={rl.remaining} quota_requests={page.quota.requests}")

            # Be a good citizen: if the bucket is nearly empty, ease off.
            if rl.remaining is not None and rl.remaining < 5 and rl.reset_seconds:
                await asyncio.sleep(min(rl.reset_seconds, 5))

        print("done; exported", total_seen, "posts")


if __name__ == "__main__":
    asyncio.run(main())
