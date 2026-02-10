"""Assembles reference architecture markdown from JSON using Jinja2 template."""

import json
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


def copy_screenshots(screenshot_paths: List[str], company_slug: str) -> List[Dict[str, str]]:
    """
    Copy screenshots to reference architecture images directory.

    Args:
        screenshot_paths: List of paths to screenshot files
        company_slug: Company slug for subdirectory

    Returns:
        List of screenshot metadata dicts with path and caption
    """
    # Create target directory
    screenshot_dir = Path(f"reference-architectures/images/{company_slug}")
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    screenshots = []
    for i, screenshot_path in enumerate(screenshot_paths[:6], 1):  # Max 6 screenshots
        source = Path(screenshot_path)

        if not source.exists():
            print(f"⚠️ Warning: Screenshot not found: {screenshot_path}", file=sys.stderr)
            continue

        # Copy screenshot with sequential naming
        dest_path = screenshot_dir / f"screenshot-{i}.jpg"
        shutil.copy(source, dest_path)

        # Add to screenshot metadata
        screenshots.append(
            {
                "path": f"images/{company_slug}/screenshot-{i}.jpg",
                "caption": f"Figure {i}: Architecture Component",
                "section": "architecture_overview",  # Default section
            }
        )

    return screenshots


def assemble_reference_architecture(json_path: str, screenshot_paths: List[str], output_path: str) -> int:
    """
    Assemble final reference architecture markdown.

    Args:
        json_path: Path to reference architecture JSON file
        screenshot_paths: List of screenshot file paths
        output_path: Output markdown file path

    Returns:
        Exit code: 0 (success), 2 (error)
    """
    # Load JSON
    try:
        with open(json_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"❌ Error loading JSON: {e}", file=sys.stderr)
        return 2

    # Extract company name and create slug
    company_name = data.get("metadata", {}).get("company_name", "unknown")
    company_slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "")

    # Copy screenshots and prepare metadata
    if screenshot_paths:
        screenshots = copy_screenshots(screenshot_paths, company_slug)
        data["screenshots"] = screenshots
        print(f"📸 Copied {len(screenshots)} screenshots to reference-architectures/images/{company_slug}/")
    else:
        data["screenshots"] = []
        print("⚠️ No screenshots provided", file=sys.stderr)

    # Load Jinja2 template
    try:
        # Try to find template in multiple locations
        template_locations = [
            Path("templates"),
            Path(__file__).parent.parent.parent / "templates",
            Path.cwd() / "templates",
        ]

        env = None
        for location in template_locations:
            if location.exists() and (location / "reference_architecture.md.j2").exists():
                env = Environment(loader=FileSystemLoader(str(location)))
                break

        if env is None:
            print(f"❌ Template not found in any of: {template_locations}", file=sys.stderr)
            return 2

        template = env.get_template("reference_architecture.md.j2")
    except TemplateNotFound as e:
        print(f"❌ Template not found: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"❌ Error loading template: {e}", file=sys.stderr)
        return 2

    # Render template
    try:
        markdown = template.render(**data)
    except Exception as e:
        print(f"❌ Error rendering template: {e}", file=sys.stderr)
        return 2

    # Write output
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(markdown)
        print(f"✅ Reference architecture assembled: {output_path}")
    except Exception as e:
        print(f"❌ Error writing output: {e}", file=sys.stderr)
        return 2

    return 0


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Assemble reference architecture markdown from JSON and screenshots")
    parser.add_argument("json_file", help="Reference architecture JSON file")
    parser.add_argument("screenshots", nargs="*", help="Screenshot files (up to 6 images)")
    parser.add_argument("--output", required=True, help="Output markdown file path")

    args = parser.parse_args()

    exit_code = assemble_reference_architecture(args.json_file, args.screenshots, args.output)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
