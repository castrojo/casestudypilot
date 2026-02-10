"""Validates reference architecture quality with technical depth scoring."""

import json
import sys
import re
from pathlib import Path
from typing import Dict, Any, Tuple


def score_cncf_project_depth(data: Dict[str, Any]) -> float:
    """
    Score CNCF project depth (0-1.0).

    Scoring:
    - 5+ projects: 1.0
    - 4 projects: 0.8
    - 3 projects: 0.6
    - 2 projects: 0.4
    - 1 or less: 0.2
    - Bonus: +0.1 if projects span 3+ categories
    - Bonus: +0.1 if integration patterns section substantial (>500 words)
    """
    projects = data.get("cncf_project_list", [])
    num_projects = len(projects)

    # Base score
    if num_projects >= 5:
        base_score = 1.0
    elif num_projects == 4:
        base_score = 0.8
    elif num_projects == 3:
        base_score = 0.6
    elif num_projects == 2:
        base_score = 0.4
    else:
        base_score = 0.2

    # Category diversity bonus
    categories = set(p.get("category", "") for p in projects if p.get("category"))
    if len(categories) >= 3:
        base_score = min(1.0, base_score + 0.1)

    # Integration patterns bonus
    integration_section = data.get("sections", {}).get("integration_patterns", "")
    if len(integration_section.split()) > 500:
        base_score = min(1.0, base_score + 0.1)

    return base_score


def score_technical_specificity(data: Dict[str, Any]) -> float:
    """
    Score technical specificity (0-1.0).

    Scoring based on presence of technical indicators:
    - Commands/code snippets (kubectl, eksctl, helm): +0.2
    - Version numbers (v1.26, v1.18): +0.2
    - Configuration details (YAML, JSON): +0.2
    - Specific tools/technologies (not generic "API"): +0.2
    - Technical patterns (sidecar, operator, circuit breaker): +0.2
    """
    score = 0.0

    # Combine all sections
    all_text = " ".join(data.get("sections", {}).values())
    all_text_lower = all_text.lower()

    # Check for commands/code
    command_indicators = ["kubectl", "helm", "eksctl", "```", "argo", "terraform"]
    if any(indicator in all_text_lower for indicator in command_indicators):
        score += 0.2

    # Check for version numbers
    version_pattern = r"v\d+\.\d+"
    if re.search(version_pattern, all_text):
        score += 0.2

    # Check for configuration (YAML/JSON keywords)
    config_indicators = ["apiVersion:", "kind:", "metadata:", "spec:", "replicas:", "nodeGroups:"]
    if any(indicator in all_text for indicator in config_indicators):
        score += 0.2

    # Check for specific technologies (not generic)
    specific_techs = ["envoy", "istio", "prometheus", "grafana", "argo", "flux", "calico"]
    if sum(1 for tech in specific_techs if tech in all_text_lower) >= 3:
        score += 0.2

    # Check for technical patterns
    patterns = ["sidecar", "operator", "circuit breaker", "canary", "blue-green", "rolling"]
    if sum(1 for pattern in patterns if pattern in all_text_lower) >= 2:
        score += 0.2

    return min(1.0, score)


def score_implementation_detail(data: Dict[str, Any]) -> float:
    """
    Score implementation detail (0-1.0).

    Scoring based on implementation details section:
    - Word count >= 700: 1.0
    - Word count >= 500: 0.8
    - Word count >= 300: 0.6
    - Word count < 300: 0.4
    - Bonus: +0.1 if mentions phases/steps
    - Bonus: +0.1 if mentions challenges and solutions
    """
    impl_section = data.get("sections", {}).get("implementation_details", "")
    word_count = len(impl_section.split())

    if word_count >= 700:
        score = 1.0
    elif word_count >= 500:
        score = 0.8
    elif word_count >= 300:
        score = 0.6
    else:
        score = 0.4

    impl_lower = impl_section.lower()

    # Phases/steps bonus
    if any(keyword in impl_lower for keyword in ["phase", "step", "stage"]):
        score = min(1.0, score + 0.1)

    # Challenges/solutions bonus
    if any(keyword in impl_lower for keyword in ["challenge", "issue", "problem", "solution"]):
        score = min(1.0, score + 0.1)

    return score


def score_metric_quality(data: Dict[str, Any]) -> float:
    """
    Score metric quality (0-1.0).

    Scoring based on key metrics:
    - 4+ quantitative metrics: 1.0
    - 3 quantitative metrics: 0.8
    - 2 quantitative metrics: 0.6
    - 1 quantitative metric: 0.4
    - 0 quantitative metrics: 0.2
    - Bonus: +0.1 if metrics have before/after values (→)
    - Bonus: +0.1 if metrics cover diverse categories
    """
    metrics = data.get("key_metrics_summary", [])
    num_metrics = len(metrics)

    if num_metrics >= 4:
        score = 1.0
    elif num_metrics == 3:
        score = 0.8
    elif num_metrics == 2:
        score = 0.6
    elif num_metrics == 1:
        score = 0.4
    else:
        score = 0.2

    # Before/after bonus
    has_before_after = all("→" in m.get("improvement", "") for m in metrics if m.get("improvement"))
    if has_before_after and num_metrics > 0:
        score = min(1.0, score + 0.1)

    # Diversity bonus (check if metrics cover different aspects)
    metric_text = " ".join(m.get("metric", "").lower() for m in metrics)
    categories = ["latency", "throughput", "error", "cost", "time", "frequency"]
    diverse = sum(1 for cat in categories if cat in metric_text) >= 2
    if diverse:
        score = min(1.0, score + 0.1)

    return score


def score_architecture_completeness(data: Dict[str, Any]) -> float:
    """
    Score architecture completeness (0-1.0).

    Scoring based on architectural sections:
    - All sections present (13 sections): 1.0
    - 11-12 sections present: 0.8
    - 9-10 sections present: 0.6
    - 7-8 sections present: 0.4
    - < 7 sections present: 0.2
    - Bonus: +0.1 if architecture diagrams section substantial (>200 words)
    - Bonus: +0.1 if observability section substantial (>300 words)
    """
    sections = data.get("sections", {})
    num_sections = len(sections)

    if num_sections >= 13:
        score = 1.0
    elif num_sections >= 11:
        score = 0.8
    elif num_sections >= 9:
        score = 0.6
    elif num_sections >= 7:
        score = 0.4
    else:
        score = 0.2

    # Architecture diagrams bonus
    diagrams_section = sections.get("architecture_diagrams", "")
    if len(diagrams_section.split()) > 200:
        score = min(1.0, score + 0.1)

    # Observability bonus
    obs_section = sections.get("observability_operations", "")
    if len(obs_section.split()) > 300:
        score = min(1.0, score + 0.1)

    return score


def calculate_technical_depth_score(ref_arch: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """
    Calculate technical depth score using 5-dimensional algorithm.

    Score = 0.25 * cncf_project_depth +
            0.20 * technical_specificity +
            0.20 * implementation_detail +
            0.20 * metric_quality +
            0.15 * architecture_completeness

    Args:
        ref_arch: Reference architecture JSON

    Returns:
        Tuple of (total_score, sub_scores_dict)
    """
    sub_scores = {
        "cncf_project_depth": score_cncf_project_depth(ref_arch),
        "technical_specificity": score_technical_specificity(ref_arch),
        "implementation_detail": score_implementation_detail(ref_arch),
        "metric_quality": score_metric_quality(ref_arch),
        "architecture_completeness": score_architecture_completeness(ref_arch),
    }

    total = (
        0.25 * sub_scores["cncf_project_depth"]
        + 0.20 * sub_scores["technical_specificity"]
        + 0.20 * sub_scores["implementation_detail"]
        + 0.20 * sub_scores["metric_quality"]
        + 0.15 * sub_scores["architecture_completeness"]
    )

    return total, sub_scores


def validate_reference_architecture(ref_arch_file: Path) -> Tuple[int, str]:
    """
    Validate reference architecture JSON output.

    Args:
        ref_arch_file: Path to reference architecture JSON file

    Returns:
        Tuple of (exit_code, message)
        - 0: Valid (score >= 0.70)
        - 1: Warning (score 0.60-0.69)
        - 2: Critical failure (score < 0.60)
    """
    # Load JSON
    try:
        with open(ref_arch_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return 2, f"Invalid JSON: {e}"
    except Exception as e:
        return 2, f"Cannot read file: {e}"

    exit_code = 0
    messages = []

    # Check 1: Technical depth score
    tech_score, sub_scores = calculate_technical_depth_score(data)
    messages.append(f"📊 Technical Depth Score: {tech_score:.2f}")
    messages.append(f"   - CNCF Project Depth: {sub_scores['cncf_project_depth']:.2f} (weight 0.25)")
    messages.append(f"   - Technical Specificity: {sub_scores['technical_specificity']:.2f} (weight 0.20)")
    messages.append(f"   - Implementation Detail: {sub_scores['implementation_detail']:.2f} (weight 0.20)")
    messages.append(f"   - Metric Quality: {sub_scores['metric_quality']:.2f} (weight 0.20)")
    messages.append(f"   - Architecture Completeness: {sub_scores['architecture_completeness']:.2f} (weight 0.15)")

    if tech_score < 0.60:
        messages.append("❌ Critical: Technical depth score below 0.60")
        return 2, "\n".join(messages)
    elif tech_score < 0.70:
        messages.append("⚠️  Warning: Technical depth score below 0.70 (acceptable but not ideal)")
        exit_code = max(exit_code, 1)
    else:
        messages.append("✅ Technical depth score meets standards (>=0.70)")

    # Check 2: Word count
    all_text = " ".join(data.get("sections", {}).values())
    word_count = len(all_text.split())
    messages.append(f"\n📝 Total Word Count: {word_count}")

    if word_count < 2000 or word_count > 5000:
        messages.append(f"❌ Critical: Word count {word_count} outside range 2000-5000")
        return 2, "\n".join(messages)
    elif word_count < 2500 or word_count > 4500:
        messages.append(f"⚠️  Warning: Word count {word_count} outside ideal range 2500-4500")
        exit_code = max(exit_code, 1)
    else:
        messages.append("✅ Word count within ideal range (2500-4500)")

    # Check 3: Required sections
    required_sections = [
        "executive_summary",
        "background",
        "technical_challenge",
        "architecture_overview",
        "cncf_projects",
        "implementation_details",
        "results_and_impact",
        "lessons_learned",
        "conclusion",
    ]
    sections = data.get("sections", {})
    missing_sections = [s for s in required_sections if s not in sections]

    if missing_sections:
        messages.append(f"\n❌ Critical: Missing required sections: {', '.join(missing_sections)}")
        return 2, "\n".join(messages)
    else:
        messages.append(f"\n✅ All {len(required_sections)} required sections present")

    # Check 4: CNCF project list
    if not data.get("cncf_project_list"):
        messages.append("❌ Critical: CNCF project list is empty")
        return 2, "\n".join(messages)
    else:
        project_count = len(data.get("cncf_project_list", []))
        messages.append(f"✅ CNCF project list contains {project_count} projects")

    # Success
    if exit_code == 0:
        messages.append("\n✅ Validation passed - Reference architecture meets all quality standards")
    elif exit_code == 1:
        messages.append("\n⚠️  Validation passed with warnings - Consider improvements")

    return exit_code, "\n".join(messages)


def main(ref_arch_file_path: str) -> int:
    """CLI entry point."""
    try:
        ref_arch_file = Path(ref_arch_file_path)

        if not ref_arch_file.exists():
            print(f"❌ File not found: {ref_arch_file_path}", file=sys.stderr)
            return 2

        exit_code, message = validate_reference_architecture(ref_arch_file)

        # Print message to appropriate stream
        if exit_code == 0:
            print(message)
        else:
            print(message, file=sys.stderr)

        return exit_code

    except Exception as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m casestudypilot.tools.validate_reference_architecture <ref_arch_file>", file=sys.stderr)
        sys.exit(2)

    sys.exit(main(sys.argv[1]))
