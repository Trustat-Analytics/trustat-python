"""Sync quickstart: profile, stats, search with auto-pagination, error handling."""

from trustat import NotFoundError, Trustat

with Trustat() as client:  # api_key from TRUSTAT_API_KEY
    # A channel profile + stats
    ch = client.channels.get("durov")
    print(f"{ch.title}: {ch.participants:,} subscribers (source={ch.source})")

    stat = client.channels.stat("durov")
    print(f"  ER/day={stat.er_day}  quality={stat.quality_score}")

    # Subscriber dynamics
    series = client.channels.subscribers("durov", days=30)
    print(f"  {len(series.points or [])} daily subscriber points")

    # Search, auto-paginating across pages; stop after 100
    print("\nTop 'crypto' channels:")
    for i, c in enumerate(client.channels.search(q="crypto", sort_by="subscribers", limit=50)):
        print(f"  {c.title} — {c.participants:,}")
        if i >= 99:
            break

    # Resolve any reference to canonical ids
    res = client.lookup("https://t.me/durov")
    print("\nresolved:", res.results[0].source, res.results[0].channel_id)

    # Errors are typed
    try:
        client.channels.get("this-channel-does-not-exist-zzz")
    except NotFoundError as e:
        print("\nnot found:", e.code, "| request_id:", e.request_id)
