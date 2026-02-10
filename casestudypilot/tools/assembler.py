"""Assembles case study from component JSON files."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from casestudypilot.utils import slugify
from casestudypilot.hyperlinks import add_hyperlinks, COMPANY_URLS, PROJECT_URLS


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_jinja_env() -> Environment:
    """Create Jinja2 environment for template rendering with custom filters."""
    template_dir = Path(__file__).parent.parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Add custom filter for hyperlinks
    def add_links_filter(text: str, company: str = "") -> str:
        """Jinja2 filter to add hyperlinks to text."""
        return add_hyperlinks(text, company if company else None)

    # Add custom filter for project URLs
    def project_url_filter(project_name: str) -> str:
        """Jinja2 filter to get project URL."""
        return PROJECT_URLS.get(
            project_name, f"https://{project_name.lower().replace(' ', '')}.io"
        )

    env.filters["add_links"] = add_links_filter
    env.filters["project_url"] = project_url_filter

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

    # Get company name
    company_name = verification.get(
        "matched_name", verification.get("query_name", "Unknown")
    )

    # Get company URL from mapping or use placeholder
    company_url = COMPANY_URLS.get(
        company_name, f"https://www.{company_name.lower().replace(' ', '')}.com"
    )

    # Merge context for template
    context = {
        "company": company_name,
        "company_url": company_url,
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
        # Use slugified video title as filename
        video_title = video_data.get("title", "unknown-video")
        title_slug = slugify(video_title)
        output_path = Path("case-studies") / f"{title_slug}.md"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write rendered content
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    # Extract project names from analysis (handles both dict and string formats)
    # Note: CNCF projects may be in dict format (with name/usage_context)
    # or simple string format from older analyses
    cncf_projects = analysis.get("cncf_projects", [])
    project_names = []
    for proj in cncf_projects:
        if isinstance(proj, dict):
            # Dict format: extract name field
            if "name" not in proj:
                # Log warning for malformed data but continue gracefully
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"CNCF project dict missing 'name' field: {proj}")
                # Use first available value as fallback
                name = next(
                    (v for k, v in proj.items() if isinstance(v, str)), "Unknown"
                )
                project_names.append(name)
            else:
                project_names.append(proj["name"])
        else:
            # String format: use directly
            project_names.append(str(proj))

    return {
        "output_path": str(output_path),
        "company_name": context["company"],
        "cncf_projects": project_names,
    }
