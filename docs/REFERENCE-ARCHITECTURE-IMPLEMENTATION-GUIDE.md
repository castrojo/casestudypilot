# Reference Architecture Implementation Guide for Future Agents

**Version:** 1.0.0  
**Date:** 2026-02-09  
**Status:** Documentation Complete - Ready for Implementation  
**Estimated Implementation Time:** 18 days (7 phases)

---

## Executive Summary

This guide provides complete specifications for implementing reference architecture generation in casestudypilot. The feature extends the existing case study generation framework to support longer, more technical reference architectures suitable for CNCF TAB submission.

**User Decisions Made:**
- ✅ Full implementation (all 7 phases)
- ✅ Textual diagram specs (no Mermaid/PlantUML code generation)
- ✅ TAB guidance only (no automatic issue creation)
- ✅ Quality threshold: 0.70 technical depth score
- ✅ Separate agent (not unified with case study agent)
- ✅ Standard testing (3-4 integration tests)
- ✅ **High priority: Documentation only** (for future agents to implement)

---

## Table of Contents

1. [Overview](#overview)
2. [Three New Skills](#three-new-skills)
3. [Three New CLI Tools](#three-new-cli-tools)
4. [One New Agent](#one-new-agent)
5. [Templates and Supporting Files](#templates-and-supporting-files)
6. [Implementation Phases](#implementation-phases)
7. [Testing Strategy](#testing-strategy)
8. [Success Criteria](#success-criteria)

---

## Overview

### What You're Building

**Reference Architecture Generator** - An AI agent that transforms technical YouTube videos into comprehensive reference architectures for CNCF TAB submission.

**Input:** YouTube URL (from GitHub issue)  
**Output:** 2000-5000 word reference architecture with 6 screenshots, 10 sections, 5+ CNCF projects

### Architecture Comparison

| Aspect | Case Study (Existing) | Reference Architecture (New) |
|--------|---------------------|----------------------------|
| **Length** | 500-1500 words | 2000-5000 words |
| **Sections** | 5 sections | 10 sections |
| **Screenshots** | 3 screenshots | 6 screenshots |
| **CNCF Projects** | 2+ projects | 5+ projects |
| **Technical Depth** | Business-focused | Technical-focused |
| **Quality Threshold** | 0.60 | 0.70 |
| **Audience** | Marketing, business | Engineers, architects |
| **Output Directory** | `case-studies/` | `reference-architectures/` |
| **TAB Submission** | No | Yes (with guidance) |
| **Agent Steps** | 14 steps | 18 steps |
| **Validation Checkpoints** | 5 checkpoints | 7 checkpoints |

### Reuse vs. New Components

**Reuse (40% of infrastructure):**
- ✅ `youtube-data` CLI tool (fetches video data)
- ✅ `validate-transcript` CLI tool (checks transcript quality)
- ✅ `validate-company` CLI tool (verifies company name)
- ✅ `cncf-member-check` CLI tool (checks CNCF membership)
- ✅ `extract-screenshots` CLI tool (extracts screenshots from video)
- ✅ `transcript-correction` skill (corrects transcript errors)

**New (60% of implementation):**
- 🆕 `transcript-deep-analysis` skill (deeper technical extraction)
- 🆕 `architecture-diagram-specification` skill (diagram specs)
- 🆕 `reference-architecture-generation` skill (content generation)
- 🆕 `validate-deep-analysis` CLI tool (validates deep analysis output)
- 🆕 `validate-reference-architecture` CLI tool (technical depth scoring)
- 🆕 `assemble-reference-architecture` CLI tool (assembles final markdown)
- 🆕 `reference-architecture-agent` agent workflow (18-step orchestration)
- 🆕 `reference_architecture.md.j2` template (Jinja2 template)

---

## Three New Skills

### Skill 1: transcript-deep-analysis

**Location:** `.github/skills/transcript-deep-analysis/SKILL.md`  
**Full Specification:** `docs/skills/transcript-deep-analysis.md` ✅ CREATED

**Purpose:** Deep technical analysis of video transcripts to extract architectural patterns, CNCF projects, integration patterns, and technical metrics for reference architectures.

**Key Differences from `transcript-analysis` (case study skill):**
- Extracts **5+ CNCF projects** (vs. 2+ for case studies)
- Documents **3-layer architecture** (infrastructure, platform, application)
- Identifies **integration patterns** (how projects work together)
- Extracts **technical metrics with transcript quotes** (for fabrication prevention)
- Generates **6 sections** of 200-800 words each (vs. 5 sections of 100-300 words)
- Identifies **6+ screenshot opportunities** (vs. 3 for case studies)

**Input Format:**
```json
{
  "transcript": "Full corrected transcript",
  "video_title": "Video title",
  "video_description": "Video description",
  "duration_seconds": 1234,
  "company_name": "Verified company name"
}
```

**Output Format:**
```json
{
  "cncf_projects": [
    {
      "name": "Kubernetes",
      "category": "orchestration",
      "usage_context": "Primary orchestration platform managing 500+ microservices",
      "integration_pattern": "native",
      "confidence": "high"
    }
  ],
  "architecture_components": {
    "infrastructure_layer": [...],
    "platform_layer": [...],
    "application_layer": [...]
  },
  "integration_patterns": [
    {
      "pattern_name": "Service Mesh Integration",
      "description": "How services communicate",
      "projects_involved": ["Istio", "Envoy"],
      "technical_details": "Specific implementation details"
    }
  ],
  "technical_metrics": [
    {
      "metric_name": "API Response Time (p95)",
      "before_value": "500",
      "after_value": "50",
      "measurement_unit": "milliseconds",
      "source_confidence": "explicit",
      "transcript_quote": "Exact quote from transcript"
    }
  ],
  "sections": {
    "background": "2-3 paragraphs...",
    "technical_challenge": "2-3 paragraphs...",
    "architecture_overview": "3-4 paragraphs...",
    "implementation_details": "4-5 paragraphs...",
    "results_and_impact": "2-3 paragraphs...",
    "lessons_learned": "2-3 paragraphs..."
  },
  "key_quotes": [...],
  "screenshot_opportunities": [...]
}
```

**Validation:**
- CLI tool: `validate-deep-analysis`
- Exit code 2 (critical) if: `len(cncf_projects) < 5`, missing architecture layers, missing transcript quotes
- Exit code 1 (warning) if: `len(cncf_projects) == 4`, `len(integration_patterns) == 1`

**Implementation Instructions:**
See `docs/skills/transcript-deep-analysis.md` for complete execution instructions (8 steps, 400+ lines).

---

### Skill 2: architecture-diagram-specification

**Location:** `.github/skills/architecture-diagram-specification/SKILL.md`  
**Full Specification:** `docs/skills/architecture-diagram-specification.md` ✅ CREATED

**Purpose:** Generate textual specifications for architecture diagrams (component diagrams, data flow diagrams, deployment diagrams) that can guide screenshot extraction or future diagram generation.

**Note:** This skill generates **textual descriptions** of diagrams, NOT Mermaid/PlantUML code (per user decision).

**Input Format:**
```json
{
  "deep_analysis": {
    "cncf_projects": [...],
    "architecture_components": {...},
    "integration_patterns": [...]
  },
  "diagram_types": ["component", "data-flow", "deployment"]
}
```

**Output Format:**
```json
{
  "diagrams": [
    {
      "type": "component",
      "title": "Microservices Architecture with Service Mesh",
      "description": "Shows 50+ microservices communicating through Istio",
      "components": [
        {
          "id": "order-service",
          "label": "Order Service",
          "type": "service",
          "layer": "application",
          "cncf_projects": [],
          "description": "Processes customer orders"
        }
      ],
      "connections": [
        {
          "from_id": "order-service",
          "to_id": "istio-mesh",
          "type": "http",
          "label": "API calls",
          "bidirectional": false,
          "protocol": "HTTP/2",
          "notes": "Circuit breaker enabled"
        }
      ],
      "annotations": [
        {
          "component_id": "order-service",
          "text": "100K req/sec peak",
          "position": "top"
        }
      ],
      "layout_hints": {
        "orientation": "horizontal",
        "groupings": [...]
      }
    }
  ]
}
```

**Validation:**
- No dedicated CLI validation tool
- Validated contextually in `reference-architecture-generation` skill
- Must have at least 2 diagrams, each with 4+ components, 3+ connections

**Implementation Instructions:**
See `docs/skills/architecture-diagram-specification.md` for complete execution instructions (5 steps, 600+ lines).

---

### Skill 3: reference-architecture-generation

**Location:** `.github/skills/reference-architecture-generation/SKILL.md`  
**Status:** 🔴 TO BE CREATED (see specification below)

**Purpose:** Generate comprehensive 10-section reference architecture content from deep analysis and diagram specifications.

**Key Differences from `case-study-generation` (existing):**
- Generates **10 sections** (vs. 5 for case studies)
- Sections are **400-800 words** each (vs. 100-300 words)
- Includes **architecture diagrams section** with diagram descriptions
- Includes **integration patterns section** describing how CNCF projects integrate
- Includes **deployment architecture section** describing multi-cluster/multi-region setup
- Includes **observability and operations section** describing monitoring and maintenance
- Includes **TAB submission metadata** (project maturity, architectural significance)
- Uses **technical tone** (for engineers) vs. business tone (for case studies)

**Input Format:**
```json
{
  "deep_analysis": {
    "cncf_projects": [...],
    "architecture_components": {...},
    "integration_patterns": [...],
    "technical_metrics": [...],
    "sections": {...},
    "key_quotes": [...]
  },
  "diagram_specifications": {
    "diagrams": [...]
  },
  "company_info": {
    "name": "Company Name",
    "industry": "E-commerce",
    "verified_membership": true
  },
  "video_metadata": {
    "title": "Video title",
    "url": "https://youtube.com/watch?v=VIDEO_ID",
    "duration_seconds": 1234
  }
}
```

**Output Format:**
```json
{
  "metadata": {
    "title": "Reference Architecture Title",
    "subtitle": "One-line description",
    "company_name": "Company Name",
    "industry": "E-commerce",
    "video_url": "https://youtube.com/watch?v=VIDEO_ID",
    "publication_date": "2026-02-09",
    "tab_metadata": {
      "project_maturity": "graduated|incubating|sandbox",
      "architectural_significance": "Why this architecture is significant",
      "primary_patterns": ["microservices", "service-mesh", "gitops"]
    }
  },
  "sections": {
    "executive_summary": "200-300 words: High-level overview...",
    "background": "300-400 words: Company context...",
    "technical_challenge": "400-600 words: Specific technical problems...",
    "architecture_overview": "500-700 words: High-level architecture description...",
    "architecture_diagrams": "300-400 words: Descriptions of diagrams with references...",
    "cncf_projects": "500-700 words: Detailed CNCF project usage...",
    "integration_patterns": "400-600 words: How projects integrate...",
    "implementation_details": "700-900 words: Step-by-step implementation...",
    "deployment_architecture": "400-600 words: Multi-cluster, multi-region setup...",
    "observability_operations": "400-600 words: Monitoring, logging, operations...",
    "results_and_impact": "400-600 words: Quantitative results...",
    "lessons_learned": "400-600 words: What worked, what didn't...",
    "conclusion": "200-300 words: Summary and future directions..."
  },
  "cncf_project_list": [
    {
      "name": "Kubernetes",
      "category": "Orchestration & Management",
      "usage_summary": "Primary container orchestration platform"
    }
  ],
  "key_metrics_summary": [
    {
      "metric": "API Latency (p95)",
      "improvement": "500ms → 50ms (10x improvement)",
      "business_impact": "Enabled 200% user growth"
    }
  ]
}
```

**Validation:**
- CLI tool: `validate-reference-architecture`
- Technical depth scoring (5 dimensions, weighted average)
- Exit code 2 (critical) if: technical_depth_score < 0.70, word count < 2000 or > 5000
- Exit code 1 (warning) if: technical_depth_score < 0.75, word count < 2500

**Implementation Instructions (High-Level):**

1. **Read all inputs:** Deep analysis, diagram specs, company info, video metadata
2. **Generate metadata:** Title, subtitle, TAB metadata based on deep analysis
3. **Generate 10 sections:**
   - Executive Summary (200-300 words): Concise overview
   - Background (300-400 words): Company and business context
   - Technical Challenge (400-600 words): Specific problems faced
   - Architecture Overview (500-700 words): High-level design
   - Architecture Diagrams (300-400 words): Describe diagrams from specs
   - CNCF Projects (500-700 words): Detailed project usage
   - Integration Patterns (400-600 words): How projects integrate
   - Implementation Details (700-900 words): Step-by-step process
   - Deployment Architecture (400-600 words): Multi-cluster/region setup
   - Observability & Operations (400-600 words): Monitoring and ops
   - Results and Impact (400-600 words): Quantitative outcomes
   - Lessons Learned (400-600 words): Reflections and advice
   - Conclusion (200-300 words): Summary and future work
4. **Generate CNCF project list:** Summary table of all projects
5. **Generate key metrics summary:** Summary table of improvements
6. **Validate output:** Ensure all sections meet word count, tone is technical

**Tone Guidelines:**
- **Target audience:** Engineers, architects, technical decision-makers
- **Style:** Technical, detailed, instructional
- **Voice:** Third-person, objective
- **Avoid:** Marketing language, vague claims, buzzwords
- **Include:** Commands, configurations, code snippets, metrics, specific tools/versions

**Example Section (Implementation Details):**
> "The implementation occurred in four phases over six months. Phase 1 focused on establishing the base Kubernetes infrastructure: three production clusters (us-east-1, us-west-2, eu-west-1) running Kubernetes v1.26 with Calico CNI for network policy enforcement. The team used eksctl to provision clusters with the following configuration:
>
> ```yaml
> apiVersion: eksctl.io/v1alpha5
> kind: ClusterConfig
> metadata:
>   name: prod-us-east-1
>   region: us-east-1
> nodeGroups:
>   - name: general
>     instanceType: m5.2xlarge
>     desiredCapacity: 20
>     maxSize: 50
> ```
>
> Phase 2 deployed Istio v1.18 to the dev cluster first for validation. The team encountered a critical issue: Istio's default resource limits caused CPU throttling under load. The solution was to increase CPU limits from 500m to 2 cores per Envoy proxy and implement horizontal pod autoscaling..."

**File to Create:**
Create `.github/skills/reference-architecture-generation/SKILL.md` with:
- Purpose and comparison to case-study-generation
- Complete input/output JSON schemas
- 10-step execution instructions (one per section + metadata + validation)
- Tone guidelines and examples
- Quality guidelines (technical depth, specificity, accuracy)
- Common mistakes section
- 2-3 complete examples

**Estimated Size:** 800-1000 lines

---

## Three New CLI Tools

### CLI Tool 1: validate-deep-analysis

**Location:** `casestudypilot/tools/validate_deep_analysis.py`  
**Status:** 🔴 TO BE CREATED

**Purpose:** Validate output from `transcript-deep-analysis` skill to ensure it meets quality standards for reference architectures.

**Command:**
```bash
python -m casestudypilot validate-deep-analysis transcript_deep_analysis.json
```

**Exit Codes:**
- **0 (PASS)**: All validations passed
- **1 (WARNING)**: Minor issues (e.g., 4 projects instead of 5, 5 screenshots instead of 6)
- **2 (CRITICAL)**: Major issues (e.g., < 4 projects, missing architecture layers, metrics without quotes)

**Validation Checks:**

| Check | Type | Exit Code if Failed |
|-------|------|-------------------|
| File exists and is valid JSON | Critical | 2 |
| `len(cncf_projects) >= 5` | Critical | 2 |
| `len(cncf_projects) >= 4` | Warning | 1 |
| All 3 architecture layers present | Critical | 2 |
| Each layer has >= 1 component | Critical | 2 |
| `len(integration_patterns) >= 2` | Critical | 2 |
| `len(integration_patterns) >= 1` | Warning | 1 |
| All technical metrics have `transcript_quote` field | Critical | 2 |
| All technical metrics have non-empty `transcript_quote` | Critical | 2 |
| `len(screenshot_opportunities) >= 6` | Critical | 2 |
| `len(screenshot_opportunities) >= 4` | Warning | 1 |
| All 6 sections present | Critical | 2 |
| Each section is 200-800 words | Warning | 1 |
| CNCF project names are valid | Warning | 1 |

**Implementation Pseudocode:**
```python
import json
import sys
from pathlib import Path

def validate_deep_analysis(filepath: str) -> int:
    """
    Validate deep analysis JSON output.
    Returns: 0 (pass), 1 (warning), 2 (critical)
    """
    # Load JSON
    try:
        with open(filepath) as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Critical: Cannot load JSON: {e}", file=sys.stderr)
        return 2
    
    exit_code = 0  # Start with PASS
    
    # Check 1: CNCF projects count
    projects = data.get("cncf_projects", [])
    if len(projects) < 4:
        print("❌ Critical: Less than 4 CNCF projects found", file=sys.stderr)
        return 2
    elif len(projects) < 5:
        print("⚠️ Warning: Only 4 CNCF projects (5 recommended)", file=sys.stderr)
        exit_code = max(exit_code, 1)
    
    # Check 2: Architecture layers
    arch = data.get("architecture_components", {})
    required_layers = ["infrastructure_layer", "platform_layer", "application_layer"]
    for layer in required_layers:
        if layer not in arch or len(arch[layer]) == 0:
            print(f"❌ Critical: Missing or empty {layer}", file=sys.stderr)
            return 2
    
    # Check 3: Integration patterns
    patterns = data.get("integration_patterns", [])
    if len(patterns) < 1:
        print("❌ Critical: No integration patterns found", file=sys.stderr)
        return 2
    elif len(patterns) < 2:
        print("⚠️ Warning: Only 1 integration pattern (2 recommended)", file=sys.stderr)
        exit_code = max(exit_code, 1)
    
    # Check 4: Technical metrics have transcript quotes
    metrics = data.get("technical_metrics", [])
    for i, metric in enumerate(metrics):
        if "transcript_quote" not in metric:
            print(f"❌ Critical: Metric {i+1} missing 'transcript_quote' field", file=sys.stderr)
            return 2
        if not metric["transcript_quote"] or len(metric["transcript_quote"]) < 10:
            print(f"❌ Critical: Metric {i+1} has empty or too-short transcript quote", file=sys.stderr)
            return 2
    
    # Check 5: Screenshot opportunities
    screenshots = data.get("screenshot_opportunities", [])
    if len(screenshots) < 4:
        print("❌ Critical: Less than 4 screenshot opportunities", file=sys.stderr)
        return 2
    elif len(screenshots) < 6:
        print("⚠️ Warning: Only {len(screenshots)} screenshots (6 recommended)", file=sys.stderr)
        exit_code = max(exit_code, 1)
    
    # Check 6: Sections present
    sections = data.get("sections", {})
    required_sections = ["background", "technical_challenge", "architecture_overview", 
                        "implementation_details", "results_and_impact", "lessons_learned"]
    for section in required_sections:
        if section not in sections:
            print(f"❌ Critical: Missing section '{section}'", file=sys.stderr)
            return 2
    
    # Check 7: Section word counts (warning only)
    for section_name, content in sections.items():
        word_count = len(content.split())
        if word_count < 200 or word_count > 800:
            print(f"⚠️ Warning: Section '{section_name}' is {word_count} words (200-800 recommended)", file=sys.stderr)
            exit_code = max(exit_code, 1)
    
    # Success
    if exit_code == 0:
        print("✅ Validation passed")
    
    return exit_code

def main():
    if len(sys.argv) != 2:
        print("Usage: python -m casestudypilot validate-deep-analysis <file.json>", file=sys.stderr)
        sys.exit(2)
    
    exit_code = validate_deep_analysis(sys.argv[1])
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
```

**Testing:**
- Test with valid deep analysis (should return 0)
- Test with 4 projects (should return 1)
- Test with 3 projects (should return 2)
- Test with missing architecture layer (should return 2)
- Test with metrics without transcript quotes (should return 2)
- Test with 5 screenshots (should return 1)

---

### CLI Tool 2: validate-reference-architecture

**Location:** `casestudypilot/tools/validate_reference_architecture.py`  
**Status:** 🔴 TO BE CREATED

**Purpose:** Validate final reference architecture JSON output with technical depth scoring algorithm.

**Command:**
```bash
python -m casestudypilot validate-reference-architecture reference_architecture.json
```

**Exit Codes:**
- **0 (PASS)**: Technical depth score >= 0.70, all validations passed
- **1 (WARNING)**: Technical depth score >= 0.60 and < 0.70, or minor issues
- **2 (CRITICAL)**: Technical depth score < 0.60, or major structural issues

**Technical Depth Scoring Algorithm:**

Technical depth score is a weighted average of 5 sub-scores:

```python
technical_depth_score = (
    0.25 * cncf_project_depth +
    0.20 * technical_specificity +
    0.20 * implementation_detail +
    0.20 * metric_quality +
    0.15 * architecture_completeness
)
```

**Sub-Score 1: CNCF Project Depth (0-1.0)**
```python
def score_cncf_project_depth(data) -> float:
    """
    Scoring:
    - 5+ projects with detailed usage: 1.0
    - 4 projects with detailed usage: 0.8
    - 3 projects with detailed usage: 0.6
    - 2 projects with detailed usage: 0.4
    - 1 project or less: 0.2
    - Bonus: +0.1 if projects span 3+ categories
    - Bonus: +0.1 if integration patterns described
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
    categories = set(p.get("category", "") for p in projects)
    if len(categories) >= 3:
        base_score = min(1.0, base_score + 0.1)
    
    # Integration patterns bonus
    integration_section = data.get("sections", {}).get("integration_patterns", "")
    if len(integration_section) > 500:  # Substantial integration section
        base_score = min(1.0, base_score + 0.1)
    
    return base_score
```

**Sub-Score 2: Technical Specificity (0-1.0)**
```python
def score_technical_specificity(data) -> float:
    """
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
    
    # Check for commands/code
    command_indicators = ["kubectl", "helm", "eksctl", "```", "argo", "terraform"]
    if any(indicator in all_text.lower() for indicator in command_indicators):
        score += 0.2
    
    # Check for version numbers
    import re
    version_pattern = r"v\d+\.\d+"
    if re.search(version_pattern, all_text):
        score += 0.2
    
    # Check for configuration (YAML/JSON keywords)
    config_indicators = ["apiVersion:", "kind:", "metadata:", "spec:", "replicas:", "nodeGroups:"]
    if any(indicator in all_text for indicator in config_indicators):
        score += 0.2
    
    # Check for specific technologies (not generic)
    specific_techs = ["envoy", "istio", "prometheus", "grafana", "argo", "flux", "calico"]
    if sum(1 for tech in specific_techs if tech in all_text.lower()) >= 3:
        score += 0.2
    
    # Check for technical patterns
    patterns = ["sidecar", "operator", "circuit breaker", "canary", "blue-green", "rolling"]
    if sum(1 for pattern in patterns if pattern in all_text.lower()) >= 2:
        score += 0.2
    
    return min(1.0, score)
```

**Sub-Score 3: Implementation Detail (0-1.0)**
```python
def score_implementation_detail(data) -> float:
    """
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
    
    # Phases/steps bonus
    if any(keyword in impl_section.lower() for keyword in ["phase", "step", "stage"]):
        score = min(1.0, score + 0.1)
    
    # Challenges/solutions bonus
    if any(keyword in impl_section.lower() for keyword in ["challenge", "issue", "problem", "solution"]):
        score = min(1.0, score + 0.1)
    
    return score
```

**Sub-Score 4: Metric Quality (0-1.0)**
```python
def score_metric_quality(data) -> float:
    """
    Scoring based on key metrics:
    - 4+ quantitative metrics: 1.0
    - 3 quantitative metrics: 0.8
    - 2 quantitative metrics: 0.6
    - 1 quantitative metric: 0.4
    - 0 quantitative metrics: 0.2
    - Bonus: +0.1 if metrics have before/after values
    - Bonus: +0.1 if metrics cover diverse categories (performance, reliability, cost)
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
    has_before_after = all("→" in m.get("improvement", "") for m in metrics)
    if has_before_after and num_metrics > 0:
        score = min(1.0, score + 0.1)
    
    # Diversity bonus (check if metrics cover different aspects)
    metric_text = " ".join(m.get("metric", "").lower() for m in metrics)
    categories = ["latency", "throughput", "error", "cost", "time", "frequency"]
    diverse = sum(1 for cat in categories if cat in metric_text) >= 2
    if diverse:
        score = min(1.0, score + 0.1)
    
    return score
```

**Sub-Score 5: Architecture Completeness (0-1.0)**
```python
def score_architecture_completeness(data) -> float:
    """
    Scoring based on architectural sections:
    - All sections present (13 sections): 1.0
    - 11-12 sections present: 0.8
    - 9-10 sections present: 0.6
    - 7-8 sections present: 0.4
    - < 7 sections present: 0.2
    - Bonus: +0.1 if architecture diagrams section is substantial (> 200 words)
    - Bonus: +0.1 if observability section is substantial (> 300 words)
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
```

**Other Validation Checks:**

| Check | Type | Exit Code if Failed |
|-------|------|-------------------|
| Total word count >= 2000 and <= 5000 | Critical | 2 |
| Total word count >= 2500 and <= 4500 | Warning | 1 |
| Technical depth score >= 0.70 | Pass | 0 |
| Technical depth score >= 0.60 and < 0.70 | Warning | 1 |
| Technical depth score < 0.60 | Critical | 2 |
| All required sections present | Critical | 2 |
| CNCF project list non-empty | Critical | 2 |

**Implementation Structure:**
```python
import json
import sys
import re
from typing import Dict, Any

def calculate_technical_depth_score(data: Dict[str, Any]) -> float:
    """Calculate overall technical depth score."""
    score1 = score_cncf_project_depth(data)
    score2 = score_technical_specificity(data)
    score3 = score_implementation_detail(data)
    score4 = score_metric_quality(data)
    score5 = score_architecture_completeness(data)
    
    overall = (
        0.25 * score1 +
        0.20 * score2 +
        0.20 * score3 +
        0.20 * score4 +
        0.15 * score5
    )
    
    return overall

def validate_reference_architecture(filepath: str) -> int:
    """
    Validate reference architecture JSON output.
    Returns: 0 (pass), 1 (warning), 2 (critical)
    """
    # Load JSON
    try:
        with open(filepath) as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Critical: Cannot load JSON: {e}", file=sys.stderr)
        return 2
    
    exit_code = 0
    
    # Check 1: Technical depth score
    tech_score = calculate_technical_depth_score(data)
    print(f"📊 Technical Depth Score: {tech_score:.2f}")
    
    if tech_score < 0.60:
        print("❌ Critical: Technical depth score below 0.60", file=sys.stderr)
        return 2
    elif tech_score < 0.70:
        print("⚠️ Warning: Technical depth score below 0.70 (acceptable but not ideal)", file=sys.stderr)
        exit_code = max(exit_code, 1)
    else:
        print("✅ Technical depth score meets standards")
    
    # Check 2: Word count
    all_text = " ".join(data.get("sections", {}).values())
    word_count = len(all_text.split())
    print(f"📝 Total Word Count: {word_count}")
    
    if word_count < 2000 or word_count > 5000:
        print(f"❌ Critical: Word count {word_count} outside range 2000-5000", file=sys.stderr)
        return 2
    elif word_count < 2500 or word_count > 4500:
        print(f"⚠️ Warning: Word count {word_count} outside ideal range 2500-4500", file=sys.stderr)
        exit_code = max(exit_code, 1)
    
    # Check 3: Required sections
    required_sections = [
        "executive_summary", "background", "technical_challenge",
        "architecture_overview", "cncf_projects", "implementation_details",
        "results_and_impact", "lessons_learned", "conclusion"
    ]
    sections = data.get("sections", {})
    for section in required_sections:
        if section not in sections:
            print(f"❌ Critical: Missing required section '{section}'", file=sys.stderr)
            return 2
    
    # Check 4: CNCF project list
    if not data.get("cncf_project_list"):
        print("❌ Critical: CNCF project list is empty", file=sys.stderr)
        return 2
    
    # Success
    if exit_code == 0:
        print("✅ Validation passed")
    
    return exit_code

def main():
    if len(sys.argv) != 2:
        print("Usage: python -m casestudypilot validate-reference-architecture <file.json>", file=sys.stderr)
        sys.exit(2)
    
    exit_code = validate_reference_architecture(sys.argv[1])
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
```

**Testing:**
- Test with high-quality reference architecture (tech score >= 0.75, should return 0)
- Test with medium-quality (tech score 0.65, should return 1)
- Test with low-quality (tech score 0.55, should return 2)
- Test with word count too low (< 2000, should return 2)
- Test with missing sections (should return 2)

---

### CLI Tool 3: assemble-reference-architecture

**Location:** `casestudypilot/tools/assemble_reference_architecture.py`  
**Status:** 🔴 TO BE CREATED

**Purpose:** Assemble final reference architecture markdown file using Jinja2 template, incorporating screenshots and diagram specifications.

**Command:**
```bash
python -m casestudypilot assemble-reference-architecture \
  reference_architecture.json \
  screenshots/*.jpg \
  --output reference-architectures/company-name.md
```

**Inputs:**
1. `reference_architecture.json` - Output from `reference-architecture-generation` skill
2. Screenshot files (6 images) - Output from `extract-screenshots` CLI tool
3. `--output` flag - Output file path

**Template:**
Uses Jinja2 template at `templates/reference_architecture.md.j2`

**Template Variables:**
```python
{
    "metadata": {
        "title": "...",
        "subtitle": "...",
        "company_name": "...",
        "industry": "...",
        "video_url": "...",
        "publication_date": "...",
        "tab_metadata": {...}
    },
    "sections": {
        "executive_summary": "...",
        "background": "...",
        ... (all 13 sections)
    },
    "cncf_project_list": [...],
    "key_metrics_summary": [...],
    "screenshots": [
        {
            "path": "images/company-name/screenshot-1.jpg",
            "caption": "Figure 1: ...",
            "section": "architecture_overview"
        }
    ],
    "diagram_specifications": {
        "diagrams": [...]
    }
}
```

**Implementation Pseudocode:**
```python
import json
import sys
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Any

def assemble_reference_architecture(
    json_path: str,
    screenshot_paths: List[str],
    output_path: str
) -> int:
    """
    Assemble final reference architecture markdown.
    Returns: 0 (success), 2 (error)
    """
    # Load JSON
    try:
        with open(json_path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON: {e}", file=sys.stderr)
        return 2
    
    # Prepare screenshots
    company_name = data["metadata"]["company_name"]
    company_slug = company_name.lower().replace(" ", "-").replace(".", "")
    
    screenshot_dir = Path(f"reference-architectures/images/{company_slug}")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    screenshots = []
    for i, screenshot_path in enumerate(screenshot_paths[:6], 1):  # Max 6
        # Copy screenshot
        dest_path = screenshot_dir / f"screenshot-{i}.jpg"
        shutil.copy(screenshot_path, dest_path)
        
        # Add to template data
        screenshots.append({
            "path": f"images/{company_slug}/screenshot-{i}.jpg",
            "caption": f"Figure {i}: [Auto-generated caption]",
            "section": "architecture_overview"  # Default, can be customized
        })
    
    data["screenshots"] = screenshots
    
    # Load Jinja2 template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("reference_architecture.md.j2")
    
    # Render template
    try:
        markdown = template.render(**data)
    except Exception as e:
        print(f"❌ Error rendering template: {e}", file=sys.stderr)
        return 2
    
    # Write output
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(markdown)
    
    print(f"✅ Reference architecture assembled: {output_path}")
    print(f"📸 {len(screenshots)} screenshots copied to {screenshot_dir}")
    
    return 0

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Assemble reference architecture markdown")
    parser.add_argument("json_file", help="Reference architecture JSON file")
    parser.add_argument("screenshots", nargs="+", help="Screenshot files (6 images)")
    parser.add_argument("--output", required=True, help="Output markdown file path")
    
    args = parser.parse_args()
    
    exit_code = assemble_reference_architecture(
        args.json_file,
        args.screenshots,
        args.output
    )
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
```

**Testing:**
- Test with valid JSON and 6 screenshots (should create markdown + copy images)
- Test with missing JSON file (should return 2)
- Test with invalid JSON (should return 2)
- Test with < 6 screenshots (should work but warn)
- Test with > 6 screenshots (should use first 6)

---

## One New Agent

### Agent: reference-architecture-agent

**Location:** `.github/agents/reference-architecture-agent.md`  
**Status:** 🔴 TO BE CREATED

**Version:** 1.0.0  
**Mission:** Automatically generate comprehensive reference architectures from YouTube videos for CNCF TAB submission

**Workflow:** 18 steps with 7 validation checkpoints

#### Full Workflow Specification

```markdown
---
name: reference-architecture-agent
description: Generate comprehensive reference architectures from YouTube videos for CNCF TAB submission
version: 1.0.0
trigger: GitHub issue with label "reference-architecture" and YouTube URL in body
---

# Reference Architecture Agent

## Mission
Automatically generate comprehensive reference architectures (2000-5000 words, 10 sections, 6 screenshots) from technical YouTube videos, suitable for CNCF Technical Advisory Board (TAB) submission.

## Workflow (18 Steps)

### Step 1: Pre-Flight Checks
**Objective:** Verify environment and inputs before starting.

```bash
# Check required tools
which python3
which yt-dlp
which ffmpeg

# Verify directory structure
ls casestudypilot/
ls templates/

# Extract video URL from issue
VIDEO_URL=$(gh issue view "$ISSUE_NUMBER" --json body --jq '.body' | grep -oP 'https://www\.youtube\.com/watch\?v=[^[:space:]]+' | head -1)

if [ -z "$VIDEO_URL" ]; then
  echo "❌ No YouTube URL found in issue"
  gh issue comment "$ISSUE_NUMBER" --body "❌ **Error:** No YouTube URL found in issue body. Please provide a YouTube URL."
  exit 2
fi
```

---

### Step 2: Fetch Video Data and Validate Transcript
**Objective:** Download video metadata and transcript, then validate quality.

```bash
# Fetch video data
python -m casestudypilot youtube-data "$VIDEO_URL" > video_data.json

# Validate transcript quality
python -m casestudypilot validate-transcript video_data.json
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  # CRITICAL failure - post error and STOP
  gh issue comment "$ISSUE_NUMBER" --body "❌ **Validation Failed: Transcript Quality**

The transcript is too short, empty, or unavailable.

**Critical Issues:**
- Transcript must be at least 2000 characters (current: $(jq -r '.transcript | length' video_data.json))
- Video must have captions enabled

**Possible Causes:**
- Video does not have captions/subtitles enabled
- Video is too short (< 10 minutes recommended for reference architectures)
- Captions are auto-generated and very poor quality

**Action Required:**
1. Verify the video has manually-created or high-quality auto-generated captions
2. Ensure video is at least 15-20 minutes long (reference architectures require substantial technical content)
3. If video is valid, try re-running this workflow

**For reference architectures, we recommend videos that:**
- Are 20-40 minutes long
- Have manually-created captions
- Include architecture diagrams and technical demos
- Feature engineers discussing implementation details"
  
  exit 2
elif [ $EXIT_CODE -eq 1 ]; then
  echo "⚠️ Warning: Transcript quality is below optimal but acceptable"
fi
```

**Checkpoint 1: Transcript Quality**
- Exit 0: Continue
- Exit 1: Log warning, continue
- Exit 2: Post error, STOP

---

### Step 3: Extract Company Name and Validate
**Objective:** Extract company name from video title/description and verify against CNCF companies list.

```bash
# Extract company name (heuristic: look for "Company at/using/with CNCF" patterns)
VIDEO_TITLE=$(jq -r '.title' video_data.json)
COMPANY_NAME=$(echo "$VIDEO_TITLE" | grep -oP '^[A-Z][a-zA-Z0-9\s]+(?=\sat\s|using|with|:|\s-\s)')

if [ -z "$COMPANY_NAME" ]; then
  echo "⚠️ Could not auto-extract company name from title: $VIDEO_TITLE"
  # Fallback: Use LLM to extract
  COMPANY_NAME="[Company Name]"  # To be extracted in transcript-deep-analysis
fi

# Validate company (will be done in Step 4 with transcript analysis)
```

---

### Step 4: Verify CNCF Membership (Optional)
**Objective:** Check if company is CNCF member (informational only, not blocking).

```bash
python -m casestudypilot cncf-member-check "$COMPANY_NAME"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ $COMPANY_NAME is a CNCF member"
elif [ $EXIT_CODE -eq 1 ]; then
  echo "ℹ️ $COMPANY_NAME is not a CNCF member (reference architecture can still be submitted)"
fi

# Non-blocking: continue regardless
```

---

### Step 5: Apply transcript-correction Skill
**Objective:** Correct transcript errors (typos, capitalization, CNCF project names).

**Use skill:** `transcript-correction` (existing skill, reused from case study agent)

**Input:**
```json
{
  "transcript": "<from video_data.json>",
  "video_title": "<from video_data.json>"
}
```

**Output:**
```json
{
  "corrected_transcript": "..."
}
```

Save to `transcript_corrected.json`

---

### Step 6: Apply transcript-deep-analysis Skill and Validate
**Objective:** Deep technical analysis to extract CNCF projects, architecture, patterns, metrics.

**Use skill:** `transcript-deep-analysis` (NEW)

**Input:**
```json
{
  "transcript": "<from transcript_corrected.json>",
  "video_title": "<from video_data.json>",
  "video_description": "<from video_data.json>",
  "duration_seconds": "<from video_data.json>",
  "company_name": "<extracted or '[Company Name]'>"
}
```

**Output:**
Save to `transcript_deep_analysis.json`

**Validation:**
```bash
python -m casestudypilot validate-deep-analysis transcript_deep_analysis.json
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  # CRITICAL failure - post error and STOP
  gh issue comment "$ISSUE_NUMBER" --body "❌ **Validation Failed: Deep Analysis**

The deep analysis did not extract sufficient technical content for a reference architecture.

**Critical Issues:**
$(python -m casestudypilot validate-deep-analysis transcript_deep_analysis.json 2>&1 | grep "❌")

**Requirements for Reference Architectures:**
- Minimum 5 CNCF projects (found: $(jq '.cncf_projects | length' transcript_deep_analysis.json))
- All 3 architecture layers documented (infrastructure, platform, application)
- At least 2 integration patterns described
- Technical metrics with supporting transcript quotes
- Minimum 6 screenshot opportunities

**Action Required:**
This video may not contain sufficient technical depth for a reference architecture. Reference architectures require:
- Detailed architecture discussion (not just high-level overview)
- Multiple CNCF projects working together
- Implementation details (not just concepts)
- Quantitative results and metrics

**Consider:**
- Using a different video with more technical depth
- Using the case-study-agent instead (for less technical content)
- Requesting the speaker provide a more detailed technical video"
  
  exit 2
elif [ $EXIT_CODE -eq 1 ]; then
  echo "⚠️ Warning: Deep analysis has minor issues but is acceptable"
fi
```

**Checkpoint 2: Deep Analysis Quality**
- Exit 0: Continue
- Exit 1: Log warning, continue
- Exit 2: Post error, STOP

---

### Step 7: Apply architecture-diagram-specification Skill
**Objective:** Generate textual diagram specifications for architecture diagrams.

**Use skill:** `architecture-diagram-specification` (NEW)

**Input:**
```json
{
  "deep_analysis": "<full content from transcript_deep_analysis.json>",
  "diagram_types": ["component", "data-flow"]
}
```

**Output:**
Save to `diagram_specifications.json`

**Note:** No validation checkpoint (validated contextually in next step)

---

### Step 8: Apply reference-architecture-generation Skill
**Objective:** Generate comprehensive 10-section reference architecture content.

**Use skill:** `reference-architecture-generation` (NEW)

**Input:**
```json
{
  "deep_analysis": "<from transcript_deep_analysis.json>",
  "diagram_specifications": "<from diagram_specifications.json>",
  "company_info": {
    "name": "<from deep analysis>",
    "industry": "<from deep analysis>",
    "verified_membership": "<from Step 4>"
  },
  "video_metadata": {
    "title": "<from video_data.json>",
    "url": "<VIDEO_URL>",
    "duration_seconds": "<from video_data.json>"
  }
}
```

**Output:**
Save to `reference_architecture.json`

---

### Step 9a: Validate Metrics (Fabrication Check)
**Objective:** Ensure all metrics have supporting transcript quotes (prevent fabrication).

```bash
python -m casestudypilot validate-metrics \
  reference_architecture.json \
  transcript_corrected.json
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  # CRITICAL: Metrics are fabricated
  gh issue comment "$ISSUE_NUMBER" --body "❌ **Validation Failed: Metric Fabrication Detected**

One or more metrics in the reference architecture cannot be verified against the transcript.

**Critical Issues:**
$(python -m casestudypilot validate-metrics reference_architecture.json transcript_corrected.json 2>&1 | grep "❌")

**This is a critical failure because:**
- Reference architectures submitted to CNCF TAB must be factually accurate
- All quantitative claims must be supported by source material
- Fabricated metrics damage credibility and can be rejected by TAB

**Action Required:**
This workflow has been stopped. Please:
1. Review the validation errors above
2. Verify all metrics are explicitly stated in the video
3. If metrics are vague in the video, this may not be suitable for a reference architecture
4. Consider re-running with a video that includes specific quantitative results"
  
  exit 2
elif [ $EXIT_CODE -eq 1 ]; then
  echo "⚠️ Warning: Some metrics are implied but not explicitly stated (acceptable with caution)"
fi
```

**Checkpoint 3: Metric Fabrication**
- Exit 0: Continue
- Exit 1: Log warning, continue
- Exit 2: Post error, STOP

---

### Step 9b: Validate Company Consistency
**Objective:** Ensure the reference architecture is about the correct company (prevent wrong-company hallucination).

```bash
python -m casestudypilot validate-consistency reference_architecture.json
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  # CRITICAL: Company mismatch
  gh issue comment "$ISSUE_NUMBER" --body "❌ **Validation Failed: Company Consistency**

The reference architecture content does not match the verified company name.

**Critical Issues:**
- Verified company: $(jq -r '.metadata.company_name' reference_architecture.json)
- Content appears to be about a different company

**This is a critical failure because:**
- This is the 'Spotify bug' - generating content about the wrong company
- Reference architecture must be factually accurate and about the correct organization
- Submitting incorrect attribution to CNCF TAB would be rejected

**Action Required:**
This workflow has been stopped. This is a bug in the content generation. Please:
1. Report this issue (this should not happen)
2. Re-run the workflow
3. If problem persists, manually review the video to ensure it's about the stated company"
  
  exit 2
fi
```

**Checkpoint 4: Company Consistency**
- Exit 0: Continue
- Exit 2: Post error, STOP (no warning level for this check)

---

### Step 10: Extract Screenshots
**Objective:** Extract 6 screenshots from video at timestamps identified in deep analysis.

```bash
# Extract top 6 high-priority screenshot opportunities
TIMESTAMPS=$(jq -r '.screenshot_opportunities | sort_by(.priority) | reverse | .[0:6] | .[].timestamp_seconds' transcript_deep_analysis.json)

mkdir -p screenshots/

# Extract screenshots using ffmpeg
i=1
for timestamp in $TIMESTAMPS; do
  python -m casestudypilot extract-screenshot \
    "$VIDEO_URL" \
    "$timestamp" \
    "screenshots/screenshot-$i.jpg"
  i=$((i + 1))
done

echo "✅ Extracted $(ls screenshots/*.jpg | wc -l) screenshots"
```

---

### Step 11: Assemble Final Markdown
**Objective:** Combine reference architecture JSON and screenshots into final markdown file.

```bash
COMPANY_NAME=$(jq -r '.metadata.company_name' reference_architecture.json)
COMPANY_SLUG=$(echo "$COMPANY_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -d '.')

OUTPUT_FILE="reference-architectures/${COMPANY_SLUG}.md"

python -m casestudypilot assemble-reference-architecture \
  reference_architecture.json \
  screenshots/*.jpg \
  --output "$OUTPUT_FILE"

if [ $? -ne 0 ]; then
  echo "❌ Failed to assemble reference architecture"
  exit 2
fi

echo "✅ Reference architecture assembled: $OUTPUT_FILE"
```

---

### Step 12: Validate Final Quality
**Objective:** Final validation with technical depth scoring.

```bash
python -m casestudypilot validate-reference-architecture reference_architecture.json
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  # CRITICAL: Quality too low
  gh issue comment "$ISSUE_NUMBER" --body "❌ **Validation Failed: Technical Depth**

The reference architecture does not meet minimum quality standards for CNCF TAB submission.

**Quality Metrics:**
$(python -m casestudypilot validate-reference-architecture reference_architecture.json 2>&1 | grep "📊\|📝")

**Critical Issues:**
$(python -m casestudypilot validate-reference-architecture reference_architecture.json 2>&1 | grep "❌")

**Requirements:**
- Technical depth score >= 0.70 (measures CNCF project depth, technical specificity, implementation detail, metric quality, architecture completeness)
- Word count: 2000-5000 words
- All required sections present

**Action Required:**
The generated content is below quality standards. This may be due to:
- Video lacks sufficient technical depth
- Video is too short or high-level
- Transcript quality is poor

**Options:**
1. Try a different video with more technical content
2. Use case-study-agent for less technical content
3. Manually enhance the generated content

**Note:** Reference architectures are held to higher standards than case studies because they are submitted to CNCF TAB for official review."
  
  exit 2
elif [ $EXIT_CODE -eq 1 ]; then
  echo "⚠️ Warning: Technical depth score is acceptable but below ideal (0.60-0.70)"
  # Continue - user can decide whether to accept or regenerate
fi
```

**Checkpoint 5: Final Quality**
- Exit 0: Continue
- Exit 1: Log warning, continue
- Exit 2: Post error, STOP

---

### Step 13: Create Branch
**Objective:** Create a feature branch for the reference architecture.

```bash
BRANCH_NAME="reference-architecture/${COMPANY_SLUG}"

git checkout -b "$BRANCH_NAME"

echo "✅ Created branch: $BRANCH_NAME"
```

---

### Step 14: Commit Files (Atomic Commit)
**Objective:** Commit reference architecture markdown and 6 screenshots in a single atomic commit.

```bash
# Add markdown file
git add "$OUTPUT_FILE"

# Add screenshots
git add "reference-architectures/images/${COMPANY_SLUG}/*.jpg"

# Create commit
git commit -m "Add reference architecture for $COMPANY_NAME with 6 screenshots

- Generated from YouTube video: $VIDEO_URL
- 10 sections, $(jq -r '.cncf_project_list | length' reference_architecture.json) CNCF projects
- Technical depth score: $(python -m casestudypilot validate-reference-architecture reference_architecture.json 2>&1 | grep -oP 'Technical Depth Score: \K[0-9.]+')
- Word count: $(jq -r '.sections | to_entries | map(.value | split(\" \") | length) | add' reference_architecture.json)

Co-authored-by: reference-architecture-agent <agent@casestudypilot>"

if [ $? -ne 0 ]; then
  echo "❌ Failed to commit files"
  exit 2
fi

echo "✅ Committed reference architecture and screenshots"
```

---

### Step 15: Push Branch
**Objective:** Push feature branch to remote repository.

```bash
git push -u origin "$BRANCH_NAME"

if [ $? -ne 0 ]; then
  echo "❌ Failed to push branch"
  exit 2
fi

echo "✅ Pushed branch: $BRANCH_NAME"
```

---

### Step 16: Create Pull Request with TAB Guidance
**Objective:** Create PR with reference architecture and include CNCF TAB submission guidance.

```bash
PR_TITLE="Add reference architecture for $COMPANY_NAME"

# Read TAB submission template
TAB_GUIDANCE=$(cat <<'EOF'
## CNCF TAB Submission Guidance

This reference architecture is ready for submission to the CNCF Technical Advisory Board (TAB) for review and potential inclusion in the official CNCF reference architectures repository.

### TAB Submission Process

1. **Review this PR**: Ensure the reference architecture meets quality standards
2. **Merge to main**: Once approved, merge this PR
3. **Create TAB Issue**: Go to https://github.com/cncf/tab/issues/new
4. **Use Template**: Select "Reference Architecture Submission" template
5. **Fill Details**:
   - **Title**: Reference Architecture: [Company Name] - [Brief Description]
   - **Company**: [Company Name]
   - **Industry**: [Industry]
   - **CNCF Projects**: [List from this reference architecture]
   - **Link**: Link to merged reference architecture in main branch
   - **Significance**: [From metadata.tab_metadata.architectural_significance]
6. **Submit**: TAB will review within 2-4 weeks

### TAB Review Stages

Reference architectures go through these stages:
- **Proposed** ← (You submit here)
- **Accepted** (TAB approves for review)
- **Reviewed** (Technical review complete)
- **Validated** (TOC validates)
- **Published** (Added to CNCF website)
- **Announced** (Promoted via CNCF channels)

### What TAB Reviews

- **Technical Accuracy**: Are CNCF projects used correctly?
- **Architectural Soundness**: Is the architecture well-designed?
- **Reproducibility**: Can others learn from this?
- **Significance**: Is this architecturally interesting or novel?

### Quality Metrics for This Reference Architecture

$(python -m casestudypilot validate-reference-architecture reference_architecture.json 2>&1 | grep "📊\|📝")

**Technical Depth Sub-Scores:**
- CNCF Project Depth: [from validation]
- Technical Specificity: [from validation]
- Implementation Detail: [from validation]
- Metric Quality: [from validation]
- Architecture Completeness: [from validation]

### Links

- TAB Reference Architecture Process: https://github.com/cncf/tab/blob/main/process/reference-architectures.md
- CNCF TAB Repo: https://github.com/cncf/tab
- TAB Meeting Schedule: https://github.com/cncf/tab#meetings
EOF
)

# Create PR with guidance
gh pr create \
  --title "$PR_TITLE" \
  --body "$(cat <<EOF
## Summary

Generated comprehensive reference architecture for **$COMPANY_NAME** from technical YouTube video.

**Video**: $VIDEO_URL

## Reference Architecture Details

- **Sections**: 10 (executive summary, background, technical challenge, architecture overview, architecture diagrams, CNCF projects, integration patterns, implementation details, deployment architecture, observability & operations, results & impact, lessons learned, conclusion)
- **Word Count**: $(jq -r '.sections | to_entries | map(.value | split(\" \") | length) | add' reference_architecture.json) words
- **CNCF Projects**: $(jq -r '.cncf_project_list | length' reference_architecture.json) projects
- **Screenshots**: 6 screenshots extracted from video
- **Technical Depth Score**: $(python -m casestudypilot validate-reference-architecture reference_architecture.json 2>&1 | grep -oP 'Technical Depth Score: \K[0-9.]+')

## CNCF Projects Featured

$(jq -r '.cncf_project_list[] | "- **\(.name)** (\(.category)): \(.usage_summary)"' reference_architecture.json)

## Key Metrics

$(jq -r '.key_metrics_summary[] | "- **\(.metric)**: \(.improvement) → \(.business_impact)"' reference_architecture.json)

## Validation Results

All validation checkpoints passed:
- ✅ Transcript quality (>2000 chars)
- ✅ Deep analysis quality (5+ CNCF projects, 3 architecture layers, 2+ integration patterns)
- ✅ Metric fabrication check (all metrics have transcript quotes)
- ✅ Company consistency check (content matches verified company)
- ✅ Final technical depth (score >= 0.70)

---

$TAB_GUIDANCE
EOF
)" \
  --base main \
  --head "$BRANCH_NAME"

PR_URL=$(gh pr view --json url --jq '.url')

if [ $? -ne 0 ]; then
  echo "❌ Failed to create PR"
  exit 2
fi

echo "✅ Created PR: $PR_URL"
```

---

### Step 17: Post Success to Issue
**Objective:** Inform user that reference architecture has been generated and PR created.

```bash
gh issue comment "$ISSUE_NUMBER" --body "✅ **Reference Architecture Generated Successfully**

Your reference architecture for **$COMPANY_NAME** has been generated and is ready for review.

**Pull Request**: $PR_URL

## What's Included

- 📄 **Reference Architecture**: $(jq -r '.metadata.title' reference_architecture.json)
- 📊 **CNCF Projects**: $(jq -r '.cncf_project_list | length' reference_architecture.json) projects ($(jq -r '.cncf_project_list[0:3] | map(.name) | join(\", \")' reference_architecture.json), ...)
- 📝 **Word Count**: $(jq -r '.sections | to_entries | map(.value | split(\" \") | length) | add' reference_architecture.json) words
- 📸 **Screenshots**: 6 screenshots from video
- 🎯 **Technical Depth Score**: $(python -m casestudypilot validate-reference-architecture reference_architecture.json 2>&1 | grep -oP 'Technical Depth Score: \K[0-9.]+') / 1.00

## Next Steps

1. **Review the PR**: Check the generated reference architecture for accuracy
2. **Request changes if needed**: Comment on the PR with requested edits
3. **Merge when ready**: Once satisfied, merge the PR to main
4. **Submit to CNCF TAB**: Follow the guidance in the PR description to submit to TAB

## CNCF TAB Submission

This reference architecture meets the quality standards for CNCF TAB submission. After merging, you can submit it to the TAB by creating an issue at: https://github.com/cncf/tab/issues/new

See the PR description for complete submission instructions.

---

Thank you for contributing to the CNCF reference architecture collection! 🎉"

# Add label
gh issue edit "$ISSUE_NUMBER" --add-label "reference-architecture-generated"
```

---

### Step 18: Cleanup
**Objective:** Clean up temporary files.

```bash
rm -f video_data.json transcript_corrected.json transcript_deep_analysis.json diagram_specifications.json reference_architecture.json
rm -rf screenshots/

echo "✅ Cleanup complete"
```

---

## Error Handling

### Error Templates

**Error Template 1: Transcript Too Short**
```markdown
❌ **Validation Failed: Transcript Quality**

The transcript is too short or empty for a reference architecture.

**Critical Issues:**
- Transcript length: [X] characters (minimum: 2000)

**Action Required:**
Reference architectures require substantial technical content. Please:
- Ensure video is at least 20 minutes long
- Verify video has captions enabled
- Check that video includes architecture discussion and implementation details

For shorter or less technical videos, consider using the `case-study` label instead.
```

**Error Template 2: Insufficient CNCF Projects**
```markdown
❌ **Validation Failed: Deep Analysis**

The deep analysis did not extract sufficient CNCF projects for a reference architecture.

**Critical Issues:**
- CNCF projects found: [X] (minimum: 5)

**Action Required:**
Reference architectures must feature at least 5 CNCF projects working together. This video may not be suitable. Consider:
- Using a different video that discusses more CNCF projects
- Using the case-study-agent for content featuring fewer projects
```

**Error Template 3: Low Technical Depth**
```markdown
❌ **Validation Failed: Technical Depth**

The reference architecture does not meet minimum technical depth score.

**Quality Metrics:**
- Technical depth score: [X] (minimum: 0.70)
- Word count: [X] words

**Sub-Scores:**
- CNCF Project Depth: [X]
- Technical Specificity: [X]
- Implementation Detail: [X]
- Metric Quality: [X]
- Architecture Completeness: [X]

**Action Required:**
The content is below quality standards for CNCF TAB submission. Options:
1. Use a more technical video with implementation details
2. Use case-study-agent for less technical content
3. Manually enhance the generated content
```

---

## Quality Standards

### Technical Depth Score >= 0.70

The technical depth score is calculated as a weighted average of 5 sub-scores:
- **CNCF Project Depth** (25%): Number and detail of CNCF projects
- **Technical Specificity** (20%): Commands, configs, versions, tools
- **Implementation Detail** (20%): Implementation section depth and challenges
- **Metric Quality** (20%): Number and quality of quantitative metrics
- **Architecture Completeness** (15%): Number of sections and diagram depth

### Word Count: 2000-5000 words

Total across all sections. Ideal range: 2500-4500 words.

### CNCF Projects: Minimum 5

At least 5 CNCF projects must be featured with detailed usage contexts.

### Screenshots: 6 images

Extracted from video at key architectural discussion points.

### All Metrics Have Transcript Quotes

Every quantitative metric must be supported by an exact quote from the transcript (fabrication prevention).

---

## Success Criteria

✅ **Reference architecture generated successfully if:**
1. All 7 validation checkpoints passed (or warnings only)
2. Technical depth score >= 0.70
3. Word count 2000-5000 words
4. 5+ CNCF projects documented
5. 6 screenshots extracted
6. PR created with TAB submission guidance
7. Issue updated with success message

---

**Version History:**
- 1.0.0 (2026-02-09): Initial agent workflow for reference architecture generation

**Related Agents:**
- `case-study-agent`: Shorter, less technical content (500-1500 words, 5 sections)

**Related Skills:**
- `transcript-correction` (reused)
- `transcript-deep-analysis` (new)
- `architecture-diagram-specification` (new)
- `reference-architecture-generation` (new)

**Related CLI Tools:**
- `youtube-data` (reused)
- `validate-transcript` (reused)
- `validate-company` (reused)
- `cncf-member-check` (reused)
- `extract-screenshot` (reused)
- `validate-deep-analysis` (new)
- `validate-metrics` (reused with new threshold)
- `validate-consistency` (reused)
- `validate-reference-architecture` (new)
- `assemble-reference-architecture` (new)
```

Save this as `.github/agents/reference-architecture-agent.md`

---

## Templates and Supporting Files

### Template: reference_architecture.md.j2

**Location:** `templates/reference_architecture.md.j2`  
**Status:** 🔴 TO BE CREATED

**Purpose:** Jinja2 template for assembling final reference architecture markdown.

**Template Structure:**

```jinja2
---
title: "{{ metadata.title }}"
subtitle: "{{ metadata.subtitle }}"
company: "{{ metadata.company_name }}"
industry: "{{ metadata.industry }}"
video_url: "{{ metadata.video_url }}"
publication_date: "{{ metadata.publication_date }}"
tab_status: "proposed"
primary_patterns: {{ metadata.tab_metadata.primary_patterns | tojson }}
---

# {{ metadata.title }}

> {{ metadata.subtitle }}

**Company:** {{ metadata.company_name }}  
**Industry:** {{ metadata.industry }}  
**Video:** [Watch on YouTube]({{ metadata.video_url }})  
**Publication Date:** {{ metadata.publication_date }}

---

## Executive Summary

{{ sections.executive_summary }}

---

## Background

{{ sections.background }}

---

## Technical Challenge

{{ sections.technical_challenge }}

---

## Architecture Overview

{{ sections.architecture_overview }}

{% if screenshots %}
{% for screenshot in screenshots %}
{% if screenshot.section == "architecture_overview" %}
![{{ screenshot.caption }}]({{ screenshot.path }})
*{{ screenshot.caption }}*
{% endif %}
{% endfor %}
{% endif %}

---

## Architecture Diagrams

{{ sections.architecture_diagrams }}

{% if diagram_specifications and diagram_specifications.diagrams %}
{% for diagram in diagram_specifications.diagrams %}
### {{ diagram.title }}

{{ diagram.description }}

**Components:**
{% for component in diagram.components %}
- **{{ component.label }}** ({{ component.type }}): {{ component.description }}
  {% if component.cncf_projects %}{% for project in component.cncf_projects %}`{{ project }}`{% if not loop.last %}, {% endif %}{% endfor %}{% endif %}
{% endfor %}

**Connections:**
{% for conn in diagram.connections %}
- {{ conn.from_id }} → {{ conn.to_id }}: {{ conn.label }} ({{ conn.protocol }})
{% endfor %}

{% endfor %}
{% endif %}

---

## CNCF Projects

{{ sections.cncf_projects }}

{% if cncf_project_list %}
### Project Summary

| Project | Category | Usage |
|---------|----------|-------|
{% for project in cncf_project_list %}
| {{ project.name }} | {{ project.category }} | {{ project.usage_summary }} |
{% endfor %}
{% endif %}

---

## Integration Patterns

{{ sections.integration_patterns }}

---

## Implementation Details

{{ sections.implementation_details }}

{% if screenshots %}
{% for screenshot in screenshots %}
{% if screenshot.section == "implementation_details" %}
![{{ screenshot.caption }}]({{ screenshot.path }})
*{{ screenshot.caption }}*
{% endif %}
{% endfor %}
{% endif %}

---

## Deployment Architecture

{{ sections.deployment_architecture }}

---

## Observability and Operations

{{ sections.observability_operations }}

{% if screenshots %}
{% for screenshot in screenshots %}
{% if screenshot.section == "observability_operations" %}
![{{ screenshot.caption }}]({{ screenshot.path }})
*{{ screenshot.caption }}*
{% endif %}
{% endfor %}
{% endif %}

---

## Results and Impact

{{ sections.results_and_impact }}

{% if key_metrics_summary %}
### Key Metrics

| Metric | Improvement | Business Impact |
|--------|-------------|-----------------|
{% for metric in key_metrics_summary %}
| {{ metric.metric }} | {{ metric.improvement }} | {{ metric.business_impact }} |
{% endfor %}
{% endif %}

---

## Lessons Learned

{{ sections.lessons_learned }}

---

## Conclusion

{{ sections.conclusion }}

---

## About This Reference Architecture

**Generated by:** [casestudypilot](https://github.com/cncf/casestudypilot) reference-architecture-agent v1.0.0  
**Source Video:** [{{ metadata.video_url }}]({{ metadata.video_url }})  
**TAB Status:** Proposed (pending submission)  
**Architectural Significance:** {{ metadata.tab_metadata.architectural_significance }}

### CNCF TAB Submission

This reference architecture is ready for submission to the CNCF Technical Advisory Board. To submit:

1. Review this reference architecture for technical accuracy
2. Create an issue at: https://github.com/cncf/tab/issues/new
3. Select "Reference Architecture Submission" template
4. Provide link to this reference architecture
5. TAB will review within 2-4 weeks

For more information on the TAB review process, see: https://github.com/cncf/tab/blob/main/process/reference-architectures.md

---

## License

This reference architecture is licensed under the Creative Commons Attribution 4.0 International License.  
© {{ metadata.publication_date }} Cloud Native Computing Foundation
```

**Variables Used:**
- `metadata.title`, `metadata.subtitle`, `metadata.company_name`, `metadata.industry`
- `metadata.video_url`, `metadata.publication_date`
- `metadata.tab_metadata.primary_patterns`, `metadata.tab_metadata.architectural_significance`
- `sections.*` (all 13 sections)
- `cncf_project_list[]` (array of CNCF project summaries)
- `key_metrics_summary[]` (array of metric summaries)
- `screenshots[]` (array of screenshot paths and captions)
- `diagram_specifications.diagrams[]` (array of diagram specs)

**Template Features:**
- YAML frontmatter with metadata
- 13 sections with auto-generated headings
- Screenshot insertion based on section association
- CNCF project summary table
- Key metrics summary table
- Diagram component/connection listings
- TAB submission guidance footer

---

## Implementation Phases

### Phase 1: Foundation (Days 1-2)

**Objective:** Set up directory structure and module stubs.

**Tasks:**
1. Create `reference-architectures/` directory
2. Create `reference-architectures/images/` directory
3. Create `.github/skills/transcript-deep-analysis/` directory
4. Create `.github/skills/architecture-diagram-specification/` directory
5. Create `.github/skills/reference-architecture-generation/` directory
6. Create Python module stubs:
   - `casestudypilot/tools/validate_deep_analysis.py`
   - `casestudypilot/tools/validate_reference_architecture.py`
   - `casestudypilot/tools/assemble_reference_architecture.py`
7. Create test structure:
   - `tests/test_validate_deep_analysis.py`
   - `tests/test_validate_reference_architecture.py`
   - `tests/test_assemble_reference_architecture.py`
8. Update `casestudypilot/__main__.py` to register new CLI commands

**Validation:**
- Directory structure exists
- Python modules importable (even if empty)
- Test files created

---

### Phase 2: LLM Skills (Days 3-6)

**Objective:** Write comprehensive SKILL.md files for all 3 skills.

**Tasks:**
1. **Day 3-4:** Write `.github/skills/transcript-deep-analysis/SKILL.md`
   - ✅ Already created in `docs/skills/transcript-deep-analysis.md`
   - Copy to `.github/skills/transcript-deep-analysis/SKILL.md`
2. **Day 4-5:** Write `.github/skills/architecture-diagram-specification/SKILL.md`
   - ✅ Already created in `docs/skills/architecture-diagram-specification.md`
   - Copy to `.github/skills/architecture-diagram-specification/SKILL.md`
3. **Day 5-6:** Write `.github/skills/reference-architecture-generation/SKILL.md`
   - Use specification from this guide (Section "Skill 3")
   - 800-1000 lines with complete instructions and examples

**Validation:**
- Each SKILL.md is 400-1000 lines
- Input/output JSON schemas defined
- Execution instructions step-by-step
- Examples provided (2-3 per skill)
- Quality guidelines documented

---

### Phase 3: CLI Tools (Days 7-10)

**Objective:** Implement and test all 3 CLI tools.

**Tasks:**
1. **Day 7:** Implement `validate-deep-analysis.py`
   - Use pseudocode from this guide
   - Implement all validation checks
   - Write unit tests
   - Test with valid/invalid inputs
2. **Day 8-9:** Implement `validate-reference-architecture.py`
   - Implement technical depth scoring algorithm
   - Implement all 5 sub-score functions
   - Implement word count validation
   - Write unit tests for each sub-score
   - Write integration tests with sample reference architectures
3. **Day 10:** Implement `assemble-reference-architecture.py`
   - Use pseudocode from this guide
   - Implement Jinja2 template rendering
   - Implement screenshot copying
   - Write unit tests
   - Test with sample JSON and images

**Validation:**
- All CLI tools have exit codes 0/1/2
- All CLI tools have comprehensive unit tests
- `pytest tests/` passes 100%
- Manual testing with sample data successful

---

### Phase 4: Template (Day 11)

**Objective:** Create Jinja2 template for reference architectures.

**Tasks:**
1. Create `templates/reference_architecture.md.j2`
   - Use template from this guide (Section "Templates")
   - 200-300 lines with all sections
2. Test template rendering with sample data
3. Verify markdown output is valid
4. Verify screenshots are embedded correctly

**Validation:**
- Template renders without errors
- Output markdown is valid
- All sections present
- YAML frontmatter correct

---

### Phase 5: Agent Workflow (Days 12-13)

**Objective:** Create agent workflow specification.

**Tasks:**
1. **Day 12:** Create `.github/agents/reference-architecture-agent.md`
   - Use specification from this guide (Section "One New Agent")
   - Copy full 18-step workflow
   - Include all error templates
2. **Day 13:** Test agent workflow manually with real YouTube video
   - Walk through all 18 steps
   - Verify validation checkpoints work
   - Verify error templates are correct
   - Fix any issues discovered

**Validation:**
- Agent workflow file is complete (600-800 lines)
- Manual test produces valid reference architecture
- All validation checkpoints work correctly
- PR is created with TAB guidance

---

### Phase 6: Documentation (Days 14-15)

**Objective:** Update all documentation and create guides.

**Tasks:**
1. **Day 14:** Update existing documentation
   - Update `README.md`:
     - Add reference architectures section
     - Add new CLI commands
     - Update architecture diagram
   - Update `AGENTS.md`:
     - Add reference-architecture-agent section
     - Add patterns for reference architectures
     - Update examples
   - Update `CONTRIBUTING.md`:
     - Add instructions for creating reference architectures
     - Add testing procedures for new components
2. **Day 15:** Create new documentation
   - Create `docs/REFERENCE-ARCHITECTURE-WORKFLOW.md`:
     - User-facing guide for generating reference architectures
     - Troubleshooting common issues
     - Quality standards explained
   - Create `docs/CASE-STUDY-VS-REFERENCE-ARCHITECTURE.md`:
     - Comparison table
     - When to use which
     - Quality standards comparison
   - Create `.github/ISSUE_TEMPLATE/reference-architecture.md`:
     - GitHub issue template for reference architecture requests

**Validation:**
- All documentation updated
- New guides created
- Documentation is consistent
- Links work correctly

---

### Phase 7: Testing and Finalization (Days 16-18)

**Objective:** Integration testing, quality validation, and finalization.

**Tasks:**
1. **Day 16:** Integration testing with 3 real videos
   - Select 3 diverse technical videos (different CNCF projects, industries)
   - Run full agent workflow for each
   - Verify quality of generated reference architectures
   - Fix any issues discovered
2. **Day 17:** Quality validation
   - Review all 3 generated reference architectures manually
   - Verify technical accuracy
   - Verify CNCF project usage is correct
   - Verify metrics are not fabricated
   - Get peer review from another engineer
3. **Day 18:** Finalization
   - Update `CHANGELOG.md` with version 3.0.0 changes
   - Create git tag `v3.0.0`
   - Generate example reference architecture for repository
   - Write release notes
   - Prepare launch announcement

**Validation:**
- 3 high-quality reference architectures generated
- All tests pass (`pytest tests/` = 100%)
- Manual review confirms quality
- Documentation is complete and accurate
- Version 3.0.0 tagged and ready for release

---

## Testing Strategy

### Unit Testing

**Test Files:**
- `tests/test_validate_deep_analysis.py` (10+ test cases)
- `tests/test_validate_reference_architecture.py` (20+ test cases for scoring)
- `tests/test_assemble_reference_architecture.py` (8+ test cases)

**Test Cases for validate-deep-analysis:**
1. Valid deep analysis (should return 0)
2. 4 CNCF projects (should return 1)
3. 3 CNCF projects (should return 2)
4. Missing infrastructure layer (should return 2)
5. Missing platform layer (should return 2)
6. Missing application layer (should return 2)
7. 1 integration pattern (should return 1)
8. 0 integration patterns (should return 2)
9. Metrics without transcript quotes (should return 2)
10. 5 screenshot opportunities (should return 1)
11. 3 screenshot opportunities (should return 2)
12. Missing sections (should return 2)
13. Section word count too low (should return 1)

**Test Cases for validate-reference-architecture:**
1. High-quality reference architecture (tech score 0.80, should return 0)
2. Medium-quality (tech score 0.68, should return 1)
3. Low-quality (tech score 0.55, should return 2)
4. Word count too low < 2000 (should return 2)
5. Word count too high > 5000 (should return 2)
6. Word count below ideal < 2500 (should return 1)
7. Missing required sections (should return 2)
8. Empty CNCF project list (should return 2)
9. Test each sub-score function individually:
   - `score_cncf_project_depth()` with 1, 3, 5, 7 projects
   - `score_technical_specificity()` with varying technical indicators
   - `score_implementation_detail()` with 200, 400, 600, 800 word sections
   - `score_metric_quality()` with 0, 1, 3, 5 metrics
   - `score_architecture_completeness()` with 6, 9, 11, 13 sections

**Test Cases for assemble-reference-architecture:**
1. Valid JSON + 6 screenshots (should create markdown + copy images)
2. Missing JSON file (should return 2)
3. Invalid JSON (should return 2)
4. 4 screenshots (should warn but continue)
5. 8 screenshots (should use first 6)
6. Screenshot file doesn't exist (should return 2)
7. Output directory doesn't exist (should create)
8. Template rendering error (should return 2)

### Integration Testing

**Integration Test 1: E-commerce Company (Kubernetes + Istio + Argo CD)**
- **Video:** Find 20-30 min technical talk about e-commerce using Kubernetes, Istio, Argo CD
- **Expected Output:**
  - 2500-4000 words
  - 5+ CNCF projects (Kubernetes, Istio, Envoy, Argo CD, Prometheus)
  - Technical depth score >= 0.72
  - Component diagram + data flow diagram
  - 6 screenshots
- **Validation:** Manual review for technical accuracy

**Integration Test 2: Financial Services (Multi-Cluster Kubernetes + Service Mesh)**
- **Video:** Find technical talk about financial services using multi-cluster Kubernetes
- **Expected Output:**
  - 3000-4500 words
  - 6+ CNCF projects
  - Technical depth score >= 0.75
  - Component diagram + deployment diagram
  - 6 screenshots
- **Validation:** Verify multi-cluster deployment described correctly

**Integration Test 3: Media/Streaming Company (Event-Driven + Observability)**
- **Video:** Find talk about media/streaming using event-driven architecture with strong observability
- **Expected Output:**
  - 2800-4200 words
  - 5+ CNCF projects (Kubernetes, Kafka, Prometheus, Grafana, Jaeger)
  - Technical depth score >= 0.70
  - Data flow diagram + component diagram
  - 6 screenshots
- **Validation:** Verify event-driven patterns correctly described

### Manual Testing Checklist

For each integration test, manually verify:

**Content Quality:**
- [ ] All CNCF project names are correct (not hallucinated)
- [ ] Metrics have supporting quotes (check against transcript)
- [ ] Company name is consistent throughout
- [ ] Architecture description matches video content
- [ ] Implementation details are specific (not generic)
- [ ] Lessons learned are insightful (not boilerplate)

**Technical Accuracy:**
- [ ] CNCF project usage is plausible (not "Kubernetes for databases")
- [ ] Integration patterns make technical sense
- [ ] Architecture layers are correctly organized
- [ ] Diagram specifications are technically sound
- [ ] Metrics are realistic (not "1000x improvement")

**Quality Standards:**
- [ ] Word count in range (2000-5000)
- [ ] Technical depth score >= 0.70
- [ ] All 10 sections present
- [ ] 6 screenshots extracted
- [ ] Markdown renders correctly
- [ ] Screenshots display correctly

**TAB Readiness:**
- [ ] Content is suitable for engineers/architects (not marketing)
- [ ] Architecture is interesting/novel (not trivial)
- [ ] Implementation is reproducible (specific enough)
- [ ] Results are quantitative (not vague "better performance")

### Performance Testing

**Benchmarks:**
- Full workflow (18 steps) should complete in < 15 minutes for 30-minute video
- `validate-deep-analysis` should complete in < 1 second
- `validate-reference-architecture` should complete in < 2 seconds (scoring is compute-intensive)
- `assemble-reference-architecture` should complete in < 3 seconds

**Test with Videos of Varying Lengths:**
- 15-minute video: Should complete in ~10 minutes
- 30-minute video: Should complete in ~15 minutes
- 60-minute video: Should complete in ~25 minutes

---

## Success Criteria

### Must Have (Required for v3.0.0 Release)

1. ✅ All 3 skills documented and functional
   - `transcript-deep-analysis` extracts 5+ CNCF projects
   - `architecture-diagram-specification` generates 2+ diagrams
   - `reference-architecture-generation` produces 10-section content
2. ✅ All 3 CLI tools implemented and tested
   - `validate-deep-analysis` has 13+ test cases
   - `validate-reference-architecture` has 20+ test cases with scoring
   - `assemble-reference-architecture` creates markdown with screenshots
3. ✅ Reference architecture agent (18-step workflow) functional
   - All 7 validation checkpoints work
   - All error templates tested
   - PR creation with TAB guidance works
4. ✅ Template renders correctly
   - All sections present
   - Screenshots embedded
   - Diagram specs included
   - TAB metadata in frontmatter
5. ✅ Integration testing successful (3 real videos)
   - All 3 generate high-quality reference architectures
   - Technical depth scores >= 0.70
   - No fabricated content
6. ✅ Documentation complete
   - README.md updated
   - AGENTS.md updated
   - New guides created
   - Issue template created
7. ✅ All tests pass (`pytest tests/` = 100% pass)

### Should Have (Desirable for v3.0.0)

1. ✅ Technical depth scoring algorithm validated
   - Tested with 10+ sample reference architectures
   - Sub-scores correlate with manual quality assessment
2. ✅ GitHub Actions workflow for automated testing
   - Run tests on every commit
   - Run integration tests on PR creation
3. ✅ Example reference architecture in repository
   - Demonstrates high-quality output
   - Shows all sections and features
4. ✅ CHANGELOG.md comprehensive
   - All changes documented
   - Migration guide from v2.x

### Nice to Have (Post-v3.0.0)

1. ⭕ Mermaid diagram code generation (not just textual specs)
2. ⭕ PlantUML diagram code generation
3. ⭕ Automatic TAB issue creation (not just guidance)
4. ⭕ Multi-language support (generate in multiple languages)
5. ⭕ Video selection recommendations (analyze multiple videos, pick best)
6. ⭕ Automated follow-up: Check TAB issue status and update PR

---

## Appendix A: File Checklist

Use this checklist to track implementation progress:

### Skills
- [ ] `.github/skills/transcript-deep-analysis/SKILL.md` (400-600 lines)
- [ ] `.github/skills/architecture-diagram-specification/SKILL.md` (400-600 lines)
- [ ] `.github/skills/reference-architecture-generation/SKILL.md` (800-1000 lines)

### CLI Tools
- [ ] `casestudypilot/tools/validate_deep_analysis.py` (150-200 lines)
- [ ] `casestudypilot/tools/validate_reference_architecture.py` (300-400 lines with scoring)
- [ ] `casestudypilot/tools/assemble_reference_architecture.py` (100-150 lines)

### Tests
- [ ] `tests/test_validate_deep_analysis.py` (13+ test cases, ~200 lines)
- [ ] `tests/test_validate_reference_architecture.py` (20+ test cases, ~400 lines)
- [ ] `tests/test_assemble_reference_architecture.py` (8+ test cases, ~150 lines)
- [ ] `tests/fixtures/sample_deep_analysis.json` (sample data)
- [ ] `tests/fixtures/sample_reference_architecture.json` (sample data)

### Templates
- [ ] `templates/reference_architecture.md.j2` (200-300 lines)

### Agent
- [ ] `.github/agents/reference-architecture-agent.md` (600-800 lines, 18 steps)

### Documentation
- [ ] `docs/REFERENCE-ARCHITECTURE-WORKFLOW.md` (user guide, 200-300 lines)
- [ ] `docs/CASE-STUDY-VS-REFERENCE-ARCHITECTURE.md` (comparison, 100-150 lines)
- [ ] `.github/ISSUE_TEMPLATE/reference-architecture.md` (issue template, 50-100 lines)
- [ ] `README.md` (updated with reference architecture section)
- [ ] `AGENTS.md` (updated with reference architecture patterns)
- [ ] `CONTRIBUTING.md` (updated with reference architecture procedures)
- [ ] `CHANGELOG.md` (version 3.0.0 changes documented)

### Directories
- [ ] `reference-architectures/` (output directory)
- [ ] `reference-architectures/images/` (screenshot directory)

### Integration Tests
- [ ] Integration test 1: E-commerce + Kubernetes + Istio
- [ ] Integration test 2: Financial + Multi-cluster
- [ ] Integration test 3: Media + Event-driven + Observability

### Finalization
- [ ] All unit tests pass (100%)
- [ ] All integration tests produce quality output
- [ ] Manual review confirms quality
- [ ] Git tag `v3.0.0` created
- [ ] Release notes written

---

## Appendix B: Quick Reference

### CLI Commands

```bash
# Validate deep analysis
python -m casestudypilot validate-deep-analysis transcript_deep_analysis.json

# Validate reference architecture (with technical depth scoring)
python -m casestudypilot validate-reference-architecture reference_architecture.json

# Assemble reference architecture
python -m casestudypilot assemble-reference-architecture \
  reference_architecture.json \
  screenshots/*.jpg \
  --output reference-architectures/company-name.md
```

### Skill Invocations

```bash
# Skills are invoked within agent workflow, not directly via CLI
# Skills are LLM-powered tasks with structured input/output

# Example: transcript-deep-analysis skill
# Input: video_data.json + transcript_corrected.json
# Output: transcript_deep_analysis.json (with CNCF projects, architecture, metrics)

# Example: reference-architecture-generation skill
# Input: transcript_deep_analysis.json + diagram_specifications.json
# Output: reference_architecture.json (with 10 sections)
```

### Agent Workflow Trigger

```bash
# Create GitHub issue with label and YouTube URL
gh issue create \
  --title "Generate reference architecture for Company X" \
  --body "YouTube URL: https://www.youtube.com/watch?v=VIDEO_ID

Please generate a reference architecture from this technical talk." \
  --label "reference-architecture"

# Agent will automatically detect and run 18-step workflow
```

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | PASS | Continue to next step |
| 1 | WARNING | Log warning, continue workflow |
| 2 | CRITICAL | Post error to issue, stop immediately |

### Quality Thresholds

| Metric | Minimum | Ideal |
|--------|---------|-------|
| Technical Depth Score | 0.70 | 0.75+ |
| Word Count | 2000 | 2500-4500 |
| CNCF Projects | 5 | 6+ |
| Screenshots | 6 | 6 |
| Integration Patterns | 2 | 3+ |
| Sections | 10 (all required) | 13 |

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-02-09  
**Status:** Complete - Ready for Implementation

---

**For Future Agents:**

This document contains everything you need to implement reference architecture generation. Follow the implementation phases sequentially, use the provided pseudocode and templates, and refer back to this guide whenever you need clarification.

**Key Files Already Created:**
- ✅ `docs/skills/transcript-deep-analysis.md` - Complete skill specification (23,000+ tokens)
- ✅ `docs/skills/architecture-diagram-specification.md` - Complete skill specification (10,000+ tokens)
- ✅ This guide - Complete implementation instructions

**Next Steps:**
1. Copy skill files to `.github/skills/` directory
2. Create `reference-architecture-generation` skill (use Section "Skill 3" as guide)
3. Implement CLI tools (use pseudocode from Section "Three New CLI Tools")
4. Create template (use Section "Templates")
5. Create agent workflow (use Section "One New Agent")
6. Run integration tests
7. Update documentation
8. Release v3.0.0

Good luck! 🚀
