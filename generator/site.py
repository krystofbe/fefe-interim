"""Site generation module for fefe-interim."""

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup


GERMAN_MONTHS = {
    1: "Januar",
    2: "Februar",
    3: "März",
    4: "April",
    5: "Mai",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Dezember",
}


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


def _group_posts_by_month(posts: list[dict]) -> dict[tuple[int, int], list[dict]]:
    """Group posts by (year, month) using created_utc timestamp.

    Returns a dict mapping (year, month) tuples to lists of posts.
    Posts within each month are sorted by created_utc descending (newest first).
    """
    grouped: dict[tuple[int, int], list[dict]] = {}
    for post in posts:
        dt = datetime.fromtimestamp(post["created_utc"], tz=timezone.utc)
        key = (dt.year, dt.month)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(post)

    # Sort posts within each month newest first
    for key in grouped:
        grouped[key].sort(key=lambda p: p["created_utc"], reverse=True)

    return grouped


def _build_archive_months(grouped: dict[tuple[int, int], list[dict]]) -> list[dict]:
    """Build the archive_months list for sidebar context.

    Each entry: {"year": int, "month": int, "label": "Monat YYYY", "count": int, "path": "YYYY/MM/index.html"}
    Sorted by date descending (newest month first).
    """
    months = []
    for (year, month), posts in grouped.items():
        label = f"{GERMAN_MONTHS[month]} {year}"
        path = f"{year}/{month:02d}/index.html"
        months.append(
            {
                "year": year,
                "month": month,
                "label": label,
                "count": len(posts),
                "path": path,
            }
        )

    # Sort newest month first
    months.sort(key=lambda m: (m["year"], m["month"]), reverse=True)
    return months


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

    posts = posts_data["posts"]

    # Group posts by month and build archive sidebar data
    grouped = _group_posts_by_month(posts)
    archive_months = _build_archive_months(grouped)

    # Render index.html
    template = env.get_template("index.html")
    html = template.render(posts=posts, archive_months=archive_months)

    index_path = output_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")
    print(f"Wrote {index_path} ({len(html)} bytes)")

    # Render archive pages for each month
    archive_template = env.get_template("archive.html")
    archive_count = 0
    for (year, month), month_posts in grouped.items():
        label = f"{GERMAN_MONTHS[month]} {year}"
        archive_dir = output_dir / str(year) / f"{month:02d}"
        archive_dir.mkdir(parents=True, exist_ok=True)

        archive_html = archive_template.render(
            posts=month_posts,
            month_label=label,
            archive_months=archive_months,
        )

        archive_path = archive_dir / "index.html"
        archive_path.write_text(archive_html, encoding="utf-8")
        archive_count += 1

    print(f"Generated {archive_count} archive pages")

    # Copy static assets to output dir
    static_src = Path("static")
    static_dst = output_dir / "static"
    if static_src.exists():
        if static_dst.exists():
            shutil.rmtree(static_dst)
        shutil.copytree(static_src, static_dst)
        print(f"Copied static/ to {static_dst}")
