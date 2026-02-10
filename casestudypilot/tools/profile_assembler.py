"""Assembles presenter profiles from component JSON files."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_jinja_env() -> Environment:
    """Create Jinja2 environment for template rendering with custom filters.

    Returns:
        Configured Jinja2 Environment
    """
    template_dir = Path(__file__).parent.parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Add custom filter for duration formatting
    def format_duration(minutes: int) -> str:
        """Convert minutes to 'X hours Y minutes' format."""
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0 and mins > 0:
            return f"{hours} hours {mins} minutes"
        elif hours > 0:
            return f"{hours} hours"
        else:
            return f"{mins} minutes"

    env.filters["format_duration"] = format_duration

    return env


def calculate_stats(aggregation_data: Dict[str, Any], biography_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate fun stats from aggregation data for profile table.

    Args:
        aggregation_data: Aggregated talk data
        biography_data: Biography and GitHub data

    Returns:
        Dictionary of stat values (not pre-formatted strings except where noted)
    """
    stats = aggregation_data.get("stats", {})

    # Total talks (return number, template handles formatting)
    total_talks = stats.get("total_talks", 0)

    # Years active (first - last with span)
    years_active = stats.get("years_active", {})
    first_year = years_active.get("first", "Unknown")
    latest_year = years_active.get("latest", "Unknown")
    span = years_active.get("span", 0)
    years_active_str = f"{first_year} - {latest_year} ({span} year{'s' if span != 1 else ''})"

    # Top technology (most discussed CNCF project from cncf_projects array)
    cncf_projects = aggregation_data.get("cncf_projects", [])
    if cncf_projects:
        # Find project with highest talk_count
        top_project = max(cncf_projects, key=lambda p: p.get("talk_count", 0))
        top_tech_name = top_project.get("name", "N/A")
        top_tech_count = top_project.get("talk_count", 0)
        top_technology_str = f"{top_tech_name} ({top_tech_count} talk{'s' if top_tech_count != 1 else ''})"
    else:
        top_technology_str = "N/A"

    # Primary focus (top expertise areas - show top 2, join with &)
    expertise_areas = aggregation_data.get("expertise_areas", [])
    if expertise_areas:
        # Get top 2 areas (sorted by talk_count in aggregation skill)
        primary_areas = [ea["area"] for ea in expertise_areas[:2]]
        primary_focus_str = " & ".join(primary_areas)
    else:
        primary_focus_str = "N/A"

    # GitHub followers (biography_data contains GitHub data directly at top level)
    followers = biography_data.get("followers", 0)
    github_followers_str = str(followers)

    # Organizations (from biography_data.organizations array at top level)
    organizations = biography_data.get("organizations", [])
    if organizations:
        # Format organization names nicely (capitalize, handle kubernetes-sigs)
        formatted_orgs = []
        for org in organizations[:3]:  # Limit to top 3
            org_lower = org.lower()
            if org_lower == "kubernetes-sigs" or "kubernetes sigs" in org_lower:
                formatted_orgs.append("Kubernetes SIGs")
            elif org_lower == "cncf":
                formatted_orgs.append("CNCF")
            elif len(org) <= 4:
                formatted_orgs.append(org.upper())
            else:
                # Capitalize properly (e.g., "kubernetes" -> "Kubernetes")
                formatted_orgs.append(org.capitalize())
        organizations_str = ", ".join(formatted_orgs)
    else:
        organizations_str = "N/A"

    # Total speaking time (convert minutes to "X hours Y minutes")
    total_minutes = stats.get("total_speaking_minutes", 0)
    hours = total_minutes // 60
    mins = total_minutes % 60
    if hours > 0 and mins > 0:
        total_speaking_time_str = f"{hours} hours {mins} minutes"
    elif hours > 0:
        total_speaking_time_str = f"{hours} hours"
    else:
        total_speaking_time_str = f"{mins} minutes"

    return {
        "total_talks": total_talks,  # Return number for template pluralization
        "years_active": years_active_str,
        "top_technology": top_technology_str,
        "primary_focus": primary_focus_str,
        "github_followers": github_followers_str,
        "organizations": organizations_str,
        "total_speaking_time": total_speaking_time_str,
    }


def determine_profile_version(existing_profile_path: Optional[Path]) -> str:
    """Determine profile version (1.0 for new, incremented for updates).

    Args:
        existing_profile_path: Path to existing profile file (None for new profiles)

    Returns:
        Version string (e.g., "1.0", "2.0")
    """
    if not existing_profile_path or not existing_profile_path.exists():
        return "1.0"

    # Try to read version from existing file frontmatter
    try:
        with open(existing_profile_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Look for profile_version in frontmatter
            if "profile_version:" in content:
                # Extract version (format: "profile_version: X.Y")
                for line in content.split("\n"):
                    if line.startswith("profile_version:"):
                        version_str = line.split(":", 1)[1].strip()
                        try:
                            # Parse and increment major version
                            major_version = int(float(version_str))
                            return f"{major_version + 1}.0"
                        except ValueError:
                            pass
    except Exception:
        pass

    # Default: increment from 1.0 to 2.0
    return "2.0"


def assemble_presenter_profile(
    biography_data: Dict[str, Any],
    aggregation_data: Dict[str, Any],
    sections_data: Dict[str, Any],
    existing_profile_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Assemble final presenter profile from component JSON files.

    Args:
        biography_data: Biography and GitHub data from biography skill
        aggregation_data: Aggregated talk data from aggregation skill
        sections_data: Generated profile sections from generation skill
        existing_profile_path: Path to existing profile (for updates)
        output_path: Optional output path for markdown file

    Returns:
        Dictionary containing:
            - output_path: Path to generated markdown file
            - metadata_path: Path to generated JSON metadata file
            - presenter_name: Full name of presenter
            - github_username: GitHub username
            - profile_version: Version number

    Raises:
        ValueError: If required data is missing
        FileNotFoundError: If template not found
    """
    # Validate required data
    if not biography_data.get("name"):
        raise ValueError("Biography data missing required 'name' field")
    if not biography_data.get("github_username"):
        raise ValueError("Biography data missing required 'github_username' field")

    # Extract key information
    name = biography_data["name"]
    github_username = biography_data["github_username"]

    # Calculate stats for table
    stats = calculate_stats(aggregation_data, biography_data)

    # Determine profile version
    profile_version = determine_profile_version(existing_profile_path)

    # Get current timestamp
    current_date = datetime.utcnow().isoformat() + "Z"
    current_date_short = datetime.utcnow().strftime("%Y-%m-%d")

    # Group talks by year for template
    talks_by_year = {}
    for talk in aggregation_data.get("talk_summaries", []):
        date_str = talk.get("date", "")
        if date_str:
            year = date_str.split("-")[0] if "-" in date_str else "Unknown"
        else:
            year = "Unknown"

        if year not in talks_by_year:
            talks_by_year[year] = []

        # Format duration nicely
        duration_secs = talk.get("duration", 0)
        duration_mins = duration_secs // 60
        if duration_mins >= 60:
            hours = duration_mins // 60
            mins = duration_mins % 60
            duration_formatted = f"{hours} hour{'s' if hours != 1 else ''} {mins} minutes"
        else:
            duration_formatted = f"{duration_mins} minutes"

        talks_by_year[year].append(
            {
                "title": talk.get("title", "Untitled"),
                "event": talk.get("event", ""),
                "url": talk.get("url", ""),
                "duration": duration_formatted,
                "summary": talk.get("summary", ""),
                "topics": talk.get("topics", []),
            }
        )

    # Sort years descending and prepare for template
    talks_by_year_list = [
        {"year": year, "talks": talks_by_year[year]} for year in sorted(talks_by_year.keys(), reverse=True)
    ]

    # Format expertise areas as list of strings with context
    expertise_formatted = []
    for area in aggregation_data.get("expertise_areas", []):
        if isinstance(area, dict):
            area_name = area.get("area", "Unknown")
            context_text = area.get("context", "")
            expertise_formatted.append(f"**{area_name}**: {context_text}")
        else:
            expertise_formatted.append(str(area))

    # Format CNCF projects with contexts (join if list, use as-is if string)
    cncf_projects_formatted = []
    for project in aggregation_data.get("cncf_projects", []):
        if isinstance(project, dict):
            project_formatted = {
                "name": project.get("name", "Unknown"),
                "talk_count": project.get("talk_count", 0),
                "contexts": project.get("usage_context", ""),
            }
            cncf_projects_formatted.append(project_formatted)

    # Merge context for template
    context = {
        "name": name,
        "github_username": github_username,
        "location": biography_data.get("location", "Unknown"),
        "role": biography_data.get("current_role", "Unknown"),
        "biography": sections_data.get("overview", ""),
        "stats": stats,
        "expertise_areas": expertise_formatted,
        "cncf_projects": cncf_projects_formatted,
        "talks_by_year": talks_by_year_list,
        "key_themes": sections_data.get("key_themes", ""),
        "generated_date": current_date_short,
        "profile_version": profile_version,
    }

    # Render template
    env = create_jinja_env()
    try:
        template = env.get_template("presenter_profile.md.j2")
    except Exception as e:
        raise FileNotFoundError(f"Template not found: presenter_profile.md.j2 - {e}")

    rendered = template.render(**context)

    # Determine output paths
    if output_path is None:
        output_path = Path("people") / f"{github_username}.md"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write rendered markdown
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    # Create metadata JSON
    metadata_path = Path("people") / "metadata" / f"{github_username}.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    # Get list of video IDs from aggregation data
    video_ids = []
    for talk in aggregation_data.get("talk_summaries", []):
        video_id = talk.get("video_id")
        if video_id:
            video_ids.append(video_id)

    # Build metadata structure
    github_data = biography_data.get("github_data", {})
    metadata = {
        "name": name,
        "github_username": github_username,
        "profile_version": float(profile_version),
        "created_date": current_date if profile_version == "1.0" else None,
        "updated_date": current_date,
        "current_role": biography_data.get("current_role", "Unknown"),
        "location": biography_data.get("location", "Unknown"),
        "organizations": github_data.get("organizations", []),
        "social_profiles": {
            "github": f"https://github.com/{github_username}",
            "website": github_data.get("website") if github_data.get("website") else None,
        },
        "video_ids_processed": video_ids,
        "stats": {
            "total_talks": aggregation_data.get("stats", {}).get("total_talks", 0),
            "years_active": aggregation_data.get("stats", {}).get("years_active", {}),
            "total_speaking_minutes": aggregation_data.get("stats", {}).get("total_speaking_minutes", 0),
            "github_followers": github_data.get("followers", 0),
            "most_discussed_project": aggregation_data.get("stats", {}).get("most_discussed_project", {}),
            "most_active_year": aggregation_data.get("stats", {}).get("most_active_year"),
        },
        "expertise_areas": aggregation_data.get("expertise_areas", []),
        "cncf_projects": aggregation_data.get("cncf_projects", []),
        "talks": [
            {
                "video_id": talk.get("video_id"),
                "title": talk.get("title", ""),
                "date": talk.get("date", ""),
                "duration": talk.get("duration", 0),
                "url": talk.get("url", ""),
                "summary": talk.get("summary", ""),
                "topics": talk.get("topics", []),
            }
            for talk in aggregation_data.get("talk_summaries", [])
        ],
    }

    # Write metadata JSON
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return {
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "presenter_name": name,
        "github_username": github_username,
        "profile_version": profile_version,
    }
