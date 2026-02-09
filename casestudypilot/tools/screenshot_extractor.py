"""Extract and download screenshots from YouTube videos."""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx


# Visual indicator phrases suggesting slides/diagrams are being shown
VISUAL_INDICATORS = [
    r"as you can see",
    r"this slide shows?",
    r"here'?s? (?:a|the) (?:diagram|chart|graph|architecture)",
    r"let me show you",
    r"looking at this",
    r"on this screen",
    r"this architecture",
    r"these (?:metrics|numbers|results)",
    r"here are (?:the|our) (?:metrics|numbers|results)",
    r"this graph illustrates",
    r"if we look at",
    r"you'll see here",
]


def analyze_transcript_for_visual_moments(
    transcript_segments: List[Dict[str, Any]], analysis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Analyze transcript to find moments where visuals are likely shown.

    Args:
        transcript_segments: List of transcript segments with text, start, duration
        analysis: Analysis data (currently unused, for future enhancements)

    Returns:
        List of visual moments with timestamp, text, and score
    """
    visual_moments = []

    for segment in transcript_segments:
        text = segment.get("text", "").lower()
        timestamp = segment.get("start", 0)

        # Score this segment based on visual indicators
        score = 0
        matched_phrases = []

        for pattern in VISUAL_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                score += 1
                matched_phrases.append(pattern)

        if score > 0:
            visual_moments.append(
                {
                    "timestamp": int(timestamp),
                    "text": segment.get("text", ""),
                    "score": score,
                    "matched_phrases": matched_phrases,
                }
            )

    return visual_moments


def format_timestamp(seconds: int) -> str:
    """Convert seconds to MM:SS format."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def select_optimal_timestamps(
    visual_moments: List[Dict[str, Any]],
    video_duration: float,
    target_sections: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    Select best timestamps for screenshots.

    Args:
        visual_moments: List of detected visual moments
        video_duration: Total video duration in seconds
        target_sections: Sections to get screenshots for (default: challenge, solution)

    Returns:
        List of selected moments with section assignments
    """
    if target_sections is None:
        target_sections = ["challenge", "solution"]

    # If we have clear visual moments, use them
    if visual_moments and len(visual_moments) >= 2:
        # Sort by score (descending), then by timestamp
        sorted_moments = sorted(
            visual_moments, key=lambda m: (m["score"], -m["timestamp"]), reverse=True
        )

        # Try to distribute across video (early = challenge, later = solution)
        first_half = [m for m in sorted_moments if m["timestamp"] < video_duration / 2]
        second_half = [
            m for m in sorted_moments if m["timestamp"] >= video_duration / 2
        ]

        selected = []

        # Challenge: use best moment from first half
        if first_half:
            moment = first_half[0]
            selected.append(
                {
                    "section": "challenge",
                    "timestamp": moment["timestamp"],
                    "timestamp_formatted": format_timestamp(moment["timestamp"]),
                    "reason": f"Visual indicators detected: {', '.join(moment['matched_phrases'][:2])}",
                    "text": moment["text"][:100] + "...",
                }
            )

        # Solution: use best moment from second half
        if second_half:
            moment = second_half[0]
            selected.append(
                {
                    "section": "solution",
                    "timestamp": moment["timestamp"],
                    "timestamp_formatted": format_timestamp(moment["timestamp"]),
                    "reason": f"Visual indicators detected: {', '.join(moment['matched_phrases'][:2])}",
                    "text": moment["text"][:100] + "...",
                }
            )

        # If we got both sections, return
        if len(selected) == 2:
            return selected

    # Fallback: use strategic timestamps (25% and 60% through video)
    # These often align with problem explanation and solution demo
    fallback_timestamps = [
        {
            "section": "challenge",
            "timestamp": int(video_duration * 0.25),
            "timestamp_formatted": format_timestamp(int(video_duration * 0.25)),
            "reason": "Strategic timestamp (challenge section typically discussed early)",
            "text": "No specific visual indicators detected",
        },
        {
            "section": "solution",
            "timestamp": int(video_duration * 0.60),
            "timestamp_formatted": format_timestamp(int(video_duration * 0.60)),
            "reason": "Strategic timestamp (solution implementation typically discussed mid-talk)",
            "text": "No specific visual indicators detected",
        },
    ]

    return fallback_timestamps


def generate_screenshot_url(video_id: str, quality: str = "sddefault") -> str:
    """
    Generate YouTube thumbnail URL.

    Note: YouTube's thumbnail API provides static video thumbnails,
    not timestamp-specific frames. Available qualities:
    - maxresdefault (1920x1080) - may not exist for all videos
    - sddefault (640x480) - good balance
    - hqdefault (480x360)
    - mqdefault (320x180)

    Args:
        video_id: YouTube video ID
        quality: Thumbnail quality (default: sddefault)

    Returns:
        URL string
    """
    return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"


def download_screenshot(url: str, output_path: Path) -> Dict[str, Any]:
    """
    Download screenshot from URL to local path.

    Args:
        url: URL to download from
        output_path: Local path to save to

    Returns:
        Metadata about download (success, file_size, etc.)
    """
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        response = httpx.get(url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()

        # Write to file
        output_path.write_bytes(response.content)

        file_size = len(response.content)

        return {
            "success": True,
            "file_size": file_size,
            "path": str(output_path),
            "url": url,
        }

    except Exception as e:
        return {"success": False, "error": str(e), "path": str(output_path), "url": url}


def generate_caption(
    section: str, sections_content: Dict[str, str], timestamp_info: Dict[str, Any]
) -> str:
    """
    Generate contextual caption for screenshot.

    Args:
        section: Section name (challenge, solution, etc.)
        sections_content: Dict of section content
        timestamp_info: Info about the timestamp/moment

    Returns:
        Caption string
    """
    # Extract key phrases from section content for context
    section_text = sections_content.get(section, "")

    # Try to find a key phrase in the first 200 chars
    first_part = section_text[:200]

    # Look for bold items (likely key concepts)
    bold_matches = re.findall(r"\*\*([^*]+)\*\*", first_part)

    if section == "challenge":
        if bold_matches:
            return f"Challenges with {bold_matches[0].lower()}"
        return "Traditional deployment pipeline challenges"

    elif section == "solution":
        if bold_matches:
            key_tech = bold_matches[0]
            return f"{key_tech} implementation architecture"
        return "Cloud-native solution architecture"

    elif section == "impact":
        return "Performance improvements and results"

    else:
        return f"Key points from {section} discussion"


def extract_screenshots(
    video_data_path: Path,
    analysis_path: Path,
    sections_path: Path,
    output_path: Path,
    download_dir: Path,
) -> Dict[str, Any]:
    """
    Main function: orchestrate screenshot extraction and download.

    Args:
        video_data_path: Path to video_data.json
        analysis_path: Path to transcript_analysis.json
        sections_path: Path to case_study_sections.json
        output_path: Path to save screenshots.json
        download_dir: Directory to download images to

    Returns:
        Dict with company_slug and screenshots list
    """
    # Load input files
    with open(video_data_path, "r", encoding="utf-8") as f:
        video_data = json.load(f)

    with open(analysis_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    with open(sections_path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    # Extract video info
    video_id = video_data.get("video_id")
    video_duration = video_data.get("duration_seconds", 1800)
    transcript_segments = video_data.get("transcript_segments", [])

    if not video_id:
        raise ValueError("video_id not found in video_data")

    # Analyze transcript for visual moments
    visual_moments = analyze_transcript_for_visual_moments(
        transcript_segments, analysis
    )

    # Select optimal timestamps
    selected_moments = select_optimal_timestamps(visual_moments, video_duration)

    # Generate company slug from download_dir
    company_slug = download_dir.name

    # Create directory
    download_dir.mkdir(parents=True, exist_ok=True)

    # Process each selected moment
    screenshots = []

    for moment in selected_moments:
        section = moment["section"]

        # Generate screenshot URL
        screenshot_url = generate_screenshot_url(video_id, quality="sddefault")

        # Determine local filename
        local_filename = f"{section}.jpg"
        local_path = download_dir / local_filename

        # Download screenshot
        download_result = download_screenshot(screenshot_url, local_path)

        # Generate caption
        caption = generate_caption(section, sections, moment)

        # Build screenshot metadata
        screenshot_data = {
            "section": section,
            "timestamp": moment["timestamp"],
            "timestamp_formatted": moment["timestamp_formatted"],
            "reason": moment["reason"],
            "youtube_url": screenshot_url,
            "local_path": str(local_path),
            "caption": caption,
            "download_success": download_result["success"],
        }

        if not download_result["success"]:
            screenshot_data["download_error"] = download_result["error"]
        else:
            screenshot_data["file_size"] = download_result["file_size"]

        screenshots.append(screenshot_data)

    # Prepare output
    result = {"company_slug": company_slug, "screenshots": screenshots}

    # Write to output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result
