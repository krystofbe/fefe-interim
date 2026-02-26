"""
Fetch posts from r/fefe_blog_interim via Reddit's RSS/Atom feed.

RSS does not require authentication or API credentials and is not blocked
on GitHub Actions datacenter IPs (unlike the JSON API which returns 403).
"""

from __future__ import annotations

import html
import logging
import re
import xml.etree.ElementTree as ET

import httpx

from scraper.types import Post

logger = logging.getLogger(__name__)

SUBREDDIT = "fefe_blog_interim"
USER_AGENT = "fefe-interim-bot/0.1 (github.com/krystofbe/fefe-interim)"
RSS_URL = f"https://www.reddit.com/r/{SUBREDDIT}/new.rss"

_ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}

# Strip HTML tags to get plain text (RSS content is HTML)
_TAG_RE = re.compile(r"<[^>]+>")
# Reddit wraps selftext in <!-- SC_OFF --><div class="md">...</div><!-- SC_ON -->
_SC_RE = re.compile(r"<!--\s*SC_(?:ON|OFF)\s*-->")
# "submitted by /u/... [link] [comments]" footer Reddit appends
# Matches after HTML→text conversion: "submitted by /u/Name [[link]](url) [[comments]](url)"
_SUBMITTED_RE = re.compile(
    r"\s*submitted\s+by\s+.*?\[*link\]*.*?\[*comments\]*.*$",
    re.DOTALL,
)


def _html_to_markdown(content_html: str) -> str:
    """Convert RSS HTML content to simple markdown.

    Preserves links as markdown [text](url) and paragraphs as double newlines.
    """
    # Remove SC markers
    text = _SC_RE.sub("", content_html)

    # Convert <a href="url">text</a> to [text](url)
    text = re.sub(
        r'<a\s+href="([^"]*)"[^>]*>(.*?)</a>',
        lambda m: f"[{m.group(2)}]({m.group(1)})" if m.group(2) != m.group(1) else m.group(1),
        text,
        flags=re.DOTALL,
    )

    # Convert <blockquote> to markdown >
    text = re.sub(r"<blockquote>(.*?)</blockquote>", lambda m: "\n".join(
        f"> {line}" for line in _TAG_RE.sub("", m.group(1)).strip().split("\n")
    ), text, flags=re.DOTALL)

    # Convert <p> to double newline
    text = re.sub(r"</p>\s*<p>", "\n\n", text)
    text = re.sub(r"</?p>", "\n", text)

    # Convert <br/> to newline
    text = re.sub(r"<br\s*/?>", "\n", text)

    # Strip remaining tags
    text = _TAG_RE.sub("", text)

    # Unescape HTML entities
    text = html.unescape(text)

    # Remove "submitted by /u/... [[link]] [[comments]]" footer
    text = _SUBMITTED_RE.sub("", text)

    # Clean up whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text


def _parse_timestamp(date_str: str) -> float:
    """Parse ISO 8601 date string to Unix timestamp."""
    # RSS dates look like: 2026-02-26T20:27:39+00:00
    from datetime import datetime, timezone

    # Handle timezone offset
    date_str = date_str.replace("+00:00", "+0000").replace("Z", "+0000")
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.timestamp()
    except ValueError:
        return 0.0


def _extract_post_id(entry_id: str) -> str:
    """Extract Reddit post ID from Atom entry ID (e.g. 't3_1rfldoo' -> '1rfldoo')."""
    if entry_id.startswith("t3_"):
        return entry_id[3:]
    return entry_id


def _extract_permalink(link: str) -> str:
    """Extract relative permalink from full Reddit URL."""
    # https://www.reddit.com/r/fefe_blog_interim/comments/... -> /r/fefe_blog_interim/comments/...
    if "reddit.com" in link:
        idx = link.find("/r/")
        if idx >= 0:
            return link[idx:]
    return link


def _parse_entry(entry: ET.Element) -> Post:
    """Parse a single Atom entry into a Post dataclass."""
    title = entry.findtext("atom:title", "", _ATOM_NS)
    author_name = ""
    author_el = entry.find("atom:author/atom:name", _ATOM_NS)
    if author_el is not None and author_el.text:
        author_name = author_el.text.lstrip("/u/")

    content_el = entry.find("atom:content", _ATOM_NS)
    content_html = content_el.text if content_el is not None and content_el.text else ""

    entry_id = entry.findtext("atom:id", "", _ATOM_NS)
    published = entry.findtext("atom:published", "", _ATOM_NS)

    link_el = entry.find("atom:link", _ATOM_NS)
    link = link_el.get("href", "") if link_el is not None else ""

    body = _html_to_markdown(content_html)
    permalink = _extract_permalink(link)

    return Post(
        id=_extract_post_id(entry_id),
        title=title,
        body=body,
        score=0,
        num_comments=0,
        created_utc=_parse_timestamp(published),
        permalink=permalink,
        url=link,
        flair=None,
        upvote_ratio=0.0,
        author=author_name,
    )


def fetch_posts(sort: str = "new", limit: int = 100) -> list[Post]:
    """Fetch up to *limit* posts from r/fefe_blog_interim via RSS.

    Args:
        sort: Reddit listing sort order ("new", "hot", "top").
        limit: Maximum number of posts to collect (RSS max is ~100).

    Returns:
        List of Post dataclasses sorted by created_utc descending (newest first).
    """
    url = f"https://www.reddit.com/r/{SUBREDDIT}/{sort}.rss"
    params = {"sort": sort, "limit": min(limit, 100)}
    headers = {"User-Agent": USER_AGENT}

    try:
        response = httpx.get(url, params=params, headers=headers, timeout=15.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Error fetching RSS feed %s: %s", url, exc)
        return []

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as exc:
        logger.warning("Failed to parse RSS XML: %s", exc)
        return []

    entries = root.findall("atom:entry", _ATOM_NS)
    posts: list[Post] = []

    for entry in entries:
        try:
            posts.append(_parse_entry(entry))
        except (KeyError, ValueError, TypeError) as exc:
            logger.warning("Could not parse RSS entry: %s", exc)

    # Sort newest-first by creation timestamp
    posts.sort(key=lambda p: p.created_utc, reverse=True)
    return posts
