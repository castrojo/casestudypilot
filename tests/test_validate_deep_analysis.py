"""Unit tests for validate_deep_analysis tool."""

import pytest
import json
import tempfile
from pathlib import Path
from casestudypilot.tools.validate_deep_analysis import validate_deep_analysis, main


class TestValidateDeepAnalysis:
    """Tests for deep analysis validation."""

    @pytest.fixture
    def valid_deep_analysis(self):
        """Fixture providing a valid deep analysis structure."""
        return {
            "cncf_projects": [
                {"name": "Kubernetes", "usage_context": "container orchestration"},
                {"name": "Prometheus", "usage_context": "monitoring"},
                {"name": "Envoy", "usage_context": "service mesh"},
                {"name": "Helm", "usage_context": "package management"},
                {"name": "etcd", "usage_context": "distributed key-value store"},
            ],
            "architecture_components": {
                "infrastructure_layer": [{"component": "Kubernetes Cluster", "description": "Core platform"}],
                "platform_layer": [{"component": "Prometheus", "description": "Metrics collection"}],
                "application_layer": [{"component": "Microservices", "description": "Business logic"}],
            },
            "integration_patterns": [
                {"pattern": "Service Mesh", "description": "Envoy-based communication"},
                {"pattern": "GitOps", "description": "Automated deployments"},
            ],
            "technical_metrics": [
                {
                    "metric": "Deployment time",
                    "value": "2 minutes",
                    "transcript_quote": "We reduced deployment time from 30 minutes to 2 minutes",
                }
            ],
            "screenshot_opportunities": [
                {"timestamp": "1:23", "description": "Architecture diagram"},
                {"timestamp": "2:45", "description": "Dashboard view"},
                {"timestamp": "3:12", "description": "Deployment pipeline"},
                {"timestamp": "4:30", "description": "Monitoring graphs"},
                {"timestamp": "5:00", "description": "Service mesh topology"},
                {"timestamp": "6:15", "description": "Performance metrics"},
            ],
            "sections": {
                "background": " ".join(["word"] * 300),  # 300 words
                "technical_challenge": " ".join(["word"] * 300),
                "architecture_overview": " ".join(["word"] * 300),
                "implementation_details": " ".join(["word"] * 300),
                "results_and_impact": " ".join(["word"] * 300),
                "lessons_learned": " ".join(["word"] * 300),
            },
        }

    def test_file_not_found_returns_error(self):
        """Test that missing file returns exit code 2."""
        exit_code = main("/nonexistent/file.json")
        assert exit_code == 2

    def test_valid_deep_analysis_passes(self, valid_deep_analysis):
        """Test that valid deep analysis returns exit code 0."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 0
            assert "Validation passed" in message
        finally:
            Path(temp_path).unlink()

    def test_invalid_json_fails(self):
        """Test that invalid JSON returns exit code 2."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 2
            assert "Invalid JSON" in message
        finally:
            Path(temp_path).unlink()

    def test_less_than_4_projects_fails(self, valid_deep_analysis):
        """Test that less than 4 CNCF projects returns exit code 2."""
        valid_deep_analysis["cncf_projects"] = valid_deep_analysis["cncf_projects"][:3]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 2
            assert "Less than 4 CNCF projects" in message
        finally:
            Path(temp_path).unlink()

    def test_exactly_4_projects_warns(self, valid_deep_analysis):
        """Test that exactly 4 CNCF projects returns exit code 1."""
        valid_deep_analysis["cncf_projects"] = valid_deep_analysis["cncf_projects"][:4]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 1
            assert "4 CNCF projects" in message
            assert "5 recommended" in message
        finally:
            Path(temp_path).unlink()

    def test_missing_infrastructure_layer_fails(self, valid_deep_analysis):
        """Test that missing infrastructure layer returns exit code 2."""
        del valid_deep_analysis["architecture_components"]["infrastructure_layer"]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 2
            assert "infrastructure_layer" in message
        finally:
            Path(temp_path).unlink()

    def test_empty_platform_layer_fails(self, valid_deep_analysis):
        """Test that empty platform layer returns exit code 2."""
        valid_deep_analysis["architecture_components"]["platform_layer"] = []

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 2
            assert "platform_layer" in message
            assert "empty" in message
        finally:
            Path(temp_path).unlink()

    def test_no_integration_patterns_fails(self, valid_deep_analysis):
        """Test that no integration patterns returns exit code 2."""
        valid_deep_analysis["integration_patterns"] = []

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 2
            assert "No integration patterns" in message
        finally:
            Path(temp_path).unlink()

    def test_one_integration_pattern_warns(self, valid_deep_analysis):
        """Test that only 1 integration pattern returns exit code 1."""
        valid_deep_analysis["integration_patterns"] = [valid_deep_analysis["integration_patterns"][0]]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 1
            assert "Only 1 integration pattern" in message
        finally:
            Path(temp_path).unlink()

    def test_metric_without_transcript_quote_fails(self, valid_deep_analysis):
        """Test that metric without transcript_quote returns exit code 2."""
        valid_deep_analysis["technical_metrics"][0] = {
            "metric": "Deployment time",
            "value": "2 minutes",
            # Missing transcript_quote
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 2
            assert "missing 'transcript_quote'" in message
        finally:
            Path(temp_path).unlink()

    def test_metric_with_empty_transcript_quote_fails(self, valid_deep_analysis):
        """Test that metric with empty transcript_quote returns exit code 2."""
        valid_deep_analysis["technical_metrics"][0]["transcript_quote"] = ""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 2
            assert "empty or too-short transcript quote" in message
        finally:
            Path(temp_path).unlink()

    def test_less_than_4_screenshots_fails(self, valid_deep_analysis):
        """Test that less than 4 screenshots returns exit code 2."""
        valid_deep_analysis["screenshot_opportunities"] = [
            {"timestamp": "1:23", "description": "Architecture diagram"},
            {"timestamp": "2:45", "description": "Dashboard view"},
            {"timestamp": "3:12", "description": "Deployment pipeline"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 2
            assert "Less than 4 screenshot opportunities" in message
        finally:
            Path(temp_path).unlink()

    def test_5_screenshots_warns(self, valid_deep_analysis):
        """Test that 5 screenshots returns exit code 1."""
        valid_deep_analysis["screenshot_opportunities"] = valid_deep_analysis["screenshot_opportunities"][:5]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 1
            assert "5 screenshot opportunities" in message
            assert "6 recommended" in message
        finally:
            Path(temp_path).unlink()

    def test_missing_section_fails(self, valid_deep_analysis):
        """Test that missing required section returns exit code 2."""
        del valid_deep_analysis["sections"]["technical_challenge"]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 2
            assert "Missing section 'technical_challenge'" in message
        finally:
            Path(temp_path).unlink()

    def test_section_too_short_warns(self, valid_deep_analysis):
        """Test that section with < 200 words returns exit code 1."""
        valid_deep_analysis["sections"]["background"] = " ".join(["word"] * 150)  # 150 words

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 1
            assert "background" in message
            assert "150 words" in message
            assert "200-800 recommended" in message
        finally:
            Path(temp_path).unlink()

    def test_section_too_long_warns(self, valid_deep_analysis):
        """Test that section with > 800 words returns exit code 1."""
        valid_deep_analysis["sections"]["implementation_details"] = " ".join(["word"] * 900)  # 900 words

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_deep_analysis, f)
            temp_path = f.name

        try:
            exit_code, message = validate_deep_analysis(Path(temp_path))
            assert exit_code == 1
            assert "implementation_details" in message
            assert "900 words" in message
            assert "200-800 recommended" in message
        finally:
            Path(temp_path).unlink()
