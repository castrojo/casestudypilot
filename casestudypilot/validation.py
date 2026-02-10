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
            message=f"Transcript lacks meaningful content: only {word_count} words" if word_count < 100 else None,
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
            message=f"Too few transcript segments: {segment_count} (minimum: 50)" if segment_count < 50 else None,
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


def validate_company_name(company_name: str, video_title: str, confidence: float = 1.0) -> ValidationResult:
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
            message=f"Company name is generic placeholder: '{company_name}'" if is_generic else None,
        )
    )

    # Check 3: Minimum length
    name_length = len(company_name) if company_name else 0
    checks.append(
        ValidationCheck(
            name="minimum_length",
            passed=name_length >= 2,
            severity=Severity.CRITICAL,
            message=f"Company name too short: '{company_name}' ({name_length} chars)" if name_length < 2 else None,
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
            message=f"Low confidence in company extraction: {confidence:.2f}" if confidence < 0.7 else None,
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
            cncf_projects[0].get("name", "unknown") if isinstance(cncf_projects[0], dict) else cncf_projects[0]
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
    missing_sections = [s for s in required_sections if s not in sections or not sections[s]]
    checks.append(
        ValidationCheck(
            name="all_sections_present",
            passed=len(missing_sections) == 0,
            severity=Severity.CRITICAL,
            message=f"Missing required sections: {missing_sections}" if missing_sections else None,
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
            if not any(fuzz.partial_ratio(metric_normalized, chunk) > 85 for chunk in transcript_chunks):
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
    clickable_screenshot_pattern = r"\[!\[.*?\]\(images/.*?\)\]\(https://www\.youtube\.com/watch\?v=.*?&t=\d+s\)"
    clickable_screenshots = re.findall(clickable_screenshot_pattern, content)

    # Also check for non-clickable images in case-studies/ (screenshots)
    # Pattern matches: ![...](images/...) or ![...](case-studies/images/...)
    # But NOT [![...](images/...)](link) (which are clickable)
    all_image_lines = []
    for line in content.split("\n"):
        # Match lines with images but filter out clickable ones
        if re.search(r"!\[.*?\]\((case-studies/)?images/", line):
            # Skip if it's a clickable link
            if not re.search(r"\[!\[.*?\]\((case-studies/)?images/.*?\)\]\(https?://", line):
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
    # Use word boundary matching to avoid false positives like "uber" in "kubernetes"
    other_companies_mentioned = []
    for company in known_companies:
        if company.lower() == expected_company.lower():
            continue
        # Use word boundary regex to match whole words only
        pattern = r"\b" + re.escape(company.lower()) + r"\b"
        if re.search(pattern, all_generated_text.lower()):
            other_companies_mentioned.append(company)

    if other_companies_mentioned:
        # Count mentions to determine if it's primary subject
        mention_counts = {}
        for company in other_companies_mentioned:
            pattern = r"\b" + re.escape(company.lower()) + r"\b"
            mention_counts[company] = len(re.findall(pattern, all_generated_text.lower()))

        most_mentioned = max(mention_counts.values()) if mention_counts else 0
        # Use word boundary for expected company count too
        expected_pattern = r"\b" + re.escape(expected_company.lower()) + r"\b"
        expected_mentions = len(re.findall(expected_pattern, all_generated_text.lower()))

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


# =============================================================================
# Presenter Profile Validation Functions
# =============================================================================


def validate_presenter(presenter_name: str, videos_data: Dict[str, Any]) -> ValidationResult:
    """Validate presenter name appears consistently across videos.

    Args:
        presenter_name: Expected presenter name
        videos_data: Multi-video data dict from fetch_multi_video_data

    Returns:
        ValidationResult with CRITICAL, WARNING, or PASS status
    """
    checks = []
    videos = videos_data.get("videos", [])
    successful_videos = [v for v in videos if v.get("success", False)]

    # Check 1: Presenter name exists
    checks.append(
        ValidationCheck(
            name="presenter_exists",
            passed=bool(presenter_name and presenter_name.strip()),
            severity=Severity.CRITICAL,
            message="No presenter name provided" if not presenter_name else None,
        )
    )

    # Check 2: Not generic
    generic_names = ["presenter", "speaker", "person", "user", "unknown", "tbd", "n/a"]
    is_generic = presenter_name.lower().strip() in generic_names if presenter_name else True
    checks.append(
        ValidationCheck(
            name="not_generic",
            passed=not is_generic,
            severity=Severity.CRITICAL,
            message=f"Presenter name is generic placeholder: '{presenter_name}'" if is_generic else None,
        )
    )

    # Check 3: At least 2 successful videos
    checks.append(
        ValidationCheck(
            name="minimum_videos",
            passed=len(successful_videos) >= 2,
            severity=Severity.CRITICAL,
            message=f"Need at least 2 successful videos for profile, got {len(successful_videos)}",
            details={"successful_count": len(successful_videos), "total_count": len(videos)},
        )
    )

    if not successful_videos:
        # Can't do further checks without videos
        status = Severity.CRITICAL
        return ValidationResult(status=status, checks=checks)

    # Check 4: Name appears in videos
    name_lower = presenter_name.lower()
    name_parts = name_lower.split()
    matches = 0

    for video in successful_videos:
        title = video.get("title", "").lower()
        description = video.get("description", "").lower()
        transcript = video.get("transcript", "").lower()

        # Check if full name or name parts appear
        full_name_match = name_lower in title or name_lower in description or name_lower in transcript
        partial_match = any(
            part in title or part in description or part in transcript for part in name_parts if len(part) > 2
        )

        if full_name_match or partial_match:
            matches += 1

    match_rate = matches / len(successful_videos)
    checks.append(
        ValidationCheck(
            name="name_in_videos",
            passed=match_rate >= 0.5,
            severity=Severity.CRITICAL if match_rate < 0.5 else Severity.WARNING if match_rate < 0.8 else Severity.PASS,
            message=f"Presenter name found in {matches}/{len(successful_videos)} videos ({match_rate:.0%}). Expected ≥50%."
            if match_rate < 0.5
            else f"Presenter name only found in {matches}/{len(successful_videos)} videos ({match_rate:.0%}). Verify identity."
            if match_rate < 0.8
            else None,
            details={"matches": matches, "total": len(successful_videos), "match_rate": match_rate},
        )
    )

    # Check 5: Detect conflicting names (fuzzy matching)
    detected_names = set()
    for video in successful_videos:
        title = video.get("title", "")
        description = video.get("description", "")

        # Look for patterns like "Speaker: Name" or "by Name"
        patterns = [
            r"(?:speaker|presenter|by):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"with\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, title + " " + description):
                name = match.group(1).strip()
                if len(name) > 5:  # Minimum reasonable name length
                    detected_names.add(name)

    # Check for conflicting names
    conflicts = []
    for detected in detected_names:
        similarity = fuzz.ratio(presenter_name.lower(), detected.lower())
        if similarity < 60:  # Less than 60% similar = likely different person
            conflicts.append(detected)

    if conflicts:
        checks.append(
            ValidationCheck(
                name="no_conflicting_names",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Detected conflicting presenter names: {conflicts}. Verify all videos are from same person.",
                details={"conflicts": conflicts, "expected": presenter_name},
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


def validate_biography(biography_data: Dict[str, Any]) -> ValidationResult:
    """Validate biography quality and completeness.

    Args:
        biography_data: Biography dict with name, bio, location, etc.

    Returns:
        ValidationResult with CRITICAL, WARNING, or PASS status
    """
    checks = []

    # Check 1: Required fields present
    required_fields = ["full_name", "biography"]
    missing_fields = [f for f in required_fields if not biography_data.get(f)]
    checks.append(
        ValidationCheck(
            name="required_fields",
            passed=len(missing_fields) == 0,
            severity=Severity.CRITICAL,
            message=f"Missing required biography fields: {missing_fields}" if missing_fields else None,
            details={"missing_fields": missing_fields},
        )
    )

    # Check 2: Full name not generic/placeholder
    full_name = biography_data.get("full_name", "")
    placeholder_patterns = [
        r"^(first|last|full)\s*name$",
        r"^name\s*(here|tbd)?$",
        r"^(presenter|speaker|user)$",
        r"lorem ipsum",
        r"todo|tbd|n/a",
    ]
    is_placeholder = any(re.search(pattern, full_name.lower()) for pattern in placeholder_patterns)
    checks.append(
        ValidationCheck(
            name="no_placeholder_name",
            passed=not is_placeholder and len(full_name) > 0,
            severity=Severity.CRITICAL,
            message=f"Name appears to be placeholder: '{full_name}'" if is_placeholder or not full_name else None,
        )
    )

    # Check 3: Biography minimum length
    biography = biography_data.get("biography", "")
    bio_length = len(biography)
    checks.append(
        ValidationCheck(
            name="minimum_biography_length",
            passed=bio_length >= 100,
            severity=Severity.CRITICAL,
            message=f"Biography too short: {bio_length} chars (minimum: 100)" if bio_length < 100 else None,
            details={"length": bio_length, "minimum": 100},
        )
    )

    # Check 4: Biography not placeholder text
    bio_lower = biography.lower()
    bio_placeholder_patterns = [
        "lorem ipsum",
        "placeholder",
        "todo",
        "tbd",
        "fill in",
        "add bio here",
    ]
    has_placeholder = any(pattern in bio_lower for pattern in bio_placeholder_patterns)
    checks.append(
        ValidationCheck(
            name="no_placeholder_bio",
            passed=not has_placeholder,
            severity=Severity.CRITICAL,
            message="Biography contains placeholder text" if has_placeholder else None,
        )
    )

    # Check 5: Biography quality (warning for short but acceptable)
    if 100 <= bio_length < 300:
        checks.append(
            ValidationCheck(
                name="biography_quality",
                passed=False,
                severity=Severity.WARNING,
                message=f"Biography is short ({bio_length} chars). Recommend ≥300 chars for quality profile.",
                details={"length": bio_length, "recommended": 300},
            )
        )

    # Check 6: Optional fields present (warnings)
    optional_fields = ["location", "current_role", "github_username"]
    missing_optional = [f for f in optional_fields if not biography_data.get(f)]
    if missing_optional:
        checks.append(
            ValidationCheck(
                name="optional_fields",
                passed=False,
                severity=Severity.WARNING,
                message=f"Missing optional fields that improve profile quality: {missing_optional}",
                details={"missing_optional": missing_optional},
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


def validate_profile_update(
    existing_profile: Dict[str, Any],
    new_videos_data: Dict[str, Any],
) -> ValidationResult:
    """Validate profile update for conflicts.

    Args:
        existing_profile: Existing profile metadata JSON
        new_videos_data: New videos data from fetch_multi_video_data

    Returns:
        ValidationResult with CRITICAL, WARNING, or PASS status
    """
    checks = []

    new_videos = [v for v in new_videos_data.get("videos", []) if v.get("success", False)]

    # Check 1: At least 1 new successful video
    checks.append(
        ValidationCheck(
            name="has_new_videos",
            passed=len(new_videos) >= 1,
            severity=Severity.CRITICAL,
            message=f"No successful new videos to add (got {len(new_videos)})",
            details={"new_video_count": len(new_videos)},
        )
    )

    if not new_videos:
        status = Severity.CRITICAL
        return ValidationResult(status=status, checks=checks)

    # Check 2: Presenter name matches
    existing_name = existing_profile.get("name", "")
    github_username = existing_profile.get("github_username", "")

    # Check if presenter name appears in new videos
    name_lower = existing_name.lower()
    name_matches = 0

    for video in new_videos:
        title = video.get("title", "").lower()
        description = video.get("description", "").lower()
        transcript = video.get("transcript", "").lower()

        if name_lower in title or name_lower in description or name_lower in transcript:
            name_matches += 1

    match_rate = name_matches / len(new_videos) if new_videos else 0
    checks.append(
        ValidationCheck(
            name="name_consistency",
            passed=match_rate >= 0.3,
            severity=Severity.CRITICAL if match_rate == 0 else Severity.WARNING,
            message=f"Presenter name '{existing_name}' not found in any new videos. Wrong person?"
            if match_rate == 0
            else f"Presenter name only found in {name_matches}/{len(new_videos)} new videos ({match_rate:.0%}). Verify identity."
            if match_rate < 0.5
            else None,
            details={"matches": name_matches, "total": len(new_videos), "match_rate": match_rate},
        )
    )

    # Check 3: No duplicate video IDs
    existing_video_ids = set(existing_profile.get("video_ids_processed", []))
    new_video_ids = {v.get("video_id") for v in new_videos}
    duplicates = existing_video_ids & new_video_ids

    if duplicates:
        checks.append(
            ValidationCheck(
                name="no_duplicates",
                passed=False,
                severity=Severity.WARNING,
                message=f"Found {len(duplicates)} video(s) already in profile: {list(duplicates)[:3]}",
                details={"duplicate_count": len(duplicates), "duplicates": list(duplicates)},
            )
        )

    # Check 4: Expertise consistency (warning only)
    existing_areas = {area.get("area") for area in existing_profile.get("expertise_areas", [])}
    # We can't fully check without running analysis, so just warn if we have data
    if existing_areas:
        checks.append(
            ValidationCheck(
                name="expertise_consistency",
                passed=True,
                severity=Severity.INFO,
                message=f"Existing expertise areas: {list(existing_areas)}. Verify new videos are consistent.",
                details={"existing_areas": list(existing_areas)},
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


def validate_presenter_profile(profile_data: Dict[str, Any], threshold: float = 0.60) -> ValidationResult:
    """Validate presenter profile quality with multi-factor scoring.

    Args:
        profile_data: Complete profile data dict
        threshold: Minimum quality score (0.0-1.0)

    Returns:
        ValidationResult with CRITICAL, WARNING, or PASS status
    """
    checks = []

    # Factor 1: Structure completeness (0.2 weight)
    required_sections = [
        "overview",
        "expertise",
        "talk_highlights",
        "key_themes",
        "stats_table",
    ]
    present_sections = sum(1 for s in required_sections if profile_data.get(s))
    structure_score = present_sections / len(required_sections)

    checks.append(
        ValidationCheck(
            name="structure_completeness",
            passed=structure_score >= 0.8,
            severity=Severity.CRITICAL if structure_score < 0.6 else Severity.WARNING,
            message=f"Missing required sections. Only {present_sections}/{len(required_sections)} present."
            if structure_score < 0.8
            else None,
            details={"score": structure_score, "present": present_sections, "required": len(required_sections)},
        )
    )

    # Factor 2: Biography depth (0.2 weight)
    biography = profile_data.get("biography", "")
    bio_length = len(biography)
    bio_score = min(bio_length / 500, 1.0)  # 500 chars = full score

    checks.append(
        ValidationCheck(
            name="biography_depth",
            passed=bio_length >= 300,
            severity=Severity.CRITICAL if bio_length < 100 else Severity.WARNING,
            message=f"Biography too short: {bio_length} chars (minimum: 300 for quality)" if bio_length < 300 else None,
            details={"length": bio_length, "score": bio_score},
        )
    )

    # Factor 3: Talk coverage (0.2 weight)
    talk_summaries = profile_data.get("talk_summaries", [])
    talk_count = len(talk_summaries)
    talk_score = min(talk_count / 5, 1.0)  # 5 talks = full score

    checks.append(
        ValidationCheck(
            name="talk_coverage",
            passed=talk_count >= 2,
            severity=Severity.CRITICAL if talk_count < 2 else Severity.WARNING,
            message=f"Too few talks analyzed: {talk_count} (minimum: 2)" if talk_count < 2 else None,
            details={"count": talk_count, "score": talk_score},
        )
    )

    # Factor 4: Expertise identification (0.2 weight)
    expertise_areas = profile_data.get("expertise_areas", [])
    cncf_projects = profile_data.get("cncf_projects", [])
    expertise_score = min((len(expertise_areas) + len(cncf_projects)) / 5, 1.0)  # 5 items = full score

    checks.append(
        ValidationCheck(
            name="expertise_identification",
            passed=len(cncf_projects) >= 1,
            severity=Severity.CRITICAL if len(cncf_projects) == 0 else Severity.WARNING,
            message=f"No CNCF projects identified. Cannot create meaningful presenter profile."
            if len(cncf_projects) == 0
            else f"Limited expertise data: {len(expertise_areas)} areas, {len(cncf_projects)} projects"
            if len(expertise_areas) + len(cncf_projects) < 3
            else None,
            details={
                "expertise_count": len(expertise_areas),
                "project_count": len(cncf_projects),
                "score": expertise_score,
            },
        )
    )

    # Factor 5: Factual consistency (0.2 weight)
    # Check for placeholder patterns and consistency
    content_parts = [
        str(profile_data.get("overview", "")),
        str(profile_data.get("expertise", "")),
        str(profile_data.get("key_themes", "")),
    ]
    combined_content = " ".join(content_parts).lower()

    placeholder_patterns = ["lorem ipsum", "placeholder", "todo", "tbd", "fill in"]
    has_placeholders = any(p in combined_content for p in placeholder_patterns)

    consistency_score = 0.0 if has_placeholders else 1.0

    checks.append(
        ValidationCheck(
            name="factual_consistency",
            passed=not has_placeholders,
            severity=Severity.CRITICAL,
            message="Profile contains placeholder text. All content must be factual." if has_placeholders else None,
            details={"score": consistency_score},
        )
    )

    # Calculate overall quality score
    weights = [0.2, 0.2, 0.2, 0.2, 0.2]
    scores = [structure_score, bio_score, talk_score, expertise_score, consistency_score]
    overall_score = sum(w * s for w, s in zip(weights, scores))

    checks.append(
        ValidationCheck(
            name="overall_quality",
            passed=overall_score >= threshold,
            severity=Severity.CRITICAL
            if overall_score < threshold
            else Severity.WARNING
            if overall_score < 0.70
            else Severity.PASS,
            message=f"Profile quality score {overall_score:.2f} below threshold {threshold}"
            if overall_score < threshold
            else f"Profile quality score {overall_score:.2f} is marginal. Recommend improvements."
            if overall_score < 0.70
            else None,
            details={
                "score": overall_score,
                "threshold": threshold,
                "factors": {
                    "structure": structure_score,
                    "biography": bio_score,
                    "talks": talk_score,
                    "expertise": expertise_score,
                    "consistency": consistency_score,
                },
            },
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
