"""Tests for profile assembler functionality."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from datetime import datetime

from casestudypilot.tools.profile_assembler import (
    load_json_file,
    calculate_stats,
    determine_profile_version,
    assemble_presenter_profile,
)


class TestLoadJsonFile:
    """Tests for load_json_file function."""

    def test_load_valid_json(self, tmp_path):
        """Test loading valid JSON file."""
        data = {"name": "Jane Doe", "bio": "Software Engineer"}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data))

        result = load_json_file(json_file)

        assert result == data

    def test_load_json_file_not_found(self):
        """Test FileNotFoundError when file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_json_file(Path("/nonexistent/file.json"))

    def test_load_invalid_json(self, tmp_path):
        """Test JSONDecodeError when file contains invalid JSON."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid json ")

        with pytest.raises(json.JSONDecodeError):
            load_json_file(json_file)


class TestCalculateStats:
    """Tests for calculate_stats function."""

    def test_calculate_stats_complete_data(self):
        """Test stats calculation with complete data."""
        aggregation_data = {
            "stats": {
                "total_talks": 5,
                "years_active": {"first": 2020, "latest": 2024, "span": 4},
                "most_discussed_project": {"name": "Kubernetes", "count": 3},
                "total_speaking_minutes": 150,
            }
        }
        biography_data = {
            "github_data": {
                "followers": 250,
                "organizations": ["cncf", "kubernetes", "kubernetes-sigs"],
            }
        }

        stats = calculate_stats(aggregation_data, biography_data)

        assert stats["total_talks"] == "5 presentations"
        assert stats["years_active"] == "2020 - 2024 (4 years)"
        assert stats["top_technology"] == "Kubernetes (3 talks)"
        assert stats["github_followers"] == "250"
        assert stats["organizations"] == "CNCF, Kubernetes, Kubernetes SIGs"
        assert stats["total_speaking_time"] == "2 hours 30 minutes"

    def test_calculate_stats_single_talk(self):
        """Test stats with single talk (singular form)."""
        aggregation_data = {
            "stats": {
                "total_talks": 1,
                "years_active": {"first": 2024, "latest": 2024, "span": 0},
                "most_discussed_project": {"name": "Envoy", "count": 1},
                "total_speaking_minutes": 45,
            }
        }
        biography_data = {"github_data": {"followers": 50, "organizations": []}}

        stats = calculate_stats(aggregation_data, biography_data)

        assert stats["total_talks"] == "1 presentation"  # Singular
        assert stats["years_active"] == "2024 - 2024 (0 years)"  # 0 years
        assert stats["top_technology"] == "Envoy (1 talk)"  # Singular
        assert stats["total_speaking_time"] == "45 minutes"

    def test_calculate_stats_duration_formatting(self):
        """Test duration formatting edge cases."""
        test_cases = [
            (60, "1 hours"),  # Exactly 1 hour
            (90, "1 hours 30 minutes"),  # 1.5 hours
            (120, "2 hours"),  # Exactly 2 hours
            (125, "2 hours 5 minutes"),  # 2 hours 5 minutes
            (30, "30 minutes"),  # Less than 1 hour
        ]

        for total_minutes, expected in test_cases:
            aggregation_data = {
                "stats": {
                    "total_talks": 1,
                    "years_active": {"first": 2024, "latest": 2024, "span": 0},
                    "most_discussed_project": {"name": "Kubernetes", "count": 1},
                    "total_speaking_minutes": total_minutes,
                }
            }
            biography_data = {"github_data": {"followers": 0, "organizations": []}}

            stats = calculate_stats(aggregation_data, biography_data)
            assert stats["total_speaking_time"] == expected

    def test_calculate_stats_primary_focus_multiple_areas(self):
        """Test primary focus with multiple expertise areas."""
        aggregation_data = {
            "stats": {
                "total_talks": 3,
                "years_active": {"first": 2022, "latest": 2024, "span": 2},
                "most_discussed_project": {"name": "Kubernetes", "count": 2},
                "total_speaking_minutes": 100,
            },
            "expertise_areas": [
                {"area": "Container Orchestration", "talk_count": 3},
                {"area": "GitOps", "talk_count": 2},
                {"area": "Service Mesh", "talk_count": 1},
            ],
        }
        biography_data = {"github_data": {"followers": 100, "organizations": []}}

        stats = calculate_stats(aggregation_data, biography_data)

        # Should show top 2 areas
        assert stats["primary_focus"] == "Container Orchestration & GitOps"

    def test_calculate_stats_no_expertise_areas(self):
        """Test primary focus when no expertise areas."""
        aggregation_data = {
            "stats": {
                "total_talks": 1,
                "years_active": {"first": 2024, "latest": 2024, "span": 0},
                "most_discussed_project": {"name": "Kubernetes", "count": 1},
                "total_speaking_minutes": 50,
            },
            "expertise_areas": [],
        }
        biography_data = {"github_data": {"followers": 0, "organizations": []}}

        stats = calculate_stats(aggregation_data, biography_data)

        assert stats["primary_focus"] == "N/A"

    def test_calculate_stats_organization_formatting(self):
        """Test organization name formatting."""
        test_cases = [
            (["cncf"], "CNCF"),  # Uppercase short names
            (["kubernetes-sigs"], "Kubernetes SIGs"),  # Special case
            (["github"], "Github"),  # Title case
            (["cncf", "kubernetes", "prometheus"], "CNCF, Kubernetes, Prometheus"),  # Multiple
            (["org1", "org2", "org3", "org4"], "Org1, Org2, Org3"),  # Limit to 3
        ]

        for orgs, expected in test_cases:
            aggregation_data = {
                "stats": {
                    "total_talks": 1,
                    "years_active": {"first": 2024, "latest": 2024, "span": 0},
                    "most_discussed_project": {"name": "K8s", "count": 1},
                    "total_speaking_minutes": 50,
                }
            }
            biography_data = {"github_data": {"followers": 0, "organizations": orgs}}

            stats = calculate_stats(aggregation_data, biography_data)
            assert stats["organizations"] == expected

    def test_calculate_stats_missing_data(self):
        """Test stats calculation with missing data."""
        aggregation_data = {"stats": {}}
        biography_data = {"github_data": {}}

        stats = calculate_stats(aggregation_data, biography_data)

        assert stats["total_talks"] == "0 presentations"
        assert stats["years_active"] == "Unknown - Unknown (0 years)"
        assert stats["top_technology"] == "N/A (0 talks)"
        assert stats["github_followers"] == "0"
        assert stats["organizations"] == "N/A"
        assert stats["total_speaking_time"] == "0 minutes"


class TestDetermineProfileVersion:
    """Tests for determine_profile_version function."""

    def test_new_profile_version(self):
        """Test version 1.0 for new profiles."""
        result = determine_profile_version(None)
        assert result == "1.0"

    def test_new_profile_nonexistent_path(self, tmp_path):
        """Test version 1.0 when path doesn't exist."""
        nonexistent = tmp_path / "nonexistent.md"
        result = determine_profile_version(nonexistent)
        assert result == "1.0"

    def test_increment_version_from_existing(self, tmp_path):
        """Test version increments from existing profile."""
        existing_profile = tmp_path / "profile.md"
        existing_profile.write_text("""---
name: Jane Doe
profile_version: 1.0
---

# Jane Doe
""")

        result = determine_profile_version(existing_profile)
        assert result == "2.0"

    def test_increment_version_from_2_0(self, tmp_path):
        """Test version increments from 2.0 to 3.0."""
        existing_profile = tmp_path / "profile.md"
        existing_profile.write_text("""---
profile_version: 2.0
---

# Profile Content
""")

        result = determine_profile_version(existing_profile)
        assert result == "3.0"

    def test_version_without_frontmatter(self, tmp_path):
        """Test default increment when no version in frontmatter."""
        existing_profile = tmp_path / "profile.md"
        existing_profile.write_text("# Jane Doe\n\nNo frontmatter here")

        result = determine_profile_version(existing_profile)
        assert result == "2.0"  # Default increment

    def test_version_with_invalid_format(self, tmp_path):
        """Test default increment when version format is invalid."""
        existing_profile = tmp_path / "profile.md"
        existing_profile.write_text("""---
profile_version: invalid
---

# Profile
""")

        result = determine_profile_version(existing_profile)
        assert result == "2.0"  # Fallback


class TestAssemblePresenterProfile:
    """Tests for assemble_presenter_profile function."""

    def test_assemble_new_profile_success(self, tmp_path):
        """Test successful assembly of new profile."""
        biography_data = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "location": "San Francisco",
            "current_role": "Software Engineer",
            "github_data": {
                "followers": 100,
                "organizations": ["cncf"],
                "website": "https://example.com",
            },
        }

        aggregation_data = {
            "stats": {
                "total_talks": 3,
                "years_active": {"first": 2022, "latest": 2024, "span": 2},
                "most_discussed_project": {"name": "Kubernetes", "count": 2},
                "total_speaking_minutes": 120,
            },
            "expertise_areas": [{"area": "Kubernetes", "context": "Expert"}],
            "cncf_projects": [{"name": "Kubernetes", "talk_count": 2, "usage_context": "Orchestration"}],
            "talk_summaries": [
                {
                    "video_id": "abc123",
                    "title": "Talk 1",
                    "date": "2024-01-15",
                    "url": "https://youtube.com/watch?v=abc123",
                    "duration": 1800,
                    "summary": "Summary 1",
                    "topics": ["k8s"],
                    "event": "KubeCon",
                },
                {
                    "video_id": "def456",
                    "title": "Talk 2",
                    "date": "2023-06-20",
                    "url": "https://youtube.com/watch?v=def456",
                    "duration": 2400,
                    "summary": "Summary 2",
                    "topics": ["ci/cd"],
                    "event": "CloudNativeCon",
                },
            ],
        }

        sections_data = {
            "overview": "Jane Doe is a software engineer...",
            "key_themes": "Container orchestration and GitOps...",
        }

        output_path = tmp_path / "people" / "janedoe.md"

        # Mock the template rendering
        with patch("casestudypilot.tools.profile_assembler.create_jinja_env") as mock_env_factory:
            mock_env = Mock()
            mock_template = Mock()
            mock_template.render.return_value = "# Jane Doe\n\nRendered profile content"
            mock_env.get_template.return_value = mock_template
            mock_env_factory.return_value = mock_env

            result = assemble_presenter_profile(
                biography_data,
                aggregation_data,
                sections_data,
                output_path=output_path,
            )

        # Verify result
        assert result["presenter_name"] == "Jane Doe"
        assert result["github_username"] == "janedoe"
        assert result["profile_version"] == "1.0"
        assert Path(result["output_path"]).exists()
        assert Path(result["metadata_path"]).exists()

        # Verify metadata JSON
        metadata_path = Path(result["metadata_path"])
        with open(metadata_path) as f:
            metadata = json.load(f)
        assert metadata["name"] == "Jane Doe"
        assert metadata["github_username"] == "janedoe"
        assert metadata["profile_version"] == 1.0
        assert len(metadata["video_ids_processed"]) == 2
        assert "abc123" in metadata["video_ids_processed"]

    def test_assemble_profile_missing_name_error(self):
        """Test ValueError when name is missing."""
        biography_data = {
            # Missing 'name'
            "github_username": "janedoe",
        }
        aggregation_data = {"stats": {}}
        sections_data = {}

        with pytest.raises(ValueError, match="missing required 'name' field"):
            assemble_presenter_profile(biography_data, aggregation_data, sections_data)

    def test_assemble_profile_missing_github_username_error(self):
        """Test ValueError when github_username is missing."""
        biography_data = {
            "name": "Jane Doe",
            # Missing 'github_username'
        }
        aggregation_data = {"stats": {}}
        sections_data = {}

        with pytest.raises(ValueError, match="missing required 'github_username' field"):
            assemble_presenter_profile(biography_data, aggregation_data, sections_data)

    def test_assemble_profile_template_not_found(self, tmp_path):
        """Test FileNotFoundError when template not found."""
        biography_data = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "github_data": {},
        }
        aggregation_data = {"stats": {}, "talk_summaries": []}
        sections_data = {}

        with patch("casestudypilot.tools.profile_assembler.create_jinja_env") as mock_env_factory:
            mock_env = Mock()
            mock_env.get_template.side_effect = Exception("Template not found")
            mock_env_factory.return_value = mock_env

            with pytest.raises(FileNotFoundError, match="Template not found"):
                assemble_presenter_profile(biography_data, aggregation_data, sections_data)

    def test_assemble_profile_update(self, tmp_path):
        """Test profile update increments version."""
        # Create existing profile
        existing_profile = tmp_path / "people" / "janedoe.md"
        existing_profile.parent.mkdir(parents=True)
        existing_profile.write_text("""---
name: Jane Doe
profile_version: 1.0
---

# Jane Doe
""")

        biography_data = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "github_data": {"followers": 100, "organizations": []},
        }
        aggregation_data = {"stats": {}, "talk_summaries": []}
        sections_data = {}

        with patch("casestudypilot.tools.profile_assembler.create_jinja_env") as mock_env_factory:
            mock_env = Mock()
            mock_template = Mock()
            mock_template.render.return_value = "Updated profile"
            mock_env.get_template.return_value = mock_template
            mock_env_factory.return_value = mock_env

            result = assemble_presenter_profile(
                biography_data,
                aggregation_data,
                sections_data,
                existing_profile_path=existing_profile,
                output_path=tmp_path / "people" / "janedoe.md",
            )

        # Version should be incremented
        assert result["profile_version"] == "2.0"

    def test_assemble_profile_talks_by_year(self, tmp_path):
        """Test that talks are grouped by year correctly."""
        biography_data = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "github_data": {},
        }
        aggregation_data = {
            "stats": {},
            "talk_summaries": [
                {
                    "video_id": "1",
                    "title": "Talk 2024-1",
                    "date": "2024-01-15",
                    "duration": 1800,
                    "url": "https://example.com",
                    "summary": "Summary",
                    "topics": [],
                    "event": "Event 1",
                },
                {
                    "video_id": "2",
                    "title": "Talk 2023-1",
                    "date": "2023-06-20",
                    "duration": 3600,
                    "url": "https://example.com",
                    "summary": "Summary",
                    "topics": [],
                    "event": "Event 2",
                },
                {
                    "video_id": "3",
                    "title": "Talk 2024-2",
                    "date": "2024-05-10",
                    "duration": 2400,
                    "url": "https://example.com",
                    "summary": "Summary",
                    "topics": [],
                    "event": "Event 3",
                },
            ],
        }
        sections_data = {}

        with patch("casestudypilot.tools.profile_assembler.create_jinja_env") as mock_env_factory:
            mock_env = Mock()
            mock_template = Mock()
            mock_template.render.return_value = "Profile"
            mock_env.get_template.return_value = mock_template
            mock_env_factory.return_value = mock_env

            assemble_presenter_profile(
                biography_data,
                aggregation_data,
                sections_data,
                output_path=tmp_path / "profile.md",
            )

            # Check template render was called with talks_by_year
            render_call = mock_template.render.call_args
            context = render_call[1] if render_call[1] else render_call[0][0]
            talks_by_year = context.get("talks_by_year", [])

            # Should have 2 years
            years = [y["year"] for y in talks_by_year]
            assert "2024" in years
            assert "2023" in years

            # 2024 should come first (descending order)
            assert talks_by_year[0]["year"] == "2024"
            assert len(talks_by_year[0]["talks"]) == 2

    def test_assemble_profile_duration_formatting(self, tmp_path):
        """Test that talk durations are formatted correctly."""
        biography_data = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "github_data": {},
        }
        aggregation_data = {
            "stats": {},
            "talk_summaries": [
                {
                    "video_id": "1",
                    "title": "Short Talk",
                    "date": "2024-01-15",
                    "duration": 1800,  # 30 minutes
                    "url": "https://example.com",
                    "summary": "Summary",
                    "topics": [],
                    "event": "Event",
                },
                {
                    "video_id": "2",
                    "title": "Long Talk",
                    "date": "2024-02-20",
                    "duration": 5400,  # 90 minutes = 1 hour 30 minutes
                    "url": "https://example.com",
                    "summary": "Summary",
                    "topics": [],
                    "event": "Event",
                },
            ],
        }
        sections_data = {}

        with patch("casestudypilot.tools.profile_assembler.create_jinja_env") as mock_env_factory:
            mock_env = Mock()
            mock_template = Mock()
            mock_template.render.return_value = "Profile"
            mock_env.get_template.return_value = mock_template
            mock_env_factory.return_value = mock_env

            assemble_presenter_profile(
                biography_data,
                aggregation_data,
                sections_data,
                output_path=tmp_path / "profile.md",
            )

            # Check duration formatting in context
            render_call = mock_template.render.call_args
            context = render_call[1] if render_call[1] else render_call[0][0]
            talks_by_year = context.get("talks_by_year", [])
            talks = talks_by_year[0]["talks"]

            assert talks[0]["duration"] == "30 minutes"
            assert talks[1]["duration"] == "1 hour 30 minutes"

    def test_assemble_profile_default_output_path(self, tmp_path):
        """Test that default output path is generated correctly."""
        biography_data = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "github_data": {},
        }
        aggregation_data = {"stats": {}, "talk_summaries": []}
        sections_data = {}

        with patch("casestudypilot.tools.profile_assembler.create_jinja_env") as mock_env_factory:
            mock_env = Mock()
            mock_template = Mock()
            mock_template.render.return_value = "Profile"
            mock_env.get_template.return_value = mock_template
            mock_env_factory.return_value = mock_env

            # Change to tmp directory for test
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmp_path)
                result = assemble_presenter_profile(
                    biography_data,
                    aggregation_data,
                    sections_data,
                    # No output_path specified
                )

                # Should use default path
                assert "people/janedoe.md" in result["output_path"]
                assert "people/metadata/janedoe.json" in result["metadata_path"]
            finally:
                os.chdir(original_cwd)
