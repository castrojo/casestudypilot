"""Tests for screenshot extraction functionality."""

import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

from casestudypilot.tools.screenshot_extractor import (
    analyze_transcript_for_visual_moments,
    select_optimal_timestamps,
    generate_screenshot_url,
    download_screenshot,
    generate_caption,
    format_timestamp,
)


def test_format_timestamp():
    """Test timestamp formatting."""
    assert format_timestamp(65) == "1:05"
    assert format_timestamp(325) == "5:25"
    assert format_timestamp(892) == "14:52"
    assert format_timestamp(3600) == "60:00"


def test_analyze_transcript_for_visual_moments():
    """Test detection of visual indicator phrases."""
    transcript_segments = [
        {"start": 100, "text": "As you can see here, our deployment times were slow"},
        {"start": 200, "text": "This is just regular talking"},
        {"start": 300, "text": "Let me show you this diagram of our architecture"},
        {"start": 400, "text": "Here are the results we achieved"},
    ]

    analysis = {}
    moments = analyze_transcript_for_visual_moments(transcript_segments, analysis)

    # Should detect 3 visual moments
    assert len(moments) == 3

    # First moment at timestamp 100
    assert moments[0]["timestamp"] == 100
    assert moments[0]["score"] >= 1

    # Third moment at timestamp 300 should have score (may match 1 or 2 patterns depending on regex)
    moment_300 = [m for m in moments if m["timestamp"] == 300][0]
    assert moment_300["score"] >= 1


def test_analyze_transcript_no_visual_moments():
    """Test when no visual indicators are present."""
    transcript_segments = [
        {"start": 100, "text": "We had problems with our system"},
        {"start": 200, "text": "It was very slow and unreliable"},
    ]

    analysis = {}
    moments = analyze_transcript_for_visual_moments(transcript_segments, analysis)

    assert len(moments) == 0


def test_select_optimal_timestamps_with_moments():
    """Test timestamp selection when visual moments exist."""
    visual_moments = [
        {
            "timestamp": 200,
            "score": 2,
            "matched_phrases": ["as you can see", "this diagram"],
            "text": "As you can see in this diagram...",
        },
        {
            "timestamp": 800,
            "score": 3,
            "matched_phrases": ["let me show", "these results", "this graph"],
            "text": "Let me show you these results...",
        },
        {
            "timestamp": 400,
            "score": 1,
            "matched_phrases": ["looking at"],
            "text": "Looking at our performance...",
        },
    ]

    selected = select_optimal_timestamps(visual_moments, video_duration=1000)

    # Should select 2 moments
    assert len(selected) == 2

    # Should have challenge and solution
    sections = [s["section"] for s in selected]
    assert "challenge" in sections
    assert "solution" in sections

    # Challenge should be from first half (timestamp < 500)
    challenge = [s for s in selected if s["section"] == "challenge"][0]
    assert challenge["timestamp"] < 500

    # Solution should be from second half (timestamp >= 500)
    solution = [s for s in selected if s["section"] == "solution"][0]
    assert solution["timestamp"] >= 500


def test_select_optimal_timestamps_fallback():
    """Test fallback when no visual moments exist."""
    visual_moments = []

    selected = select_optimal_timestamps(visual_moments, video_duration=1000)

    # Should still return 2 timestamps (25% and 60%)
    assert len(selected) == 2
    assert selected[0]["timestamp"] == 250  # 25% of 1000
    assert selected[1]["timestamp"] == 600  # 60% of 1000

    # Should have fallback reasons
    assert "Strategic timestamp" in selected[0]["reason"]
    assert "Strategic timestamp" in selected[1]["reason"]


def test_generate_screenshot_url():
    """Test YouTube thumbnail URL generation."""
    video_id = "V6L-xOUdoRQ"

    # Default quality (sddefault)
    url = generate_screenshot_url(video_id)
    assert url == "https://img.youtube.com/vi/V6L-xOUdoRQ/sddefault.jpg"

    # Maxres quality
    url = generate_screenshot_url(video_id, quality="maxresdefault")
    assert url == "https://img.youtube.com/vi/V6L-xOUdoRQ/maxresdefault.jpg"

    # HQ quality
    url = generate_screenshot_url(video_id, quality="hqdefault")
    assert url == "https://img.youtube.com/vi/V6L-xOUdoRQ/hqdefault.jpg"


@patch("casestudypilot.tools.screenshot_extractor.httpx.get")
def test_download_screenshot_success(mock_get):
    """Test successful screenshot download."""
    # Mock HTTP response
    mock_response = Mock()
    mock_response.content = b"fake image data"
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    # Create temp path
    output_path = Path("/tmp/test_screenshot.jpg")

    # Mock file writing
    with patch.object(Path, "write_bytes") as mock_write:
        with patch.object(Path, "parent", new_callable=lambda: Mock(mkdir=Mock())):
            result = download_screenshot("https://example.com/image.jpg", output_path)

    assert result["success"] is True
    assert result["file_size"] == 15
    assert result["url"] == "https://example.com/image.jpg"


@patch("casestudypilot.tools.screenshot_extractor.httpx.get")
def test_download_screenshot_failure(mock_get):
    """Test screenshot download failure."""
    # Mock HTTP error
    mock_get.side_effect = Exception("Network error")

    output_path = Path("/tmp/test_screenshot.jpg")

    with patch.object(Path, "parent", new_callable=lambda: Mock(mkdir=Mock())):
        result = download_screenshot("https://example.com/image.jpg", output_path)

    assert result["success"] is False
    assert "error" in result
    assert "Network error" in result["error"]


def test_generate_caption_challenge():
    """Test caption generation for challenge section."""
    sections = {
        "challenge": "Before adopting cloud-native technologies, Intuit struggled with **slow manual deployments**."
    }
    timestamp_info = {"timestamp": 325, "reason": "Visual indicators detected"}

    caption = generate_caption("challenge", sections, timestamp_info)

    # Should extract key phrase from bold text
    assert "slow manual deployments" in caption.lower()


def test_generate_caption_solution():
    """Test caption generation for solution section."""
    sections = {
        "solution": "Intuit adopted **Kubernetes** as its standard container orchestration platform."
    }
    timestamp_info = {"timestamp": 892, "reason": "Architecture diagram"}

    caption = generate_caption("solution", sections, timestamp_info)

    # Should mention Kubernetes
    assert "Kubernetes" in caption


def test_generate_caption_fallback():
    """Test caption generation with no bold text."""
    sections = {"challenge": "Some regular text without any emphasis"}
    timestamp_info = {"timestamp": 100, "reason": "Test"}

    caption = generate_caption("challenge", sections, timestamp_info)

    # Should use fallback caption
    assert "deployment pipeline" in caption.lower() or "challenge" in caption.lower()


def test_generate_caption_impact():
    """Test caption generation for impact section."""
    sections = {
        "impact": "The transformation delivered **50% reduction** in deployment time."
    }
    timestamp_info = {"timestamp": 1200, "reason": "Metrics shown"}

    caption = generate_caption("impact", sections, timestamp_info)

    assert "improvement" in caption.lower() or "result" in caption.lower()
