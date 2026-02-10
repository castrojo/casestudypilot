"""Validates screenshot uniqueness in generated markdown files."""

import sys
import re
from pathlib import Path
from collections import Counter


def validate_screenshots(markdown_file: Path) -> int:
    """
    Validate that screenshots are not duplicated in markdown.

    Args:
        markdown_file: Path to markdown file

    Returns:
        Exit code:
        - 0: All screenshots unique
        - 1: Warnings about screenshot usage
        - 2: Critical - duplicate screenshots found
    """
    try:
        content = markdown_file.read_text()
    except Exception as e:
        print(f"❌ Cannot read file: {e}", file=sys.stderr)
        return 2

    # Extract all screenshot references from markdown
    # Pattern: ![...](images/slug/screenshot-N.jpg)
    screenshot_pattern = r"!\[.*?\]\(images/[^)]+/(screenshot-\d+\.jpg)\)"
    screenshots = re.findall(screenshot_pattern, content)

    if not screenshots:
        print("⚠️  Warning: No screenshots found in document", file=sys.stderr)
        return 1

    # Count occurrences of each screenshot
    screenshot_counts = Counter(screenshots)
    duplicates = {name: count for name, count in screenshot_counts.items() if count > 1}

    if duplicates:
        print("❌ Critical: Duplicate screenshots detected", file=sys.stderr)
        print(f"\n📸 Total screenshot references: {len(screenshots)}", file=sys.stderr)
        print(f"📸 Unique screenshots: {len(screenshot_counts)}", file=sys.stderr)
        print("\nDuplicate screenshots:", file=sys.stderr)
        for screenshot, count in sorted(duplicates.items()):
            print(f"  - {screenshot}: appears {count} times", file=sys.stderr)

        print("\n**Action Required:**", file=sys.stderr)
        print("Each screenshot must appear EXACTLY ONCE in the document.", file=sys.stderr)
        print(
            "To fix: Use different screenshots for different sections, or refer to diagrams with text.", file=sys.stderr
        )
        return 2

    # Check if screenshots are sequential (1, 2, 3, ... not 1, 3, 5)
    screenshot_numbers = sorted([int(re.search(r"screenshot-(\d+)", s).group(1)) for s in screenshots])
    expected_numbers = list(range(1, len(screenshot_numbers) + 1))

    if screenshot_numbers != expected_numbers:
        print("⚠️  Warning: Screenshot numbering is not sequential", file=sys.stderr)
        print(f"   Found: {screenshot_numbers}", file=sys.stderr)
        print(f"   Expected: {expected_numbers}", file=sys.stderr)
        print("   This may indicate missing or skipped screenshots.", file=sys.stderr)
        return 1

    # Success
    print(f"✅ Screenshot validation passed", file=sys.stderr)
    print(f"   - {len(screenshots)} unique screenshots found", file=sys.stderr)
    print(f"   - Sequential numbering: screenshot-1 through screenshot-{len(screenshots)}", file=sys.stderr)
    return 0


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate screenshot uniqueness in markdown")
    parser.add_argument("markdown_file", type=Path, help="Path to markdown file")

    args = parser.parse_args()

    exit_code = validate_screenshots(args.markdown_file)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
