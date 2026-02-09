"""Tests for screenshot extraction functionality."""

import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import pytest

from casestudypilot.tools.screenshot_extractor import (
    analyze_transcript_for_visual_moments,
    analyze_transcript_for_metric_moments,
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


def test_analyze_transcript_for_metric_moments():
    """Test metric detection in transcript."""
    transcript_segments = [
        {"start": 100, "text": "We reduced deployment time by 50 percent"},
        {"start": 200, "text": "This is just talking about general stuff"},
        {"start": 300, "text": "We manage 10,000 pods across our clusters"},
        {"start": 400, "text": "This achieved a 3x improvement in speed"},
    ]

    key_metrics = [
        "50% reduction in deployment time",
        "10,000 pods managed",
        "3x increase in deployment frequency",
    ]

    moments = analyze_transcript_for_metric_moments(transcript_segments, key_metrics)

    # Should detect 3 metric moments
    assert len(moments) == 3

    # Check timestamps
    assert moments[0]["timestamp"] == 100
    assert moments[1]["timestamp"] == 300
    assert moments[2]["timestamp"] == 400

    # Check that metrics were detected
    assert any(
        "50" in str(m.get("matched_metric", "")) or "50" in m["text"] for m in moments
    )
    assert any(
        "10,000" in str(m.get("matched_metric", ""))
        or "10000" in m["text"]
        or "10,000" in m["text"]
        for m in moments
    )
    assert any(
        "3x" in str(m.get("matched_metric", "")) or "3x" in m["text"] for m in moments
    )


def test_analyze_transcript_no_metric_moments():
    """Test when no metrics are detected."""
    transcript_segments = [
        {"start": 100, "text": "We had some problems"},
        {"start": 200, "text": "Things were not working well"},
    ]

    key_metrics = ["50% reduction", "10,000 pods"]
    moments = analyze_transcript_for_metric_moments(transcript_segments, key_metrics)

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

    # Should select 3 moments (default: challenge, solution, impact)
    assert len(selected) == 3

    # Should have challenge, solution, and impact
    sections = [s["section"] for s in selected]
    assert "challenge" in sections
    assert "solution" in sections
    assert "impact" in sections


def test_select_optimal_timestamps_with_metrics():
    """Test timestamp selection prioritizes metrics for impact section."""
    visual_moments = [
        {
            "timestamp": 200,
            "score": 2,
            "matched_phrases": ["as you can see"],
            "text": "Visual content here",
        }
    ]

    metric_moments = [
        {
            "timestamp": 900,
            "score": 5,
            "matched_metric": "50% reduction in deployment time",
            "matched_patterns": [],
            "text": "We achieved a 50% reduction in deployment time...",
        }
    ]

    selected = select_optimal_timestamps(
        visual_moments,
        video_duration=1000,
        target_sections=["challenge", "solution", "impact"],
        metric_moments=metric_moments,
    )

    # Should select 3 moments
    assert len(selected) == 3

    # Impact section should use the metric moment
    impact_moment = [m for m in selected if m["section"] == "impact"][0]
    assert impact_moment["timestamp"] == 900
    assert (
        "metric" in impact_moment["reason"].lower() or "50%" in impact_moment["reason"]
    )


def test_select_optimal_timestamps_fallback():
    """Test fallback when no visual moments exist."""
    visual_moments = []

    selected = select_optimal_timestamps(visual_moments, video_duration=1000)

    # Should still return 3 timestamps (strategic: 25%, 60%, 85%)
    assert len(selected) == 3
    assert selected[0]["timestamp"] == 250  # 25% of 1000
    assert selected[1]["timestamp"] == 600  # 60% of 1000
    assert selected[2]["timestamp"] == 850  # 85% of 1000

    # Should have fallback reasons
    assert "Strategic timestamp" in selected[0]["reason"]
    assert "Strategic timestamp" in selected[1]["reason"]
    assert "Strategic timestamp" in selected[2]["reason"]


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


def test_generate_caption_with_matched_metric():
    """Test caption generation when metric is matched."""
    sections = {"impact": "The transformation delivered significant improvements."}
    timestamp_info = {
        "timestamp": 1200,
        "reason": "Metric mentioned",
        "matched_metric": "50% reduction in deployment time",
    }

    caption = generate_caption("impact", sections, timestamp_info)

    # Should use the matched metric in caption
    assert "50%" in caption or "reduction" in caption.lower()


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

    assert "50% reduction" in caption or "result" in caption.lower()
