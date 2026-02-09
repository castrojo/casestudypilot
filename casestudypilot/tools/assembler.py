"""Assembles case study from component JSON files."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_jinja_env() -> Environment:
    """Create Jinja2 environment for template rendering."""
    template_dir = Path(__file__).parent.parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def assemble_case_study(
    video_data_path: Path,
    analysis_path: Path,
    sections_path: Path,
    verification_path: Path,
    output_path: Optional[Path] = None,
    screenshots_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Assemble final case study from component JSON files."""
    # Load all JSON files
    video_data = load_json_file(video_data_path)
    analysis = load_json_file(analysis_path)
    sections = load_json_file(sections_path)
    verification = load_json_file(verification_path)

    # Verify company is member
    if not verification.get("is_member", False):
        raise ValueError(
            f"Company '{verification.get('query_name')}' is not a CNCF end-user member "
            f"(confidence: {verification.get('confidence', 0)})"
        )

    # Load screenshots if provided
    screenshots = None
    if screenshots_path and screenshots_path.exists():
        screenshots_data = load_json_file(screenshots_path)
        # Convert list to dict keyed by section for easier template access
        screenshots = {s["section"]: s for s in screenshots_data.get("screenshots", [])}

    # Merge context for template
    context = {
        "company": verification.get(
            "matched_name", verification.get("query_name", "Unknown")
        ),
        "video": video_data,
        "analysis": analysis,
        "sections": sections,
        "verification": verification,
        "screenshots": screenshots,
    }

    # Render template
    env = create_jinja_env()
    template = env.get_template("case_study.md.j2")
    rendered = template.render(**context)

    # Determine output path
    if output_path is None:
        company_slug = context["company"].lower().replace(" ", "-").replace(",", "")
        output_path = Path("case-studies") / f"{company_slug}.md"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write rendered content
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    return {
        "output_path": str(output_path),
        "company_name": context["company"],
        "cncf_projects": analysis.get("cncf_projects", []),
    }
