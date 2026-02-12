"""Validates case study quality."""

import re
from pathlib import Path
from typing import Dict, List, Any
from casestudypilot.validation import validate_case_study_format, Severity, ValidationResult, ValidationCheck


# Quality scoring weights
WEIGHTS = {
    "structure": 0.25,
    "content_depth": 0.35,
    "cncf_mentions": 0.15,
    "formatting": 0.10,
    "format_compliance": 0.15,  # New: image paths and links
}

# Required sections
REQUIRED_SECTIONS = ["Overview", "Challenge", "Solution", "Impact", "Conclusion"]

# Minimum word counts per section
MIN_WORDS_PER_SECTION = {
    "Overview": 50,
    "Challenge": 100,
    "Solution": 150,
    "Impact": 100,
    "Conclusion": 50,
}


def read_case_study(file_path: Path) -> str:
    """Read case study file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Case study not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_sections(content: str) -> Dict[str, str]:
    """Extract sections from markdown content."""
    sections = {}

    # Split by headers (##)
    section_pattern = r"##\s+(.+?)\n(.*?)(?=##\s+|\Z)"
    matches = re.finditer(section_pattern, content, re.DOTALL)

    for match in matches:
        section_name = match.group(1).strip()
        section_content = match.group(2).strip()
        sections[section_name] = section_content

    return sections


def count_words(text: str) -> int:
    """Count words in text."""
    # Remove markdown formatting
    text = re.sub(r"[*_`#\[\]()]", "", text)
    words = text.split()
    return len(words)


def validate_structure(sections: Dict[str, str]) -> Dict[str, Any]:
    """Validate structure (presence of required sections)."""
    missing_sections = []

    for required in REQUIRED_SECTIONS:
        if required not in sections:
            missing_sections.append(required)

    score = 1.0 - (len(missing_sections) / len(REQUIRED_SECTIONS))

    return {
        "score": score,
        "missing_sections": missing_sections,
        "passed": len(missing_sections) == 0,
    }


def validate_content_depth(sections: Dict[str, str]) -> Dict[str, Any]:
    """Validate content depth (word counts)."""
    issues = []
    total_penalty = 0.0

    for section_name, min_words in MIN_WORDS_PER_SECTION.items():
        if section_name in sections:
            word_count = count_words(sections[section_name])
            if word_count < min_words:
                issues.append(f"{section_name}: {word_count} words (minimum {min_words})")
                total_penalty += 0.2
        else:
            issues.append(f"{section_name}: missing")
            total_penalty += 0.25

    score = max(0.0, 1.0 - total_penalty)

    return {"score": score, "issues": issues, "passed": len(issues) == 0}


def validate_cncf_mentions(content: str) -> Dict[str, Any]:
    """Validate CNCF project mentions."""
    # Common CNCF projects
    cncf_projects = [
        "Kubernetes",
        "Prometheus",
        "Envoy",
        "CoreDNS",
        "containerd",
        "Fluentd",
        "Jaeger",
        "Vitess",
        "TUF",
        "Notary",
        "Helm",
        "Argo",
        "Cilium",
        "Flux",
        "Linkerd",
        "etcd",
        "CRI-O",
        "Harbor",
        "Falco",
        "Dragonfly",
        "Rook",
        "TiKV",
        "gRPC",
        "CNI",
        "Istio",
        "Knative",
        "OpenTelemetry",
    ]

    mentioned_projects = []
    for project in cncf_projects:
        if project in content:
            mentioned_projects.append(project)

    # Score based on number of projects mentioned
    if len(mentioned_projects) >= 3:
        score = 1.0
    elif len(mentioned_projects) == 2:
        score = 0.8
    elif len(mentioned_projects) == 1:
        score = 0.5
    else:
        score = 0.0

    return {
        "score": score,
        "mentioned_projects": mentioned_projects,
        "passed": len(mentioned_projects) >= 2,
    }


def validate_formatting(content: str) -> Dict[str, Any]:
    """Validate markdown formatting."""
    issues = []

    # Check for bold metrics (e.g., **50%**)
    bold_metrics = re.findall(r"\*\*\d+[%x]?\*\*", content)
    if len(bold_metrics) == 0:
        issues.append("No bold metrics found")

    # Check for bullet lists
    if "- " not in content and "* " not in content:
        issues.append("No bullet lists found")

    # Check for links
    if "[" not in content or "](" not in content:
        issues.append("No links found")

    score = max(0.0, 1.0 - (len(issues) * 0.2))

    return {"score": score, "issues": issues, "passed": len(issues) <= 1}


def validate_format_compliance(file_path: Path) -> Dict[str, Any]:
    """Validate image paths and clickable timestamp links."""
    result = validate_case_study_format(str(file_path))

    # Convert validation result to dict format matching other validators
    issues = []
    for check in result.get_failed_checks():
        if check.message:
            issues.append(check.message)

    # Score: 1.0 if all pass, 0.5 if warnings, 0.0 if critical
    if result.status == Severity.PASS:
        score = 1.0
    elif result.status == Severity.WARNING:
        score = 0.5
    else:  # CRITICAL
        score = 0.0

    return {
        "score": score,
        "issues": issues,
        "passed": result.status == Severity.PASS,
        "validation_details": result.to_dict(),
    }


def calculate_quality_score(
    structure: Dict,
    content_depth: Dict,
    cncf_mentions: Dict,
    formatting: Dict,
    format_compliance: Dict,
) -> float:
    """Calculate overall quality score."""
    score = (
        structure["score"] * WEIGHTS["structure"]
        + content_depth["score"] * WEIGHTS["content_depth"]
        + cncf_mentions["score"] * WEIGHTS["cncf_mentions"]
        + formatting["score"] * WEIGHTS["formatting"]
        + format_compliance["score"] * WEIGHTS["format_compliance"]
    )
    return round(score, 2)


def generate_warnings(
    structure: Dict,
    content_depth: Dict,
    cncf_mentions: Dict,
    formatting: Dict,
    format_compliance: Dict,
) -> List[str]:
    """Generate warning messages."""
    warnings = []

    if not structure["passed"]:
        warnings.append(f"Missing sections: {', '.join(structure['missing_sections'])}")

    if not content_depth["passed"]:
        warnings.extend(content_depth["issues"])

    if not cncf_mentions["passed"]:
        warnings.append(f"Only {len(cncf_mentions['mentioned_projects'])} CNCF projects mentioned (minimum 2)")

    if not formatting["passed"]:
        warnings.extend(formatting["issues"])

    if not format_compliance["passed"]:
        warnings.extend(format_compliance["issues"])

    return warnings


def validate_case_study(file_path: Path, threshold: float = 0.60) -> ValidationResult:
    """Validate case study and return quality assessment."""
    content = read_case_study(file_path)
    sections = extract_sections(content)

    # Run all validations
    structure = validate_structure(sections)
    content_depth = validate_content_depth(sections)
    cncf_mentions = validate_cncf_mentions(content)
    formatting = validate_formatting(content)
    format_compliance = validate_format_compliance(file_path)

    # Calculate overall score
    quality_score = calculate_quality_score(structure, content_depth, cncf_mentions, formatting, format_compliance)

    # Build ValidationChecks
    checks = []

    # Overall score check
    if quality_score < 0.60:
        severity = Severity.CRITICAL
        passed = False
    elif quality_score < 0.75:
        severity = Severity.WARNING
        passed = False
    else:
        severity = Severity.PASS
        passed = True

    checks.append(
        ValidationCheck(
            name="overall_score",
            passed=passed,
            severity=severity,
            message=f"Overall quality score: {quality_score:.2f} (threshold: {threshold:.2f})",
            details={
                "score": quality_score,
                "threshold": threshold,
                "section_scores": {
                    "structure": structure,
                    "content_depth": content_depth,
                    "cncf_mentions": cncf_mentions,
                    "formatting": formatting,
                    "format_compliance": format_compliance,
                },
            },
        )
    )

    # Generate warnings from individual categories
    warnings = generate_warnings(structure, content_depth, cncf_mentions, formatting, format_compliance)

    for warning in warnings:
        checks.append(
            ValidationCheck(
                name="content_issue",
                passed=False,
                severity=Severity.WARNING,
                message=warning,
            )
        )

    return ValidationResult.from_checks(checks)
