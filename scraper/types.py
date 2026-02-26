"""
Post dataclass representing a single Reddit post from r/fefe_blog_interim.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


# Matches markdown links: [text](url) — captures the URL in the parentheses
_MARKDOWN_LINK_RE = re.compile(r'\[[^\]]*\]\((https?://[^)]+)\)')
# After stripping markdown links, match any remaining bare https:// URLs
_BARE_URL_RE = re.compile(r'https?://[^\s\)>]+')


@dataclass
class Post:
    """A single post from r/fefe_blog_interim."""

    id: str
    title: str
    body: str  # selftext (markdown)
    score: int
    num_comments: int
    created_utc: float  # Unix timestamp
    permalink: str  # relative Reddit URL, e.g. /r/fefe_blog_interim/comments/...
    url: str  # full URL — same as permalink for self posts, external for link posts
    flair: str | None  # link_flair_text
    upvote_ratio: float  # 0.0–1.0
    author: str

    @property
    def reddit_url(self) -> str:
        """Full Reddit URL for this post."""
        return f"https://www.reddit.com{self.permalink}"

    @property
    def external_links(self) -> list[str]:
        """Extract non-Reddit URLs from the post body.

        Collects markdown link targets [text](url) first, then strips all
        markdown links from the body and collects any remaining bare https://
        URLs. Filters out reddit.com links (internal). Deduplicates.
        """
        body = self.body

        # Step 1: Collect all URLs from markdown link targets
        markdown_urls = _MARKDOWN_LINK_RE.findall(body)

        # Step 2: Remove all markdown link syntax from body, then find bare URLs.
        # This avoids double-counting URLs used as both display text and href.
        stripped = _MARKDOWN_LINK_RE.sub("", body)
        bare_urls = _BARE_URL_RE.findall(stripped)

        # Step 3: Deduplicate while preserving order, filter Reddit-internal URLs
        seen: set[str] = set()
        result: list[str] = []
        for url in markdown_urls + bare_urls:
            if url in seen:
                continue
            seen.add(url)
            if "reddit.com" not in url:
                result.append(url)

        return result
