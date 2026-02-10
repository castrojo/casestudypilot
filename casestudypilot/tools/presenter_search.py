"""CNCF YouTube presenter search with hybrid name matching."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import yt_dlp
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    """Normalize presenter name for matching."""
    return name.lower().strip()


def strict_match(presenter_name: str, text: str) -> bool:
    """Check if presenter name appears exactly in text (case-insensitive)."""
    return normalize_name(presenter_name) in normalize_name(text)


def fuzzy_match_name(presenter_name: str, text: str, threshold: float = 0.85) -> Tuple[bool, float]:
    """
    Fuzzy match presenter name in text.

    Returns:
        (match_found: bool, confidence_score: float)
    """
    normalized_presenter = normalize_name(presenter_name)
    normalized_text = normalize_name(text)

    # Check if name appears as-is
    if normalized_presenter in normalized_text:
        return (True, 1.0)

    # Split text into phrases (2-4 words)
    words = normalized_text.split()
    for i in range(len(words) - 1):
        for length in [2, 3, 4]:  # 2-4 word phrases
            if i + length <= len(words):
                phrase = " ".join(words[i : i + length])
                score = fuzz.ratio(normalized_presenter, phrase) / 100.0
                if score >= threshold:
                    return (True, score)

    return (False, 0.0)


def search_presenter_videos(
    presenter_name: str,
    github_username: Optional[str] = None,
    months: int = 24,
    channel_id: str = "UCvqbFHwN-nwalWPjPUKpvTA",  # CNCF
) -> Dict[str, Any]:
    """
    Search CNCF YouTube channel for presenter's videos.

    Args:
        presenter_name: Full name to search for
        github_username: Optional GitHub username for cross-reference
        months: Search past N months (default: 24)
        channel_id: YouTube channel ID (default: CNCF)

    Returns:
        {
            "presenter_name": str,
            "videos_found": int,
            "videos": [
                {
                    "video_id": str,
                    "url": str,
                    "title": str,
                    "description": str,
                    "upload_date": str,
                    "match_confidence": float,  # 0.0-1.0
                    "match_method": "strict|fuzzy",
                    "match_location": "title|description|both"
                }
            ],
            "search_metadata": {
                "months_searched": int,
                "strict_matches": int,
                "fuzzy_matches": int,
                "github_username": str | None
            }
        }
    """
    logger.info(f"Searching CNCF channel for '{presenter_name}' (past {months} months)")

    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=months * 30)

    # Search configuration
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": True,
        "playlistend": 500,  # Fetch up to 500 recent videos
    }

    matching_videos = []
    strict_count = 0
    fuzzy_count = 0

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Fetch channel uploads playlist
            channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"
            logger.info(f"Fetching videos from: {channel_url}")

            playlist_info = ydl.extract_info(channel_url, download=False)

            if not playlist_info or "entries" not in playlist_info:
                logger.warning("No videos found in channel")
                return {
                    "presenter_name": presenter_name,
                    "videos_found": 0,
                    "videos": [],
                    "search_metadata": {
                        "months_searched": months,
                        "strict_matches": 0,
                        "fuzzy_matches": 0,
                        "github_username": github_username,
                    },
                }

            for entry in playlist_info["entries"]:
                if not entry:
                    continue

                # Check upload date
                upload_date_str = entry.get("upload_date", "")
                if upload_date_str:
                    try:
                        upload_date = datetime.strptime(upload_date_str, "%Y%m%d")
                        if upload_date < cutoff_date:
                            continue  # Skip videos older than cutoff
                    except ValueError:
                        logger.warning(f"Invalid upload date: {upload_date_str}")

                video_id = entry.get("id")
                title = entry.get("title", "")
                description = entry.get("description", "")

                # Hybrid matching strategy
                match_found = False
                confidence = 0.0
                match_method = None
                match_location = None

                # Strategy 1: Strict match (highest confidence)
                if strict_match(presenter_name, title):
                    match_found = True
                    confidence = 1.0
                    match_method = "strict"
                    match_location = "title"
                    strict_count += 1
                elif strict_match(presenter_name, description):
                    match_found = True
                    confidence = 0.95  # Slightly lower than title match
                    match_method = "strict"
                    match_location = "description"
                    strict_count += 1

                # Strategy 2: Fuzzy match (medium confidence)
                if not match_found:
                    title_match, title_score = fuzzy_match_name(presenter_name, title)
                    desc_match, desc_score = fuzzy_match_name(presenter_name, description)

                    if title_match and title_score >= 0.85:
                        match_found = True
                        confidence = title_score
                        match_method = "fuzzy"
                        match_location = "title"
                        fuzzy_count += 1
                    elif desc_match and desc_score >= 0.85:
                        match_found = True
                        confidence = desc_score * 0.9  # Penalize description matches slightly
                        match_method = "fuzzy"
                        match_location = "description"
                        fuzzy_count += 1

                if match_found:
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    matching_videos.append(
                        {
                            "video_id": video_id,
                            "url": video_url,
                            "title": title,
                            "description": description[:500],  # Truncate long descriptions
                            "upload_date": upload_date_str,
                            "match_confidence": confidence,
                            "match_method": match_method,
                            "match_location": match_location,
                        }
                    )
                    logger.info(f"Found match: {title} (confidence: {confidence:.2f})")

        # Sort by confidence (highest first), then by date (newest first)
        matching_videos.sort(key=lambda v: (-v["match_confidence"], v["upload_date"]), reverse=False)

        logger.info(f"Search complete: {len(matching_videos)} videos found")
        logger.info(f"  Strict matches: {strict_count}, Fuzzy matches: {fuzzy_count}")

        return {
            "presenter_name": presenter_name,
            "videos_found": len(matching_videos),
            "videos": matching_videos,
            "search_metadata": {
                "months_searched": months,
                "strict_matches": strict_count,
                "fuzzy_matches": fuzzy_count,
                "github_username": github_username,
            },
        }

    except Exception as e:
        logger.error(f"Error searching for presenter videos: {e}")
        return {
            "presenter_name": presenter_name,
            "videos_found": 0,
            "videos": [],
            "search_metadata": {
                "months_searched": months,
                "strict_matches": 0,
                "fuzzy_matches": 0,
                "github_username": github_username,
                "error": str(e),
            },
        }
