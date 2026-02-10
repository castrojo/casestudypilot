"""Update README.md with index of generated case studies and reference architectures."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def extract_company_from_markdown(file_path: Path) -> str:
    """
    Extract company name from markdown H1 heading.

    Expected format:
        # [Company Name](url) Case Study
        # [Company Name](url) Reference Architecture

    Args:
        file_path: Path to markdown file

    Returns:
        Company name extracted from H1, or title-cased filename slug as fallback
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Match H1 with markdown link: # [Company](url) ...
        h1_pattern = r"^#\s+\[([^\]]+)\]"
        match = re.search(h1_pattern, content, re.MULTILINE)

        if match:
            return match.group(1)

        # Fallback: convert filename slug to title case
        # e.g., "intuit.md" -> "Intuit"
        # e.g., "the-hard-life-of-securing.md" -> "The Hard Life Of Securing"
        stem = file_path.stem
        return stem.replace("-", " ").title()

    except Exception:
        # If reading fails, use filename as fallback
        return file_path.stem.replace("-", " ").title()


def scan_directory(directory: Path, exclude_names: Optional[List[str]] = None) -> List[Tuple[str, Path, float]]:
    """
    Scan directory for markdown files and extract metadata.

    Args:
        directory: Directory path to scan
        exclude_names: List of filenames to exclude (default: ["README.md"])

    Returns:
        List of tuples: (company_name, file_path, mtime)
        Sorted by mtime descending (newest first)
    """
    if exclude_names is None:
        exclude_names = ["README.md"]

    if not directory.exists():
        return []

    files = []
    for md_file in directory.glob("*.md"):
        # Skip excluded files
        if md_file.name in exclude_names:
            continue

        company = extract_company_from_markdown(md_file)
        mtime = md_file.stat().st_mtime
        files.append((company, md_file, mtime))

    # Sort by mtime descending (newest first)
    files.sort(key=lambda x: x[2], reverse=True)

    return files


def generate_index_list(files: List[Tuple[str, Path, float]], base_dir: Path) -> str:
    """
    Generate markdown list for index.

    Args:
        files: List of (company_name, file_path, mtime) tuples
        base_dir: Base directory for calculating relative paths

    Returns:
        Markdown list as string
    """
    if not files:
        return "*(No content generated yet)*\n"

    lines = []
    for company, file_path, _ in files:
        # Get relative path from base_dir (e.g., "case-studies/intuit.md")
        if file_path.is_absolute():
            rel_path = file_path.relative_to(base_dir)
        else:
            rel_path = file_path
        lines.append(f"- [{company}]({rel_path})")

    return "\n".join(lines) + "\n"


def update_readme_section(
    readme_content: str, start_marker: str, end_marker: str, new_content: str
) -> Tuple[str, bool]:
    """
    Replace content between marker comments.

    Args:
        readme_content: Full README.md content
        start_marker: Start marker comment (e.g., "<!-- GENERATED_CONTENT_START:case-studies -->")
        end_marker: End marker comment (e.g., "<!-- GENERATED_CONTENT_END:case-studies -->")
        new_content: New content to insert between markers

    Returns:
        Tuple of (updated_content, was_found)

    Raises:
        ValueError: If markers don't exist in content
    """
    # Check if both markers exist
    if start_marker not in readme_content or end_marker not in readme_content:
        raise ValueError(f"Markers not found in README.md: {start_marker} / {end_marker}")

    # Find marker positions
    start_pos = readme_content.find(start_marker)
    end_pos = readme_content.find(end_marker)

    if start_pos == -1 or end_pos == -1 or end_pos < start_pos:
        raise ValueError(f"Invalid marker positions in README.md")

    # Calculate positions for replacement
    # Keep start marker line, replace content after it until end marker
    start_line_end = readme_content.find("\n", start_pos)
    if start_line_end == -1:
        start_line_end = len(readme_content)

    # Build updated content
    updated = readme_content[: start_line_end + 1] + new_content + readme_content[end_pos:]

    return updated, True


def update_readme_index(dry_run: bool = False) -> Dict:
    """
    Update README.md with generated content index.

    Scans case-studies/ and reference-architectures/ directories,
    then updates README.md sections between marker comments.

    Args:
        dry_run: If True, don't write changes (default: False)

    Returns:
        Dict with keys:
            - case_studies_count: Number of case studies found
            - reference_architectures_count: Number of reference architectures found
            - updated: Boolean indicating if README was updated

    Raises:
        FileNotFoundError: If README.md not found
        ValueError: If marker comments don't exist in README
    """
    # Define paths
    base_dir = Path.cwd()
    readme_path = base_dir / "README.md"
    case_studies_dir = base_dir / "case-studies"
    ref_arch_dir = base_dir / "reference-architectures"

    # Check README exists
    if not readme_path.exists():
        raise FileNotFoundError(f"README.md not found at {readme_path}")

    # Scan directories
    case_studies = scan_directory(case_studies_dir)
    ref_architectures = scan_directory(ref_arch_dir)

    # Generate index content
    case_studies_list = generate_index_list(case_studies, base_dir)
    ref_arch_list = generate_index_list(ref_architectures, base_dir)

    # Read README
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()

    # Update case studies section
    updated_content, _ = update_readme_section(
        readme_content,
        "<!-- GENERATED_CONTENT_START:case-studies -->",
        "<!-- GENERATED_CONTENT_END:case-studies -->",
        case_studies_list,
    )

    # Update reference architectures section
    updated_content, _ = update_readme_section(
        updated_content,
        "<!-- GENERATED_CONTENT_START:reference-architectures -->",
        "<!-- GENERATED_CONTENT_END:reference-architectures -->",
        ref_arch_list,
    )

    # Write updated README (unless dry run)
    if not dry_run:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

    return {
        "case_studies_count": len(case_studies),
        "reference_architectures_count": len(ref_architectures),
        "updated": not dry_run,
    }
