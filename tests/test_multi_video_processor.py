"""Tests for multi-video processor functionality."""

import pytest
from unittest.mock import Mock, patch

from casestudypilot.tools.multi_video_processor import (
    fetch_multi_video_data,
    get_successful_videos,
    get_failed_videos,
    get_all_transcripts,
    calculate_total_duration,
)


class TestFetchMultiVideoData:
    """Tests for fetch_multi_video_data function."""

    @patch("casestudypilot.tools.multi_video_processor.fetch_video_data")
    def test_all_videos_succeed(self, mock_fetch):
        """Test successful fetch of all videos."""
        # Mock video data
        video_data_1 = {
            "video_id": "abc123",
            "url": "https://youtube.com/watch?v=abc123",
            "title": "Video 1",
            "transcript": "Transcript 1",
            "duration_seconds": 600,
            "validation": {"severity": "PASS"},
        }
        video_data_2 = {
            "video_id": "def456",
            "url": "https://youtube.com/watch?v=def456",
            "title": "Video 2",
            "transcript": "Transcript 2",
            "duration_seconds": 900,
            "validation": {"severity": "PASS"},
        }

        mock_fetch.side_effect = [video_data_1, video_data_2]

        urls = [
            "https://youtube.com/watch?v=abc123",
            "https://youtube.com/watch?v=def456",
        ]

        result = fetch_multi_video_data(urls)

        # Verify structure
        assert "videos" in result
        assert "stats" in result
        assert len(result["videos"]) == 2

        # Verify stats
        assert result["stats"]["total"] == 2
        assert result["stats"]["succeeded"] == 2
        assert result["stats"]["failed"] == 0
        assert result["stats"]["success_rate"] == 1.0

        # Verify videos marked as successful
        assert result["videos"][0]["success"] is True
        assert result["videos"][1]["success"] is True

    @patch("casestudypilot.tools.multi_video_processor.fetch_video_data")
    def test_some_videos_fail(self, mock_fetch):
        """Test partial success when some videos fail."""
        # First video succeeds
        video_data_1 = {
            "video_id": "abc123",
            "url": "https://youtube.com/watch?v=abc123",
            "title": "Video 1",
            "transcript": "Transcript 1",
            "duration_seconds": 600,
            "validation": {"severity": "PASS"},
        }

        # Second video fails with exception
        # Third video has critical validation failure
        video_data_3 = {
            "video_id": "ghi789",
            "url": "https://youtube.com/watch?v=ghi789",
            "title": "Video 3",
            "transcript": "",
            "duration_seconds": 0,
            "validation": {"severity": "CRITICAL"},
        }

        mock_fetch.side_effect = [
            video_data_1,
            Exception("Network error"),
            video_data_3,
        ]

        urls = [
            "https://youtube.com/watch?v=abc123",
            "https://youtube.com/watch?v=def456",
            "https://youtube.com/watch?v=ghi789",
        ]

        result = fetch_multi_video_data(urls)

        # Verify stats
        assert result["stats"]["total"] == 3
        assert result["stats"]["succeeded"] == 1
        assert result["stats"]["failed"] == 2
        assert result["stats"]["success_rate"] == pytest.approx(0.333, rel=0.01)

        # Verify success/failure flags
        assert result["videos"][0]["success"] is True
        assert result["videos"][1]["success"] is False
        assert result["videos"][2]["success"] is False

        # Verify error handling
        assert result["videos"][1]["error"] == "Network error"
        assert result["videos"][2]["error"] == "Critical validation failure"

    @patch("casestudypilot.tools.multi_video_processor.fetch_video_data")
    def test_all_videos_fail(self, mock_fetch):
        """Test when all videos fail."""
        mock_fetch.side_effect = [
            Exception("Error 1"),
            Exception("Error 2"),
        ]

        urls = [
            "https://youtube.com/watch?v=abc123",
            "https://youtube.com/watch?v=def456",
        ]

        result = fetch_multi_video_data(urls)

        # Verify stats
        assert result["stats"]["total"] == 2
        assert result["stats"]["succeeded"] == 0
        assert result["stats"]["failed"] == 2
        assert result["stats"]["success_rate"] == 0.0

        # All videos marked as failed
        assert all(not v["success"] for v in result["videos"])

    @patch("casestudypilot.tools.multi_video_processor.fetch_video_data")
    @patch("casestudypilot.tools.multi_video_processor.extract_video_id")
    def test_error_record_creation(self, mock_extract, mock_fetch):
        """Test that error records are created properly."""
        mock_fetch.side_effect = Exception("Network timeout")
        mock_extract.return_value = "abc123"

        urls = ["https://youtube.com/watch?v=abc123"]

        result = fetch_multi_video_data(urls)

        # Verify error record structure
        error_video = result["videos"][0]
        assert error_video["video_id"] == "abc123"
        assert error_video["url"] == urls[0]
        assert error_video["success"] is False
        assert error_video["error"] == "Network timeout"
        assert error_video["title"] == "Video abc123"
        assert error_video["transcript"] == ""
        assert error_video["duration_seconds"] == 0

    def test_empty_url_list(self):
        """Test with empty URL list."""
        result = fetch_multi_video_data([])

        # Verify empty result
        assert result["videos"] == []
        assert result["stats"]["total"] == 0
        assert result["stats"]["succeeded"] == 0
        assert result["stats"]["failed"] == 0
        assert result["stats"]["success_rate"] == 0.0

    @patch("casestudypilot.tools.multi_video_processor.fetch_video_data")
    def test_critical_validation_failure_handling(self, mock_fetch):
        """Test that critical validation failures are marked as failed."""
        video_data = {
            "video_id": "abc123",
            "url": "https://youtube.com/watch?v=abc123",
            "title": "Video 1",
            "transcript": "",
            "duration_seconds": 0,
            "validation": {"severity": "CRITICAL"},
        }

        mock_fetch.return_value = video_data

        urls = ["https://youtube.com/watch?v=abc123"]

        result = fetch_multi_video_data(urls)

        # Should be marked as failed
        assert result["videos"][0]["success"] is False
        assert result["videos"][0]["error"] == "Critical validation failure"
        assert result["stats"]["failed"] == 1
        assert result["stats"]["succeeded"] == 0


class TestGetSuccessfulVideos:
    """Tests for get_successful_videos function."""

    def test_filter_successful_videos(self):
        """Test filtering successful videos."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": True, "title": "Video 1"},
                {"video_id": "2", "success": False, "title": "Video 2"},
                {"video_id": "3", "success": True, "title": "Video 3"},
            ],
            "stats": {"total": 3, "succeeded": 2, "failed": 1},
        }

        successful = get_successful_videos(multi_video_data)

        assert len(successful) == 2
        assert successful[0]["video_id"] == "1"
        assert successful[1]["video_id"] == "3"

    def test_no_successful_videos(self):
        """Test when no videos succeeded."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": False},
                {"video_id": "2", "success": False},
            ],
            "stats": {"total": 2, "succeeded": 0, "failed": 2},
        }

        successful = get_successful_videos(multi_video_data)

        assert successful == []

    def test_all_successful_videos(self):
        """Test when all videos succeeded."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": True},
                {"video_id": "2", "success": True},
            ],
            "stats": {"total": 2, "succeeded": 2, "failed": 0},
        }

        successful = get_successful_videos(multi_video_data)

        assert len(successful) == 2


class TestGetFailedVideos:
    """Tests for get_failed_videos function."""

    def test_filter_failed_videos(self):
        """Test filtering failed videos."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": True, "title": "Video 1"},
                {"video_id": "2", "success": False, "error": "Error 2"},
                {"video_id": "3", "success": False, "error": "Error 3"},
            ],
            "stats": {"total": 3, "succeeded": 1, "failed": 2},
        }

        failed = get_failed_videos(multi_video_data)

        assert len(failed) == 2
        assert failed[0]["video_id"] == "2"
        assert failed[1]["video_id"] == "3"

    def test_no_failed_videos(self):
        """Test when no videos failed."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": True},
                {"video_id": "2", "success": True},
            ],
            "stats": {"total": 2, "succeeded": 2, "failed": 0},
        }

        failed = get_failed_videos(multi_video_data)

        assert failed == []

    def test_all_failed_videos(self):
        """Test when all videos failed."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": False},
                {"video_id": "2", "success": False},
            ],
            "stats": {"total": 2, "succeeded": 0, "failed": 2},
        }

        failed = get_failed_videos(multi_video_data)

        assert len(failed) == 2


class TestGetAllTranscripts:
    """Tests for get_all_transcripts function."""

    def test_combine_transcripts(self):
        """Test combining transcripts from successful videos."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": True, "transcript": "First transcript"},
                {"video_id": "2", "success": False, "transcript": "Should not appear"},
                {"video_id": "3", "success": True, "transcript": "Second transcript"},
            ],
        }

        combined = get_all_transcripts(multi_video_data)

        assert combined == "First transcript\n\nSecond transcript"

    def test_combine_transcripts_empty_transcripts(self):
        """Test that empty transcripts are filtered out."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": True, "transcript": "Valid transcript"},
                {"video_id": "2", "success": True, "transcript": ""},
                {"video_id": "3", "success": True, "transcript": "Another transcript"},
            ],
        }

        combined = get_all_transcripts(multi_video_data)

        # Empty transcript should be filtered
        assert combined == "Valid transcript\n\nAnother transcript"

    def test_combine_transcripts_no_successful_videos(self):
        """Test when no successful videos exist."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": False, "transcript": ""},
                {"video_id": "2", "success": False, "transcript": ""},
            ],
        }

        combined = get_all_transcripts(multi_video_data)

        assert combined == ""

    def test_combine_transcripts_single_video(self):
        """Test with single video."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": True, "transcript": "Single transcript"},
            ],
        }

        combined = get_all_transcripts(multi_video_data)

        assert combined == "Single transcript"


class TestCalculateTotalDuration:
    """Tests for calculate_total_duration function."""

    def test_calculate_duration_multiple_videos(self):
        """Test total duration calculation with multiple videos."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": True, "duration_seconds": 600},
                {"video_id": "2", "success": False, "duration_seconds": 1000},  # Ignored
                {"video_id": "3", "success": True, "duration_seconds": 900},
            ],
        }

        total = calculate_total_duration(multi_video_data)

        assert total == 1500  # 600 + 900

    def test_calculate_duration_no_successful_videos(self):
        """Test duration calculation with no successful videos."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": False, "duration_seconds": 600},
                {"video_id": "2", "success": False, "duration_seconds": 900},
            ],
        }

        total = calculate_total_duration(multi_video_data)

        assert total == 0

    def test_calculate_duration_missing_duration_field(self):
        """Test duration calculation when duration field is missing."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": True, "duration_seconds": 600},
                {"video_id": "2", "success": True},  # No duration_seconds
                {"video_id": "3", "success": True, "duration_seconds": 300},
            ],
        }

        total = calculate_total_duration(multi_video_data)

        assert total == 900  # 600 + 0 + 300

    def test_calculate_duration_empty_videos(self):
        """Test duration calculation with empty video list."""
        multi_video_data = {"videos": []}

        total = calculate_total_duration(multi_video_data)

        assert total == 0

    def test_calculate_duration_single_video(self):
        """Test duration calculation with single video."""
        multi_video_data = {
            "videos": [
                {"video_id": "1", "success": True, "duration_seconds": 1200},
            ],
        }

        total = calculate_total_duration(multi_video_data)

        assert total == 1200


class TestHelperFunctionEdgeCases:
    """Tests for edge cases in helper functions."""

    def test_missing_videos_key(self):
        """Test helpers handle missing 'videos' key gracefully."""
        multi_video_data = {}

        successful = get_successful_videos(multi_video_data)
        failed = get_failed_videos(multi_video_data)
        transcripts = get_all_transcripts(multi_video_data)
        duration = calculate_total_duration(multi_video_data)

        assert successful == []
        assert failed == []
        assert transcripts == ""
        assert duration == 0

    def test_videos_missing_success_flag(self):
        """Test filtering when 'success' flag is missing."""
        multi_video_data = {
            "videos": [
                {"video_id": "1"},  # No success flag
                {"video_id": "2", "success": True},
            ],
        }

        successful = get_successful_videos(multi_video_data)
        failed = get_failed_videos(multi_video_data)

        # Video without success flag should be treated as failed
        assert len(successful) == 1
        assert len(failed) == 1
