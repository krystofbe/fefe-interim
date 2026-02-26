"""fefe-interim build pipeline."""

import json
from datetime import datetime, timezone
from pathlib import Path

from generator import generate_site
from scraper import fetch_posts, filter_posts


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

    # Step 3: Persist as JSON
    posts_json = output_dir / "posts.json"
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "r/fefe_blog_interim",
        "total_fetched": len(raw_posts),
        "total_filtered": len(filtered),
        "posts": [
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
        ],
    }
    posts_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(filtered)} posts to {posts_json}")

    # Step 4: Generate static site
    print("Generating static site...")
    generate_site(data, output_dir)

    print("Build complete")


if __name__ == "__main__":
    main()
