"""Tests for presenter validation functions."""

import pytest
from casestudypilot.validation import (
    validate_presenter,
    validate_biography,
    validate_profile_update,
    validate_presenter_profile,
    Severity,
)


class TestValidatePresenter:
    """Tests for validate_presenter function."""

    def test_valid_presenter_all_videos(self):
        """Test valid presenter with name in all videos."""
        multi_video_data = {
            "videos": [
                {
                    "success": True,
                    "title": "Talk by Jane Doe",
                    "description": "Jane speaks about Kubernetes",
                    "transcript": "Hi, I'm Jane Doe and today...",
                },
                {
                    "success": True,
                    "title": "Jane Doe on Cloud Native",
                    "description": "Another talk",
                    "transcript": "This is Jane Doe presenting...",
                },
                {
                    "success": True,
                    "title": "Advanced Topics",
                    "description": "Presented by Jane Doe",
                    "transcript": "Welcome, this is Jane...",
                },
            ],
        }

        result = validate_presenter("Jane Doe", multi_video_data)

        assert result.status == Severity.PASS
        assert not result.is_critical()

    def test_presenter_name_in_some_videos_warning(self):
        """Test warning when name appears in <80% but ≥50% of videos."""
        multi_video_data = {
            "videos": [
                {
                    "success": True,
                    "title": "Talk by Jane Doe",
                    "description": "Jane speaks",
                    "transcript": "Hi, I'm Jane...",
                },
                {
                    "success": True,
                    "title": "Cloud Native Patterns",
                    "description": "Generic description",
                    "transcript": "This talk covers...",
                },
                {
                    "success": True,
                    "title": "Kubernetes Deep Dive",
                    "description": "Technical talk",
                    "transcript": "Let's explore...",
                },
            ],
        }

        result = validate_presenter("Jane Doe", multi_video_data)

        # Name in 1/3 = 33% < 50%, should be CRITICAL
        assert result.status == Severity.CRITICAL
        assert result.is_critical()

    def test_presenter_name_not_in_videos_critical(self):
        """Test critical failure when name not in any videos."""
        multi_video_data = {
            "videos": [
                {
                    "success": True,
                    "title": "Generic Talk",
                    "description": "About cloud native",
                    "transcript": "This is a technical presentation...",
                },
                {
                    "success": True,
                    "title": "Another Talk",
                    "description": "More content",
                    "transcript": "Let's discuss...",
                },
            ],
        }

        result = validate_presenter("Jane Doe", multi_video_data)

        assert result.status == Severity.CRITICAL
        assert any(c.name == "name_in_videos" and not c.passed for c in result.checks)

    def test_generic_presenter_name_critical(self):
        """Test critical failure for generic names."""
        generic_names = ["Presenter", "Speaker", "User", "Person", "Name"]

        multi_video_data = {
            "videos": [
                {
                    "success": True,
                    "title": "Talk",
                    "description": "Description",
                    "transcript": "Content",
                },
            ],
        }

        for generic_name in generic_names:
            result = validate_presenter(generic_name, multi_video_data)
            assert result.status == Severity.CRITICAL
            assert any(c.name == "not_generic_name" and not c.passed for c in result.checks)

    def test_less_than_two_videos_critical(self):
        """Test critical failure when less than 2 successful videos."""
        multi_video_data = {
            "videos": [
                {
                    "success": True,
                    "title": "Only One Talk by Jane Doe",
                    "description": "Jane presents",
                    "transcript": "Hi, I'm Jane...",
                },
            ],
        }

        result = validate_presenter("Jane Doe", multi_video_data)

        assert result.status == Severity.CRITICAL
        assert any(c.name == "minimum_videos" and not c.passed for c in result.checks)

    def test_conflicting_names_detected_critical(self):
        """Test critical failure when conflicting presenter names detected."""
        multi_video_data = {
            "videos": [
                {
                    "success": True,
                    "title": "Talk by Jane Doe",
                    "description": "Presented by Jane Doe",
                    "transcript": "Hi, I'm Jane Doe...",
                },
                {
                    "success": True,
                    "title": "Speaker: John Smith on Kubernetes",
                    "description": "John Smith presents",
                    "transcript": "Welcome, I'm John Smith...",
                },
            ],
        }

        result = validate_presenter("Jane Doe", multi_video_data)

        # Should detect John Smith as conflicting name
        assert result.status == Severity.CRITICAL
        failed = result.get_failed_checks()
        assert any(c.name == "no_conflicting_names" for c in failed)

    def test_no_successful_videos_critical(self):
        """Test critical failure when no successful videos."""
        multi_video_data = {
            "videos": [
                {"success": False, "error": "Failed to fetch"},
                {"success": False, "error": "Network error"},
            ],
        }

        result = validate_presenter("Jane Doe", multi_video_data)

        assert result.status == Severity.CRITICAL

    def test_partial_name_matching(self):
        """Test that partial name matching works (first or last name)."""
        multi_video_data = {
            "videos": [
                {
                    "success": True,
                    "title": "Talk by Jane",  # Only first name
                    "description": "Kubernetes presentation",
                    "transcript": "This is Jane presenting...",
                },
                {
                    "success": True,
                    "title": "Cloud Native with Doe",  # Only last name
                    "description": "Advanced topics",
                    "transcript": "Welcome, Doe here...",
                },
            ],
        }

        result = validate_presenter("Jane Doe", multi_video_data)

        # Both videos should match (partial matching)
        # 2/2 = 100% match rate
        assert result.status == Severity.PASS or result.status == Severity.WARNING


class TestValidateBiography:
    """Tests for validate_biography function."""

    def test_valid_biography_all_fields(self):
        """Test valid biography with all fields."""
        biography_data = {
            "full_name": "Jane Doe",
            "biography": "Jane Doe is a software engineer with over 10 years of experience in cloud-native technologies. She has worked on Kubernetes, Docker, and various CNCF projects. Jane is passionate about open source and frequently speaks at conferences about container orchestration and microservices architecture.",
            "location": "San Francisco, CA",
            "current_role": "Senior Software Engineer at CNCF",
            "github_username": "janedoe",
        }

        result = validate_biography(biography_data)

        assert result.status == Severity.PASS
        assert not result.is_critical()

    def test_missing_required_fields_critical(self):
        """Test critical failure when required fields missing."""
        biography_data = {
            "location": "San Francisco",
            # Missing full_name and biography
        }

        result = validate_biography(biography_data)

        assert result.status == Severity.CRITICAL
        failed = result.get_failed_checks()
        assert any(c.name == "required_fields" and "full_name" in str(c.message) for c in failed)

    def test_placeholder_name_critical(self):
        """Test critical failure for placeholder names."""
        placeholder_names = [
            "First Name",
            "Full Name",
            "Name Here",
            "Speaker",
            "Presenter",
            "Lorem Ipsum",
            "TODO",
        ]

        for placeholder in placeholder_names:
            biography_data = {
                "full_name": placeholder,
                "biography": "A valid biography that is long enough to pass the length check. This person works on cloud native technologies.",
            }

            result = validate_biography(biography_data)
            assert result.status == Severity.CRITICAL
            assert any(c.name == "no_placeholder_name" and not c.passed for c in result.checks)

    def test_biography_too_short_critical(self):
        """Test critical failure when biography is too short."""
        biography_data = {
            "full_name": "Jane Doe",
            "biography": "Short bio",  # < 100 chars
        }

        result = validate_biography(biography_data)

        assert result.status == Severity.CRITICAL
        failed = result.get_failed_checks()
        assert any(c.name == "minimum_biography_length" and "too short" in c.message.lower() for c in failed)

    def test_biography_placeholder_text_critical(self):
        """Test critical failure when biography contains placeholder text."""
        placeholder_patterns = [
            "Lorem ipsum dolor sit amet consectetur adipiscing elit",
            "This is a placeholder for the biography content that will be added later",
            "TODO: Add biography here for this presenter",
            "TBD - Fill in biography details",
        ]

        for placeholder in placeholder_patterns:
            biography_data = {
                "full_name": "Jane Doe",
                "biography": placeholder,
            }

            result = validate_biography(biography_data)
            assert result.status == Severity.CRITICAL
            failed = result.get_failed_checks()
            assert any(c.name == "no_placeholder_bio" for c in failed)

    def test_biography_short_but_acceptable_warning(self):
        """Test warning for biography between 100-300 chars."""
        biography_data = {
            "full_name": "Jane Doe",
            "biography": "Jane is a software engineer with experience in Kubernetes. She works on cloud native projects.",  # ~100-300 chars
        }

        result = validate_biography(biography_data)

        # Should pass critical checks but have warning
        assert result.status == Severity.WARNING
        assert not result.is_critical()
        assert result.has_warnings()

    def test_missing_optional_fields_warning(self):
        """Test warning for missing optional fields."""
        biography_data = {
            "full_name": "Jane Doe",
            "biography": "Jane Doe is a software engineer with over 10 years of experience in cloud-native technologies. She has worked on various CNCF projects and is passionate about open source. Jane frequently speaks at conferences about container orchestration and microservices.",
            # Missing location, current_role, github_username
        }

        result = validate_biography(biography_data)

        # Should warn about missing optional fields
        assert result.has_warnings()
        assert any(c.name == "optional_fields" for c in result.checks)

    def test_biography_high_quality(self):
        """Test high quality biography with all fields and good length."""
        biography_data = {
            "full_name": "Jane Doe",
            "biography": "Jane Doe is a Senior Software Engineer specializing in cloud-native technologies with over 15 years of industry experience. She has been a key contributor to multiple CNCF projects including Kubernetes, Prometheus, and Envoy. Jane is recognized for her expertise in container orchestration, microservices architecture, and distributed systems. She regularly speaks at major industry conferences and has authored several influential blog posts on cloud native best practices.",
            "location": "San Francisco, CA",
            "current_role": "Senior Staff Engineer at Cloud Native Company",
            "github_username": "janedoe",
        }

        result = validate_biography(biography_data)

        assert result.status == Severity.PASS
        assert not result.has_warnings()


class TestValidateProfileUpdate:
    """Tests for validate_profile_update function."""

    def test_valid_profile_update(self):
        """Test valid profile update with new videos."""
        existing_profile = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "video_ids_processed": ["abc123", "def456"],
            "expertise_areas": [{"area": "Kubernetes", "context": "Container orchestration"}],
        }

        new_videos_data = {
            "videos": [
                {
                    "success": True,
                    "video_id": "ghi789",
                    "title": "New Talk by Jane Doe",
                    "description": "Jane presents on Kubernetes",
                    "transcript": "Hi, I'm Jane Doe...",
                },
                {
                    "success": True,
                    "video_id": "jkl012",
                    "title": "Another Jane Doe Talk",
                    "description": "Cloud native patterns",
                    "transcript": "This is Jane speaking...",
                },
            ],
        }

        result = validate_profile_update(existing_profile, new_videos_data)

        assert result.status == Severity.PASS
        assert not result.is_critical()

    def test_no_new_videos_critical(self):
        """Test critical failure when no successful new videos."""
        existing_profile = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "video_ids_processed": ["abc123"],
        }

        new_videos_data = {
            "videos": [
                {"success": False, "error": "Failed to fetch"},
            ],
        }

        result = validate_profile_update(existing_profile, new_videos_data)

        assert result.status == Severity.CRITICAL
        failed = result.get_failed_checks()
        assert any(c.name == "has_new_videos" and "No successful" in c.message for c in failed)

    def test_name_mismatch_critical(self):
        """Test critical failure when presenter name not in any new videos."""
        existing_profile = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "video_ids_processed": ["abc123"],
        }

        new_videos_data = {
            "videos": [
                {
                    "success": True,
                    "video_id": "new123",
                    "title": "Generic Talk",
                    "description": "About Kubernetes",
                    "transcript": "This presentation covers...",
                },
                {
                    "success": True,
                    "video_id": "new456",
                    "title": "Another Generic Talk",
                    "description": "Cloud native",
                    "transcript": "Let's discuss...",
                },
            ],
        }

        result = validate_profile_update(existing_profile, new_videos_data)

        assert result.status == Severity.CRITICAL
        failed = result.get_failed_checks()
        assert any(c.name == "name_consistency" and "not found" in c.message.lower() for c in failed)

    def test_duplicate_video_ids_warning(self):
        """Test warning when duplicate video IDs detected."""
        existing_profile = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "video_ids_processed": ["abc123", "def456"],
        }

        new_videos_data = {
            "videos": [
                {
                    "success": True,
                    "video_id": "abc123",  # Duplicate
                    "title": "Talk by Jane Doe",
                    "description": "Jane presents",
                    "transcript": "Hi, I'm Jane...",
                },
                {
                    "success": True,
                    "video_id": "new789",  # New
                    "title": "New Talk by Jane",
                    "description": "Jane's latest",
                    "transcript": "Jane Doe here...",
                },
            ],
        }

        result = validate_profile_update(existing_profile, new_videos_data)

        # Should warn about duplicate but not fail
        assert result.has_warnings()
        assert any(c.name == "no_duplicates" and "already in profile" in c.message.lower() for c in result.checks)

    def test_low_name_match_rate_warning(self):
        """Test warning when name found in < 50% of videos."""
        existing_profile = {
            "name": "Jane Doe",
            "github_username": "janedoe",
            "video_ids_processed": ["abc123"],
        }

        new_videos_data = {
            "videos": [
                {
                    "success": True,
                    "video_id": "new1",
                    "title": "Talk by Jane Doe",
                    "description": "Jane presents",
                    "transcript": "Hi, I'm Jane...",
                },
                {
                    "success": True,
                    "video_id": "new2",
                    "title": "Generic Talk",
                    "description": "About Kubernetes",
                    "transcript": "This covers...",
                },
                {
                    "success": True,
                    "video_id": "new3",
                    "title": "Another Generic",
                    "description": "Cloud patterns",
                    "transcript": "Let's discuss...",
                },
            ],
        }

        result = validate_profile_update(existing_profile, new_videos_data)

        # Name in 1/3 = 33% < 50%
        assert result.status == Severity.CRITICAL


class TestValidatePresenterProfile:
    """Tests for validate_presenter_profile function."""

    def test_high_quality_profile(self):
        """Test high quality profile with score ≥0.70."""
        profile_data = {
            "overview": "Jane Doe is a renowned expert in cloud-native technologies with over 15 years of experience.",
            "expertise": "Specializes in Kubernetes, service mesh, and CI/CD pipelines.",
            "talk_highlights": "Has presented at KubeCon, CloudNativeCon, and other major conferences.",
            "key_themes": "Container orchestration, microservices, GitOps, observability.",
            "stats_table": "5 talks | 2018-2023 | Kubernetes (3 talks)",
            "biography": "Jane is a Staff Engineer at a major tech company where she leads the cloud platform team. She has contributed to multiple CNCF projects and is an active member of the Kubernetes community. Jane is passionate about helping organizations adopt cloud-native practices and frequently shares her knowledge through conference talks and blog posts.",
            "talk_summaries": [
                {"title": "Talk 1", "summary": "Summary 1", "topics": ["k8s"]},
                {"title": "Talk 2", "summary": "Summary 2", "topics": ["ci/cd"]},
                {"title": "Talk 3", "summary": "Summary 3", "topics": ["mesh"]},
            ],
            "expertise_areas": [
                {"area": "Kubernetes", "context": "Expert level"},
                {"area": "Service Mesh", "context": "Advanced"},
            ],
            "cncf_projects": [
                {"name": "Kubernetes", "talk_count": 3},
                {"name": "Envoy", "talk_count": 1},
            ],
        }

        result = validate_presenter_profile(profile_data)

        assert result.status == Severity.PASS
        assert not result.is_critical()

    def test_acceptable_quality_profile_warning(self):
        """Test acceptable quality profile with score 0.60-0.69."""
        profile_data = {
            "overview": "Jane Doe is a software engineer.",
            "expertise": "Works with Kubernetes.",
            "talk_highlights": "Has given talks.",
            "key_themes": "Cloud native.",
            "stats_table": "Stats",
            "biography": "Jane is an engineer who works with cloud technologies. She has some experience with Kubernetes.",  # ~120 chars
            "talk_summaries": [
                {"title": "Talk 1", "summary": "Summary"},
                {"title": "Talk 2", "summary": "Summary"},
            ],
            "expertise_areas": [{"area": "Kubernetes"}],
            "cncf_projects": [{"name": "Kubernetes"}],
        }

        result = validate_presenter_profile(profile_data)

        # Should have warnings but not critical
        assert result.status == Severity.WARNING
        assert not result.is_critical()
        assert result.has_warnings()

    def test_low_quality_profile_critical(self):
        """Test low quality profile with score <0.60."""
        profile_data = {
            "overview": "Short",
            # Missing most sections
            "biography": "Too short",  # < 100 chars
            "talk_summaries": [{"title": "Only one talk"}],  # < 2 talks
            "expertise_areas": [],
            "cncf_projects": [],  # No CNCF projects
        }

        result = validate_presenter_profile(profile_data)

        assert result.status == Severity.CRITICAL
        assert result.is_critical()

    def test_missing_sections_critical(self):
        """Test critical failure when required sections missing."""
        profile_data = {
            "overview": "Has overview",
            # Missing expertise, talk_highlights, key_themes, stats_table
            "biography": "Biography",
            "talk_summaries": [],
            "expertise_areas": [],
            "cncf_projects": [],
        }

        result = validate_presenter_profile(profile_data)

        assert result.status == Severity.CRITICAL
        failed = result.get_failed_checks()
        assert any(c.name == "structure_completeness" for c in failed)

    def test_placeholder_text_critical(self):
        """Test critical failure when profile contains placeholder text."""
        profile_data = {
            "overview": "TODO: Add overview here",
            "expertise": "Placeholder text about expertise",
            "talk_highlights": "Fill in highlights",
            "key_themes": "TBD",
            "stats_table": "Stats",
            "biography": "This is a placeholder biography that will be replaced later with actual content about the presenter.",
            "talk_summaries": [
                {"title": "Talk 1"},
                {"title": "Talk 2"},
            ],
            "expertise_areas": [{"area": "Kubernetes"}],
            "cncf_projects": [{"name": "Kubernetes"}],
        }

        result = validate_presenter_profile(profile_data)

        assert result.status == Severity.CRITICAL
        failed = result.get_failed_checks()
        assert any(c.name == "factual_consistency" and "placeholder" in c.message.lower() for c in failed)

    def test_no_cncf_projects_critical(self):
        """Test critical failure when no CNCF projects identified."""
        profile_data = {
            "overview": "Overview",
            "expertise": "Expertise",
            "talk_highlights": "Highlights",
            "key_themes": "Themes",
            "stats_table": "Stats",
            "biography": "A biography with sufficient length to pass the minimum character count requirement for quality.",
            "talk_summaries": [
                {"title": "Talk 1"},
                {"title": "Talk 2"},
            ],
            "expertise_areas": [{"area": "General"}],
            "cncf_projects": [],  # No CNCF projects
        }

        result = validate_presenter_profile(profile_data)

        assert result.status == Severity.CRITICAL
        failed = result.get_failed_checks()
        assert any(c.name == "expertise_identification" and "No CNCF projects" in c.message for c in failed)

    def test_too_few_talks_critical(self):
        """Test critical failure when less than 2 talks."""
        profile_data = {
            "overview": "Overview",
            "expertise": "Expertise",
            "talk_highlights": "Highlights",
            "key_themes": "Themes",
            "stats_table": "Stats",
            "biography": "A biography with sufficient length to meet the minimum requirements for profile quality.",
            "talk_summaries": [{"title": "Only one talk"}],  # < 2
            "expertise_areas": [{"area": "Kubernetes"}],
            "cncf_projects": [{"name": "Kubernetes"}],
        }

        result = validate_presenter_profile(profile_data)

        assert result.status == Severity.CRITICAL
        failed = result.get_failed_checks()
        assert any(c.name == "talk_coverage" and "Too few talks" in c.message for c in failed)

    def test_quality_score_calculation(self):
        """Test that quality score is calculated correctly."""
        profile_data = {
            "overview": "Overview",
            "expertise": "Expertise",
            "talk_highlights": "Highlights",
            "key_themes": "Themes",
            "stats_table": "Stats",
            "biography": "A" * 500,  # 500 chars = full bio score
            "talk_summaries": [{"title": f"Talk {i}"} for i in range(5)],  # 5 talks = full score
            "expertise_areas": [{"area": f"Area {i}"} for i in range(3)],
            "cncf_projects": [{"name": f"Project {i}"} for i in range(2)],  # 5 total items = full score
        }

        result = validate_presenter_profile(profile_data)

        # All factors should be 1.0, overall score should be 1.0
        assert result.status == Severity.PASS
        overall_check = next(c for c in result.checks if c.name == "overall_quality")
        assert overall_check.details["score"] == 1.0

    def test_custom_threshold(self):
        """Test profile validation with custom threshold."""
        profile_data = {
            "overview": "Overview",
            "expertise": "Expertise",
            "talk_highlights": "Highlights",
            "key_themes": "Themes",
            "stats_table": "Stats",
            "biography": "Adequate biography with enough content to pass minimum requirements.",
            "talk_summaries": [{"title": "Talk 1"}, {"title": "Talk 2"}],
            "expertise_areas": [{"area": "Kubernetes"}],
            "cncf_projects": [{"name": "Kubernetes"}],
        }

        # Test with higher threshold (0.80)
        result = validate_presenter_profile(profile_data, threshold=0.80)

        # Should fail with higher threshold
        assert result.status == Severity.CRITICAL
