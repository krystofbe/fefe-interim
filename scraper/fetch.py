"""
Fetch posts from r/fefe_blog_interim via Reddit's public JSON API.

No authentication required — Reddit allows anonymous access to public subreddits
via the .json suffix on any listing URL.
"""

from __future__ import annotations

import logging
import time

import httpx

from scraper.types import Post

logger = logging.getLogger(__name__)

SUBREDDIT = "fefe_blog_interim"
USER_AGENT = "fefe-interim-bot/0.1 (github.com/krystof/fefe-interim)"
BASE_URL = f"https://www.reddit.com/r/{SUBREDDIT}"

_PER_PAGE = 100  # Reddit max per request
_SLEEP_BETWEEN_PAGES = 1  # seconds, per Reddit rate-limit guidelines


def _parse_post(data: dict) -> Post:
    """Parse a single Reddit listing child into a Post dataclass."""
    return Post(
        id=data["id"],
        title=data.get("title", ""),
        body=data.get("selftext", ""),
        score=int(data.get("score", 0)),
        num_comments=int(data.get("num_comments", 0)),
        created_utc=float(data.get("created_utc", 0.0)),
        permalink=data.get("permalink", ""),
        url=data.get("url", ""),
        flair=data.get("link_flair_text") or None,
        upvote_ratio=float(data.get("upvote_ratio", 0.0)),
        author=data.get("author", ""),
    )


def fetch_posts(sort: str = "new", limit: int = 500) -> list[Post]:
    """Fetch up to *limit* posts from r/fefe_blog_interim.

    Args:
        sort: Reddit listing sort order ("new", "hot", "top", …).
        limit: Maximum number of posts to collect across all pages.

    Returns:
        List of Post dataclasses sorted by created_utc descending (newest first).
    """
    posts: list[Post] = []
    after: str | None = None

    headers = {"User-Agent": USER_AGENT}

    with httpx.Client(timeout=15.0, headers=headers) as client:
        while len(posts) < limit:
            page_limit = min(_PER_PAGE, limit - len(posts))
            params: dict[str, str | int] = {"limit": page_limit}
            if after:
                params["after"] = after

            url = f"{BASE_URL}/{sort}.json"
            try:
                response = client.get(url, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "HTTP error fetching %s (status %s) — returning %d posts collected so far",
                    url,
                    exc.response.status_code,
                    len(posts),
                )
                break
            except httpx.RequestError as exc:
                logger.warning(
                    "Request error fetching %s: %s — returning %d posts collected so far",
                    url,
                    exc,
                    len(posts),
                )
                break

            payload = response.json()
            children = payload.get("data", {}).get("children", [])
            if not children:
                break

            for child in children:
                child_data = child.get("data", {})
                try:
                    posts.append(_parse_post(child_data))
                except (KeyError, ValueError, TypeError) as exc:
                    logger.warning("Could not parse post: %s", exc)

            after = payload.get("data", {}).get("after")
            if not after:
                # No more pages
                break

            if len(posts) < limit:
                time.sleep(_SLEEP_BETWEEN_PAGES)

    # Sort newest-first by creation timestamp
    posts.sort(key=lambda p: p.created_utc, reverse=True)
    return posts
