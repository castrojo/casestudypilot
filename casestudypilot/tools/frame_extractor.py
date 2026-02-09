"""Extract video frames at specific timestamps using yt-dlp and ffmpeg."""

import subprocess
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class FrameExtractionError(Exception):
    """Raised when frame extraction fails due to missing dependencies or errors."""

    pass


def check_dependencies() -> Dict[str, bool]:
    """
    Check if required tools (yt-dlp, ffmpeg) are installed.

    Returns:
        Dict with availability status for each dependency and overall status.
        Example: {"yt-dlp": True, "ffmpeg": True, "all_available": True}
    """
    dependencies = {}

    # Check yt-dlp
    try:
        result = subprocess.run(
            ["yt-dlp", "--version"], capture_output=True, timeout=5, check=False
        )
        dependencies["yt-dlp"] = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        dependencies["yt-dlp"] = False

    # Check ffmpeg
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, timeout=5, check=False
        )
        dependencies["ffmpeg"] = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        dependencies["ffmpeg"] = False

    dependencies["all_available"] = all(
        [dependencies["yt-dlp"], dependencies["ffmpeg"]]
    )

    return dependencies


def extract_frame_at_timestamp(
    video_url: str, timestamp_seconds: int, output_path: Path, quality: str = "best"
) -> Dict[str, Any]:
    """
    Extract a single frame from YouTube video at specific timestamp.

    Uses yt-dlp to stream video and ffmpeg to extract frame.
    Optimized for GitHub Actions (Ubuntu runner environment).

    Args:
        video_url: Full YouTube URL (e.g., "https://www.youtube.com/watch?v=...")
        timestamp_seconds: Exact second to extract frame from
        output_path: Path to save extracted frame (e.g., "images/intuit/challenge.jpg")
        quality: Video quality selector for yt-dlp (default: "best")

    Returns:
        Dict with extraction result:
        {
            "success": bool,
            "file_path": str,
            "file_size": int,
            "method": "frame_extraction",
            "error": str (only if failed)
        }

    Example:
        >>> result = extract_frame_at_timestamp(
        ...     "https://www.youtube.com/watch?v=V6L-xOUdoRQ",
        ...     450,
        ...     Path("case-studies/images/intuit/challenge.jpg")
        ... )
        >>> result["success"]
        True
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # yt-dlp command: stream video at specific timestamp
        # Uses ffmpeg as external downloader to seek to timestamp before downloading
        ytdlp_cmd = [
            "yt-dlp",
            "--quiet",
            "--no-warnings",
            "--external-downloader",
            "ffmpeg",
            "--external-downloader-args",
            f"ffmpeg_i:-ss {timestamp_seconds} -t 1",
            "--format",
            f"bestvideo[height<=1080]",  # Best quality, max 1080p
            "--output",
            "-",  # Output to stdout
            video_url,
        ]

        # ffmpeg command: extract single frame from piped stream
        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            "pipe:0",  # Input from stdin
            "-frames:v",
            "1",  # Extract exactly 1 frame
            "-q:v",
            "2",  # Quality (1-31, lower is better)
            "-y",  # Overwrite output file
            str(output_path),
        ]

        # Execute pipeline: yt-dlp stdout → ffmpeg stdin
        ytdlp_process = subprocess.Popen(
            ytdlp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdin=ytdlp_process.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Close yt-dlp stdout in parent process (allow it to receive SIGPIPE)
        ytdlp_process.stdout.close()

        # Wait for ffmpeg to complete
        _, ffmpeg_stderr = ffmpeg_process.communicate(timeout=60)

        # Check if extraction succeeded
        if ffmpeg_process.returncode != 0:
            error_msg = ffmpeg_stderr.decode("utf-8", errors="ignore")[:200]
            logger.warning(f"Frame extraction failed: {error_msg}")
            return {"success": False, "error": f"ffmpeg error: {error_msg}"}

        # Verify output file exists and has content
        if not output_path.exists() or output_path.stat().st_size == 0:
            return {"success": False, "error": "Output file not created or empty"}

        return {
            "success": True,
            "file_path": str(output_path),
            "file_size": output_path.stat().st_size,
            "method": "frame_extraction",
        }

    except FileNotFoundError as e:
        tool_name = "yt-dlp" if "yt-dlp" in str(e) else "ffmpeg"
        error_msg = f"{tool_name} not found. Please install it."
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except subprocess.TimeoutExpired:
        error_msg = "Frame extraction timed out after 60 seconds"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    except Exception as e:
        error_msg = str(e)[:200]
        logger.error(f"Unexpected error during frame extraction: {error_msg}")
        return {"success": False, "error": error_msg}
