"""
Wilson Score filtering for Reddit posts.

Uses the Wilson Score Interval lower bound to rank posts by statistical
significance. A post with 150/200 upvotes outranks a post with 5/5 upvotes
because the larger sample gives us more confidence in the quality signal.
"""

from __future__ import annotations

import math
import statistics

from scraper.types import Post


def wilson_score_lower_bound(
    upvote_ratio: float,
    total_votes: int,
    z: float = 1.96,
) -> float:
    """Compute the Wilson Score Interval lower bound for a post.

    Args:
        upvote_ratio: Fraction of upvotes, 0.0–1.0 (Reddit's upvote_ratio field).
        total_votes: Total vote count used as sample size proxy (Reddit's score field).
        z: Z-score for the desired confidence level (1.96 = 95% confidence).

    Returns:
        Lower bound of the Wilson confidence interval. Higher values indicate
        more statistically reliable quality. Returns 0.0 if total_votes == 0.

    Formula:
        (p + z²/2n − z·√((p(1−p) + z²/4n) / n)) / (1 + z²/n)
        where p = upvote_ratio, n = total_votes.
    """
    n = total_votes
    if n == 0:
        return 0.0

    p = upvote_ratio
    z2 = z * z
    numerator = p + z2 / (2 * n) - z * math.sqrt((p * (1 - p) + z2 / (4 * n)) / n)
    denominator = 1 + z2 / n
    return numerator / denominator


def _compute_wilson_scores(posts: list[Post]) -> list[tuple[Post, float]]:
    """Return posts paired with their Wilson Score lower bounds.

    Useful for debugging, logging, and inspection. Does NOT apply any filtering.

    Args:
        posts: Posts to score.

    Returns:
        List of (post, wilson_score) tuples, unsorted.
    """
    return [
        (post, wilson_score_lower_bound(post.upvote_ratio, post.score))
        for post in posts
    ]


def filter_posts(
    posts: list[Post],
    min_score: int = 3,
    min_wilson: float | None = None,
    top_n: int | None = None,
) -> list[Post]:
    """Filter posts to statistically significant ones using the Wilson Score.

    Steps:
    1. Remove posts with score < min_score (eliminate single-vote noise).
    2. Compute Wilson Score lower bound for each remaining post.
    3. If min_wilson is None, use the median Wilson Score as adaptive threshold.
    4. Retain only posts at or above the threshold.
    5. Sort by Wilson Score descending (highest confidence first).
    6. If top_n is set, return at most top_n posts.

    Args:
        posts: Raw posts from fetch_posts().
        min_score: Minimum vote count to consider. Default 3 filters out noise
            posts with 1–2 votes that would skew the Wilson distribution.
        min_wilson: Explicit Wilson Score threshold. If None, the median of the
            pool is used — this adapts automatically to subreddit activity level.
        top_n: If set, return only the top N posts after filtering.

    Returns:
        Filtered and sorted list of posts.
    """
    # Step 1: Remove low-vote noise
    candidates = [p for p in posts if p.score >= min_score]

    if not candidates:
        return []

    # Step 2: Compute Wilson Scores
    scored = _compute_wilson_scores(candidates)

    # Step 3: Determine threshold
    if min_wilson is None:
        wilson_values = [ws for _, ws in scored]
        threshold = statistics.median(wilson_values)
    else:
        threshold = min_wilson

    # Step 4: Filter to posts at or above threshold
    filtered = [(post, ws) for post, ws in scored if ws >= threshold]

    # Step 5: Sort by Wilson Score descending
    filtered.sort(key=lambda pair: pair[1], reverse=True)

    # Step 6: Extract posts (drop scores), apply top_n limit
    result = [post for post, _ in filtered]
    if top_n is not None:
        result = result[:top_n]

    return result
