"""GitHub issue parser for extracting content generation metadata.

This module provides functions to parse GitHub issues created via content
generation templates (case studies, reference architectures) and extract
relevant metadata including YouTube URLs, content types, and company names.
"""

import json
import logging
import re
import subprocess
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def extract_youtube_url(text: str) -> Optional[str]:
    """Extract YouTube URL from text and normalize to standard format.

    Supports both standard (youtube.com/watch?v=...) and short (youtu.be/...)
    URL formats. Always returns URLs in standard format.

    Args:
        text: Text content to search for YouTube URLs

    Returns:
        Normalized YouTube URL in standard format, or None if not found

    Example:
        >>> extract_youtube_url("Check out https://youtu.be/abc123")
        'https://www.youtube.com/watch?v=abc123'
    """
    # Pattern for standard YouTube URLs
    standard_pattern = r"https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)"
    match = re.search(standard_pattern, text)
    if match:
        return match.group(0)

    # Pattern for short YouTube URLs (youtu.be)
    short_pattern = r"https?://youtu\.be/([a-zA-Z0-9_-]+)"
    match = re.search(short_pattern, text)
    if match:
        video_id = match.group(1)
        # Convert to standard format
        return f"https://www.youtube.com/watch?v={video_id}"

    return None


def extract_company_name(text: str) -> Optional[str]:
    """Extract optional company name from issue body.

    Looks for patterns like:
    - "Company: Acme Corp"
    - "Company Name: Acme Corp"
    - "Company (Optional): Acme Corp"

    Ignores placeholder values like "n/a", "none", "unknown", or empty strings
    (case-insensitive comparison).

    Args:
        text: Issue body text to search

    Returns:
        Company name if found and valid, None otherwise
    """
    # Pattern to match company name field (case insensitive)
    # Captures content until end of line
    pattern = r"Company(?:\s+Name)?(?:\s+\(Optional\))?:\s*([^\n\r]+)"
    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return None

    company = match.group(1).strip()

    # Ignore placeholder values (case-insensitive comparison)
    placeholder_values = {"", "n/a", "none", "unknown"}
    if company.lower() in placeholder_values:
        return None

    return company


def detect_content_type(labels: list) -> str:
    """Detect content type from issue labels.

    Args:
        labels: List of label objects from GitHub API

    Returns:
        Content type string ("case-study", "reference-architecture", or "presenter-profile")

    Raises:
        ValueError: If no recognized content type label found
    """
    label_names = [label.get("name", "") for label in labels]

    if "case-study" in label_names:
        return "case-study"
    elif "reference-architecture" in label_names:
        return "reference-architecture"
    elif "presenter-profile" in label_names:
        return "presenter-profile"
    else:
        raise ValueError(
            f"Could not detect content type from labels: {label_names}. "
            "Expected 'case-study', 'reference-architecture', or 'presenter-profile' label."
        )


def parse_issue(issue_number: int) -> Dict[str, Any]:
    """Parse GitHub issue and extract content generation metadata.

    Fetches issue data using gh CLI and extracts:
    - Issue number and title
    - Content type (from labels)
    - YouTube video URL
    - Optional company name

    Args:
        issue_number: GitHub issue number to parse

    Returns:
        Dictionary containing:
        - issue_number: int
        - title: str
        - content_type: str (e.g., "case-study")
        - video_url: str
        - company_name: str or None

    Raises:
        RuntimeError: If gh CLI command fails
        ValueError: If YouTube URL not found or invalid content type

    Example:
        >>> result = parse_issue(42)
        >>> result['content_type']
        'case-study'
        >>> result['video_url']
        'https://www.youtube.com/watch?v=abc123'
    """
    logger.info(f"Parsing issue #{issue_number}")

    # Fetch issue data using gh CLI
    cmd = ["gh", "issue", "view", str(issue_number), "--json", "number,title,body,labels"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as e:
        logger.error(f"Failed to run gh CLI: {e}")
        raise RuntimeError(f"Failed to fetch issue #{issue_number}: {e}")

    if result.returncode != 0:
        logger.error(f"gh CLI returned exit code {result.returncode}: {result.stderr}")
        raise RuntimeError(f"Failed to fetch issue #{issue_number}. gh CLI error: {result.stderr}")

    # Parse JSON response
    try:
        issue_data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse gh CLI JSON output: {e}")
        # Include snippet of problematic output for debugging
        output_snippet = result.stdout[:500] if result.stdout else "(empty)"
        logger.debug(f"Problematic output: {output_snippet}")
        raise RuntimeError(f"Failed to parse issue data. Invalid JSON from gh CLI: {e}")

    # Extract fields
    issue_num = issue_data.get("number")
    title = issue_data.get("title", "")
    body = issue_data.get("body", "")
    labels = issue_data.get("labels", [])

    logger.debug(f"Issue #{issue_num}: {title}")

    # Detect content type from labels
    try:
        content_type = detect_content_type(labels)
        logger.info(f"Detected content type: {content_type}")
    except ValueError as e:
        logger.error(str(e))
        raise

    # Extract YouTube URL (required)
    video_url = extract_youtube_url(body)
    if not video_url:
        raise ValueError(
            f"No YouTube URL found in issue #{issue_number}. "
            "Please ensure the issue body contains a valid YouTube link "
            "(e.g., https://www.youtube.com/watch?v=... or https://youtu.be/...)"
        )

    logger.info(f"Extracted video URL: {video_url}")

    # Extract optional company name
    company_name = extract_company_name(body)
    if company_name:
        logger.info(f"Extracted company name: {company_name}")
    else:
        logger.debug("No company name found in issue body (will extract from video)")

    return {
        "issue_number": issue_num,
        "title": title,
        "content_type": content_type,
        "video_url": video_url,
        "company_name": company_name,
    }
