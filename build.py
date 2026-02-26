"""fefe-interim build pipeline."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from generator import generate_site, generate_feed
from scraper import fetch_posts


# Base URL for the live site. Override via environment variable for local testing
# or alternative hosting. Must NOT have a trailing slash.
# Example: SITE_URL="" python build.py  (for local file:// testing)
SITE_URL = os.environ.get("SITE_URL", "https://krystofbe.github.io/fefe-interim")


def main() -> None:
    print("fefe-interim build started")

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Fetch posts from Reddit via RSS
    print("Fetching posts from r/fefe_blog_interim via RSS...")
    posts = fetch_posts(sort="new", limit=100)
    print(f"Fetched {len(posts)} posts")

    if not posts:
        print("WARNING: No posts fetched — site will be empty")

    # Step 2: Persist as JSON
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
        for p in posts
    ]
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "r/fefe_blog_interim (RSS)",
        "total_fetched": len(posts),
        "posts": posts_list,
    }
    posts_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(posts)} posts to {posts_json}")

    # Step 3: Generate static site
    print("Generating static site...")
    print(f"Using SITE_URL: {SITE_URL}")
    generate_site(data, output_dir)

    # Step 4: Generate RSS feed with the live site URL
    generate_feed(data, output_dir, site_url=SITE_URL)
    print(f"Wrote RSS feed to {output_dir / 'feed.xml'}")

    print("Build complete")


if __name__ == "__main__":
    main()
