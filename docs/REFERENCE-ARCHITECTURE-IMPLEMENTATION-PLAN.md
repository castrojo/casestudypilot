# Reference Architecture Generation - Complete Implementation Plan

**Status:** Documentation Complete - Ready for Future Implementation  
**Issue:** #15 - Generate a skill for reference architectures  
**Estimated Duration:** 18 days  
**Version:** 1.0.0  
**Date Created:** February 9, 2026  
**User Decision:** High Priority - Documentation Only (for future agents)

---

## Important Notice

**This document is the original high-level planning document. For complete implementation specifications, see:**

**📘 [REFERENCE-ARCHITECTURE-IMPLEMENTATION-GUIDE.md](./REFERENCE-ARCHITECTURE-IMPLEMENTATION-GUIDE.md)**

The implementation guide contains:
- ✅ Complete skill specifications (3 skills fully documented)
- ✅ Complete CLI tool specifications with pseudocode (3 tools)
- ✅ Complete agent workflow (18 steps, 600-800 lines)
- ✅ Complete Jinja2 template specification
- ✅ Step-by-step implementation phases
- ✅ Testing strategy with specific test cases
- ✅ File checklist and quick reference

**This document remains as:**
- Original planning and requirements analysis
- High-level architecture overview
- Background research and comparison analysis

---

## Executive Summary

This document provides the original implementation plan for extending the casestudypilot framework to generate CNCF reference architectures from YouTube videos. This capability builds upon the existing case study generation system but provides significantly deeper technical analysis and comprehensive architectural documentation suitable for CNCF End User TAB review and publication.

**Primary Objective:** Enable automated generation of publication-ready reference architectures that meet CNCF TAB standards.

**Key Success Metric:** Generate reference architectures with technical depth score >= 0.70 and word count 2000-5000 words.

**Implementation Status:** All specifications complete. See implementation guide for execution details.

---

## Table of Contents

1. [Background and Context](#1-background-and-context)
2. [Requirements Analysis](#2-requirements-analysis)
3. [Architecture Design](#3-architecture-design)
4. [Implementation Phases](#4-implementation-phases)
5. [Quality Standards](#5-quality-standards)
6. [Testing Strategy](#6-testing-strategy)
7. [Risk Management](#7-risk-management)
8. [Open Questions](#8-open-questions)

---

## 1. Background and Context

### 1.1 What Are CNCF Reference Architectures?

Reference architectures are comprehensive technical documents that describe real-world implementations of cloud-native systems using CNCF projects. Unlike case studies (which focus on business outcomes), reference architectures provide deep technical detail about system design, architecture patterns, and implementation decisions.

**Published At:** https://architecture.cncf.io/  
**Governed By:** CNCF End User Technical Advisory Board (TAB)  
**Approval Process:** TAB review → TOC validation → Publication → Announcement

### 1.2 Comparison: Case Studies vs. Reference Architectures

| Aspect | Case Studies (Existing) | Reference Architectures (New) |
|--------|------------------------|-------------------------------|
| **Primary Focus** | Business outcomes, metrics, ROI | Technical architecture, patterns, design |
| **Target Audience** | Business leaders, managers, mixed | Platform engineers, architects, technical |
| **Length** | 500-1500 words | 2000-5000 words |
| **Depth** | Problem → Solution → Results | System design, integrations, tradeoffs |
| **CNCF Projects** | 2-3 typical | 5-10+ typical |
| **Sections** | 5 sections | 8-10 sections |
| **Diagrams** | 3 screenshots | 6 screenshots + architecture diagrams |
| **Technical Detail** | High-level implementation | Detailed architecture, integration patterns |
| **Metrics Focus** | Business metrics (time, cost savings) | Technical metrics (scale, performance, reliability) |
| **Approval Process** | Internal validation only | TAB review + TOC validation required |
| **Quality Threshold** | Score >= 0.60 | Score >= 0.70 (technical depth) |
| **Output Directory** | `/case-studies/` | `/reference-architectures/` |

### 1.3 CNCF TAB Submission Process

Reference architectures follow a formal submission and review process:

**Step 1: Proposed** - Submitted via GitHub issue to cncf/tab  
**Step 2: Accepted** - TAB reviews and approves relevance to community  
**Step 3: Reviewed** - Iterative review with assigned TAB members  
**Step 4: Validated** - TOC validates CNCF project descriptions  
**Step 5: Published** - Published to https://architecture.cncf.io/  
**Step 6: Announced** - Announced via TAB meetings, mailing lists, Slack

**Required Information:**
- Contact person for the reference architecture
- End user organization(s) backing the submission
- CNCF projects being used in the architecture
- Domain or industry (optional)
- Comprehensive technical details

**Source:** `/tmp/cncf-tab/process/reference-architectures.md`

### 1.4 Why This Extension Matters

The existing case study generation system successfully produces business-focused narratives. However, the CNCF community also needs detailed technical reference architectures that:

1. **Guide implementation decisions** - Show real-world architectural patterns
2. **Demonstrate best practices** - Illustrate how CNCF projects integrate
3. **Address technical challenges** - Document scalability, reliability, observability
4. **Support platform teams** - Provide reusable patterns for platform engineering
5. **Validate technology choices** - Show proven combinations of CNCF projects

Reference architectures complement case studies by providing the technical depth that architects and platform engineers need for implementation.

---

## 2. Requirements Analysis

### 2.1 Functional Requirements

**FR1: Extended Analysis Capability**
- Must extract architectural patterns from video transcripts
- Must identify system components and their relationships
- Must capture integration patterns between CNCF projects
- Must document scalability and reliability considerations
- Must identify minimum 5 CNCF projects (vs. 2 for case studies)

**FR2: Comprehensive Content Generation**
- Must generate 8-10 sections (vs. 5 for case studies)
- Must achieve 2000-5000 word count (vs. 500-1500)
- Must maintain technical accuracy throughout
- Must include architecture diagram specifications
- Must document technology decision rationale

**FR3: Enhanced Validation**
- Must validate technical depth score >= 0.70
- Must ensure minimum 5 CNCF projects mentioned
- Must verify architecture components defined
- Must check integration patterns described
- Must validate transcript quality (min 2000 chars)

**FR4: TAB Submission Support**
- Must include TAB submission guidance in PR
- Must format output for TAB review readiness
- Must include all required metadata
- Must provide submission checklist

**FR5: Reuse Existing Infrastructure**
- Must reuse youtube-data tool
- Must reuse transcript-correction skill
- Must reuse validation framework (exit codes 0/1/2)
- Must reuse hyperlink automation
- Must reuse company verification tools

### 2.2 Non-Functional Requirements

**NFR1: Quality**
- Technical depth score >= 0.70 (vs. 0.60 for case studies)
- Zero fabricated technical claims (validated)
- Accurate CNCF project descriptions
- Consistent technical terminology

**NFR2: Performance**
- Workflow execution: 20-30% longer than case studies (acceptable)
- Validation should fail fast (critical errors stop immediately)
- Memory usage should remain reasonable (<4GB)

**NFR3: Maintainability**
- Code follows existing framework patterns
- Skills are self-contained and documented
- CLI tools have comprehensive tests
- Documentation kept in sync with implementation

**NFR4: Extensibility**
- Framework supports future architecture types
- Skills can be enhanced without breaking changes
- Validation rules are configurable
- Templates are customizable

### 2.3 Constraints

**C1: Framework Architecture**
- Must follow three-layer design (Agents → Skills → CLI Tools)
- Must use fail-fast validation pattern
- Must return meaningful exit codes (0/1/2)
- Must maintain backward compatibility with case studies

**C2: External Dependencies**
- No new external API dependencies
- No authentication required (zero configuration)
- Reuse existing Python packages
- YouTube transcript API remains sufficient

**C3: Output Format**
- Markdown format (same as case studies)
- Compatible with existing template system
- Hyperlinks follow CNCF conventions
- Metadata format matches case studies

---

## 3. Architecture Design

### 3.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│ AGENT: reference-architecture-agent (18 steps)              │
│ - Orchestrates reference architecture generation            │
│ - Invokes skills and CLI tools                              │
│ - Manages validation checkpoints (7 checkpoints)            │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ NEW SKILLS      │ │ REUSED SKILLS   │ │ NEW CLI TOOLS   │
│                 │ │                 │ │                 │
│ • deep-analysis │ │ • transcript-   │ │ • validate-     │
│ • diagram-spec  │ │   correction    │ │   deep-analysis │
│ • arch-gen      │ │                 │ │ • validate-ref- │
│                 │ │                 │ │   architecture  │
│                 │ │                 │ │ • assemble-ref- │
│                 │ │                 │ │   architecture  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌─────────────────────────────────────┐ ┌─────────────────┐
│ REUSED CLI TOOLS                    │ │ NEW TEMPLATE    │
│ • youtube-data                      │ │                 │
│ • validate-transcript (higher bar)  │ │ • reference_    │
│ • validate-company                  │ │   architecture. │
│ • verify-company                    │ │   md.j2         │
│ • extract-screenshots (6 images)    │ │                 │
└─────────────────────────────────────┘ └─────────────────┘
```

### 3.2 New Skills (Layer 2: LLM-Powered)

#### Skill 1: transcript-deep-analysis

**File:** `.github/skills/transcript-deep-analysis/SKILL.md`

**Purpose:** Extract comprehensive architectural patterns and technical details from video transcripts.

**Input Format:**
```json
{
  "transcript": "corrected transcript text from transcript-correction skill",
  "video_title": "from video_data.json",
  "duration": 1800
}
```

**Output Format:**
```json
{
  "system_architecture": {
    "components": [
      {
        "name": "Component name",
        "type": "service|database|cache|queue|api-gateway|load-balancer",
        "description": "What this component does",
        "cncf_projects": ["Kubernetes", "Envoy"]
      }
    ],
    "layers": [
      {
        "name": "Layer name (e.g., 'Data Layer', 'Service Mesh')",
        "components": ["component1", "component2"],
        "description": "Purpose of this layer"
      }
    ]
  },
  "cncf_projects": [
    {
      "name": "Kubernetes",
      "usage_context": "container orchestration and workload scheduling",
      "key_features": ["horizontal pod autoscaling", "rolling updates"],
      "scale": "10,000 pods across 50 clusters",
      "integration_points": ["Prometheus for metrics", "Envoy for service mesh"]
    }
  ],
  "integration_patterns": [
    {
      "pattern_name": "Service Mesh",
      "description": "All service-to-service communication through Envoy",
      "cncf_projects": ["Envoy", "Linkerd"],
      "benefits": ["mTLS encryption", "traffic management", "observability"]
    }
  ],
  "scalability_patterns": [
    {
      "pattern_name": "Horizontal Pod Autoscaling",
      "description": "Automatic scaling based on CPU and custom metrics",
      "scale_achieved": "5,000 to 10,000 pods dynamically",
      "cncf_projects": ["Kubernetes", "Prometheus"]
    }
  ],
  "observability_approach": {
    "metrics": {
      "tool": "Prometheus",
      "collection_method": "Service mesh + exporters",
      "retention": "30 days"
    },
    "logging": {
      "tool": "Fluentd",
      "centralization": "ElasticSearch cluster",
      "volume": "10TB/day"
    },
    "tracing": {
      "tool": "Jaeger",
      "sampling": "1% of requests",
      "storage": "Cassandra"
    }
  },
  "security_considerations": [
    {
      "category": "Authentication",
      "approach": "OAuth2 with Keycloak",
      "cncf_projects": []
    },
    {
      "category": "Secrets Management",
      "approach": "Sealed Secrets in Git",
      "cncf_projects": ["Kubernetes"]
    }
  ],
  "technical_metrics": [
    {
      "metric": "10,000 pods",
      "category": "scale",
      "context": "managed across production clusters"
    }
  ],
  "technology_decisions": [
    {
      "decision": "Chose Envoy over NGINX",
      "rationale": "Native Kubernetes integration and observability",
      "tradeoffs": "Higher resource usage, steeper learning curve"
    }
  ]
}
```

**Key Validation Rules:**
- Minimum 5 CNCF projects identified
- At least 3 system architecture components defined
- At least 2 integration patterns described
- Scalability approach documented
- Observability approach documented

---

#### Skill 2: architecture-diagram-specification

**File:** `.github/skills/architecture-diagram-specification/SKILL.md`

**Purpose:** Generate textual specifications for architecture diagrams that can be converted to visual diagrams (manually or via tools like Mermaid/PlantUML).

**Input Format:**
```json
{
  "system_architecture": "from deep_analysis.json",
  "cncf_projects": "from deep_analysis.json",
  "integration_patterns": "from deep_analysis.json"
}
```

**Output Format:**
```json
{
  "diagrams": [
    {
      "type": "component",
      "title": "High-Level System Architecture",
      "description": "Shows major system components and their relationships",
      "components": [
        {
          "id": "k8s",
          "label": "Kubernetes Cluster",
          "type": "platform",
          "description": "Container orchestration"
        },
        {
          "id": "envoy",
          "label": "Envoy Service Mesh",
          "type": "networking",
          "description": "Service-to-service communication"
        }
      ],
      "connections": [
        {
          "from": "k8s",
          "to": "envoy",
          "label": "manages",
          "description": "Kubernetes deploys and manages Envoy proxies"
        }
      ],
      "mermaid_syntax": "graph TD\n  k8s[Kubernetes] --> envoy[Envoy]\n  ..."
    },
    {
      "type": "data-flow",
      "title": "Request Flow Through System",
      "description": "Shows how requests flow through components",
      "steps": [
        "User request → Load Balancer",
        "Load Balancer → Envoy Ingress Gateway",
        "Envoy → Service A (with mTLS)",
        "Service A → Service B (through Envoy)",
        "Service B → Database"
      ]
    },
    {
      "type": "deployment",
      "title": "Multi-Cluster Deployment Topology",
      "description": "Shows how system is deployed across environments",
      "environments": [
        {
          "name": "Production",
          "clusters": 3,
          "regions": ["us-east-1", "us-west-2", "eu-west-1"],
          "components": ["All services", "Databases", "Caches"]
        }
      ]
    }
  ]
}
```

**Diagram Types:**
1. **Component Diagram** - System architecture overview
2. **Data Flow Diagram** - How data/requests flow through system
3. **Deployment Topology** - How system is deployed across infrastructure
4. **Integration Diagram** - How CNCF projects integrate with each other

---

#### Skill 3: reference-architecture-generation

**File:** `.github/skills/reference-architecture-generation/SKILL.md`

**Purpose:** Generate comprehensive reference architecture content in CNCF style with deep technical detail.

**Input Format:**
```json
{
  "deep_analysis": "from deep_analysis.json",
  "video_data": "from video_data.json",
  "diagram_specs": "from diagram_specs.json",
  "company_verification": "from company_verification.json"
}
```

**Output Format:**
```json
{
  "sections": {
    "executive_summary": "150-250 words markdown",
    "background_context": "300-500 words markdown",
    "technical_requirements": "250-400 words markdown",
    "architecture_overview": "400-700 words markdown",
    "cncf_technology_stack": "500-800 words markdown",
    "integration_patterns": "400-600 words markdown",
    "scalability_reliability": "350-550 words markdown",
    "observability_operations": "300-500 words markdown",
    "security_considerations": "250-400 words markdown",
    "lessons_learned": "300-500 words markdown"
  }
}
```

**Section Specifications:**

**1. Executive Summary (150-250 words)**
- Company overview and scale
- Primary challenge addressed
- High-level architecture approach
- Key CNCF projects used (bolded)
- Major outcomes achieved

**2. Background and Context (300-500 words)**
- Company industry and business context
- Team size and organizational structure
- Previous architecture and limitations
- Business drivers for change
- Technical constraints and requirements

**3. Technical Requirements (250-400 words)**
- Functional requirements
- Non-functional requirements (scale, performance, availability)
- Compliance and security requirements
- Integration requirements
- Budget and timeline constraints

**4. Architecture Overview (400-700 words)**
- High-level system design
- Major architectural layers
- Core components and their roles
- Reference to architecture diagram
- Key architectural decisions

**5. CNCF Technology Stack (500-800 words)**
- Detailed description of each CNCF project used
- Version information where available
- Why each project was chosen
- How projects integrate with each other
- Configuration highlights
- Alternative options considered

**6. Integration Patterns (400-600 words)**
- How components communicate
- API patterns (REST, gRPC, etc.)
- Service mesh implementation
- Data consistency patterns
- Event-driven patterns
- Synchronous vs. asynchronous communication

**7. Scalability and Reliability (350-550 words)**
- Horizontal scaling strategies
- Load balancing approach
- Database scaling patterns
- Caching strategies
- Circuit breakers and fault tolerance
- Disaster recovery and backup

**8. Observability and Operations (300-500 words)**
- Metrics collection and storage
- Logging aggregation
- Distributed tracing
- Alerting and on-call
- Debugging and troubleshooting
- Performance monitoring

**9. Security Considerations (250-400 words)**
- Authentication and authorization
- Network security (mTLS, network policies)
- Secrets management
- Vulnerability scanning
- Compliance requirements
- Security monitoring

**10. Lessons Learned and Recommendations (300-500 words)**
- What worked well
- What was challenging
- Unexpected issues encountered
- Advice for similar implementations
- Future improvements planned
- When this architecture is appropriate

**Style Guidelines:**
- Professional, technical tone
- Third-person narrative
- Present tense for current state, past tense for implementation
- Bold all CNCF project names
- Bold all key technical metrics
- Use code blocks for configuration examples
- Include bullet lists for clarity
- Link to CNCF project pages
- 2000-5000 words total

---

### 3.3 New CLI Tools (Layer 3: Python)

#### Tool 1: validate-deep-analysis

**File:** `casestudypilot/tools/validate_deep_analysis.py`

**Command:**
```bash
python -m casestudypilot validate-deep-analysis deep_analysis.json
```

**Validation Rules:**

1. **CNCF Projects (CRITICAL)**
   - Minimum 5 CNCF projects identified
   - Each project has name, usage_context, key_features
   - Exit code 2 if < 5 projects

2. **Architecture Components (CRITICAL)**
   - Minimum 3 system components defined
   - Each component has name, type, description
   - Exit code 2 if < 3 components

3. **Integration Patterns (WARNING)**
   - At least 2 integration patterns described
   - Each pattern has name, description, benefits
   - Exit code 1 if < 2 patterns

4. **Scalability Considerations (WARNING)**
   - Scalability approach documented
   - At least 1 scalability pattern defined
   - Exit code 1 if missing

5. **Observability Approach (WARNING)**
   - Metrics collection documented
   - Logging approach documented
   - Exit code 1 if missing major components

**Exit Codes:**
- `0` - PASS: All validations passed
- `1` - WARNING: Has warnings but can continue
- `2` - CRITICAL: Fatal errors, must stop workflow

**Output:**
```json
{
  "status": "pass|warning|critical",
  "exit_code": 0,
  "checks": {
    "cncf_projects": {
      "status": "pass",
      "count": 7,
      "minimum": 5
    },
    "architecture_components": {
      "status": "pass",
      "count": 5,
      "minimum": 3
    },
    "integration_patterns": {
      "status": "pass",
      "count": 3,
      "minimum": 2
    }
  },
  "warnings": [],
  "errors": []
}
```

---

#### Tool 2: validate-reference-architecture

**File:** `casestudypilot/tools/validate_reference_architecture.py`

**Command:**
```bash
python -m casestudypilot validate-reference-architecture reference_architecture.md --threshold 0.70
```

**Validation Rules:**

1. **Word Count (CRITICAL)**
   - Total word count between 2000-5000
   - Exit code 2 if outside range

2. **Section Presence (CRITICAL)**
   - All 8-10 required sections present
   - Section headers match expected format
   - Exit code 2 if missing required sections

3. **CNCF Project Mentions (CRITICAL)**
   - Minimum 5 unique CNCF projects mentioned and bolded
   - Projects are from official CNCF project list
   - Exit code 2 if < 5 projects

4. **Technical Depth Score (CRITICAL)**
   - Calculate multi-factor technical depth score
   - Score must be >= threshold (default 0.70)
   - Exit code 2 if below threshold

5. **Architecture Diagrams (WARNING)**
   - At least 1 architecture diagram referenced
   - Diagram captions present
   - Exit code 1 if missing

**Technical Depth Scoring Algorithm:**

```python
technical_depth_score = (
    architecture_detail_score * 0.30 +    # Component descriptions, layers
    integration_detail_score * 0.25 +     # How components connect
    scalability_detail_score * 0.20 +     # Scaling patterns described
    observability_detail_score * 0.15 +   # Metrics, logging, tracing
    security_detail_score * 0.10          # Security patterns
)

# Each sub-score calculated as:
# - 1.0: Comprehensive detail (multiple paragraphs, specific examples)
# - 0.7: Good detail (paragraphs with some specifics)
# - 0.5: Adequate detail (mentions with brief description)
# - 0.3: Minimal detail (only mentions)
# - 0.0: No detail
```

**Exit Codes:**
- `0` - PASS: Quality threshold met
- `1` - WARNING: Below optimal but acceptable
- `2` - CRITICAL: Below minimum threshold

**Output:**
```json
{
  "quality_score": 0.75,
  "technical_depth_score": 0.75,
  "passed": true,
  "threshold": 0.70,
  "word_count": 3542,
  "sections_present": 10,
  "cncf_projects_count": 8,
  "warnings": ["No deployment topology diagram"],
  "details": {
    "architecture_detail": {"score": 0.85},
    "integration_detail": {"score": 0.75},
    "scalability_detail": {"score": 0.70},
    "observability_detail": {"score": 0.75},
    "security_detail": {"score": 0.65}
  }
}
```

---

#### Tool 3: assemble-reference-architecture

**File:** `casestudypilot/tools/assemble_reference_architecture.py`

**Command:**
```bash
python -m casestudypilot assemble-reference-architecture \
  video_data.json \
  deep_analysis.json \
  reference_architecture_sections.json \
  company_verification.json \
  --screenshots screenshots.json \
  --diagrams diagram_specs.json \
  --output reference-architectures/company-architecture.md
```

**Functionality:**
1. Load all JSON inputs
2. Verify company is CNCF member
3. Load Jinja2 template: `templates/reference_architecture.md.j2`
4. Combine all data into template context
5. Render template with automatic hyperlink injection
6. Embed 6 screenshots with captions
7. Add diagram specifications as text blocks
8. Include TAB submission metadata
9. Save to `reference-architectures/` directory

**Template Context:**
```python
{
    "company": "Company name",
    "company_url": "https://company.com",
    "video": {
        "title": "Video title",
        "url": "YouTube URL",
        "duration": "30:00"
    },
    "sections": {
        "executive_summary": "markdown content",
        "background_context": "markdown content",
        # ... all 10 sections
    },
    "cncf_projects": [
        {"name": "Kubernetes", "url": "https://kubernetes.io", ...}
    ],
    "technical_metrics": [...],
    "diagrams": [...],
    "screenshots": [
        {"path": "images/company/screenshot1.jpg", "caption": "...", "timestamp": "15:00"}
    ],
    "validation_summary": {
        "technical_depth_score": 0.75,
        "word_count": 3542,
        "cncf_projects_count": 8
    }
}
```

---

### 3.4 New Agent Workflow

**File:** `.github/agents/reference-architecture-agent.md`

**Agent Metadata:**
```yaml
---
name: reference-architecture-agent
description: Generates comprehensive CNCF reference architectures from YouTube videos
version: 1.0.0
---
```

**18-Step Workflow:**

**Step 0: Pre-flight Validation**
- Verify Python environment ready
- Check required packages installed
- Validate GitHub environment
- Verify output directory exists

**Step 1: Extract Video URL from Issue**
- Parse GitHub issue body
- Extract YouTube URL
- Validate URL format

**Step 2: Fetch Video Data**
```bash
python -m casestudypilot youtube-data "$VIDEO_URL" --output video_data.json
```

**Step 3: Validate Transcript Quality** ⚠️ CHECKPOINT 1
```bash
python -m casestudypilot validate-transcript video_data.json --min-chars 2000
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
  # Post error to issue and STOP
  gh issue comment $ISSUE_NUMBER --body "$(cat error_templates/transcript_quality.md)"
  exit 2
fi
```
- Exit 2: Transcript < 2000 chars or empty → STOP
- Exit 1: Transcript 2000-3000 chars (warning) → Continue
- Exit 0: Transcript > 3000 chars → Continue

**Step 4: Extract Company Name**
- Parse issue title and body for company name
- Use video title if not in issue

**Step 5: Validate Company Identification** ⚠️ CHECKPOINT 2
```bash
python -m casestudypilot validate-company "$COMPANY" "$VIDEO_TITLE" --confidence 1.0
EXIT_CODE=$?
```
- Exit 2: Generic placeholder detected → STOP
- Exit 1: Low confidence → Continue with warning
- Exit 0: High confidence → Continue

**Step 6: Verify CNCF Membership**
```bash
python -m casestudypilot verify-company "$COMPANY" --output company_verification.json
```

**Step 7: Apply transcript-correction Skill**
- Use existing skill to fix transcript errors
- Save corrected transcript back to video_data.json

**Step 8: Apply transcript-deep-analysis Skill** (NEW)
- Extract architectural patterns
- Identify system components
- Document CNCF projects and their roles
- Capture integration patterns
- Document scalability and observability
- Save to deep_analysis.json

**Step 9: Validate Deep Analysis** ⚠️ CHECKPOINT 3
```bash
python -m casestudypilot validate-deep-analysis deep_analysis.json
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
  gh issue comment $ISSUE_NUMBER --body "$(cat error_templates/deep_analysis_quality.md)"
  exit 2
fi
```
- Exit 2: < 5 CNCF projects or missing architecture → STOP
- Exit 1: Missing some patterns → Continue with warning
- Exit 0: All requirements met → Continue

**Step 10: Apply architecture-diagram-specification Skill** (NEW)
- Generate diagram specifications from deep analysis
- Create component, data flow, and deployment diagrams
- Save to diagram_specs.json

**Step 11: Extract Screenshots**
```bash
python -m casestudypilot extract-screenshots \
  video_data.json \
  deep_analysis.json \
  reference_architecture_sections.json \
  --count 6 \
  --download-dir reference-architectures/images/$COMPANY/ \
  --output screenshots.json
```
- Extract 6 key moments (vs. 3 for case studies)
- Focus on architecture diagrams, system views, metrics dashboards

**Step 12: Apply reference-architecture-generation Skill** (NEW)
- Generate comprehensive 10-section reference architecture
- Use deep_analysis.json, video_data.json, diagram_specs.json
- Save to reference_architecture_sections.json

**Step 13: Validate Architecture Content** ⚠️ CHECKPOINT 4, 5, 6
```bash
# Check CNCF project consistency
python -m casestudypilot validate-consistency \
  reference_architecture_sections.json \
  video_data.json \
  company_verification.json
EXIT_CODE=$?

# Check for fabricated technical claims
python -m casestudypilot validate-metrics \
  reference_architecture_sections.json \
  video_data.json \
  deep_analysis.json
```

**Step 14: Assemble Reference Architecture**
```bash
python -m casestudypilot assemble-reference-architecture \
  video_data.json \
  deep_analysis.json \
  reference_architecture_sections.json \
  company_verification.json \
  --screenshots screenshots.json \
  --diagrams diagram_specs.json \
  --output reference-architectures/${SLUG}.md
```

**Step 15: Validate Final Quality** ⚠️ CHECKPOINT 7
```bash
python -m casestudypilot validate-reference-architecture \
  reference-architectures/${SLUG}.md \
  --threshold 0.70
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  gh issue comment $ISSUE_NUMBER --body "$(cat error_templates/final_quality.md)"
  exit 2
fi
```
- Exit 2: Score < 0.70 or critical issues → STOP
- Exit 1: Score 0.70-0.75 (acceptable) → Continue with warning
- Exit 0: Score > 0.75 (excellent) → Continue

**Step 16: Create Branch**
```bash
BRANCH="ref-arch/${COMPANY}-$(date +%Y%m%d)"
git checkout -b "$BRANCH"
```

**Step 17: Commit (Atomic)**
```bash
git add reference-architectures/${SLUG}.md
git add reference-architectures/images/$COMPANY/*.jpg
git commit -m "Add reference architecture for $COMPANY with architecture diagrams"
```

**Step 18: Create Pull Request**
```bash
gh pr create \
  --title "Add reference architecture for $COMPANY" \
  --body "$(cat pr_templates/reference_architecture.md)" \
  --base main \
  --head "$BRANCH"
```

PR description includes:
- Reference architecture summary
- Validation results
- TAB submission checklist
- TAB submission guidance
- Review checklist

---

### 3.5 New Jinja2 Template

**File:** `templates/reference_architecture.md.j2`

**Structure:**

```jinja2
# [{{ company }}]({{ company_url }}) Reference Architecture

> **Source:** [{{ video.title }}]({{ video.url }})  
> **Duration:** {{ video.duration }}  
> **Domain:** {{ domain }}

---

## Executive Summary

{{ sections.executive_summary }}

---

## Background and Context

{{ sections.background_context }}

---

## Technical Requirements

{{ sections.technical_requirements }}

---

## Architecture Overview

{{ sections.architecture_overview }}

{% for diagram in diagrams %}
### {{ diagram.title }}

{{ diagram.description }}

{% if diagram.type == "component" %}
```mermaid
{{ diagram.mermaid_syntax }}
```
{% else %}
<!-- Diagram specification: {{ diagram.type }} -->
{{ diagram.textual_description }}
{% endif %}

![{{ diagram.title }}]({{ diagram.screenshot_path }})
*{{ diagram.caption }} ({{ diagram.timestamp }})*

{% endfor %}

---

## CNCF Technology Stack

{{ sections.cncf_technology_stack }}

**Projects Used:**
{% for project in cncf_projects %}
- **[{{ project.name }}]({{ project.url }})**: {{ project.usage_context }}
  - Scale: {{ project.scale }}
  - Key features: {{ project.key_features | join(", ") }}
{% endfor %}

---

## Integration Patterns

{{ sections.integration_patterns }}

---

## Scalability and Reliability

{{ sections.scalability_reliability }}

---

## Observability and Operations

{{ sections.observability_operations }}

---

## Security Considerations

{{ sections.security_considerations }}

---

## Lessons Learned and Recommendations

{{ sections.lessons_learned }}

---

## Metadata

**Company:** [{{ company }}]({{ company_url }})  
**Industry:** {{ industry }}  
**Team Size:** {{ team_size }}

**CNCF Projects Used:** {{ cncf_projects | length }}
{% for project in cncf_projects %}
- [{{ project.name }}]({{ project.url }})
{% endfor %}

**Key Technical Metrics:**
{% for metric in technical_metrics %}
- {{ metric }}
{% endfor %}

**Video Source:**
- **Title:** {{ video.title }}
- **URL:** {{ video.url }}
- **Duration:** {{ video.duration }}

**Quality Validation:**
- Technical Depth Score: {{ validation_summary.technical_depth_score }}
- Word Count: {{ validation_summary.word_count }}
- CNCF Projects: {{ validation_summary.cncf_projects_count }}

---

## TAB Submission

This reference architecture is ready for submission to the CNCF End User TAB.

**Submission Checklist:**
- [x] End user organization identified and verified
- [x] CNCF projects documented with usage details
- [x] Architecture patterns described
- [x] Technical depth validated (score: {{ validation_summary.technical_depth_score }})
- [x] Diagram specifications provided

**To Submit:**
1. Review this reference architecture for accuracy
2. Visit: https://github.com/cncf/tab/issues/new?template=reference-architecture.yml
3. Fill in required information
4. Await TAB review and feedback

---

*This reference architecture was automatically generated from the video interview using the casestudypilot framework.*
```

---

## 4. Implementation Phases

### Phase 1: Foundation (Days 1-2)

**Objective:** Set up directory structure and prepare Python package for new components.

**Tasks:**

**Task 1.1:** Create directory structure
```bash
mkdir -p reference-architectures/
mkdir -p .github/skills/transcript-deep-analysis
mkdir -p .github/skills/architecture-diagram-specification
mkdir -p .github/skills/reference-architecture-generation
touch reference-architectures/.gitkeep
```

**Task 1.2:** Create Python module stubs
```bash
touch casestudypilot/tools/validate_deep_analysis.py
touch casestudypilot/tools/validate_reference_architecture.py
touch casestudypilot/tools/assemble_reference_architecture.py
```

**Task 1.3:** Update .gitignore
```
# Add if not present
reference-architectures/*.md
!reference-architectures/.gitkeep
```

**Task 1.4:** Create test structure
```bash
mkdir -p tests/test_data/reference_architectures
touch tests/test_validate_deep_analysis.py
touch tests/test_validate_reference_architecture.py
touch tests/test_assemble_reference_architecture.py
```

**Acceptance Criteria:**
- [ ] All directories created
- [ ] Python module files exist
- [ ] Test structure ready
- [ ] Git tracks .gitkeep files

---

### Phase 2: LLM Skills (Days 3-6)

**Objective:** Create comprehensive LLM skill definitions for deep analysis, diagram specification, and architecture generation.

#### Task 2.1: Create transcript-deep-analysis Skill (Day 3)

**File:** `.github/skills/transcript-deep-analysis/SKILL.md`

**Content Structure:**
1. **Purpose** - Extract comprehensive architectural patterns
2. **Input Format** - JSON schema with transcript, video metadata
3. **Output Format** - Detailed JSON with 8 major sections:
   - system_architecture (components, layers)
   - cncf_projects (detailed usage, scale, integration)
   - integration_patterns
   - scalability_patterns
   - observability_approach
   - security_considerations
   - technical_metrics
   - technology_decisions
4. **Execution Instructions** - Step-by-step for LLM:
   - Read entire transcript for context
   - Identify all CNCF projects (case-insensitive)
   - Extract system architecture components
   - Document integration patterns
   - Capture scalability approaches
   - Note observability tools and methods
   - Identify security patterns
   - Extract quantitative technical metrics
   - Document technology choices and rationale
5. **Examples** - 2 comprehensive examples:
   - Simple architecture (3-4 CNCF projects)
   - Complex architecture (8-10 CNCF projects)
6. **Quality Guidelines**:
   - Minimum 5 CNCF projects required
   - At least 3 architecture components
   - At least 2 integration patterns
   - Be thorough, don't miss technical details
   - Preserve exact metrics from transcript
   - Don't invent or extrapolate

**Acceptance Criteria:**
- [ ] Skill file is 400-600 lines
- [ ] Input/output schemas are complete
- [ ] 2 examples provided
- [ ] Quality guidelines comprehensive

#### Task 2.2: Create architecture-diagram-specification Skill (Day 4)

**File:** `.github/skills/architecture-diagram-specification/SKILL.md`

**Content Structure:**
1. **Purpose** - Generate textual diagram specifications
2. **Input Format** - deep_analysis.json
3. **Output Format** - JSON with diagram array:
   - Component diagrams
   - Data flow diagrams
   - Deployment topology diagrams
   - Each with: type, title, description, components, connections
   - Optional: mermaid_syntax for automatic rendering
4. **Diagram Types:**
   - **Component:** Boxes and arrows showing system structure
   - **Data Flow:** How requests/data move through system
   - **Deployment:** How system is deployed across infrastructure
   - **Integration:** How CNCF projects connect
5. **Execution Instructions:**
   - Analyze architecture components
   - Create component diagram first (high-level)
   - Add data flow diagram (request paths)
   - Add deployment diagram if multi-region/cluster
   - For each diagram: define nodes, edges, labels
6. **Examples:**
   - Microservices architecture with service mesh
   - Platform architecture with GitOps
7. **Mermaid Syntax Guide:**
   - Provide examples of Mermaid syntax
   - Graph TD (top-down), LR (left-right)
   - Node shapes, arrow types

**Acceptance Criteria:**
- [ ] Supports 4 diagram types
- [ ] Mermaid syntax guide included
- [ ] 2 complete examples
- [ ] Clear instructions for LLM

#### Task 2.3: Create reference-architecture-generation Skill (Days 5-6)

**File:** `.github/skills/reference-architecture-generation/SKILL.md`

**Content Structure:**
1. **Purpose** - Generate comprehensive reference architecture
2. **Input Format** - deep_analysis.json, video_data.json, diagram_specs.json
3. **Output Format** - JSON with 10 sections (markdown)
4. **Section Specifications** (detailed for each):

**Section 1: Executive Summary (150-250 words)**
- Purpose: High-level overview for decision makers
- Content: Company scale, challenge, approach, projects, outcomes
- Style: Concise, accessible, bolded metrics
- Example provided

**Section 2: Background and Context (300-500 words)**
- Purpose: Set the stage
- Content: Industry, team, previous state, drivers for change
- Style: Narrative, context-building
- Example provided

**Section 3: Technical Requirements (250-400 words)**
- Purpose: What the system needed to do
- Content: Functional, non-functional, compliance, integration
- Format: Bullet lists with descriptions
- Example provided

**Section 4: Architecture Overview (400-700 words)**
- Purpose: High-level system design
- Content: Layers, components, key decisions
- References: Architecture diagrams
- Style: Technical but accessible
- Example provided

**Section 5: CNCF Technology Stack (500-800 words)**
- Purpose: Deep dive into each CNCF project
- Content: Per project: purpose, why chosen, how configured, version
- Format: Subsections per major project
- Style: Technical, detailed, with configuration snippets
- Example provided

**Section 6: Integration Patterns (400-600 words)**
- Purpose: How components work together
- Content: Communication patterns, APIs, service mesh, events
- Format: Pattern-by-pattern breakdown
- Style: Technical, with diagrams referenced
- Example provided

**Section 7: Scalability and Reliability (350-550 words)**
- Purpose: How system scales and stays reliable
- Content: Horizontal scaling, load balancing, caching, fault tolerance
- Format: Pattern descriptions with metrics
- Style: Technical, quantitative
- Example provided

**Section 8: Observability and Operations (300-500 words)**
- Purpose: How system is monitored and operated
- Content: Metrics, logging, tracing, alerting, debugging
- Format: Tool-by-tool breakdown
- Style: Operational focus
- Example provided

**Section 9: Security Considerations (250-400 words)**
- Purpose: How system is secured
- Content: Authentication, authorization, encryption, secrets, compliance
- Format: Category-by-category
- Style: Security-focused, practical
- Example provided

**Section 10: Lessons Learned and Recommendations (300-500 words)**
- Purpose: Wisdom for others
- Content: Successes, challenges, surprises, advice
- Format: Narrative with bullet points
- Style: Honest, practical, forward-looking
- Example provided

5. **Style Guidelines** (comprehensive):
   - Professional, technical tone
   - Third-person narrative
   - Bold CNCF project names and metrics
   - Use code blocks for configs
   - Include bullet lists
   - Link to CNCF projects
   - 2000-5000 words total
   - No marketing fluff

6. **Quality Checklist** (20 items):
   - All sections present
   - Word count in range
   - Projects bolded
   - Metrics bolded
   - Technical accuracy
   - No fabrication
   - Smooth narrative
   - Etc.

7. **Examples:**
   - Complete example section set (abbreviated)
   - Before/after comparison with case study

**Acceptance Criteria:**
- [ ] All 10 sections specified in detail
- [ ] Each section has: purpose, content, length, style, example
- [ ] Quality checklist has 20+ items
- [ ] Style guidelines comprehensive
- [ ] Complete example provided

---

### Phase 3: CLI Tools (Days 7-10)

**Objective:** Implement Python CLI tools for validation and assembly with comprehensive testing.

#### Task 3.1: Implement validate-deep-analysis (Day 7)

**File:** `casestudypilot/tools/validate_deep_analysis.py`

**Implementation:**

```python
"""
Validate Deep Analysis Output

Validates the output from transcript-deep-analysis skill to ensure
comprehensive architectural information has been extracted.

Exit Codes:
  0 - PASS: All validations passed
  1 - WARNING: Has warnings but can continue
  2 - CRITICAL: Fatal errors, must stop
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple

def validate_deep_analysis(analysis_file: str) -> Tuple[int, Dict]:
    """
    Validate deep analysis JSON.
    
    Returns:
        (exit_code, validation_results)
    """
    try:
        data = json.loads(Path(analysis_file).read_text())
    except Exception as e:
        return 2, {"error": f"Failed to load analysis file: {e}"}
    
    results = {
        "status": "pass",
        "checks": {},
        "warnings": [],
        "errors": []
    }
    
    exit_code = 0
    
    # Check 1: CNCF Projects (CRITICAL)
    cncf_projects = data.get("cncf_projects", [])
    if len(cncf_projects) < 5:
        results["errors"].append(
            f"Insufficient CNCF projects: found {len(cncf_projects)}, minimum 5 required"
        )
        exit_code = 2
    results["checks"]["cncf_projects"] = {
        "status": "pass" if len(cncf_projects) >= 5 else "critical",
        "count": len(cncf_projects),
        "minimum": 5
    }
    
    # Check 2: Architecture Components (CRITICAL)
    components = data.get("system_architecture", {}).get("components", [])
    if len(components) < 3:
        results["errors"].append(
            f"Insufficient architecture components: found {len(components)}, minimum 3 required"
        )
        exit_code = 2
    results["checks"]["architecture_components"] = {
        "status": "pass" if len(components) >= 3 else "critical",
        "count": len(components),
        "minimum": 3
    }
    
    # Check 3: Integration Patterns (WARNING)
    integration_patterns = data.get("integration_patterns", [])
    if len(integration_patterns) < 2:
        results["warnings"].append(
            f"Few integration patterns: found {len(integration_patterns)}, recommended 2+"
        )
        if exit_code == 0:
            exit_code = 1
    results["checks"]["integration_patterns"] = {
        "status": "pass" if len(integration_patterns) >= 2 else "warning",
        "count": len(integration_patterns),
        "minimum": 2
    }
    
    # Check 4: Scalability Patterns (WARNING)
    scalability_patterns = data.get("scalability_patterns", [])
    if len(scalability_patterns) < 1:
        results["warnings"].append("No scalability patterns documented")
        if exit_code == 0:
            exit_code = 1
    results["checks"]["scalability_patterns"] = {
        "status": "pass" if len(scalability_patterns) >= 1 else "warning",
        "count": len(scalability_patterns),
        "minimum": 1
    }
    
    # Check 5: Observability Approach (WARNING)
    observability = data.get("observability_approach", {})
    if not observability.get("metrics") or not observability.get("logging"):
        results["warnings"].append("Incomplete observability approach")
        if exit_code == 0:
            exit_code = 1
    results["checks"]["observability_approach"] = {
        "status": "pass" if observability.get("metrics") and observability.get("logging") else "warning",
        "has_metrics": bool(observability.get("metrics")),
        "has_logging": bool(observability.get("logging")),
        "has_tracing": bool(observability.get("tracing"))
    }
    
    # Set overall status
    if exit_code == 2:
        results["status"] = "critical"
    elif exit_code == 1:
        results["status"] = "warning"
    else:
        results["status"] = "pass"
    
    return exit_code, results

def main(analysis_file: str):
    """CLI entry point."""
    exit_code, results = validate_deep_analysis(analysis_file)
    
    # Print results
    if exit_code == 0:
        print(f"✅ PASS: Deep analysis validation successful")
    elif exit_code == 1:
        print(f"⚠️ WARNING: Deep analysis has warnings")
        for warning in results["warnings"]:
            print(f"  - {warning}")
    else:
        print(f"❌ CRITICAL: Deep analysis validation failed", file=sys.stderr)
        for error in results["errors"]:
            print(f"  - {error}", file=sys.stderr)
    
    # Print summary
    print(f"\nValidation Summary:")
    for check_name, check_result in results["checks"].items():
        status_icon = "✅" if check_result["status"] == "pass" else ("⚠️" if check_result["status"] == "warning" else "❌")
        print(f"  {status_icon} {check_name}: {check_result}")
    
    sys.exit(exit_code)
```

**Tests:** `tests/test_validate_deep_analysis.py`

```python
import pytest
import json
from pathlib import Path
from casestudypilot.tools.validate_deep_analysis import validate_deep_analysis

def test_valid_deep_analysis(tmp_path):
    """Test with valid deep analysis."""
    analysis = {
        "cncf_projects": [{"name": f"Project{i}"} for i in range(6)],
        "system_architecture": {
            "components": [{"name": f"Component{i}"} for i in range(4)]
        },
        "integration_patterns": [{"name": "Pattern1"}, {"name": "Pattern2"}],
        "scalability_patterns": [{"name": "HPA"}],
        "observability_approach": {
            "metrics": {"tool": "Prometheus"},
            "logging": {"tool": "Fluentd"}
        }
    }
    
    file = tmp_path / "analysis.json"
    file.write_text(json.dumps(analysis))
    
    exit_code, results = validate_deep_analysis(str(file))
    
    assert exit_code == 0
    assert results["status"] == "pass"
    assert len(results["errors"]) == 0

def test_insufficient_cncf_projects(tmp_path):
    """Test with < 5 CNCF projects (CRITICAL)."""
    analysis = {
        "cncf_projects": [{"name": "Kubernetes"}],
        "system_architecture": {"components": [{"name": "C1"}, {"name": "C2"}, {"name": "C3"}]},
        "integration_patterns": [{"name": "P1"}, {"name": "P2"}],
        "scalability_patterns": [{"name": "HPA"}],
        "observability_approach": {"metrics": {}, "logging": {}}
    }
    
    file = tmp_path / "analysis.json"
    file.write_text(json.dumps(analysis))
    
    exit_code, results = validate_deep_analysis(str(file))
    
    assert exit_code == 2  # CRITICAL
    assert results["status"] == "critical"
    assert any("CNCF projects" in error for error in results["errors"])

def test_insufficient_components(tmp_path):
    """Test with < 3 components (CRITICAL)."""
    analysis = {
        "cncf_projects": [{"name": f"Project{i}"} for i in range(6)],
        "system_architecture": {"components": [{"name": "C1"}]},
        "integration_patterns": [{"name": "P1"}, {"name": "P2"}],
        "scalability_patterns": [{"name": "HPA"}],
        "observability_approach": {"metrics": {}, "logging": {}}
    }
    
    file = tmp_path / "analysis.json"
    file.write_text(json.dumps(analysis))
    
    exit_code, results = validate_deep_analysis(str(file))
    
    assert exit_code == 2  # CRITICAL
    assert "architecture components" in results["errors"][0]

def test_missing_integration_patterns(tmp_path):
    """Test with missing integration patterns (WARNING)."""
    analysis = {
        "cncf_projects": [{"name": f"Project{i}"} for i in range(6)],
        "system_architecture": {"components": [{"name": f"C{i}"} for i in range(4)]},
        "integration_patterns": [],
        "scalability_patterns": [{"name": "HPA"}],
        "observability_approach": {"metrics": {}, "logging": {}}
    }
    
    file = tmp_path / "analysis.json"
    file.write_text(json.dumps(analysis))
    
    exit_code, results = validate_deep_analysis(str(file))
    
    assert exit_code == 1  # WARNING
    assert results["status"] == "warning"
    assert any("integration patterns" in warning for warning in results["warnings"])
```

**Acceptance Criteria:**
- [ ] All validation rules implemented
- [ ] Exit codes correct (0/1/2)
- [ ] Helpful error/warning messages
- [ ] Tests achieve 100% coverage
- [ ] CLI command registered in __main__.py

#### Task 3.2: Implement validate-reference-architecture (Days 8-9)

**File:** `casestudypilot/tools/validate_reference_architecture.py`

**Implementation:**

```python
"""
Validate Reference Architecture Document

Validates generated reference architecture markdown for quality,
completeness, and technical depth.

Exit Codes:
  0 - PASS: Quality threshold met
  1 - WARNING: Below optimal but acceptable
  2 - CRITICAL: Below minimum threshold
"""

import sys
import re
from pathlib import Path
from typing import Dict, Tuple

# CNCF projects list (from existing code)
CNCF_PROJECTS = [
    "Kubernetes", "Prometheus", "Envoy", "CoreDNS", "containerd",
    "Fluentd", "Jaeger", "Vitess", "Helm", "Argo CD", "Flux",
    # ... (full list from existing validator)
]

REQUIRED_SECTIONS = [
    "Executive Summary",
    "Background and Context",
    "Technical Requirements",
    "Architecture Overview",
    "CNCF Technology Stack",
    "Integration Patterns",
    "Scalability and Reliability",
    "Observability and Operations",
    "Security Considerations",
    "Lessons Learned"
]

def count_words(text: str) -> int:
    """Count words in text."""
    return len(re.findall(r'\b\w+\b', text))

def find_sections(markdown: str) -> Dict[str, str]:
    """Extract sections from markdown."""
    sections = {}
    lines = markdown.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def count_cncf_projects(text: str) -> int:
    """Count unique bolded CNCF projects."""
    projects_found = set()
    for project in CNCF_PROJECTS:
        # Look for **ProjectName**
        if f"**{project}**" in text or f"**[{project}]" in text:
            projects_found.add(project)
    return len(projects_found)

def calculate_technical_depth_score(sections: Dict[str, str]) -> Dict:
    """
    Calculate technical depth score based on content analysis.
    
    Returns dict with overall score and subscores.
    """
    scores = {}
    
    # Architecture detail score (0.30 weight)
    arch_section = sections.get("Architecture Overview", "")
    arch_word_count = count_words(arch_section)
    if arch_word_count >= 500:
        scores["architecture_detail"] = 1.0
    elif arch_word_count >= 400:
        scores["architecture_detail"] = 0.8
    elif arch_word_count >= 300:
        scores["architecture_detail"] = 0.6
    else:
        scores["architecture_detail"] = 0.3
    
    # Integration detail score (0.25 weight)
    integration_section = sections.get("Integration Patterns", "")
    integration_word_count = count_words(integration_section)
    if integration_word_count >= 500:
        scores["integration_detail"] = 1.0
    elif integration_word_count >= 400:
        scores["integration_detail"] = 0.8
    elif integration_word_count >= 300:
        scores["integration_detail"] = 0.6
    else:
        scores["integration_detail"] = 0.3
    
    # Scalability detail score (0.20 weight)
    scalability_section = sections.get("Scalability and Reliability", "")
    scalability_word_count = count_words(scalability_section)
    if scalability_word_count >= 450:
        scores["scalability_detail"] = 1.0
    elif scalability_word_count >= 350:
        scores["scalability_detail"] = 0.8
    elif scalability_word_count >= 250:
        scores["scalability_detail"] = 0.6
    else:
        scores["scalability_detail"] = 0.3
    
    # Observability detail score (0.15 weight)
    observability_section = sections.get("Observability and Operations", "")
    observability_word_count = count_words(observability_section)
    if observability_word_count >= 400:
        scores["observability_detail"] = 1.0
    elif observability_word_count >= 300:
        scores["observability_detail"] = 0.8
    elif observability_word_count >= 200:
        scores["observability_detail"] = 0.6
    else:
        scores["observability_detail"] = 0.3
    
    # Security detail score (0.10 weight)
    security_section = sections.get("Security Considerations", "")
    security_word_count = count_words(security_section)
    if security_word_count >= 350:
        scores["security_detail"] = 1.0
    elif security_word_count >= 250:
        scores["security_detail"] = 0.8
    elif security_word_count >= 150:
        scores["security_detail"] = 0.6
    else:
        scores["security_detail"] = 0.3
    
    # Calculate weighted overall score
    technical_depth_score = (
        scores["architecture_detail"] * 0.30 +
        scores["integration_detail"] * 0.25 +
        scores["scalability_detail"] * 0.20 +
        scores["observability_detail"] * 0.15 +
        scores["security_detail"] * 0.10
    )
    
    scores["overall"] = round(technical_depth_score, 2)
    
    return scores

def validate_reference_architecture(
    markdown_file: str,
    threshold: float = 0.70
) -> Tuple[int, Dict]:
    """
    Validate reference architecture markdown.
    
    Returns:
        (exit_code, validation_results)
    """
    try:
        content = Path(markdown_file).read_text()
    except Exception as e:
        return 2, {"error": f"Failed to load markdown file: {e}"}
    
    results = {
        "quality_score": 0.0,
        "technical_depth_score": 0.0,
        "passed": False,
        "threshold": threshold,
        "word_count": 0,
        "sections_present": 0,
        "cncf_projects_count": 0,
        "warnings": [],
        "errors": [],
        "details": {}
    }
    
    # Count words
    word_count = count_words(content)
    results["word_count"] = word_count
    
    # Check word count range
    if word_count < 2000:
        results["errors"].append(
            f"Word count too low: {word_count} words (minimum 2000)"
        )
    elif word_count > 5000:
        results["warnings"].append(
            f"Word count high: {word_count} words (recommended max 5000)"
        )
    
    # Find sections
    sections = find_sections(content)
    results["sections_present"] = len([s for s in REQUIRED_SECTIONS if s in sections])
    
    # Check required sections
    missing_sections = [s for s in REQUIRED_SECTIONS if s not in sections]
    if missing_sections:
        results["errors"].append(
            f"Missing required sections: {', '.join(missing_sections)}"
        )
    
    # Count CNCF projects
    cncf_count = count_cncf_projects(content)
    results["cncf_projects_count"] = cncf_count
    
    if cncf_count < 5:
        results["errors"].append(
            f"Insufficient CNCF projects: {cncf_count} (minimum 5)"
        )
    
    # Calculate technical depth score
    depth_scores = calculate_technical_depth_score(sections)
    results["technical_depth_score"] = depth_scores["overall"]
    results["details"] = {
        "architecture_detail": {"score": depth_scores["architecture_detail"]},
        "integration_detail": {"score": depth_scores["integration_detail"]},
        "scalability_detail": {"score": depth_scores["scalability_detail"]},
        "observability_detail": {"score": depth_scores["observability_detail"]},
        "security_detail": {"score": depth_scores["security_detail"]}
    }
    
    # Calculate overall quality score (average of checks)
    checks_passed = 0
    total_checks = 0
    
    # Word count check
    total_checks += 1
    if 2000 <= word_count <= 5000:
        checks_passed += 1
    
    # Sections check
    total_checks += 1
    if len(missing_sections) == 0:
        checks_passed += 1
    
    # CNCF projects check
    total_checks += 1
    if cncf_count >= 5:
        checks_passed += 1
    
    # Technical depth check
    total_checks += 1
    if depth_scores["overall"] >= threshold:
        checks_passed += 1
    
    results["quality_score"] = round(checks_passed / total_checks, 2)
    results["passed"] = results["quality_score"] >= 0.75 and depth_scores["overall"] >= threshold
    
    # Determine exit code
    if results["errors"]:
        exit_code = 2
    elif results["warnings"]:
        exit_code = 1
    else:
        exit_code = 0
    
    # Override: if technical depth below threshold, always exit 2
    if depth_scores["overall"] < threshold:
        exit_code = 2
        results["errors"].append(
            f"Technical depth score {depth_scores['overall']:.2f} below threshold {threshold}"
        )
    
    return exit_code, results

def main(markdown_file: str, threshold: float = 0.70):
    """CLI entry point."""
    exit_code, results = validate_reference_architecture(markdown_file, threshold)
    
    # Print results
    if exit_code == 0:
        print(f"✅ PASS: Reference architecture validation successful")
    elif exit_code == 1:
        print(f"⚠️ WARNING: Reference architecture has warnings")
    else:
        print(f"❌ CRITICAL: Reference architecture validation failed", file=sys.stderr)
    
    print(f"\nQuality Metrics:")
    print(f"  Quality Score: {results['quality_score']:.2f}")
    print(f"  Technical Depth: {results['technical_depth_score']:.2f} (threshold: {threshold})")
    print(f"  Word Count: {results['word_count']} (target: 2000-5000)")
    print(f"  Sections Present: {results['sections_present']}/{len(REQUIRED_SECTIONS)}")
    print(f"  CNCF Projects: {results['cncf_projects_count']} (minimum: 5)")
    
    if results["warnings"]:
        print(f"\nWarnings:")
        for warning in results["warnings"]:
            print(f"  ⚠️ {warning}")
    
    if results["errors"]:
        print(f"\nErrors:")
        for error in results["errors"]:
            print(f"  ❌ {error}")
    
    print(f"\nTechnical Depth Breakdown:")
    for category, details in results["details"].items():
        print(f"  {category}: {details['score']:.2f}")
    
    sys.exit(exit_code)
```

**Tests:** `tests/test_validate_reference_architecture.py`

```python
import pytest
from pathlib import Path
from casestudypilot.tools.validate_reference_architecture import (
    validate_reference_architecture,
    count_words,
    find_sections,
    count_cncf_projects
)

def test_count_words():
    """Test word counting."""
    assert count_words("Hello world") == 2
    assert count_words("This is a test.") == 4
    assert count_words("") == 0

def test_find_sections():
    """Test section extraction."""
    markdown = """
# Title

## Section 1

Content 1

## Section 2

Content 2
"""
    sections = find_sections(markdown)
    assert "Section 1" in sections
    assert "Section 2" in sections
    assert "Content 1" in sections["Section 1"]

def test_count_cncf_projects():
    """Test CNCF project counting."""
    text = "Using **Kubernetes** and **Prometheus** and **Envoy**"
    assert count_cncf_projects(text) == 3
    
    # Should not count unbolded
    text2 = "Using Kubernetes and Prometheus"
    assert count_cncf_projects(text2) == 0

def test_valid_reference_architecture(tmp_path):
    """Test with valid reference architecture."""
    content = f"""
# Company Reference Architecture

## Executive Summary

{'word ' * 200}

## Background and Context

{'word ' * 350}

## Technical Requirements

{'word ' * 300}

## Architecture Overview

{'word ' * 500} **Kubernetes** **Prometheus** **Envoy** **Helm** **Argo CD** **Fluentd**

## CNCF Technology Stack

{'word ' * 600}

## Integration Patterns

{'word ' * 450}

## Scalability and Reliability

{'word ' * 400}

## Observability and Operations

{'word ' * 350}

## Security Considerations

{'word ' * 300}

## Lessons Learned

{'word ' * 400}
"""
    
    file = tmp_path / "ref-arch.md"
    file.write_text(content)
    
    exit_code, results = validate_reference_architecture(str(file), threshold=0.70)
    
    assert exit_code == 0
    assert results["passed"] == True
    assert results["word_count"] >= 2000
    assert results["cncf_projects_count"] >= 5
    assert results["technical_depth_score"] >= 0.70

def test_too_short(tmp_path):
    """Test with insufficient word count."""
    content = """
# Short Document

## Executive Summary

Only 100 words here.
"""
    
    file = tmp_path / "ref-arch.md"
    file.write_text(content)
    
    exit_code, results = validate_reference_architecture(str(file))
    
    assert exit_code == 2
    assert "Word count too low" in results["errors"][0]

def test_missing_sections(tmp_path):
    """Test with missing required sections."""
    content = f"""
# Incomplete Document

## Executive Summary

{'word ' * 500}

## Background and Context

{'word ' * 500}
"""
    
    file = tmp_path / "ref-arch.md"
    file.write_text(content)
    
    exit_code, results = validate_reference_architecture(str(file))
    
    assert exit_code == 2
    assert any("Missing required sections" in error for error in results["errors"])

def test_insufficient_cncf_projects(tmp_path):
    """Test with < 5 CNCF projects."""
    content = f"""
# Document with Few Projects

{''.join([f'## {section}\n\n' + 'word ' * 300 + '\n\n' for section in [
    "Executive Summary",
    "Background and Context",
    "Technical Requirements",
    "Architecture Overview",
    "CNCF Technology Stack",
    "Integration Patterns",
    "Scalability and Reliability",
    "Observability and Operations",
    "Security Considerations",
    "Lessons Learned"
]])}

Only **Kubernetes** mentioned.
"""
    
    file = tmp_path / "ref-arch.md"
    file.write_text(content)
    
    exit_code, results = validate_reference_architecture(str(file))
    
    assert exit_code == 2
    assert "Insufficient CNCF projects" in results["errors"][0]
```

**Acceptance Criteria:**
- [ ] Word count validation (2000-5000)
- [ ] Section presence check
- [ ] CNCF project counting
- [ ] Technical depth scoring implemented
- [ ] Tests achieve 95%+ coverage
- [ ] CLI command registered

#### Task 3.3: Implement assemble-reference-architecture (Day 10)

**File:** `casestudypilot/tools/assemble_reference_architecture.py`

**Implementation:** Similar to existing `assemble.py` but:
- Uses `reference_architecture.md.j2` template
- Includes diagram specifications
- Embeds 6 screenshots instead of 3
- Adds TAB submission metadata
- Adds validation summary

**File:** `templates/reference_architecture.md.j2`

**Implementation:** See detailed template in section 3.5

**Acceptance Criteria:**
- [ ] Assembler tool implemented
- [ ] Template created with all 10 sections
- [ ] Diagram placeholders work
- [ ] 6 screenshots embedded correctly
- [ ] TAB metadata included
- [ ] Tests achieve 90%+ coverage

---

### Phase 4: Agent Workflow (Days 11-13)

**Objective:** Create the reference architecture agent with 18-step workflow and comprehensive error handling.

#### Task 4.1: Create reference-architecture-agent.md (Days 11-12)

**File:** `.github/agents/reference-architecture-agent.md`

**Content:** See detailed 18-step workflow in section 3.4

**Additional Elements:**

1. **Error Templates** (7 templates for each checkpoint):
   - `error_templates/transcript_quality.md`
   - `error_templates/company_identification.md`
   - `error_templates/deep_analysis_quality.md`
   - `error_templates/architecture_consistency.md`
   - `error_templates/metric_fabrication.md`
   - `error_templates/company_consistency.md`
   - `error_templates/final_quality.md`

2. **PR Template:**
   - `pr_templates/reference_architecture.md`
   - Includes validation summary
   - TAB submission checklist
   - TAB submission guidance
   - Review checklist

**Acceptance Criteria:**
- [ ] All 18 steps documented
- [ ] 7 validation checkpoints specified
- [ ] Error templates created
- [ ] PR template created
- [ ] Exit code handling clear
- [ ] GitHub issue workflow integrated

#### Task 4.2: Update Validation Thresholds (Day 12)

**Files to Update:**
- `casestudypilot/tools/youtube_client.py` - Add `--min-chars` parameter
- `casestudypilot/tools/validator.py` - Add `--threshold` parameter

**Changes:**
```python
# In validate-transcript
def validate_transcript(video_data_file: str, min_chars: int = 1000):
    # Existing code...
    # Allow override of minimum characters
    # Default 1000 for case studies, 2000 for reference architectures

# In validate (final quality)
def validate(markdown_file: str, threshold: float = 0.60):
    # Existing code...
    # Allow override of threshold
    # Default 0.60 for case studies, 0.70 for reference architectures
```

**Acceptance Criteria:**
- [ ] Transcript validation supports higher minimum
- [ ] Final validation supports higher threshold
- [ ] Backward compatible with case studies
- [ ] Tests updated

#### Task 4.3: Test Agent End-to-End (Day 13)

**Test Plan:**
1. Select test video (e.g., Intuit GitOps video)
2. Create test GitHub issue
3. Execute all 18 steps manually
4. Verify each validation checkpoint
5. Test error paths (simulate failures)
6. Generate complete reference architecture
7. Review output quality

**Acceptance Criteria:**
- [ ] All steps execute successfully
- [ ] Validation checkpoints work
- [ ] Error handling works
- [ ] Generated reference architecture passes validation
- [ ] Output is TAB-submission ready

---

### Phase 5: Documentation (Days 14-15)

**Objective:** Create comprehensive documentation for the reference architecture system.

#### Task 5.1: Update Framework Documentation (Day 14)

**README.md Updates:**

Add to "Framework Capabilities" section:
```markdown
### Reference Architecture Generation (v3.0.0)

**Input:** GitHub issue with YouTube URL  
**Output:** Pull request with TAB-ready reference architecture

**Workflow:** 18-step agent orchestration with 7 validation checkpoints

**Example:**
```
Issue: "Reference Architecture Request: Intuit Platform Engineering"
URL: https://www.youtube.com/watch?v=V6L-xOUdoRQ

@reference-architecture-agent please generate this reference architecture

→ Agent: Fetches transcript, validates quality (min 2000 chars)
→ Agent: Applies transcript-deep-analysis skill (extracts architecture)
→ Agent: Applies architecture-diagram-specification skill
→ Agent: Applies reference-architecture-generation skill (10 sections)
→ Agent: Creates PR with reference-architectures/intuit-platform.md + 6 images
```

**Comparison: Case Studies vs. Reference Architectures**

| Feature | Case Studies | Reference Architectures |
|---------|-------------|------------------------|
| Length | 500-1500 words | 2000-5000 words |
| Focus | Business outcomes | Technical architecture |
| CNCF Projects | 2-3 typical | 5-10+ typical |
| Sections | 5 sections | 10 sections |
| Screenshots | 3 images | 6 images |
| Quality Threshold | 0.60 | 0.70 (technical depth) |
| Approval | Internal only | TAB + TOC review |
```

Update CLI commands table:
```markdown
#### Reference Architecture Commands (3 new commands)

```bash
# Validate deep analysis output
python -m casestudypilot validate-deep-analysis deep_analysis.json

# Validate reference architecture document  
python -m casestudypilot validate-reference-architecture ref-arch.md --threshold 0.70

# Assemble reference architecture from components
python -m casestudypilot assemble-reference-architecture \
  video.json analysis.json sections.json verification.json \
  --screenshots screenshots.json \
  --output reference-architectures/company.md
```
```

Update skills table:
```markdown
| Skill | Input | Output | Purpose |
|-------|-------|--------|---------|
| ... existing skills ... |
| `transcript-deep-analysis` | Corrected transcript | Architecture JSON | Extract comprehensive technical details |
| `architecture-diagram-specification` | Deep analysis | Diagram specs JSON | Generate diagram specifications |
| `reference-architecture-generation` | Deep analysis + diagrams | 10 sections JSON | Generate TAB-ready reference architecture |
```

Update agents table:
```markdown
| Agent | Version | Workflow | Validation Checkpoints |
|-------|---------|----------|------------------------|
| `case-study-agent` | 2.2.0 | 14 steps | 5 fail-fast validations |
| `reference-architecture-agent` | 1.0.0 | 18 steps | 7 fail-fast validations |
```

**AGENTS.md Updates:**

Add new section:
```markdown
### Current Implementation: Reference Architecture Generation

**Agent:** `reference-architecture-agent` (v1.0.0)  
**Workflow:** 18 steps with 7 validation checkpoints  
**Location:** `.github/agents/reference-architecture-agent.md`

**Summary:**
1. Pre-flight checks
2. Fetch video data → Validate transcript (min 2000 chars)
3. Extract company name → Validate company
4. Verify CNCF membership
5. **Skill:** Correct transcript
6. **Skill:** Deep analysis (extract architecture patterns)
7. Validate deep analysis (min 5 CNCF projects)
8. **Skill:** Generate diagram specifications
9. Extract 6 screenshots
10. **Skill:** Generate reference architecture (10 sections)
11. Validate architecture content (consistency, fabrication)
12. Assemble markdown with diagrams
13. Validate final quality (technical depth >= 0.70)
14. Create branch
15. Commit (atomic: 1 markdown + 6 images)
16. Create PR with TAB submission guidance

**This extends the case study pattern for deeper technical documentation.**
```

**CONTRIBUTING.md Updates:**

Add comparison section showing when to generate case study vs. reference architecture:
```markdown
### Choosing Case Study vs. Reference Architecture

**Generate Case Study when:**
- Video focuses on business outcomes and metrics
- Less technical depth (primarily problem → solution → results)
- 2-3 CNCF projects mentioned
- Target audience: business stakeholders, managers
- Output: 500-1500 words

**Generate Reference Architecture when:**
- Video provides deep technical details
- Architectural patterns and system design discussed
- 5+ CNCF projects used and integrated
- Target audience: platform engineers, architects
- Output: 2000-5000 words with diagrams
- Intent: Submit to CNCF TAB for publication
```

**Acceptance Criteria:**
- [ ] README.md updated with reference architecture section
- [ ] CLI commands table includes 3 new commands
- [ ] Skills table includes 3 new skills
- [ ] Agents table includes new agent
- [ ] AGENTS.md includes workflow summary
- [ ] CONTRIBUTING.md includes guidance

#### Task 5.2: Create Reference Architecture Docs (Day 15)

**File 1:** `docs/REFERENCE-ARCHITECTURE-WORKFLOW.md`

**Content:**
- Detailed explanation of 18-step workflow
- When to use reference architecture vs. case study
- TAB submission process overview
- Quality standards and expectations
- Example timeline for TAB review
- FAQ section

**File 2:** `docs/REFERENCE-ARCHITECTURE-COMPARISON.md`

**Content:**
- Side-by-side comparison of case study vs. reference architecture
- Input requirements comparison
- Output quality comparison
- Use case examples
- Decision matrix

**File 3:** Update `docs/validation-workflow-updates.md`

**Content:**
- Add reference architecture validation checkpoints
- Document new validation tools
- Explain technical depth scoring
- Compare validation standards

**Acceptance Criteria:**
- [ ] REFERENCE-ARCHITECTURE-WORKFLOW.md created (1000+ words)
- [ ] REFERENCE-ARCHITECTURE-COMPARISON.md created (800+ words)
- [ ] validation-workflow-updates.md updated
- [ ] All documentation uses consistent terminology
- [ ] Examples provided throughout

#### Task 5.3: Create GitHub Issue Template (Day 15)

**File:** `.github/ISSUE_TEMPLATE/reference-architecture-request.yml`

**Content:**
```yaml
name: Reference Architecture Request
description: Request generation of a CNCF reference architecture from a video
title: ""
labels: ["reference-architecture"]
body:
  - type: markdown
    attributes:
      value: |
        ## Reference Architecture Generation Request
        
        This will generate a comprehensive technical reference architecture document suitable for CNCF TAB submission.
        
        **Note:** Reference architectures are more detailed than case studies. Use this template when the video contains deep technical details about system architecture.
  
  - type: input
    id: video-url
    attributes:
      label: YouTube Video URL
      description: The full YouTube video URL
      placeholder: https://www.youtube.com/watch?v=...
    validations:
      required: true
  
  - type: input
    id: company
    attributes:
      label: Company Name
      description: The company featured in the video
      placeholder: Example Corp
    validations:
      required: true
  
  - type: dropdown
    id: domain
    attributes:
      label: Domain/Industry
      description: What domain or industry does this reference architecture apply to?
      options:
        - Platform Engineering
        - Cloud Infrastructure
        - DevOps/GitOps
        - Observability
        - Security
        - Data/AI
        - Edge Computing
        - Other
    validations:
      required: false
  
  - type: textarea
    id: technical-focus
    attributes:
      label: Technical Focus
      description: What are the main technical topics covered? (e.g., "Multi-cluster Kubernetes with service mesh and GitOps")
      placeholder: Multi-cluster Kubernetes, Envoy service mesh, Argo CD GitOps, Prometheus observability
    validations:
      required: false
  
  - type: checkboxes
    id: cncf-projects
    attributes:
      label: CNCF Projects Mentioned (if known)
      description: Check all CNCF projects mentioned in the video (helps with validation)
      options:
        - label: Kubernetes
        - label: Prometheus
        - label: Envoy
        - label: Argo CD
        - label: Helm
        - label: Fluentd
        - label: Jaeger
        - label: Other (specify in notes)
  
  - type: textarea
    id: additional-notes
    attributes:
      label: Additional Notes
      description: Any other information that would help with generation
      placeholder: This video is particularly detailed about the service mesh implementation...
    validations:
      required: false
  
  - type: checkboxes
    id: requirements
    attributes:
      label: Requirements
      description: Confirm you have reviewed the requirements
      options:
        - label: Video is from the CNCF YouTube channel
          required: true
        - label: Video has English captions/transcript
          required: true
        - label: Video contains deep technical details (not just business overview)
          required: true
        - label: Company is a CNCF end user member (or verification provided)
          required: true
  
  - type: markdown
    attributes:
      value: |
        ---
        
        ## Next Steps
        
        Once submitted, the `@reference-architecture-agent` will:
        1. Extract and validate the transcript (min 2000 characters)
        2. Perform deep technical analysis
        3. Generate comprehensive 10-section reference architecture
        4. Create a pull request with the result
        
        The generated reference architecture will be suitable for submission to the CNCF End User TAB for review and publication.
        
        **Estimated time:** 5-10 minutes for generation, then TAB review process (weeks)
```

**Acceptance Criteria:**
- [ ] Issue template created
- [ ] Fields appropriate for reference architectures
- [ ] Auto-labels with `reference-architecture`
- [ ] Clear requirements checklist
- [ ] Next steps documented

---

### Phase 6: Testing and Validation (Days 16-17)

**Objective:** Comprehensive testing of the reference architecture system.

#### Task 6.1: Integration Testing (Day 16)

**Test 1: Complete Workflow with Real Video**

Select video: Intuit GitOps journey (already tested for case study)

```bash
# Step-by-step execution
python -m casestudypilot youtube-data "https://www.youtube.com/watch?v=V6L-xOUdoRQ" \
  --output video_data.json

python -m casestudypilot validate-transcript video_data.json --min-chars 2000

# Apply transcript-correction skill (manual)
# ... (LLM execution)

# Apply transcript-deep-analysis skill (manual)
# ... (LLM execution)

python -m casestudypilot validate-deep-analysis deep_analysis.json

# Apply architecture-diagram-specification skill (manual)
# ... (LLM execution)

python -m casestudypilot extract-screenshots \
  video_data.json deep_analysis.json ref_arch_sections.json \
  --count 6 --download-dir reference-architectures/images/intuit/

# Apply reference-architecture-generation skill (manual)
# ... (LLM execution)

python -m casestudypilot assemble-reference-architecture \
  video_data.json deep_analysis.json ref_arch_sections.json company_verification.json \
  --screenshots screenshots.json \
  --output reference-architectures/intuit-platform.md

python -m casestudypilot validate-reference-architecture \
  reference-architectures/intuit-platform.md --threshold 0.70
```

**Expected Results:**
- All validations pass
- Technical depth score >= 0.70
- Word count 2000-5000
- 5+ CNCF projects identified
- All 10 sections present

**Test 2: Different Video (Different Technical Focus)**

Select video with different technical focus (e.g., observability-focused vs. GitOps-focused)

Repeat workflow, verify:
- Skills adapt to different technical content
- Diagram specifications appropriate for architecture type
- Quality standards maintained

**Test 3: Error Path Testing**

Simulate failures:
- Short transcript (< 2000 chars) → Should stop at checkpoint 1
- < 5 CNCF projects in deep analysis → Should stop at checkpoint 3
- Low technical depth score → Should stop at checkpoint 7

**Acceptance Criteria:**
- [ ] 2-3 reference architectures generated successfully
- [ ] All pass validation (technical depth >= 0.70)
- [ ] Error paths tested and work correctly
- [ ] Quality comparable or better than existing case studies in technical depth

#### Task 6.2: Quality Validation (Day 17)

**Manual Review Checklist:**

For each generated reference architecture:

**Content Quality:**
- [ ] All 10 sections present and substantive
- [ ] Technical details accurate (cross-check with video)
- [ ] CNCF projects correctly identified
- [ ] Integration patterns accurately described
- [ ] No fabricated technical claims
- [ ] Metrics match video transcript

**Technical Depth:**
- [ ] Architecture components clearly explained
- [ ] Integration patterns detailed
- [ ] Scalability considerations documented
- [ ] Observability approach comprehensive
- [ ] Security considerations present

**Format Quality:**
- [ ] Markdown formatting correct
- [ ] CNCF projects bolded
- [ ] Metrics bolded
- [ ] Hyperlinks work
- [ ] Screenshots embedded correctly
- [ ] Diagram specifications clear

**TAB Readiness:**
- [ ] TAB submission metadata present
- [ ] Submission checklist complete
- [ ] Quality validation summary included
- [ ] Appropriate for TAB review

**Comparison with Case Study:**
- [ ] Significantly more technical depth than case study version
- [ ] Complementary rather than duplicate
- [ ] Architecture focus vs. business outcomes focus

**Acceptance Criteria:**
- [ ] Manual review checklist completed for 2+ reference architectures
- [ ] Quality issues documented and addressed
- [ ] Side-by-side comparison with case study shows clear differentiation
- [ ] Ready for TAB submission (if desired)

#### Task 6.3: Performance Validation (Day 17)

**Metrics to Measure:**

```bash
# Time workflow execution
time {
  # Execute all 18 steps
  # ...
}
```

**Expected Performance:**
- Total execution time: 20-30% longer than case studies (acceptable)
- Transcript fetching: Same as case studies
- Screenshot extraction: ~2x longer (6 images vs. 3)
- Validation: Minimal overhead (<10 seconds total)
- Assembly: Minimal overhead (<5 seconds)

**Resource Usage:**
- Memory: <4GB
- Disk: ~1-2MB per reference architecture (markdown + images)
- CPU: Normal (LLM execution is external)

**Acceptance Criteria:**
- [ ] Execution time documented
- [ ] Performance acceptable (no blocking issues)
- [ ] Resource usage reasonable
- [ ] No memory leaks or resource exhaustion

---

### Phase 7: Finalization (Day 18)

**Objective:** Final review, example generation, and release preparation.

#### Task 7.1: Final Review (Morning)

**Code Review:**
- [ ] All Python code follows PEP 8
- [ ] Type hints present where appropriate
- [ ] Docstrings complete
- [ ] No hardcoded values
- [ ] Error handling comprehensive
- [ ] Logging appropriate

**Skill Review:**
- [ ] All 3 skills have complete SKILL.md files
- [ ] Input/output schemas clear
- [ ] Execution instructions detailed
- [ ] Examples provided
- [ ] Quality guidelines comprehensive

**Documentation Review:**
- [ ] README.md updates complete
- [ ] AGENTS.md updates complete
- [ ] CONTRIBUTING.md updates complete
- [ ] New docs files created
- [ ] Issue template created
- [ ] All docs use consistent terminology

**Test Review:**
- [ ] Test coverage >= 80% for new tools
- [ ] Integration tests pass
- [ ] Error path tests pass
- [ ] Performance acceptable

**Acceptance Criteria:**
- [ ] All code reviews completed
- [ ] No critical issues found
- [ ] Test coverage meets standards
- [ ] Documentation complete and accurate

#### Task 7.2: Generate Example Reference Architecture (Afternoon)

**Select Best Video:**
- Choose video with rich technical content
- Ideally 30+ minutes with architectural details
- Clear CNCF project usage

**Generate Complete Example:**
1. Create GitHub issue using new template
2. Execute complete 18-step workflow
3. Review and refine if needed
4. Use as gold standard example

**Polish Example:**
- Ensure highest quality
- Verify TAB readiness
- Add inline comments if helpful
- Create PR as example

**Acceptance Criteria:**
- [ ] 1 high-quality reference architecture generated
- [ ] Passes all validations with high scores
- [ ] Technical depth score >= 0.80
- [ ] Ready for TAB submission (optional)
- [ ] Can serve as template for future generations

#### Task 7.3: Update Changelog and Release (Late Afternoon)

**File:** `CHANGELOG.md`

**Content:**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-02-XX

### Added - Reference Architecture Generation

**New Capability:** Generate comprehensive CNCF reference architectures suitable for End User TAB submission.

#### New LLM Skills (3)
- `transcript-deep-analysis` - Extract comprehensive architectural patterns from transcripts
  - Identifies system architecture components and layers
  - Documents 5+ CNCF projects with detailed usage context
  - Captures integration patterns, scalability approaches, observability
  - Minimum 5 CNCF projects required
- `architecture-diagram-specification` - Generate textual diagram specifications
  - Component diagrams, data flow, deployment topology
  - Mermaid syntax support for automatic rendering
- `reference-architecture-generation` - Generate 10-section reference architecture
  - 2000-5000 words comprehensive technical documentation
  - Architecture-focused vs. business-focused
  - TAB submission ready

#### New CLI Tools (3)
- `validate-deep-analysis` - Validate architectural analysis output
  - Minimum 5 CNCF projects (vs. 2 for case studies)
  - Architecture components validation
  - Integration patterns validation
  - Exit codes: 0/1/2
- `validate-reference-architecture` - Validate final reference architecture
  - Technical depth scoring (5 sub-scores)
  - Threshold 0.70 (vs. 0.60 for case studies)
  - Word count range: 2000-5000
  - 10 required sections
- `assemble-reference-architecture` - Assemble reference architecture from components
  - New template: `reference_architecture.md.j2`
  - 6 screenshots (vs. 3 for case studies)
  - Diagram specifications included
  - TAB submission metadata

#### New Agent (1)
- `reference-architecture-agent` (v1.0.0) - 18-step workflow
  - 7 validation checkpoints (vs. 5 for case studies)
  - Higher quality thresholds throughout
  - TAB submission guidance in PR

#### Enhanced Validation
- Technical depth scoring system (5 dimensions):
  - Architecture detail (30% weight)
  - Integration detail (25% weight)
  - Scalability detail (20% weight)
  - Observability detail (15% weight)
  - Security detail (10% weight)
- Configurable thresholds for different document types
- Minimum transcript length configurable (2000 chars for ref arch)

#### Documentation
- Added `docs/REFERENCE-ARCHITECTURE-WORKFLOW.md`
- Added `docs/REFERENCE-ARCHITECTURE-COMPARISON.md`
- Updated README.md with reference architecture capabilities
- Updated AGENTS.md with new agent workflow
- Updated CONTRIBUTING.md with guidance
- Added `.github/ISSUE_TEMPLATE/reference-architecture-request.yml`

#### Testing
- 1,500+ lines of new tests
- Integration tests for full workflow
- Quality validation tests
- Performance validation

### Changed
- `validate-transcript` now accepts `--min-chars` parameter (default 1000, 2000 for ref arch)
- `validate` (final quality) now accepts `--threshold` parameter (default 0.60, 0.70 for ref arch)
- Framework version bump: 2.2.0 → 3.0.0

### Technical Details
- Backward compatible with case study generation
- Reuses 40% of existing infrastructure
- No new external dependencies
- Zero configuration (no API keys required)

### For LLM Agents
- Reference architectures are deeper than case studies (see comparison table)
- Use `reference-architecture-agent` for architectural content
- Use `case-study-agent` for business outcome content
- Both can be generated from the same video if content supports it

## [2.2.0] - 2026-02-09

### Added - Fail-Fast Validation Framework
... (existing content)
```

**Version Bumps:**
Update version numbers in:
- `README.md` - Change "Version: 2.2.0" to "Version: 3.0.0"
- `casestudypilot/__init__.py` - `__version__ = "3.0.0"`
- `.github/agents/reference-architecture-agent.md` - `version: 1.0.0`

**Git Tag:**
```bash
git tag -a v3.0.0 -m "Release v3.0.0: Reference Architecture Generation"
```

**Acceptance Criteria:**
- [ ] CHANGELOG.md updated with comprehensive v3.0.0 entry
- [ ] Version numbers updated in all files
- [ ] Git tag created (after final commit)
- [ ] Release notes prepared

---

## 5. Quality Standards

### 5.1 Reference Architecture Quality Thresholds

**Minimum Requirements (CRITICAL - Must Pass):**
- Word count: 2000-5000 words
- CNCF projects: Minimum 5 unique projects identified and bolded
- Sections: All 10 required sections present with content
- Technical depth score: >= 0.70
- Transcript quality: Minimum 2000 characters

**Optimal Targets (Recommended):**
- Word count: 3000-4000 words (sweet spot)
- CNCF projects: 7-10 projects
- Technical depth score: >= 0.80
- Section balance: Each section meets word count targets
- Diagrams: 3-4 diagram specifications provided
- Screenshots: 6 high-quality images embedded

### 5.2 Technical Depth Scoring

**Architecture Detail (30% weight):**
- **1.0:** Multiple paragraphs with specific component descriptions, clear layers, integration points detailed
- **0.8:** Good component descriptions with some integration detail
- **0.6:** Basic component descriptions
- **0.3:** Only high-level mentions
- **0.0:** No architectural detail

**Integration Detail (25% weight):**
- **1.0:** Detailed patterns with examples, API specs, data flow explained
- **0.8:** Good pattern descriptions with some specifics
- **0.6:** Basic pattern mentions
- **0.3:** Only high-level integration mentions
- **0.0:** No integration detail

**Scalability Detail (20% weight):**
- **1.0:** Multiple scaling patterns with metrics, load balancing details, auto-scaling configs
- **0.8:** Good scalability description with some specifics
- **0.6:** Basic scalability mentions
- **0.3:** Only high-level scalability mentions
- **0.0:** No scalability detail

**Observability Detail (15% weight):**
- **1.0:** Detailed metrics, logging, tracing with tools, retention, volume specs
- **0.8:** Good observability description
- **0.6:** Basic observability mentions
- **0.3:** Only high-level mentions
- **0.0:** No observability detail

**Security Detail (10% weight):**
- **1.0:** Multiple security patterns, authentication details, encryption, secrets management
- **0.8:** Good security description
- **0.6:** Basic security mentions
- **0.3:** Only high-level mentions
- **0.0:** No security detail

**Overall Score Calculation:**
```python
technical_depth_score = (
    architecture_detail * 0.30 +
    integration_detail * 0.25 +
    scalability_detail * 0.20 +
    observability_detail * 0.15 +
    security_detail * 0.10
)

# Must be >= 0.70 to pass
```

### 5.3 Validation Checkpoint Standards

**Checkpoint 1: Transcript Quality (Step 3)**
- CRITICAL: Transcript >= 2000 characters
- WARNING: Transcript 2000-3000 characters
- PASS: Transcript > 3000 characters

**Checkpoint 2: Company Identification (Step 5)**
- CRITICAL: Generic placeholder detected
- WARNING: Low confidence match
- PASS: High confidence match

**Checkpoint 3: Deep Analysis Quality (Step 9)**
- CRITICAL: < 5 CNCF projects OR < 3 architecture components
- WARNING: < 2 integration patterns OR missing scalability
- PASS: All requirements met

**Checkpoint 4: Architecture Consistency (Step 13)**
- CRITICAL: Wrong company mentioned
- WARNING: Inconsistent project mentions
- PASS: Company and projects consistent

**Checkpoint 5: Metric Fabrication (Step 13)**
- CRITICAL: Fabricated metrics detected
- WARNING: Possible fabrication (low confidence)
- PASS: All metrics from transcript

**Checkpoint 6: Company Consistency (Step 13)**
- CRITICAL: Company name changes throughout document
- WARNING: Minor inconsistencies
- PASS: Company consistent

**Checkpoint 7: Final Quality (Step 15)**
- CRITICAL: Technical depth < 0.70 OR word count out of range OR missing sections
- WARNING: Technical depth 0.70-0.75 OR minor issues
- PASS: Technical depth >= 0.75 AND all requirements met

### 5.4 Comparison Standards

**vs. Case Studies:**

Reference architectures should be:
- **2-3x longer** in word count
- **2-3x more CNCF projects** identified
- **2x more sections** (10 vs. 5)
- **2x more screenshots** (6 vs. 3)
- **Higher technical depth** (0.70+ vs. 0.60+)
- **More technical focus** (architecture vs. business outcomes)

**Differentiation Test:**
If a reference architecture could easily be cut down to a case study without losing critical architectural detail, it may not have sufficient depth.

**Complementarity Test:**
An ideal situation: both a case study AND a reference architecture can be generated from the same video, targeting different audiences and purposes.

---

## 6. Testing Strategy

### 6.1 Unit Tests

**Test Coverage Targets:**
- `validate_deep_analysis.py`: 100% coverage
- `validate_reference_architecture.py`: 95% coverage
- `assemble_reference_architecture.py`: 90% coverage

**Test Categories:**

**1. Validation Logic Tests:**
```python
# Test all validation rules
- Test CNCF project counting (5 min)
- Test architecture component validation
- Test integration pattern validation
- Test technical depth scoring algorithm
- Test word counting
- Test section detection
```

**2. Edge Case Tests:**
```python
# Test boundary conditions
- Exactly 2000 words (minimum)
- Exactly 5000 words (maximum)
- Exactly 5 CNCF projects (minimum)
- Technical depth score exactly 0.70 (threshold)
- Missing one section vs. all sections
```

**3. Error Handling Tests:**
```python
# Test error conditions
- Malformed JSON input
- Missing required fields
- File not found
- Invalid markdown structure
- Empty content
```

**4. Integration Tests:**
```python
# Test component interactions
- Deep analysis → Diagram spec → Generation
- Generation → Assembly → Validation
- Full workflow simulation
```

### 6.2 Integration Tests

**End-to-End Workflow Tests:**

**Test 1: Happy Path**
- Input: Well-structured video with rich technical content
- Expected: All steps pass, technical depth >= 0.75
- Validates: Complete workflow works

**Test 2: Minimum Requirements**
- Input: Video with exactly minimum requirements (5 projects, 2000 chars)
- Expected: All steps pass, technical depth ~0.70
- Validates: Minimum threshold works

**Test 3: Insufficient Content**
- Input: Video with only 3 CNCF projects, 1500 chars transcript
- Expected: Fails at checkpoint 3 (deep analysis validation)
- Validates: Fail-fast works

**Test 4: Low Technical Depth**
- Input: Video with light technical details
- Expected: Fails at checkpoint 7 (final quality)
- Validates: Technical depth scoring works

**Test 5: Different Architecture Types**
- Input A: GitOps-focused architecture
- Input B: Observability-focused architecture
- Input C: Security-focused architecture
- Expected: All pass with appropriate focus distribution
- Validates: Flexibility across architecture types

### 6.3 Manual Testing

**Skill Testing:**
Skills cannot be unit tested (LLM-powered). Manual testing required:

**1. transcript-deep-analysis:**
- Test with 3 different videos
- Verify architectural components extracted correctly
- Verify CNCF projects identified accurately
- Verify integration patterns make sense
- Verify output JSON is valid

**2. architecture-diagram-specification:**
- Test diagram specs are clear
- Test Mermaid syntax is valid (if generated)
- Test different diagram types work
- Verify diagrams match architecture

**3. reference-architecture-generation:**
- Test with 2-3 different inputs
- Verify all 10 sections generated
- Verify word count in range
- Verify technical depth appropriate
- Verify no fabrication
- Verify quality meets standards

**Quality Review Checklist:**
For each manually tested output:
- [ ] Technical accuracy (cross-check with video)
- [ ] CNCF projects correct
- [ ] Integration patterns valid
- [ ] No fabricated claims
- [ ] Appropriate technical depth
- [ ] TAB submission ready

### 6.4 Performance Testing

**Metrics to Track:**

**Execution Time:**
- Transcript fetching: <30 seconds (same as case studies)
- Deep analysis validation: <5 seconds
- Screenshot extraction (6 images): <60 seconds
- Reference architecture validation: <10 seconds
- Assembly: <5 seconds
- **Total workflow: 5-7 minutes** (vs. 4-5 minutes for case studies)

**Resource Usage:**
- Memory peak: <4GB
- Disk per reference architecture: ~1-2MB (markdown + 6 images)
- CPU: Normal (LLM execution is external)

**Scalability:**
- Should handle concurrent workflows (if multiple agents running)
- No file locking issues
- No resource exhaustion

**Performance Acceptance Criteria:**
- [ ] Total execution time <10 minutes
- [ ] Memory usage <4GB
- [ ] No blocking operations
- [ ] No resource leaks

---

## 7. Risk Management

### 7.1 Technical Risks

**Risk 1: Insufficient Technical Depth in Transcripts**

**Probability:** Medium  
**Impact:** High (cannot generate quality reference architecture)

**Mitigation:**
- Higher transcript quality threshold (2000 chars vs. 1000)
- Early validation checkpoint (step 3)
- Deep analysis validation (step 9) catches insufficient detail
- Provide clear guidance in issue template

**Contingency:**
- If validation fails, post helpful error message
- Suggest generating case study instead
- Suggest different video

**Risk 2: LLM Hallucination of Architecture Details**

**Probability:** Medium  
**Impact:** Critical (inaccurate technical information)

**Mitigation:**
- Strict skill instructions: "only use information from transcript"
- Fabrication detection: cross-check technical claims against transcript
- Multiple validation checkpoints
- TAB review process catches errors (external validation)

**Contingency:**
- Validation checkpoint stops workflow if critical hallucination detected
- Manual review before TAB submission

**Risk 3: Diagram Specification Quality**

**Probability:** Low  
**Impact:** Medium (unclear diagrams)

**Mitigation:**
- Detailed examples in skill documentation
- Structured output format
- Textual specifications allow manual diagram creation

**Contingency:**
- Diagram specs are guidance, not requirements
- Manual diagram creation from specifications

**Risk 4: Complex Architectures Exceed Word Limit**

**Probability:** Low  
**Impact:** Low (can be edited down)

**Mitigation:**
- Skills trained to target 3000-4000 words (middle of range)
- Validation allows up to 5000 words

**Contingency:**
- Edit generated content to reduce word count
- Split into multiple reference architectures if necessary

### 7.2 Process Risks

**Risk 5: TAB Rejection Rate**

**Probability:** Medium-High (first submissions)  
**Impact:** High (wasted effort, framework credibility)

**Mitigation:**
- Higher quality thresholds (0.70 vs. 0.60)
- More comprehensive validation
- Study existing published reference architectures
- Include TAB submission guidance
- First submissions should be manually reviewed before TAB submission

**Contingency:**
- Iterate based on TAB feedback
- Improve skills and validation based on patterns
- Build library of successful examples

**Risk 6: Longer Execution Time Impacts User Experience**

**Probability:** Low  
**Impact:** Low (acceptable tradeoff)

**Mitigation:**
- 20-30% longer execution time is acceptable for higher quality
- Set expectations in documentation
- Optimize where possible (parallel validation)

**Contingency:**
- If execution time becomes problematic, optimize bottlenecks
- Consider async processing for long operations

**Risk 7: Skills Difficult to Maintain**

**Probability:** Medium  
**Impact:** Medium (quality degradation)

**Mitigation:**
- Comprehensive skill documentation
- Clear examples in skills
- Validation checkpoints catch quality issues
- Regular testing with new videos

**Contingency:**
- Iterative skill improvement based on outputs
- Community feedback integration
- Version control for skills

### 7.3 Risk Monitoring

**Metrics to Track:**
1. **Validation Failure Rate** - How often reference architectures fail each checkpoint
2. **Technical Depth Scores** - Average and distribution
3. **TAB Rejection Rate** - If submitted, how many accepted vs. rejected
4. **Word Count Distribution** - Are outputs consistently in range?
5. **CNCF Project Counts** - Average number identified

**Red Flags:**
- Checkpoint 3 failure rate >50% (deep analysis issues)
- Checkpoint 7 failure rate >30% (final quality issues)
- Technical depth scores consistently <0.75 (marginal quality)
- TAB rejection rate >70% (not meeting standards)

**Action Plan:**
- Weekly review of metrics during first month
- Iterate on skills based on failure patterns
- Adjust validation thresholds if needed
- Document lessons learned

---

## 8. Open Questions

**For User Decision Before Implementation:**

### Q1: Scope and Phasing

**Question:** Should we implement all features in one release (v3.0.0) or phase the rollout?

**Options:**
- **A. Full Implementation:** All 3 skills, 3 tools, 1 agent, complete docs (18 days)
- **B. MVP First:** Core skills + basic validation, then enhance (10 days + 8 days)
- **C. Parallel with Case Studies:** Develop alongside case study improvements

**Recommendation:** Option A (Full Implementation)  
**Rationale:** Maintains consistency, avoids partial features, users get complete capability

**Decision:** _____________

### Q2: Diagram Generation Approach

**Question:** How should we handle architecture diagrams?

**Options:**
- **A. Textual Specifications Only:** Skills generate text descriptions, manual diagram creation
- **B. Mermaid Integration:** Auto-generate Mermaid diagrams from specifications
- **C. PlantUML Support:** Support multiple diagramming tools
- **D. External Tool:** Integrate with dedicated diagramming service

**Recommendation:** Option A for MVP, Option B for future enhancement  
**Rationale:** Textual specs provide value immediately, Mermaid can be added incrementally

**Decision:** _____________

### Q3: TAB Integration Level

**Question:** How deeply should we integrate with CNCF TAB workflow?

**Options:**
- **A. Guidance Only:** Provide submission checklist and instructions in PR (manual submission)
- **B. Draft Issue:** Auto-create draft GitHub issue in cncf/tab repo (requires auth)
- **C. API Integration:** Fully automate TAB submission process

**Recommendation:** Option A for initial release  
**Rationale:** Respects TAB process, avoids authentication complexity, allows human review

**Decision:** _____________

### Q4: Quality Threshold Calibration

**Question:** Are the proposed quality thresholds appropriate?

**Current Proposal:**
- Technical depth score >= 0.70 (vs. 0.60 for case studies)
- Word count 2000-5000 (vs. 500-1500)
- Minimum 5 CNCF projects (vs. 2)
- Transcript minimum 2000 characters (vs. 1000)

**Options:**
- **A. Keep As Proposed:** Thresholds seem appropriate
- **B. Lower Thresholds:** Make easier to pass (e.g., 0.65, 1500-4000 words, 4 projects)
- **C. Higher Thresholds:** Make more stringent (e.g., 0.75, 2500-5000 words, 6 projects)
- **D. Configurable:** Allow threshold configuration per invocation

**Recommendation:** Option A, with Option D for future flexibility  
**Rationale:** Start with reasonable standards, adjust based on real-world results

**Decision:** _____________

### Q5: Agent Reuse Strategy

**Question:** How should reference architecture agent relate to case study agent?

**Options:**
- **A. Separate Agents:** Completely independent (current plan)
  - Pros: Clear separation, optimized for each purpose
  - Cons: Some code duplication, two agents to maintain
- **B. Unified Agent with Mode:** Single agent with `--mode=case-study|reference-architecture`
  - Pros: Code reuse, single agent to maintain
  - Cons: More complex logic, risk of coupling
- **C. Base Agent + Extensions:** Shared base workflow with pluggable extensions
  - Pros: Maximum reuse, clean architecture
  - Cons: More upfront design complexity

**Recommendation:** Option A for v3.0.0, consider Option C for future refactoring  
**Rationale:** Clear separation for initial release, refactor when patterns emerge

**Decision:** _____________

### Q6: Testing Requirements

**Question:** What level of testing is required before production use?

**Criteria:**
- How many reference architectures should we generate for validation?
- Should we submit one to CNCF TAB for real-world validation?
- What test coverage percentage is acceptable?
- Should we get external review before release?

**Options:**
- **A. Minimum Viable:** 2 reference architectures, 80% test coverage, internal review only
- **B. Standard:** 3-4 reference architectures, 90% test coverage, community feedback
- **C. Comprehensive:** 5+ reference architectures, 95% test coverage, TAB submission for validation

**Recommendation:** Option B (Standard)  
**Rationale:** Balance between thoroughness and time-to-market

**Decision:** _____________

### Q7: Priority and Timeline

**Question:** What is the priority for this work relative to other framework enhancements?

**Context:**
- Issue #16: Landscape MCP server integration
- Potential: Multi-language support
- Potential: Batch processing
- Potential: Web UI

**Options:**
- **A. High Priority:** Start immediately after this planning document approved
- **B. Medium Priority:** Start after completing Issue #16
- **C. Low Priority:** Defer to future milestone

**Recommendation:** Option A (High Priority)  
**Rationale:** Natural extension of case study system, high value for CNCF community

**Decision:** _____________

---

## 9. Implementation Checklist

**Use this checklist to track progress:**

### Phase 1: Foundation (Days 1-2)
- [ ] Create directory structure
- [ ] Create Python module stubs
- [ ] Update .gitignore
- [ ] Create test structure

### Phase 2: LLM Skills (Days 3-6)
- [ ] Create transcript-deep-analysis skill (Day 3)
- [ ] Create architecture-diagram-specification skill (Day 4)
- [ ] Create reference-architecture-generation skill (Days 5-6)
- [ ] Review all skills for completeness

### Phase 3: CLI Tools (Days 7-10)
- [ ] Implement validate-deep-analysis (Day 7)
- [ ] Implement validate-reference-architecture (Days 8-9)
- [ ] Implement assemble-reference-architecture (Day 10)
- [ ] Create reference_architecture.md.j2 template
- [ ] Register CLI commands in __main__.py
- [ ] Tests achieve target coverage

### Phase 4: Agent Workflow (Days 11-13)
- [ ] Create reference-architecture-agent.md (Days 11-12)
- [ ] Create error templates (7 templates)
- [ ] Create PR template
- [ ] Update validation thresholds (Day 12)
- [ ] Test agent end-to-end (Day 13)

### Phase 5: Documentation (Days 14-15)
- [ ] Update README.md (Day 14)
- [ ] Update AGENTS.md (Day 14)
- [ ] Update CONTRIBUTING.md (Day 14)
- [ ] Create REFERENCE-ARCHITECTURE-WORKFLOW.md (Day 15)
- [ ] Create REFERENCE-ARCHITECTURE-COMPARISON.md (Day 15)
- [ ] Update validation-workflow-updates.md (Day 15)
- [ ] Create GitHub issue template (Day 15)

### Phase 6: Testing (Days 16-17)
- [ ] Integration testing with real videos (Day 16)
- [ ] Quality validation - manual review (Day 17)
- [ ] Performance validation (Day 17)
- [ ] Error path testing
- [ ] Side-by-side comparison with case studies

### Phase 7: Finalization (Day 18)
- [ ] Final code review (Morning)
- [ ] Final documentation review (Morning)
- [ ] Generate example reference architecture (Afternoon)
- [ ] Update CHANGELOG.md (Afternoon)
- [ ] Update version numbers (Afternoon)
- [ ] Create git tag v3.0.0

### Post-Implementation
- [ ] Generate 2-3 reference architectures for validation
- [ ] Consider TAB submission for one example
- [ ] Gather community feedback
- [ ] Iterate based on real-world usage

---

## 10. Success Criteria

### Must Have (MVP)
- [ ] All 3 new skills documented and functional
- [ ] All 3 new CLI tools implemented with tests
- [ ] Reference architecture agent executes end-to-end (18 steps)
- [ ] Generated architectures pass technical depth validation (>= 0.70)
- [ ] Word count consistently 2000-5000 words
- [ ] Minimum 5 CNCF projects identified per architecture
- [ ] At least 1 complete reference architecture generated and reviewed
- [ ] TAB submission guidance included and clear
- [ ] Documentation comprehensive
- [ ] Backward compatible with case studies

### Should Have
- [ ] Architecture diagram specifications clear and actionable
- [ ] Technical depth scoring accurate and meaningful
- [ ] Error handling covers all failure modes
- [ ] Test coverage >= 80% for new tools
- [ ] 2-3 reference architectures generated for validation
- [ ] Quality consistently high (technical depth >= 0.75)
- [ ] Performance acceptable (execution time <10 minutes)

### Nice to Have
- [ ] Automatic Mermaid diagram generation
- [ ] Integration with TAB GitHub issue workflow (auto-draft)
- [ ] Batch processing support
- [ ] Comparison mode (generate both case study + ref arch)
- [ ] Quality metrics dashboard
- [ ] Community feedback incorporated
- [ ] One reference architecture submitted to TAB for validation

### Success Metrics

**Quantitative:**
- Technical depth score average: >= 0.75
- TAB submission readiness: 100% of generated architectures
- Validation failure rate: <30% at any checkpoint
- Word count compliance: 90%+ in target range
- CNCF project identification: Average 7+ projects

**Qualitative:**
- Generated architectures are substantively different from case studies
- Technical depth is sufficient for platform engineers/architects
- Diagram specifications are clear and implementable
- TAB submission guidance is helpful and complete
- Framework remains maintainable and extensible

---

## 11. Conclusion

This implementation plan provides a comprehensive roadmap for extending the casestudypilot framework to generate CNCF reference architectures. The 18-day timeline is realistic, the architecture design reuses proven patterns while adding necessary depth, and the quality standards ensure TAB-ready output.

**Key Strengths:**
✅ Builds on successful case study system (40% code reuse)  
✅ Comprehensive validation (7 checkpoints vs. 5)  
✅ Clear quality standards (technical depth scoring)  
✅ Detailed implementation plan (7 phases)  
✅ Risk mitigation strategies identified  
✅ Extensible architecture for future enhancements

**Next Steps:**
1. **User reviews this plan** and answers open questions
2. **User provides approval** to proceed
3. **Agent begins Phase 1** (Foundation setup)
4. **Progress updates** at completion of each phase
5. **Final review** before v3.0.0 release

**Framework Evolution:**
```
v1.0.0 → Basic case study generation
v2.0.0 → Production-ready with screenshots
v2.2.0 → Fail-fast validation framework
v3.0.0 → Reference architecture generation (this plan)
v4.0.0 → Future enhancements (TBD)
```

This represents a significant capability addition that maintains the framework's core principles (LLM-first design, fail-fast validation, zero configuration) while extending its reach to serve the architectural needs of the CNCF community.

---

**Document Status:** ✅ Complete and Ready for User Approval  
**Next Action:** Await user decision on open questions and approval to proceed  
**Estimated Implementation:** 18 days from approval  
**Framework Version Target:** 3.0.0

