"""fefe-interim build pipeline."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from generator import generate_site, generate_feed
from scraper import fetch_posts, filter_posts

# Base URL for the live site. Override via environment variable for local testing
# or alternative hosting. Must NOT have a trailing slash.
# Example: SITE_URL="" python build.py  (for local file:// testing)
SITE_URL = os.environ.get("SITE_URL", "https://krystofbe.github.io/fefe-interim")

# Fallback cache used when Reddit API is unreachable (e.g. blocked on CI runners).
POSTS_CACHE = Path("data/posts-cache.json")


def _load_cache_posts() -> list[dict]:
    """Load posts from the committed cache file.

    Returns an empty list if the cache file does not exist or is malformed.
    """
    if not POSTS_CACHE.exists():
        print(f"Cache file not found at {POSTS_CACHE} — no fallback available")
        return []
    try:
        cache = json.loads(POSTS_CACHE.read_text(encoding="utf-8"))
        posts = cache.get("posts", [])
        print(f"Loaded {len(posts)} posts from cache ({POSTS_CACHE})")
        return posts
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Could not read cache {POSTS_CACHE}: {exc}")
        return []


def main() -> None:
    print("fefe-interim build started")

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Fetch posts from Reddit
    print("Fetching posts from r/fefe_blog_interim...")
    raw_posts = fetch_posts(sort="new", limit=500)
    print(f"Fetched {len(raw_posts)} raw posts")

    # Step 2: Filter by Wilson Score
    filtered = filter_posts(raw_posts, min_score=3)
    print(f"Filtered to {len(filtered)} significant posts")

    # Step 2b: Fall back to cached posts if Reddit returned nothing
    # (Reddit blocks requests from GitHub Actions runner IPs with HTTP 403)
    if not filtered:
        print(
            "Reddit returned 0 posts — falling back to cached posts-cache.json"
        )
        cached_posts = _load_cache_posts()
        if cached_posts:
            # Build data dict directly from cache; skip re-writing posts.json
            data = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source": "r/fefe_blog_interim (cached)",
                "total_fetched": 0,
                "total_filtered": len(cached_posts),
                "posts": cached_posts,
            }
            posts_json = output_dir / "posts.json"
            posts_json.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            print(f"Wrote {len(cached_posts)} cached posts to {posts_json}")

            print("Generating static site from cache...")
            print(f"Using SITE_URL: {SITE_URL}")
            generate_site(data, output_dir)
            generate_feed(data, output_dir, site_url=SITE_URL)
            print(f"Wrote RSS feed to {output_dir / 'feed.xml'}")
            print("Build complete (from cache)")
            return
        else:
            print("No cache available — deploying empty site")

    # Step 3: Persist as JSON
    posts_json = output_dir / "posts.json"
    posts_list = [
        {
            "id": p.id,
            "title": p.title,
            "body": p.body,
            "score": p.score,
            "num_comments": p.num_comments,
            "created_utc": p.created_utc,
            "permalink": p.permalink,
            "reddit_url": p.reddit_url,
            "url": p.url,
            "flair": p.flair,
            "upvote_ratio": p.upvote_ratio,
            "author": p.author,
            "external_links": p.external_links,
        }
        for p in filtered
    ]
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "r/fefe_blog_interim",
        "total_fetched": len(raw_posts),
        "total_filtered": len(filtered),
        "posts": posts_list,
    }
    posts_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(filtered)} posts to {posts_json}")

    # Update the in-repo cache so future CI runs have fresh fallback data
    POSTS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    POSTS_CACHE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Updated cache at {POSTS_CACHE} with {len(filtered)} posts")

    # Step 4: Generate static site
    print("Generating static site...")
    print(f"Using SITE_URL: {SITE_URL}")
    generate_site(data, output_dir)

    # Step 5: Generate RSS feed with the live site URL
    generate_feed(data, output_dir, site_url=SITE_URL)
    print(f"Wrote RSS feed to {output_dir / 'feed.xml'}")

    print("Build complete")


if __name__ == "__main__":
    main()
