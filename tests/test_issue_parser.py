"""Tests for GitHub issue parser."""

import json
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from casestudypilot.tools.issue_parser import (
    parse_issue,
    extract_youtube_url,
    extract_company_name,
    detect_content_type,
)


def test_extract_youtube_url_standard_format():
    """Test extracting standard YouTube URL."""
    body = """
    Please generate a case study for this video:
    https://www.youtube.com/watch?v=dQw4w9WgXcQ
    """
    url = extract_youtube_url(body)
    assert url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_extract_youtube_url_short_format():
    """Test extracting short YouTube URL."""
    body = "Check out https://youtu.be/dQw4w9WgXcQ for more info"
    url = extract_youtube_url(body)
    assert url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # NOTE: Converts to standard format


def test_extract_youtube_url_not_found():
    """Test when no YouTube URL present."""
    body = "This is an issue without a YouTube link"
    url = extract_youtube_url(body)
    assert url is None


@patch("casestudypilot.tools.issue_parser.subprocess.run")
def test_parse_issue_case_study(mock_run):
    """Test parsing a case study issue."""
    # Mock gh CLI response
    mock_run.return_value = Mock(
        returncode=0,
        stdout=json.dumps(
            {
                "number": 42,
                "title": "Generate case study for Intuit",
                "body": "YouTube URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ\n\nCompany: Intuit",
                "labels": [{"name": "case-study"}],
            }
        ),
    )

    result = parse_issue(42)

    assert result["issue_number"] == 42
    assert result["content_type"] == "case-study"
    assert result["video_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert result["company_name"] == "Intuit"


@patch("casestudypilot.tools.issue_parser.subprocess.run")
def test_parse_issue_reference_architecture(mock_run):
    """Test parsing a reference architecture issue."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout=json.dumps(
            {
                "number": 43,
                "title": "Generate reference architecture for CERN",
                "body": "https://www.youtube.com/watch?v=xyz123abc",
                "labels": [{"name": "reference-architecture"}],
            }
        ),
    )

    result = parse_issue(43)

    assert result["issue_number"] == 43
    assert result["content_type"] == "reference-architecture"
    assert result["video_url"] == "https://www.youtube.com/watch?v=xyz123abc"


@patch("casestudypilot.tools.issue_parser.subprocess.run")
def test_parse_issue_presenter_profile(mock_run):
    """Test parsing a presenter profile issue."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout=json.dumps(
            {
                "number": 45,
                "title": "Generate presenter profile for Kelsey Hightower",
                "body": "https://www.youtube.com/watch?v=abc123xyz",
                "labels": [{"name": "presenter-profile"}],
            }
        ),
    )

    result = parse_issue(45)

    assert result["issue_number"] == 45
    assert result["content_type"] == "presenter-profile"
    assert result["video_url"] == "https://www.youtube.com/watch?v=abc123xyz"


@patch("casestudypilot.tools.issue_parser.subprocess.run")
def test_parse_issue_no_url(mock_run):
    """Test parsing issue without YouTube URL."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout=json.dumps(
            {"number": 44, "title": "Missing URL", "body": "No video link here", "labels": [{"name": "case-study"}]}
        ),
    )

    with pytest.raises(ValueError, match="No YouTube URL found"):
        parse_issue(44)


@patch("casestudypilot.tools.issue_parser.subprocess.run")
def test_parse_issue_gh_cli_error(mock_run):
    """Test handling gh CLI errors."""
    mock_run.return_value = Mock(returncode=1, stderr="Issue not found")

    with pytest.raises(RuntimeError, match="Failed to fetch issue"):
        parse_issue(999)


def test_detect_content_type_empty_labels():
    """Test detecting content type with empty labels list."""
    with pytest.raises(ValueError, match="Could not detect content type"):
        detect_content_type([])


def test_detect_content_type_multiple_content_labels():
    """Test detecting content type when multiple content type labels present."""
    # Documents current behavior: first match wins
    from casestudypilot.tools.issue_parser import detect_content_type

    labels = [{"name": "case-study"}, {"name": "reference-architecture"}]
    result = detect_content_type(labels)
    assert result == "case-study"  # First match in if/elif chain


def test_extract_youtube_url_multiple_urls():
    """Test extracting first URL when multiple present."""
    body = """
    First video: https://youtube.com/watch?v=abc123
    Second video: https://youtube.com/watch?v=xyz789
    """
    url = extract_youtube_url(body)
    assert url == "https://youtube.com/watch?v=abc123"


def test_extract_youtube_url_with_query_params():
    """Test extracting URL with additional query parameters."""
    body = "Video: https://youtube.com/watch?v=abc123&t=120s&feature=share"
    url = extract_youtube_url(body)
    # Should extract just the base URL with video ID
    assert url == "https://youtube.com/watch?v=abc123"


def test_extract_company_name_multiline():
    """Test extracting company name with multiline content after."""
    from casestudypilot.tools.issue_parser import extract_company_name

    body = """Company: Acme Corp
    
    Some other content here"""
    company = extract_company_name(body)
    assert company == "Acme Corp"


def test_extract_company_name_case_insensitive_placeholder():
    """Test that placeholders are detected case-insensitively."""
    from casestudypilot.tools.issue_parser import extract_company_name

    test_cases = ["Company: N/A", "Company: None", "Company: UNKNOWN"]
    for body in test_cases:
        company = extract_company_name(body)
        assert company is None
