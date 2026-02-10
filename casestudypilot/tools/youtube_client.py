"""YouTube client for fetching video data and transcripts."""

import re
import logging
from typing import Dict, List, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from casestudypilot.validation import validate_transcript
import yt_dlp

logger = logging.getLogger(__name__)


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    patterns = [
        r"(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be\/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from URL: {url}")


def fetch_transcript(video_id: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch transcript for a YouTube video.

    Returns None if transcript cannot be fetched, allowing the system to
    continue with fallback behavior (using strategic timestamps).
    """
    try:
        logger.info(f"Fetching transcript for video {video_id}")
        # Use the new API (youtube-transcript-api >= 1.0.0)
        api = YouTubeTranscriptApi()
        transcript_obj = api.fetch(video_id)
        # Convert to old format for compatibility
        transcript = transcript_obj.to_raw_data()
        logger.info(f"Successfully fetched {len(transcript)} transcript segments")
        return transcript
    except Exception as e:
        logger.warning(
            f"Could not fetch transcript for video {video_id}: {e}. "
            "Will use strategic timestamp selection instead."
        )
        return None


def format_duration(seconds: float) -> str:
    """Convert seconds to HH:MM:SS or MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def fetch_youtube_metadata(video_id: str, url: str) -> Dict[str, Any]:
    """Fetch real metadata from YouTube using yt-dlp.

    Args:
        video_id: YouTube video ID
        url: Full YouTube URL

    Returns:
        Metadata dict with title, description, channel, duration
    """
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return {
                "video_id": video_id,
                "url": url,
                "title": info.get("title", f"Video {video_id}"),
                "description": info.get("description", "No description available"),
                "duration_seconds": info.get("duration", 0),
                "channel_name": info.get(
                    "channel", "CNCF [Cloud Native Computing Foundation]"
                ),
            }
    except Exception as e:
        logger.warning(f"Could not fetch YouTube metadata for {video_id}: {e}")
        # Return basic metadata as fallback
        return {
            "video_id": video_id,
            "url": url,
            "title": f"Video {video_id}",
            "description": "Placeholder description",
            "duration_seconds": 0,
            "channel_name": "CNCF [Cloud Native Computing Foundation]",
        }


def fetch_video_data(url: str, duration_hint: Optional[int] = None) -> Dict[str, Any]:
    """Fetch complete video data including transcript with validation.

    Args:
        url: YouTube video URL
        duration_hint: Optional duration in seconds if known (used as fallback)

    Returns:
        Video metadata dict with transcript and validation results
    """
    video_id = extract_video_id(url)

    # Fetch real metadata from YouTube
    metadata = fetch_youtube_metadata(video_id, url)

    # Fetch transcript
    transcript_segments = fetch_transcript(video_id)

    # Calculate duration from last transcript segment, or use hint
    if transcript_segments is not None and len(transcript_segments) > 0:
        last_segment = transcript_segments[-1]
        duration = last_segment["start"] + last_segment["duration"]
        metadata["duration_seconds"] = duration
        metadata["duration_formatted"] = format_duration(duration)

        # Combine transcript text
        transcript_text = " ".join([seg["text"] for seg in transcript_segments])
        metadata["transcript"] = transcript_text
        metadata["transcript_segments"] = transcript_segments
    elif duration_hint:
        # Use fallback duration if provided
        metadata["duration_seconds"] = duration_hint
        metadata["duration_formatted"] = format_duration(duration_hint)
        metadata["transcript"] = ""
        metadata["transcript_segments"] = []
        logger.warning(f"Using fallback duration: {duration_hint}s")
    else:
        # No transcript and no duration hint
        metadata["transcript"] = ""
        metadata["transcript_segments"] = []
        logger.warning("No transcript or duration information available")

    # Validate transcript quality
    validation_result = validate_transcript(
        metadata.get("transcript", ""), metadata.get("transcript_segments", [])
    )
    metadata["validation"] = validation_result.to_dict()

    # Log validation results
    if validation_result.is_critical():
        logger.error(f"CRITICAL transcript validation failure for video {video_id}")
        for check in validation_result.get_failed_checks():
            logger.error(f"  - {check.name}: {check.message}")
    elif validation_result.has_warnings():
        logger.warning(f"Transcript validation warnings for video {video_id}")
        for check in validation_result.get_failed_checks():
            logger.warning(f"  - {check.name}: {check.message}")

    return metadata
