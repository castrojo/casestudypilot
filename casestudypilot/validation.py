"""Validation framework for fail-fast error detection in case study generation.

This module provides comprehensive validation at critical decision points to prevent
hallucination and ensure data quality throughout the case study generation pipeline.
"""

import re
import logging
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from rapidfuzz import fuzz

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Validation severity levels."""

    CRITICAL = "CRITICAL"  # Stop workflow immediately
    WARNING = "WARNING"  # Continue with degraded quality
    INFO = "INFO"  # Informational only
    PASS = "PASS"  # All checks passed


@dataclass
class ValidationCheck:
    """Individual validation check result."""

    name: str
    passed: bool
    severity: Severity
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Aggregated validation result."""

    status: Severity  # Highest severity from all checks
    checks: List[ValidationCheck]

    def is_critical(self) -> bool:
        """Check if validation failed critically."""
        return self.status == Severity.CRITICAL

    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return any(c.severity == Severity.WARNING for c in self.checks)

    def get_failed_checks(self) -> List[ValidationCheck]:
        """Get all failed checks."""
        return [c for c in self.checks if not c.passed]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "severity": c.severity.value,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }


def validate_transcript(transcript: str, segments: List[Dict]) -> ValidationResult:
    """Validate transcript quality and completeness.

    Args:
        transcript: Full transcript text
        segments: List of transcript segments with timing info

    Returns:
        ValidationResult with CRITICAL, WARNING, or PASS status
    """
    checks = []

    # Check 1: Transcript exists
    checks.append(
        ValidationCheck(
            name="transcript_exists",
            passed=bool(transcript),
            severity=Severity.CRITICAL,
            message="Transcript is empty or None" if not transcript else None,
        )
    )

    # Check 2: Minimum length
    min_length = 1000
    transcript_length = len(transcript) if transcript else 0
    checks.append(
        ValidationCheck(
            name="minimum_length",
            passed=transcript_length >= min_length,
            severity=Severity.CRITICAL,
            message=f"Transcript too short: {transcript_length} chars (minimum: {min_length})"
            if transcript_length < min_length
            else None,
            details={"length": transcript_length, "minimum": min_length},
        )
    )

    # Check 3: Contains meaningful content (not just URLs/noise)
    word_count = len(transcript.split()) if transcript else 0
    checks.append(
        ValidationCheck(
            name="meaningful_content",
            passed=word_count >= 100,
            severity=Severity.CRITICAL,
            message=f"Transcript lacks meaningful content: only {word_count} words"
            if word_count < 100
            else None,
            details={"word_count": word_count},
        )
    )

    # Check 4: Sufficient segments
    segment_count = len(segments) if segments else 0
    checks.append(
        ValidationCheck(
            name="sufficient_segments",
            passed=segment_count >= 50,
            severity=Severity.CRITICAL,
            message=f"Too few transcript segments: {segment_count} (minimum: 50)"
            if segment_count < 50
            else None,
            details={"segment_count": segment_count},
        )
    )

    # Check 5: Warning for short transcript
    if transcript and len(transcript) < 5000:
        checks.append(
            ValidationCheck(
                name="short_transcript",
                passed=False,
                severity=Severity.WARNING,
                message=f"Short transcript ({len(transcript)} chars). Generated case study may lack detail.",
                details={"length": len(transcript)},
            )
        )

    # Determine overall status (highest severity that failed)
    status = Severity.PASS
    for check in checks:
        if not check.passed:
            if check.severity == Severity.CRITICAL:
                status = Severity.CRITICAL
                break
            elif check.severity == Severity.WARNING and status == Severity.PASS:
                status = Severity.WARNING

    return ValidationResult(status=status, checks=checks)


def validate_company_name(
    company_name: str, video_title: str, confidence: float = 1.0
) -> ValidationResult:
    """Validate extracted company name.

    Args:
        company_name: Extracted company name
        video_title: Original video title for context
        confidence: Confidence score (0.0-1.0)

    Returns:
        ValidationResult with CRITICAL, WARNING, or PASS status
    """
    checks = []

    # Check 1: Company name exists
    checks.append(
        ValidationCheck(
            name="company_exists",
            passed=bool(company_name and company_name.strip()),
            severity=Severity.CRITICAL,
            message="No company name provided" if not company_name else None,
        )
    )

    # Check 2: Not a generic placeholder
    generic_names = ["company", "organization", "tech", "unknown", "tbd", "n/a", "none"]
    is_generic = company_name.lower().strip() in generic_names if company_name else True
    checks.append(
        ValidationCheck(
            name="not_generic",
            passed=not is_generic,
            severity=Severity.CRITICAL,
            message=f"Company name is generic placeholder: '{company_name}'"
            if is_generic
            else None,
        )
    )

    # Check 3: Minimum length
    name_length = len(company_name) if company_name else 0
    checks.append(
        ValidationCheck(
            name="minimum_length",
            passed=name_length >= 2,
            severity=Severity.CRITICAL,
            message=f"Company name too short: '{company_name}' ({name_length} chars)"
            if name_length < 2
            else None,
        )
    )

    # Check 4: Confidence threshold
    if confidence < 0.5:
        severity = Severity.CRITICAL
    elif confidence < 0.7:
        severity = Severity.WARNING
    else:
        severity = Severity.INFO

    checks.append(
        ValidationCheck(
            name="confidence_threshold",
            passed=confidence >= 0.7,
            severity=severity,
            message=f"Low confidence in company extraction: {confidence:.2f}"
            if confidence < 0.7
            else None,
            details={"confidence": confidence},
        )
    )

    # Determine status
    status = Severity.PASS
    for check in checks:
        if not check.passed:
            if check.severity == Severity.CRITICAL and status != Severity.CRITICAL:
                status = Severity.CRITICAL
            elif check.severity == Severity.WARNING and status == Severity.PASS:
                status = Severity.WARNING

    return ValidationResult(status=status, checks=checks)


def validate_analysis(analysis: Dict[str, Any]) -> ValidationResult:
    """Validate transcript analysis output.

    Args:
        analysis: Analysis output with cncf_projects, key_metrics, sections

    Returns:
        ValidationResult with CRITICAL, WARNING, or PASS status
    """
    checks = []

    # Check 1: Required keys present
    required_keys = ["cncf_projects", "key_metrics", "sections"]
    missing_keys = [k for k in required_keys if k not in analysis]
    checks.append(
        ValidationCheck(
            name="required_keys",
            passed=len(missing_keys) == 0,
            severity=Severity.CRITICAL,
            message=f"Missing required keys: {missing_keys}" if missing_keys else None,
            details={"missing_keys": missing_keys},
        )
    )

    # Check 2: At least 1 CNCF project
    cncf_projects = analysis.get("cncf_projects", [])
    checks.append(
        ValidationCheck(
            name="has_cncf_projects",
            passed=len(cncf_projects) >= 1,
            severity=Severity.CRITICAL,
            message="No CNCF projects identified. Cannot generate case study without cloud-native technology mentions."
            if len(cncf_projects) == 0
            else None,
            details={"project_count": len(cncf_projects)},
        )
    )

    # Check 3: Warning for only 1 project
    if len(cncf_projects) == 1:
        project_name = (
            cncf_projects[0].get("name", "unknown")
            if isinstance(cncf_projects[0], dict)
            else cncf_projects[0]
        )
        checks.append(
            ValidationCheck(
                name="multiple_projects",
                passed=False,
                severity=Severity.WARNING,
                message=f"Only 1 CNCF project found: {project_name}. Case study may lack technical depth.",
                details={"project_count": 1},
            )
        )

    # Check 4: All sections present
    sections = analysis.get("sections", {})
    required_sections = ["background", "challenge", "solution", "impact"]
    missing_sections = [
        s for s in required_sections if s not in sections or not sections[s]
    ]
    checks.append(
        ValidationCheck(
            name="all_sections_present",
            passed=len(missing_sections) == 0,
            severity=Severity.CRITICAL,
            message=f"Missing required sections: {missing_sections}"
            if missing_sections
            else None,
            details={"missing_sections": missing_sections},
        )
    )

    # Check 5: Sections have minimum content
    for section_name in required_sections:
        if section_name in sections:
            section_content = sections[section_name]
            min_chars = 100
            section_length = len(section_content) if section_content else 0
            checks.append(
                ValidationCheck(
                    name=f"section_{section_name}_length",
                    passed=section_length >= min_chars,
                    severity=Severity.CRITICAL,
                    message=f"Section '{section_name}' too short: {section_length} chars (minimum: {min_chars})"
                    if section_length < min_chars
                    else None,
                    details={"section": section_name, "length": section_length},
                )
            )

    # Check 6: Warning if no metrics
    metrics = analysis.get("key_metrics", [])
    if len(metrics) == 0:
        checks.append(
            ValidationCheck(
                name="has_metrics",
                passed=False,
                severity=Severity.WARNING,
                message="No quantitative metrics found. Case study will lack measurable impact data.",
                details={"metric_count": 0},
            )
        )

    # Determine status
    status = Severity.PASS
    for check in checks:
        if not check.passed:
            if check.severity == Severity.CRITICAL:
                status = Severity.CRITICAL
                break
            elif check.severity == Severity.WARNING and status == Severity.PASS:
                status = Severity.WARNING

    return ValidationResult(status=status, checks=checks)


def validate_metrics(
    generated_sections: Dict[str, Any],
    original_transcript: str,
    analysis: Dict[str, Any],
) -> ValidationResult:
    """Detect if metrics in generated case study exist in original transcript.

    Args:
        generated_sections: Generated case study sections
        original_transcript: Original video transcript
        analysis: Transcript analysis with extracted metrics

    Returns:
        ValidationResult with WARNING if fabricated metrics detected
    """
    checks = []

    # Extract all numbers/metrics from generated content
    all_generated_text = " ".join(str(v) for v in generated_sections.values())

    # Patterns for metrics: percentages, numbers with units, time expressions
    metric_patterns = [
        r"\d+%",  # 50%
        r"\d+x",  # 3x
        r"\d+[,\d]*\s+(?:pods?|services?|nodes?|clusters?|users?|requests?|microservices?)",  # 10,000 pods
        r"\d+\s+(?:hours?|minutes?|seconds?|days?|weeks?|months?)",  # 2 hours
        r"\$\d+[,\d]*",  # $100,000
    ]

    found_metrics = []
    for pattern in metric_patterns:
        found_metrics.extend(re.findall(pattern, all_generated_text, re.IGNORECASE))

    # Check each metric against original transcript
    fabricated_metrics = []
    for metric in found_metrics:
        # Use fuzzy matching to allow for rephrasing
        # e.g., "50%" might appear as "50 percent" in transcript
        if metric not in original_transcript:
            # Try fuzzy match
            metric_normalized = metric.replace(",", "").replace("$", "")
            # Split transcript into chunks for fuzzy matching
            transcript_chunks = original_transcript.split()
            if not any(
                fuzz.partial_ratio(metric_normalized, chunk) > 85
                for chunk in transcript_chunks
            ):
                fabricated_metrics.append(metric)

    if fabricated_metrics:
        # Limit to first 5 for readability
        displayed_metrics = fabricated_metrics[:5]
        more_count = len(fabricated_metrics) - 5
        message = f"Found {len(fabricated_metrics)} metric(s) in case study that don't appear in transcript: {displayed_metrics}"
        if more_count > 0:
            message += f" (and {more_count} more)"
        message += ". Review for accuracy."

        checks.append(
            ValidationCheck(
                name="metrics_in_transcript",
                passed=False,
                severity=Severity.WARNING,
                message=message,
                details={"fabricated_metrics": fabricated_metrics},
            )
        )
    else:
        checks.append(
            ValidationCheck(
                name="metrics_in_transcript",
                passed=True,
                severity=Severity.INFO,
                message="All metrics verified against transcript",
            )
        )

    status = Severity.WARNING if fabricated_metrics else Severity.PASS
    return ValidationResult(status=status, checks=checks)


def validate_case_study_format(case_study_path: str) -> ValidationResult:
    """Validate case study markdown formatting and links.

    Args:
        case_study_path: Path to generated case study markdown file

    Returns:
        ValidationResult with CRITICAL if formatting issues detected
    """
    checks = []

    # Read the case study file
    try:
        with open(case_study_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        checks.append(
            ValidationCheck(
                name="file_exists",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Case study file not found: {case_study_path}",
            )
        )
        return ValidationResult(status=Severity.CRITICAL, checks=checks)

    checks.append(
        ValidationCheck(
            name="file_exists",
            passed=True,
            severity=Severity.INFO,
            message="Case study file exists",
        )
    )

    # Check 1: Image paths must be relative (not absolute from repo root)
    # Pattern: ![...](<path>) where path starts with "case-studies/"
    absolute_image_pattern = r"!\[.*?\]\(case-studies/images/"
    absolute_images = re.findall(absolute_image_pattern, content)

    if absolute_images:
        checks.append(
            ValidationCheck(
                name="relative_image_paths",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Found {len(absolute_images)} image(s) with absolute paths (case-studies/images/...). "
                "Images must use relative paths (images/...) from case-studies/ directory.",
                details={"absolute_paths_found": len(absolute_images)},
            )
        )
    else:
        checks.append(
            ValidationCheck(
                name="relative_image_paths",
                passed=True,
                severity=Severity.INFO,
                message="All image paths are relative",
            )
        )

    # Check 2: Screenshots must be clickable links to video timestamps
    # Pattern: [![...](images/...)](video_url&t=XXXs)
    clickable_screenshot_pattern = (
        r"\[!\[.*?\]\(images/.*?\)\]\(https://www\.youtube\.com/watch\?v=.*?&t=\d+s\)"
    )
    clickable_screenshots = re.findall(clickable_screenshot_pattern, content)

    # Also check for non-clickable images in case-studies/ (screenshots)
    # Pattern matches: ![...](images/...) or ![...](case-studies/images/...)
    # But NOT [![...](images/...)](link) (which are clickable)
    all_image_lines = []
    for line in content.split("\n"):
        # Match lines with images but filter out clickable ones
        if re.search(r"!\[.*?\]\((case-studies/)?images/", line):
            # Skip if it's a clickable link
            if not re.search(
                r"\[!\[.*?\]\((case-studies/)?images/.*?\)\]\(https?://", line
            ):
                all_image_lines.append(line.strip())

    if all_image_lines:
        checks.append(
            ValidationCheck(
                name="clickable_screenshot_links",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Found {len(all_image_lines)} non-clickable screenshot(s). "
                "Screenshots must be wrapped in clickable links to video timestamps: [![...](image)](video&t=XXs)",
                details={"non_clickable_count": len(all_image_lines)},
            )
        )
    elif clickable_screenshots:
        checks.append(
            ValidationCheck(
                name="clickable_screenshot_links",
                passed=True,
                severity=Severity.INFO,
                message=f"All {len(clickable_screenshots)} screenshot(s) are clickable links to video timestamps",
                details={"clickable_count": len(clickable_screenshots)},
            )
        )
    else:
        # No screenshots found - this is OK if screenshots weren't generated
        checks.append(
            ValidationCheck(
                name="clickable_screenshot_links",
                passed=True,
                severity=Severity.INFO,
                message="No screenshots found in case study",
            )
        )

    # Check 3: Timestamp format validation (if clickable links exist)
    if clickable_screenshots:
        # Extract all timestamp values
        timestamp_pattern = r"&t=(\d+)s"
        timestamps = [int(t) for t in re.findall(timestamp_pattern, content)]

        if all(t >= 0 for t in timestamps):
            checks.append(
                ValidationCheck(
                    name="valid_timestamps",
                    passed=True,
                    severity=Severity.INFO,
                    message=f"All {len(timestamps)} timestamp(s) are valid",
                    details={"timestamps": timestamps},
                )
            )
        else:
            invalid = [t for t in timestamps if t < 0]
            checks.append(
                ValidationCheck(
                    name="valid_timestamps",
                    passed=False,
                    severity=Severity.CRITICAL,
                    message=f"Found {len(invalid)} invalid timestamp(s): {invalid}",
                    details={"invalid_timestamps": invalid},
                )
            )

    # Determine overall status
    status = Severity.PASS
    for check in checks:
        if not check.passed:
            if check.severity == Severity.CRITICAL:
                status = Severity.CRITICAL
                break
            elif check.severity == Severity.WARNING and status == Severity.PASS:
                status = Severity.WARNING

    return ValidationResult(status=status, checks=checks)


def validate_company_consistency(
    expected_company: str,
    generated_sections: Dict[str, Any],
    video_data: Dict[str, Any],
) -> ValidationResult:
    """Detect if generated case study is about the wrong company.

    This prevents the "Spotify hallucination" bug where the agent generates
    a case study about the wrong company due to empty/bad transcript data.

    Args:
        expected_company: Expected company name from extraction
        generated_sections: Generated case study sections
        video_data: Original video metadata

    Returns:
        ValidationResult with CRITICAL if company mismatch detected
    """
    checks = []

    all_generated_text = " ".join(str(v) for v in generated_sections.values())

    # Common company names to check against (expand as needed)
    known_companies = [
        "Spotify",
        "Netflix",
        "Uber",
        "Airbnb",
        "Adobe",
        "Apple",
        "Google",
        "Microsoft",
        "Amazon",
        "Facebook",
        "Meta",
        "Twitter",
        "LinkedIn",
        "Slack",
        "Dropbox",
        "GitHub",
        "GitLab",
        "Atlassian",
        "Salesforce",
        "Oracle",
        "IBM",
        "Red Hat",
        "Intel",
        "Nvidia",
        "Tesla",
        "Intuit",
        "PayPal",
        "eBay",
        "Etsy",
        "Lyft",
        "DoorDash",
        "Stripe",
        "Square",
        "Shopify",
    ]

    # Check if expected company is mentioned
    expected_mentioned = expected_company.lower() in all_generated_text.lower()
    checks.append(
        ValidationCheck(
            name="expected_company_mentioned",
            passed=expected_mentioned,
            severity=Severity.CRITICAL,
            message=f"Expected company '{expected_company}' not mentioned in generated case study!"
            if not expected_mentioned
            else None,
        )
    )

    # Check for mentions of other major companies
    other_companies_mentioned = [
        company
        for company in known_companies
        if company.lower() != expected_company.lower()
        and company.lower() in all_generated_text.lower()
    ]

    if other_companies_mentioned:
        # Count mentions to determine if it's primary subject
        mention_counts = {
            company: all_generated_text.lower().count(company.lower())
            for company in other_companies_mentioned
        }

        most_mentioned = max(mention_counts.values()) if mention_counts else 0
        expected_mentions = all_generated_text.lower().count(expected_company.lower())

        # CRITICAL if another company mentioned more than expected
        if most_mentioned > expected_mentions:
            top_company = max(mention_counts.items(), key=lambda x: x[1])[0]
            checks.append(
                ValidationCheck(
                    name="company_mismatch",
                    passed=False,
                    severity=Severity.CRITICAL,
                    message=f"Company mismatch! Expected '{expected_company}' ({expected_mentions} mentions) but case study appears to be about '{top_company}' ({most_mentioned} mentions). STOPPING to prevent incorrect attribution.",
                    details={
                        "expected": expected_company,
                        "expected_mentions": expected_mentions,
                        "other_companies": mention_counts,
                    },
                )
            )
        else:
            # Just a warning if other companies mentioned less frequently (likely partners/competitors)
            checks.append(
                ValidationCheck(
                    name="other_companies_mentioned",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"Other companies mentioned: {list(mention_counts.keys())}. Verify they are partners/competitors, not primary subject.",
                    details={"other_companies": mention_counts},
                )
            )

    # Determine status
    status = Severity.PASS
    for check in checks:
        if not check.passed:
            if check.severity == Severity.CRITICAL:
                status = Severity.CRITICAL
                break
            elif check.severity == Severity.WARNING and status == Severity.PASS:
                status = Severity.WARNING

    return ValidationResult(status=status, checks=checks)
