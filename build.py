"""
fefe-interim build pipeline entry point.

Phase 2 will extend this with actual scraper calls.
Phase 3 will extend this with actual generator calls.
"""

from pathlib import Path

import scraper
import generator


def main() -> None:
    print("fefe-interim build started")

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir.resolve()}")

    print("Build complete (no tasks configured yet)")


if __name__ == "__main__":
    main()
