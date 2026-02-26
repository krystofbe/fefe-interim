"""Site generation module for fefe-interim."""

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup


def _markdown_to_html(text: str) -> Markup:
    """Convert Reddit markdown to safe HTML using regex only.

    Handles:
    - [text](url) -> <a href="url" target="_blank">text</a>
    - **bold** -> <strong>bold</strong>
    - Double newlines -> paragraph breaks
    - Wraps content in <p> tags
    """
    if not text:
        return Markup("<p></p>")

    # Split into paragraphs on double newlines
    paragraphs = re.split(r"\n\n+", text.strip())

    result_parts = []
    for para in paragraphs:
        if not para.strip():
            continue

        # Convert markdown links [text](url) to HTML anchors
        para = re.sub(
            r"\[([^\[\]]+)\]\((https?://[^\s\)]+)\)",
            r'<a href="\2" target="_blank">\1</a>',
            para,
        )

        # Convert **bold** to <strong>
        para = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", para)

        # Convert bare URLs (not already in an href) to links
        # Match URLs not preceded by href=" or >(
        para = re.sub(
            r'(?<!href=")(https?://[^\s<>\)"]+)',
            r'<a href="\1" target="_blank">\1</a>',
            para,
        )

        result_parts.append(f"<p>{para}</p>")

    return Markup("\n".join(result_parts))


def _format_date(timestamp: float) -> str:
    """Convert Unix timestamp to 'YYYY-MM-DD · HH:MM' string."""
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d · %H:%M")


def _tag_class(flair: str | None) -> str:
    """Convert flair string to CSS class name.

    Examples:
    - 'Security' -> 'tag-security'
    - 'Politik' -> 'tag-politik'
    - None -> ''
    """
    if not flair:
        return ""
    return f"tag-{flair.lower()}"


def generate_site(posts_data: dict, output_dir: Path) -> None:
    """Generate the static site HTML from posts data.

    Args:
        posts_data: Dict with 'posts' list (from posts.json structure)
        output_dir: Directory to write output files to
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape(["html"]),
    )

    # Register custom filters
    env.filters["markdown_to_html"] = _markdown_to_html
    env.filters["format_date"] = _format_date
    env.filters["tag_class"] = _tag_class

    # Render index.html
    template = env.get_template("index.html")
    html = template.render(posts=posts_data["posts"])

    index_path = output_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")
    print(f"Wrote {index_path} ({len(html)} bytes)")

    # Copy static assets to output dir
    static_src = Path("static")
    static_dst = output_dir / "static"
    if static_src.exists():
        if static_dst.exists():
            shutil.rmtree(static_dst)
        shutil.copytree(static_src, static_dst)
        print(f"Copied static/ to {static_dst}")
