"""RSS 2.0 feed generator for fefe-interim."""

import xml.etree.ElementTree as ET
from email.utils import formatdate
from pathlib import Path


def generate_feed(posts_data: dict, output_dir: Path, site_url: str = "") -> None:
    """Generate an RSS 2.0 feed from posts_data and write to output_dir/feed.xml.

    Args:
        posts_data: Dict with 'posts' list, each post having id, title, body,
                    score, num_comments, created_utc, permalink, reddit_url,
                    url, flair, upvote_ratio, author, external_links.
        output_dir: Directory where feed.xml will be written.
        site_url: Base URL of the site (e.g. "https://fefe-interim.example.com").
    """
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "fefe's blog — interim"
    ET.SubElement(channel, "link").text = site_url
    ET.SubElement(channel, "description").text = (
        "Kuratierte Posts aus r/fefe_blog_interim — inoffizieller Ersatz während fefes Pause"
    )
    ET.SubElement(channel, "language").text = "de-de"

    # lastBuildDate: use the most recent post or current time
    posts = posts_data.get("posts", [])
    if posts:
        latest_ts = max(p.get("created_utc", 0) for p in posts)
        ET.SubElement(channel, "lastBuildDate").text = formatdate(timeval=latest_ts, usegmt=True)
    else:
        ET.SubElement(channel, "lastBuildDate").text = formatdate(usegmt=True)

    # Atom self-link
    atom_link = ET.SubElement(channel, "atom:link")
    atom_link.set("href", f"{site_url}/feed.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for post in posts:
        item = ET.SubElement(channel, "item")

        # Title: use post title or fall back to first 80 chars of body
        title_text = post.get("title", "").strip()
        if not title_text:
            body = post.get("body", "")
            title_text = body[:80].strip() + "..." if len(body) > 80 else body.strip()

        ET.SubElement(item, "title").text = title_text

        # Link: Reddit discussion page
        reddit_url = post.get("reddit_url", "")
        ET.SubElement(item, "link").text = reddit_url

        # Description: post body as plain text
        body = post.get("body", "")
        description_text = _strip_markdown_links(body)
        desc_elem = ET.SubElement(item, "description")
        desc_elem.text = description_text

        # pubDate: RFC 822 from created_utc
        created_utc = post.get("created_utc", 0)
        ET.SubElement(item, "pubDate").text = formatdate(timeval=created_utc, usegmt=True)

        # guid
        guid_elem = ET.SubElement(item, "guid")
        guid_elem.set("isPermaLink", "true")
        guid_elem.text = reddit_url

        # category (flair)
        flair = post.get("flair", "")
        if flair:
            ET.SubElement(item, "category").text = flair

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    tree.write(str(output_dir / "feed.xml"), encoding="unicode", xml_declaration=True)


def _strip_markdown_links(text: str) -> str:
    """Strip markdown link syntax, keeping the link text.

    Converts [text](url) -> text and bare URLs remain as-is.
    """
    import re
    # Replace [text](url) with just text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text
