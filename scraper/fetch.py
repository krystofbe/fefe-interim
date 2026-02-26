"""
Fetch posts from r/fefe_blog_interim via Reddit's OAuth API.

Uses OAuth2 "script" app credentials (client_id / client_secret) to authenticate.
Falls back to the public JSON API if no credentials are set.
"""

from __future__ import annotations

import logging
import os
import time

import httpx

from scraper.types import Post

logger = logging.getLogger(__name__)

SUBREDDIT = "fefe_blog_interim"
USER_AGENT = "fefe-interim-bot/0.1 (github.com/krystofbe/fefe-interim)"

# OAuth credentials — set via environment variables or GitHub Actions secrets
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")

_PER_PAGE = 100  # Reddit max per request
_SLEEP_BETWEEN_PAGES = 1  # seconds, per Reddit rate-limit guidelines


def _get_oauth_token() -> str | None:
    """Obtain an OAuth2 bearer token using client credentials grant."""
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        return None

    try:
        response = httpx.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": USER_AGENT},
            timeout=10.0,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if token:
            logger.info("Obtained Reddit OAuth token")
        return token
    except (httpx.HTTPError, KeyError) as exc:
        logger.warning("Failed to obtain OAuth token: %s", exc)
        return None


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

    # Try OAuth first, fall back to public API
    token = _get_oauth_token()
    if token:
        base_url = f"https://oauth.reddit.com/r/{SUBREDDIT}"
        headers = {
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {token}",
        }
        logger.info("Using Reddit OAuth API")
    else:
        base_url = f"https://www.reddit.com/r/{SUBREDDIT}"
        headers = {"User-Agent": USER_AGENT}
        logger.info("Using Reddit public JSON API (no credentials)")

    with httpx.Client(timeout=15.0, headers=headers) as client:
        while len(posts) < limit:
            page_limit = min(_PER_PAGE, limit - len(posts))
            params: dict[str, str | int] = {"limit": page_limit}
            if after:
                params["after"] = after

            url = f"{base_url}/{sort}.json"
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
