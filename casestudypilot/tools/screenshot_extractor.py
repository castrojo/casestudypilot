"""Extract and download screenshots from YouTube videos."""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


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

# Patterns that indicate metrics/numbers are being discussed
METRIC_INDICATORS = [
    r"\d+%\s+(?:reduction|decrease|improvement|increase|growth)",
    r"\d+x\s+(?:faster|slower|increase|improvement|more|less)",
    r"\d+[,\d]*\s+(?:pods|services|clusters|deployments|instances|nodes)",
    r"from\s+\d+(?:\.\d+)?\s*(?:hours?|minutes?|seconds?)\s+to\s+\d+",
    r"(?:reduced|improved|increased|decreased)\s+(?:by\s+)?\d+%",
    r"(?:deployment|build|response)\s+time[s]?\s*:\s*\d+",
    r"achieved\s+\d+(?:%|x)?",
    r"went\s+from\s+\d+.*to\s+\d+",
]

# Patterns specific to impact/results discussion
IMPACT_INDICATORS = [
    r"(?:the\s+)?results?",
    r"achieved",
    r"delivered",
    r"improved by",
    r"measured",
    r"metrics? show",
    r"performance gains?",
    r"success",
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


def analyze_transcript_for_metric_moments(
    transcript_segments: List[Dict[str, Any]], key_metrics: List[str]
) -> List[Dict[str, Any]]:
    """
    Analyze transcript to find moments where key metrics are mentioned.

    Args:
        transcript_segments: List of transcript segments with text, start, duration
        key_metrics: List of key metrics from analysis (e.g., ["50% reduction", "10,000 pods"])

    Returns:
        List of metric moments with timestamp, text, score, and matched metric
    """
    from rapidfuzz import fuzz

    metric_moments = []

    for segment in transcript_segments:
        text = segment.get("text", "")
        text_lower = text.lower()
        timestamp = segment.get("start", 0)

        score = 0
        matched_metric = None
        matched_patterns = []

        # Check for exact or fuzzy key metric matches
        for metric in key_metrics:
            metric_lower = metric.lower()
            # Fuzzy match with 80% threshold
            if fuzz.partial_ratio(metric_lower, text_lower) >= 80:
                # Exact match bonus
                if metric_lower in text_lower:
                    score += 5
                    matched_metric = metric
                else:
                    score += 3
                    matched_metric = metric
                break

        # Check for metric indicator patterns
        for pattern in METRIC_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                score += 1
                matched_patterns.append(pattern)

        # Check for impact indicator patterns
        for pattern in IMPACT_INDICATORS:
            if re.search(pattern, text, re.IGNORECASE):
                score += 1
                matched_patterns.append(pattern)

        # Only include if score is significant (threshold: 2)
        if score >= 2:
            metric_moments.append(
                {
                    "timestamp": int(timestamp),
                    "text": text,
                    "score": score,
                    "matched_metric": matched_metric,
                    "matched_patterns": matched_patterns,
                }
            )

    return metric_moments


def format_timestamp(seconds: int) -> str:
    """Convert seconds to MM:SS format."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def select_optimal_timestamps(
    visual_moments: List[Dict[str, Any]],
    video_duration: float,
    target_sections: Optional[List[str]] = None,
    metric_moments: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Select best timestamps for screenshots with metric prioritization.

    Args:
        visual_moments: List of detected visual moments
        video_duration: Total video duration in seconds
        target_sections: Sections to get screenshots for (default: challenge, solution, impact)
        metric_moments: List of detected metric moments (optional)

    Returns:
        List of selected moments with section assignments
    """
    if target_sections is None:
        target_sections = ["challenge", "solution", "impact"]

    if metric_moments is None:
        metric_moments = []

    # Define video regions for each section
    regions = {
        "challenge": (0, video_duration * 0.40),
        "solution": (video_duration * 0.40, video_duration * 0.70),
        "impact": (video_duration * 0.70, video_duration * 1.0),
    }

    # Combine all moments for processing
    all_moments = []
    for moment in visual_moments:
        all_moments.append({**moment, "type": "visual"})
    for moment in metric_moments:
        all_moments.append({**moment, "type": "metric"})

    selected = []

    for section in target_sections:
        start_time, end_time = regions.get(section, (0, video_duration))

        # Filter moments in this region
        region_moments = [
            m for m in all_moments if start_time <= m["timestamp"] < end_time
        ]

        if not region_moments:
            # Fallback to strategic timestamp
            strategic_pct = {"challenge": 0.25, "solution": 0.60, "impact": 0.85}.get(
                section, 0.50
            )
            timestamp = int(video_duration * strategic_pct)
            selected.append(
                {
                    "section": section,
                    "timestamp": timestamp,
                    "timestamp_formatted": format_timestamp(timestamp),
                    "reason": f"Strategic timestamp ({section} section typically discussed at {int(strategic_pct * 100)}%)",
                    "text": "No specific visual or metric indicators detected",
                }
            )
            continue

        # Priority: Metric moments for impact section, visual moments for others
        if section == "impact":
            # Prefer metric moments for impact section
            metric_in_region = [m for m in region_moments if m.get("type") == "metric"]
            if metric_in_region:
                best_moment = max(metric_in_region, key=lambda m: m["score"])
            else:
                best_moment = max(region_moments, key=lambda m: m["score"])
        else:
            # Prefer visual moments for challenge/solution, but accept metrics
            visual_in_region = [m for m in region_moments if m.get("type") == "visual"]
            if visual_in_region:
                best_moment = max(visual_in_region, key=lambda m: m["score"])
            else:
                best_moment = max(region_moments, key=lambda m: m["score"])

        # Build reason string
        if best_moment.get("type") == "metric":
            matched_metric = best_moment.get("matched_metric", "")
            reason = (
                f"Metric mentioned: '{matched_metric}'"
                if matched_metric
                else "Metric indicators detected"
            )
        else:
            matched_phrases = best_moment.get("matched_phrases", [])
            reason = (
                f"Visual indicators detected: {', '.join(matched_phrases[:2])}"
                if matched_phrases
                else "Visual content detected"
            )

        selected.append(
            {
                "section": section,
                "timestamp": best_moment["timestamp"],
                "timestamp_formatted": format_timestamp(best_moment["timestamp"]),
                "reason": reason,
                "text": best_moment.get("text", "")[:100] + "...",
                "matched_metric": best_moment.get("matched_metric"),
            }
        )

    return selected


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
    Generate contextual caption for screenshot, prioritizing matched metrics.

    Args:
        section: Section name (challenge, solution, impact)
        sections_content: Dict of section content
        timestamp_info: Info about the timestamp/moment (may include matched_metric)

    Returns:
        Caption string
    """
    # Check if we matched a specific metric
    matched_metric = timestamp_info.get("matched_metric")

    if matched_metric:
        # Use the specific metric in caption
        if section == "impact":
            return f"Results: {matched_metric}"
        elif section == "challenge":
            # Extract problem statement from metric
            if "hour" in matched_metric.lower() or "time" in matched_metric.lower():
                return f"Challenge: {matched_metric}"
            return f"Before: {matched_metric}"
        else:
            return f"{matched_metric} - Implementation"

    # Fallback to section-based captions
    section_text = sections_content.get(section, "")

    # Try to find a key phrase in the first 300 chars
    first_part = section_text[:300]

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
        # Look for metrics in bold text
        metric_bold = [b for b in bold_matches if any(c.isdigit() for c in b)]
        if metric_bold:
            return f"Results: {metric_bold[0]}"
        return "Performance improvements and key results"

    else:
        return f"Key points from {section} discussion"


def extract_frame_with_fallback(
    video_url: str, video_id: str, timestamp: int, output_path: Path
) -> Dict[str, Any]:
    """
    Attempt frame extraction, fallback to thumbnail API if it fails.

    Args:
        video_url: Full YouTube URL
        video_id: YouTube video ID
        timestamp: Timestamp in seconds
        output_path: Where to save the image

    Returns:
        Dict with success status, method used, and file info
    """
    from .frame_extractor import extract_frame_at_timestamp, check_dependencies

    # Check if dependencies are available
    deps = check_dependencies()

    if deps["all_available"]:
        # Try frame extraction
        logger.info(
            f"Attempting frame extraction at {timestamp}s for {output_path.name}"
        )
        result = extract_frame_at_timestamp(video_url, timestamp, output_path)

        if result["success"]:
            logger.info(f"Successfully extracted frame: {output_path.name}")
            result["method"] = "frame_extraction"
            return result

        # Log warning but continue to fallback
        logger.warning(
            f"Frame extraction failed: {result.get('error')}, falling back to thumbnail"
        )
    else:
        logger.warning(
            f"Dependencies not available (yt-dlp: {deps['yt-dlp']}, ffmpeg: {deps['ffmpeg']}), using thumbnail fallback"
        )

    # Fallback to thumbnail API
    thumbnail_url = generate_screenshot_url(video_id)
    download_result = download_screenshot(thumbnail_url, output_path)

    if download_result["success"]:
        download_result["method"] = "thumbnail_fallback"
        download_result["fallback_reason"] = (
            "dependencies_unavailable"
            if not deps["all_available"]
            else "frame_extraction_failed"
        )
        logger.info(f"Using thumbnail fallback for {output_path.name}")
    else:
        download_result["method"] = "failed"
        logger.error(
            f"Both frame extraction and thumbnail download failed for {output_path.name}"
        )

    return download_result


def extract_screenshots(
    video_data_path: Path,
    analysis_path: Path,
    sections_path: Path,
    output_path: Path,
    download_dir: Path,
) -> Dict[str, Any]:
    """
    Main function: orchestrate screenshot extraction with frame extraction support.

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
    video_url = video_data.get("url")
    video_duration = video_data.get("duration_seconds", 1800)
    transcript_segments = video_data.get("transcript_segments", [])

    if not video_id:
        raise ValueError("video_id not found in video_data")

    if not video_url:
        raise ValueError("url not found in video_data")

    # Extract key metrics from analysis
    key_metrics = analysis.get("key_metrics", [])
    logger.info(f"Found {len(key_metrics)} key metrics in analysis")

    # Analyze transcript for visual AND metric moments
    visual_moments = analyze_transcript_for_visual_moments(
        transcript_segments, analysis
    )
    logger.info(f"Found {len(visual_moments)} visual moments")

    metric_moments = analyze_transcript_for_metric_moments(
        transcript_segments, key_metrics
    )
    logger.info(f"Found {len(metric_moments)} metric moments")

    # Select optimal timestamps for 3 screenshots (challenge, solution, impact)
    selected_moments = select_optimal_timestamps(
        visual_moments,
        video_duration,
        target_sections=["challenge", "solution", "impact"],
        metric_moments=metric_moments,
    )
    logger.info(
        f"Selected {len(selected_moments)} timestamps: {[m['section'] for m in selected_moments]}"
    )

    # Generate company slug from download_dir
    company_slug = download_dir.name

    # Create directory
    download_dir.mkdir(parents=True, exist_ok=True)

    # Process each selected moment
    screenshots = []

    for moment in selected_moments:
        section = moment["section"]
        logger.info(f"Processing {section} screenshot at {moment['timestamp']}s")

        # Determine local filename
        local_filename = f"{section}.jpg"
        local_path = download_dir / local_filename

        # Extract frame with fallback to thumbnail
        extraction_result = extract_frame_with_fallback(
            video_url=video_url,
            video_id=video_id,
            timestamp=moment["timestamp"],
            output_path=local_path,
        )

        # Generate caption
        caption = generate_caption(section, sections, moment)

        # Build screenshot metadata
        screenshot_data = {
            "section": section,
            "timestamp": moment["timestamp"],
            "timestamp_formatted": moment["timestamp_formatted"],
            "reason": moment["reason"],
            "local_path": str(local_path),
            "caption": caption,
            "extraction_method": extraction_result.get("method", "unknown"),
            "download_success": extraction_result["success"],
        }

        # Add matched metric if available
        if moment.get("matched_metric"):
            screenshot_data["matched_metric"] = moment["matched_metric"]

        if not extraction_result["success"]:
            screenshot_data["download_error"] = extraction_result.get(
                "error", "Unknown error"
            )
        else:
            screenshot_data["file_size"] = extraction_result.get("file_size", 0)

        # Add fallback reason if applicable
        if "fallback_reason" in extraction_result:
            screenshot_data["fallback_reason"] = extraction_result["fallback_reason"]

        screenshots.append(screenshot_data)

    # Prepare output
    result = {"company_slug": company_slug, "screenshots": screenshots}

    # Write to output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    logger.info(f"Screenshot extraction complete. Saved metadata to {output_path}")

    return result
