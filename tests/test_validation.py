"""Unit tests for validation framework."""

import pytest
import tempfile
import os
from pathlib import Path
from casestudypilot.validation import (
    validate_transcript,
    validate_company_name,
    validate_analysis,
    validate_metrics,
    validate_company_consistency,
    validate_case_study_format,
    Severity,
)


class TestValidateTranscript:
    """Tests for transcript validation."""

    def test_valid_transcript_passes(self):
        """Test transcript validation with good data."""
        transcript = (
            "This is a detailed transcript about Kubernetes and cloud native technologies. "
            * 100
        )
        segments = [
            {"text": f"segment {i}", "start": i, "duration": 1} for i in range(100)
        ]

        result = validate_transcript(transcript, segments)

        assert result.status == Severity.PASS
        assert not result.is_critical()
        assert not result.has_warnings()

    def test_empty_transcript_fails_critically(self):
        """Test empty transcript fails critically."""
        result = validate_transcript("", [])

        assert result.status == Severity.CRITICAL
        assert result.is_critical()
        assert any(
            "empty" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_short_transcript_fails_critically(self):
        """Test short transcript fails critically."""
        transcript = "Short text"
        segments = [{"text": "Short", "start": 0, "duration": 1}]

        result = validate_transcript(transcript, segments)

        assert result.status == Severity.CRITICAL
        assert any(
            "too short" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_few_segments_fails_critically(self):
        """Test too few segments fails critically."""
        transcript = "This is a transcript. " * 100  # Long enough text
        segments = [
            {"text": "segment", "start": 0, "duration": 1}
        ] * 10  # Only 10 segments

        result = validate_transcript(transcript, segments)

        assert result.status == Severity.CRITICAL
        assert any(
            "few" in c.message.lower() and "segment" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_short_but_valid_transcript_warns(self):
        """Test short but valid transcript produces warning."""
        transcript = "Valid transcript content. " * 100  # 2700 chars, < 5000
        segments = [
            {"text": f"segment {i}", "start": i, "duration": 1} for i in range(100)
        ]

        result = validate_transcript(transcript, segments)

        # Should pass critical checks but have warning
        assert result.status == Severity.WARNING
        assert not result.is_critical()
        assert result.has_warnings()
        assert any(
            "short transcript" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_no_meaningful_content_fails(self):
        """Test transcript without meaningful content fails."""
        transcript = "a b c d e"  # Very few words
        segments = [{"text": "a", "start": i, "duration": 1} for i in range(60)]

        result = validate_transcript(transcript, segments)

        assert result.status == Severity.CRITICAL
        assert any(
            "meaningful content" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )


class TestValidateCompanyName:
    """Tests for company name validation."""

    def test_valid_company_passes(self):
        """Test valid company name passes."""
        result = validate_company_name(
            "Intuit", "Intuit's Journey to Cloud Native", confidence=1.0
        )

        assert result.status == Severity.PASS
        assert not result.is_critical()

    def test_generic_company_name_fails(self):
        """Test generic company names fail."""
        generic_names = ["Company", "Organization", "Tech", "Unknown", "TBD"]

        for name in generic_names:
            result = validate_company_name(name, "Some video title")

            assert result.status == Severity.CRITICAL
            assert any(
                "generic" in c.message.lower()
                for c in result.get_failed_checks()
                if c.message
            )

    def test_empty_company_name_fails(self):
        """Test empty company name fails."""
        result = validate_company_name("", "Some video title")

        assert result.status == Severity.CRITICAL
        assert any(
            "no company name" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_short_company_name_fails(self):
        """Test very short company name fails."""
        result = validate_company_name("X", "Some video title")

        assert result.status == Severity.CRITICAL
        assert any(
            "too short" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_low_confidence_fails_critically(self):
        """Test low confidence (< 0.5) fails critically."""
        result = validate_company_name("SomeCompany", "Video title", confidence=0.3)

        assert result.status == Severity.CRITICAL
        assert any(
            "low confidence" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_medium_confidence_warns(self):
        """Test medium confidence (0.5-0.7) produces warning."""
        result = validate_company_name("SomeCompany", "Video title", confidence=0.6)

        assert result.status == Severity.WARNING
        assert any(
            "low confidence" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_high_confidence_passes(self):
        """Test high confidence (>= 0.7) passes."""
        result = validate_company_name("Intuit", "Video title", confidence=0.8)

        assert result.status == Severity.PASS


class TestValidateAnalysis:
    """Tests for analysis validation."""

    def test_valid_analysis_passes(self):
        """Test valid analysis passes."""
        analysis = {
            "cncf_projects": [
                {"name": "Kubernetes", "usage_context": "orchestration"},
                {"name": "Argo CD", "usage_context": "GitOps"},
            ],
            "key_metrics": [
                {
                    "value": "50%",
                    "type": "percentage",
                    "context": "deployment time reduction",
                }
            ],
            "sections": {
                "background": "Company background information with sufficient detail to understand context and business needs."
                * 2,
                "challenge": "Technical challenges faced by the organization requiring cloud native solutions and modernization."
                * 2,
                "solution": "Implementation approach using CNCF technologies to solve the problems and achieve goals."
                * 2,
                "impact": "Measurable results and business outcomes from the cloud native transformation and adoption."
                * 2,
            },
        }

        result = validate_analysis(analysis)

        assert result.status == Severity.PASS
        assert not result.is_critical()

    def test_missing_keys_fails(self):
        """Test missing required keys fails."""
        analysis = {
            "cncf_projects": []
            # Missing key_metrics and sections
        }

        result = validate_analysis(analysis)

        assert result.status == Severity.CRITICAL
        assert any(
            "missing required keys" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_no_cncf_projects_fails(self):
        """Test analysis with no CNCF projects fails."""
        analysis = {
            "cncf_projects": [],
            "key_metrics": [],
            "sections": {
                "background": "test" * 30,
                "challenge": "test" * 30,
                "solution": "test" * 30,
                "impact": "test" * 30,
            },
        }

        result = validate_analysis(analysis)

        assert result.status == Severity.CRITICAL
        assert any(
            "no cncf projects" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_only_one_project_warns(self):
        """Test analysis with only 1 project produces warning."""
        analysis = {
            "cncf_projects": [{"name": "Kubernetes", "usage_context": "orchestration"}],
            "key_metrics": [{"value": "50%", "type": "percentage"}],
            "sections": {
                "background": "test" * 30,
                "challenge": "test" * 30,
                "solution": "test" * 30,
                "impact": "test" * 30,
            },
        }

        result = validate_analysis(analysis)

        assert result.status == Severity.WARNING
        assert any(
            "only 1 cncf project" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_missing_sections_fails(self):
        """Test missing sections fails."""
        analysis = {
            "cncf_projects": [{"name": "Kubernetes", "usage_context": "orchestration"}],
            "key_metrics": [],
            "sections": {
                "background": "test" * 30
                # Missing challenge, solution, impact
            },
        }

        result = validate_analysis(analysis)

        assert result.status == Severity.CRITICAL
        assert any(
            "missing required sections" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_short_sections_fail(self):
        """Test sections with insufficient content fail."""
        analysis = {
            "cncf_projects": [{"name": "Kubernetes", "usage_context": "orchestration"}],
            "key_metrics": [],
            "sections": {
                "background": "short",  # < 100 chars
                "challenge": "test" * 30,
                "solution": "test" * 30,
                "impact": "test" * 30,
            },
        }

        result = validate_analysis(analysis)

        assert result.status == Severity.CRITICAL
        assert any(
            "too short" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_no_metrics_warns(self):
        """Test no metrics produces warning."""
        analysis = {
            "cncf_projects": [{"name": "Kubernetes", "usage_context": "orchestration"}],
            "key_metrics": [],  # No metrics
            "sections": {
                "background": "test" * 30,
                "challenge": "test" * 30,
                "solution": "test" * 30,
                "impact": "test" * 30,
            },
        }

        result = validate_analysis(analysis)

        # Should have warning about no metrics (but may also have warning about 1 project)
        assert result.has_warnings()
        assert any(
            "no quantitative metrics" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )


class TestValidateMetrics:
    """Tests for metric fabrication detection."""

    def test_all_metrics_in_transcript_passes(self):
        """Test metrics that exist in transcript pass."""
        generated = {
            "overview": "Company achieved 50% improvement",
            "impact": "Deployed 10,000 pods in production",
        }
        transcript = "We achieved a 50% improvement in deployment time. We now run 10,000 pods in production."
        analysis = {"key_metrics": []}

        result = validate_metrics(generated, transcript, analysis)

        assert result.status == Severity.PASS
        assert not result.has_warnings()

    def test_fabricated_metrics_warn(self):
        """Test fabricated metrics produce warning."""
        generated = {
            "overview": "Company achieved 99% uptime",
            "impact": "Reduced costs by 50%",
        }
        transcript = "We improved our uptime significantly and reduced costs"  # No "99%" or "50%"
        analysis = {"key_metrics": []}

        result = validate_metrics(generated, transcript, analysis)

        assert result.status == Severity.WARNING
        assert result.has_warnings()
        assert any(
            "don't appear in transcript" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_fuzzy_matching_allows_variations(self):
        """Test fuzzy matching allows reasonable variations."""
        generated = {"impact": "Achieved 50% reduction"}
        # Transcript has "50 percent" instead of "50%"
        transcript = "We achieved a 50 percent reduction in deployment time"
        analysis = {"key_metrics": []}

        result = validate_metrics(generated, transcript, analysis)

        # Should pass due to fuzzy matching
        assert result.status == Severity.PASS


class TestValidateCompanyConsistency:
    """Tests for company mismatch detection."""

    def test_correct_company_passes(self):
        """Test case study about correct company passes."""
        generated = {
            "overview": "Acme Corp is a software company that adopted cloud native technologies.",
            "challenge": "Acme Corp faced scaling challenges with their legacy infrastructure.",
        }
        video_data = {"title": "Acme Corp's Journey to Cloud Native"}

        result = validate_company_consistency("Acme Corp", generated, video_data)

        assert result.status == Severity.PASS
        assert not result.is_critical()

    def test_wrong_company_fails_critically(self):
        """Test case study about wrong company fails critically (Spotify incident)."""
        generated = {
            "overview": "Spotify is a music streaming company that uses Kubernetes.",
            "challenge": "Spotify faced challenges scaling their microservices.",
            "solution": "Spotify implemented a cloud-native architecture.",
            "impact": "Spotify achieved significant improvements.",
        }
        video_data = {"title": "Intuit's Cloud Native Journey"}

        result = validate_company_consistency("Intuit", generated, video_data)

        assert result.status == Severity.CRITICAL
        assert result.is_critical()
        assert any(
            "mismatch" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_expected_company_not_mentioned_fails(self):
        """Test expected company not mentioned fails."""
        generated = {
            "overview": "This company uses Kubernetes for orchestration.",
            "challenge": "The organization faced scaling challenges.",
        }
        video_data = {"title": "Intuit's Journey"}

        result = validate_company_consistency("Intuit", generated, video_data)

        assert result.status == Severity.CRITICAL
        assert any(
            "not mentioned" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_other_companies_as_partners_warns(self):
        """Test mentioning other companies as partners/competitors produces warning."""
        generated = {
            "overview": "Intuit is a financial software company, competing with companies like TurboTax and H&R Block.",
            "challenge": "Intuit faced challenges similar to those at Microsoft and Google.",
            "solution": "Intuit implemented Kubernetes.",
            "impact": "Intuit achieved improvements.",
        }
        video_data = {"title": "Intuit's Journey"}

        result = validate_company_consistency("Intuit", generated, video_data)

        # Should warn about other companies but not fail critically
        # (Intuit is mentioned more than others)
        assert result.status in [Severity.WARNING, Severity.PASS]
        if result.status == Severity.WARNING:
            assert any(
                "other companies mentioned" in c.message.lower()
                for c in result.get_failed_checks()
                if c.message
            )


class TestValidationResult:
    """Tests for ValidationResult methods."""

    def test_is_critical_detects_critical_status(self):
        """Test is_critical() method."""
        from casestudypilot.validation import ValidationResult, ValidationCheck

        result = ValidationResult(
            status=Severity.CRITICAL,
            checks=[ValidationCheck("test", False, Severity.CRITICAL, "Failed")],
        )

        assert result.is_critical()

    def test_has_warnings_detects_warnings(self):
        """Test has_warnings() method."""
        from casestudypilot.validation import ValidationResult, ValidationCheck

        result = ValidationResult(
            status=Severity.WARNING,
            checks=[
                ValidationCheck("test1", True, Severity.INFO),
                ValidationCheck("test2", False, Severity.WARNING, "Warning"),
            ],
        )

        assert result.has_warnings()

    def test_get_failed_checks_returns_only_failures(self):
        """Test get_failed_checks() method."""
        from casestudypilot.validation import ValidationResult, ValidationCheck

        result = ValidationResult(
            status=Severity.WARNING,
            checks=[
                ValidationCheck("pass1", True, Severity.INFO),
                ValidationCheck("fail1", False, Severity.WARNING, "Warning"),
                ValidationCheck("pass2", True, Severity.INFO),
                ValidationCheck("fail2", False, Severity.CRITICAL, "Error"),
            ],
        )

        failed = result.get_failed_checks()
        assert len(failed) == 2
        assert all(not check.passed for check in failed)

    def test_to_dict_serialization(self):
        """Test to_dict() serialization."""
        from casestudypilot.validation import ValidationResult, ValidationCheck

        result = ValidationResult(
            status=Severity.PASS,
            checks=[
                ValidationCheck("test1", True, Severity.INFO, details={"count": 5}),
                ValidationCheck("test2", False, Severity.WARNING, "Warning message"),
            ],
        )

        data = result.to_dict()

        assert data["status"] == "PASS"
        assert len(data["checks"]) == 2
        assert data["checks"][0]["name"] == "test1"
        assert data["checks"][0]["passed"] is True
        assert data["checks"][0]["details"] == {"count": 5}
        assert data["checks"][1]["message"] == "Warning message"


class TestValidateCaseStudyFormat:
    """Tests for case study format validation (images and links)."""

    def test_relative_image_paths_pass(self):
        """Test case study with relative image paths passes."""
        content = """# Company Case Study

## Challenge

[![Screenshot](images/company/challenge.jpg)](https://www.youtube.com/watch?v=ABC123&t=109s)
*Challenge screenshot (1:49)*

## Solution

[![Screenshot](images/company/solution.jpg)](https://www.youtube.com/watch?v=ABC123&t=500s)
*Solution screenshot (8:20)*
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            result = validate_case_study_format(temp_path)

            assert result.status == Severity.PASS
            assert not result.is_critical()
            # Check that relative_image_paths check passed
            assert any(
                c.name == "relative_image_paths" and c.passed for c in result.checks
            )
        finally:
            os.unlink(temp_path)

    def test_absolute_image_paths_fail(self):
        """Test case study with absolute image paths fails critically."""
        content = """# Company Case Study

## Challenge

[![Screenshot](case-studies/images/company/challenge.jpg)](https://www.youtube.com/watch?v=ABC123&t=109s)
*Challenge screenshot (1:49)*
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            result = validate_case_study_format(temp_path)

            assert result.status == Severity.CRITICAL
            assert result.is_critical()
            # Check that relative_image_paths check failed
            failed = result.get_failed_checks()
            assert any(
                c.name == "relative_image_paths"
                and "absolute paths" in c.message.lower()
                for c in failed
                if c.message
            )
        finally:
            os.unlink(temp_path)

    def test_clickable_screenshot_links_pass(self):
        """Test case study with clickable screenshot links passes."""
        content = """# Company Case Study

## Challenge

[![Screenshot caption](images/company/challenge.jpg)](https://www.youtube.com/watch?v=ABC123&t=109s)
*Challenge screenshot (1:49)*
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            result = validate_case_study_format(temp_path)

            assert result.status == Severity.PASS
            # Check that clickable_screenshot_links check passed
            assert any(
                c.name == "clickable_screenshot_links" and c.passed
                for c in result.checks
            )
        finally:
            os.unlink(temp_path)

    def test_non_clickable_screenshots_fail(self):
        """Test case study with non-clickable screenshots fails critically."""
        content = """# Company Case Study

## Challenge

![Screenshot caption](images/company/challenge.jpg)
*Challenge screenshot*

Some text here.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            result = validate_case_study_format(temp_path)

            assert result.status == Severity.CRITICAL
            assert result.is_critical()
            # Check that clickable_screenshot_links check failed
            failed = result.get_failed_checks()
            assert any(
                c.name == "clickable_screenshot_links"
                and "non-clickable" in c.message.lower()
                for c in failed
                if c.message
            )
        finally:
            os.unlink(temp_path)

    def test_valid_timestamps_pass(self):
        """Test case study with valid timestamps passes."""
        content = """# Company Case Study

[![Screenshot 1](images/company/challenge.jpg)](https://www.youtube.com/watch?v=ABC123&t=0s)
[![Screenshot 2](images/company/solution.jpg)](https://www.youtube.com/watch?v=ABC123&t=100s)
[![Screenshot 3](images/company/impact.jpg)](https://www.youtube.com/watch?v=ABC123&t=999s)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            result = validate_case_study_format(temp_path)

            assert result.status == Severity.PASS
            # Check that valid_timestamps check passed
            assert any(c.name == "valid_timestamps" and c.passed for c in result.checks)
        finally:
            os.unlink(temp_path)

    def test_no_screenshots_passes(self):
        """Test case study without screenshots passes (acceptable)."""
        content = """# Company Case Study

## Challenge

The company faced many challenges with their infrastructure.

## Solution

They implemented cloud native technologies.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            result = validate_case_study_format(temp_path)

            assert result.status == Severity.PASS
            # Check that it handled no screenshots gracefully
            assert any(
                c.name == "clickable_screenshot_links"
                and "no screenshots" in c.message.lower()
                for c in result.checks
                if c.message
            )
        finally:
            os.unlink(temp_path)

    def test_missing_file_fails(self):
        """Test validation of non-existent file fails critically."""
        result = validate_case_study_format("/nonexistent/path/to/file.md")

        assert result.status == Severity.CRITICAL
        assert result.is_critical()
        assert any(
            c.name == "file_exists" and "not found" in c.message.lower()
            for c in result.get_failed_checks()
            if c.message
        )

    def test_combined_issues_multiple_failures(self):
        """Test case study with multiple format issues reports all failures."""
        content = """# Company Case Study

## Challenge

![Not clickable](case-studies/images/company/challenge.jpg)
*Should be clickable and relative*

## Solution

Some content here.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            result = validate_case_study_format(temp_path)

            assert result.status == Severity.CRITICAL
            failed = result.get_failed_checks()

            # Should have both failures
            assert len(failed) >= 2
            assert any(c.name == "relative_image_paths" for c in failed)
            assert any(c.name == "clickable_screenshot_links" for c in failed)
        finally:
            os.unlink(temp_path)
