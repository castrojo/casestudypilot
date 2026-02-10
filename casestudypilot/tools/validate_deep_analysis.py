"""Validates deep analysis output for reference architectures."""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple


def validate_deep_analysis(analysis_file: Path) -> Tuple[int, str]:
    """
    Validate deep analysis JSON output.

    Args:
        analysis_file: Path to deep analysis JSON file

    Returns:
        Tuple of (exit_code, message)
        - 0: Valid
        - 1: Warning
        - 2: Critical failure
    """
    # Load and parse JSON
    try:
        with open(analysis_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return 2, f"Invalid JSON: {e}"
    except Exception as e:
        return 2, f"Cannot read file: {e}"

    exit_code = 0
    warnings = []

    # Check 1: CNCF projects count (5+ required, 4+ warning)
    projects = data.get("cncf_projects", [])
    if len(projects) < 4:
        return 2, f"Critical: Less than 4 CNCF projects found ({len(projects)})"
    elif len(projects) < 5:
        warnings.append(f"Only {len(projects)} CNCF projects (5 recommended)")
        exit_code = max(exit_code, 1)

    # Check 2: Architecture layers (all 3 required)
    arch = data.get("architecture_components", {})
    required_layers = ["infrastructure_layer", "platform_layer", "application_layer"]
    for layer in required_layers:
        if layer not in arch:
            return 2, f"Critical: Missing architecture layer '{layer}'"
        if not isinstance(arch[layer], list) or len(arch[layer]) == 0:
            return 2, f"Critical: Architecture layer '{layer}' is empty"

    # Check 3: Integration patterns (2+ required, 1+ warning)
    patterns = data.get("integration_patterns", [])
    if len(patterns) < 1:
        return 2, "Critical: No integration patterns found"
    elif len(patterns) < 2:
        warnings.append("Only 1 integration pattern (2 recommended)")
        exit_code = max(exit_code, 1)

    # Check 4: Technical metrics have transcript quotes
    metrics = data.get("technical_metrics", [])
    for i, metric in enumerate(metrics):
        if "transcript_quote" not in metric:
            return 2, f"Critical: Metric {i + 1} missing 'transcript_quote' field"
        quote = metric.get("transcript_quote", "")
        if not quote or len(quote) < 10:
            return 2, f"Critical: Metric {i + 1} has empty or too-short transcript quote"

    # Check 5: Screenshot opportunities (6+ required, 4+ warning)
    screenshots = data.get("screenshot_opportunities", [])
    if len(screenshots) < 4:
        return 2, f"Critical: Less than 4 screenshot opportunities ({len(screenshots)})"
    elif len(screenshots) < 6:
        warnings.append(f"Only {len(screenshots)} screenshot opportunities (6 recommended)")
        exit_code = max(exit_code, 1)

    # Check 6: Sections present (all 6 required)
    sections = data.get("sections", {})
    required_sections = [
        "background",
        "technical_challenge",
        "architecture_overview",
        "implementation_details",
        "results_and_impact",
        "lessons_learned",
    ]
    for section in required_sections:
        if section not in sections:
            return 2, f"Critical: Missing section '{section}'"

    # Check 7: Section word counts (200-800 words, warning only)
    for section_name, content in sections.items():
        if not isinstance(content, str):
            warnings.append(f"Section '{section_name}' is not a string")
            exit_code = max(exit_code, 1)
            continue

        word_count = len(content.split())
        if word_count < 200:
            warnings.append(f"Section '{section_name}' is only {word_count} words (200-800 recommended)")
            exit_code = max(exit_code, 1)
        elif word_count > 800:
            warnings.append(f"Section '{section_name}' is {word_count} words (200-800 recommended)")
            exit_code = max(exit_code, 1)

    # Build result message
    if exit_code == 0:
        return 0, "Validation passed"
    elif exit_code == 1:
        return 1, f"Validation passed with warnings:\n  - " + "\n  - ".join(warnings)
    else:
        return exit_code, "Validation failed"


def main(analysis_file_path: str) -> int:
    """CLI entry point."""
    try:
        analysis_file = Path(analysis_file_path)

        if not analysis_file.exists():
            print(f"❌ File not found: {analysis_file_path}", file=sys.stderr)
            return 2

        exit_code, message = validate_deep_analysis(analysis_file)

        if exit_code == 0:
            print(f"✅ {message}")
        elif exit_code == 1:
            print(f"⚠️ {message}", file=sys.stderr)
        else:
            print(f"❌ {message}", file=sys.stderr)

        return exit_code

    except Exception as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m casestudypilot.tools.validate_deep_analysis <analysis_file>", file=sys.stderr)
        sys.exit(2)

    sys.exit(main(sys.argv[1]))
