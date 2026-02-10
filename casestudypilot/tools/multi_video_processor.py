"""Multi-video processor for batch fetching YouTube data."""

import logging
from typing import List, Dict, Any
from casestudypilot.tools.youtube_client import fetch_video_data, extract_video_id

logger = logging.getLogger(__name__)


def fetch_multi_video_data(urls: List[str]) -> Dict[str, Any]:
    """Fetch data for multiple YouTube videos.

    Processes videos sequentially to avoid rate limits. Continues on individual
    failures and collects all results.

    Args:
        urls: List of YouTube video URLs

    Returns:
        Dict with:
            - videos: List of video data dicts (with 'success' flag)
            - stats: Summary statistics (total, succeeded, failed)
    """
    logger.info(f"Processing {len(urls)} videos")

    videos = []
    succeeded = 0
    failed = 0

    for i, url in enumerate(urls, 1):
        try:
            logger.info(f"Processing video {i}/{len(urls)}: {url}")
            video_data = fetch_video_data(url)

            # Check if validation shows critical failure
            validation = video_data.get("validation", {})
            is_critical = validation.get("severity") == "CRITICAL"

            if is_critical:
                logger.warning(f"Video {i} has critical validation failure but continuing")
                video_data["success"] = False
                video_data["error"] = "Critical validation failure"
                failed += 1
            else:
                video_data["success"] = True
                succeeded += 1
                logger.info(f"Successfully processed video {i}")

            videos.append(video_data)

        except Exception as e:
            logger.error(f"Failed to process video {i} ({url}): {e}")
            # Add failure record
            try:
                video_id = extract_video_id(url)
            except:
                video_id = url

            videos.append(
                {
                    "video_id": video_id,
                    "url": url,
                    "success": False,
                    "error": str(e),
                    "title": f"Video {video_id}",
                    "description": "",
                    "duration_seconds": 0,
                    "transcript": "",
                    "transcript_segments": [],
                }
            )
            failed += 1

    result = {
        "videos": videos,
        "stats": {
            "total": len(urls),
            "succeeded": succeeded,
            "failed": failed,
            "success_rate": succeeded / len(urls) if urls else 0.0,
        },
    }

    logger.info(f"Batch processing complete: {succeeded}/{len(urls)} succeeded")

    return result


def get_successful_videos(multi_video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter and return only successfully fetched videos.

    Args:
        multi_video_data: Output from fetch_multi_video_data

    Returns:
        List of video data dicts that succeeded
    """
    videos = multi_video_data.get("videos", [])
    return [v for v in videos if v.get("success", False)]


def get_failed_videos(multi_video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter and return only failed videos.

    Args:
        multi_video_data: Output from fetch_multi_video_data

    Returns:
        List of video data dicts that failed
    """
    videos = multi_video_data.get("videos", [])
    return [v for v in videos if not v.get("success", False)]


def get_all_transcripts(multi_video_data: Dict[str, Any]) -> str:
    """Combine all successful transcripts into single text.

    Args:
        multi_video_data: Output from fetch_multi_video_data

    Returns:
        Combined transcript text
    """
    successful = get_successful_videos(multi_video_data)
    transcripts = [v.get("transcript", "") for v in successful]
    return "\n\n".join(t for t in transcripts if t)


def calculate_total_duration(multi_video_data: Dict[str, Any]) -> int:
    """Calculate total duration of all successful videos.

    Args:
        multi_video_data: Output from fetch_multi_video_data

    Returns:
        Total duration in seconds
    """
    successful = get_successful_videos(multi_video_data)
    return sum(v.get("duration_seconds", 0) for v in successful)
