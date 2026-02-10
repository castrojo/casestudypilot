# CNCF Case Study Automation

This tool takes an existing talk from CNCF Events like KubeCon + CloudNativeCon and generates content:

TLDR: Ingests the youtube closed caption (which has timestamps!) and then generates a report based on community standards. It ingests the CNCF requirements for a case study and then uses all the existing case studies as examples. For bonus points it takes the image from the video when something interesting is mentioned in the video. Once we have the speaker's slides it should be even cooler.

### Case Studies

<!-- GENERATED_CONTENT_START:case-studies -->
- [Airbnb](case-studies/spark-on-kubernetes-a-practical-guide.md)
- [Niantic](case-studies/niantic.md)
- [Intuit](case-studies/supercharge-your-canary-deployments-with-argo-rollouts-step-plu-alexandre-gaudreault-zach-aller.md)
- [Intuit](case-studies/intuit.md)
<!-- GENERATED_CONTENT_END:case-studies -->

### Reference Architectures

<!-- GENERATED_CONTENT_START:reference-architectures -->
- [Airbnb](reference-architectures/airbnb.md)
- [CERN](reference-architectures/the-hard-life-of-securing-a-particle-accelerator-antonio-nappi-sebastian-lopienski-cern.md)
<!-- GENERATED_CONTENT_END:reference-architectures -->

---

## Architecture

**Agent-Centric Design:**
- GitHub Copilot custom agent orchestrates entire workflow
- Python CLI tools handle data operations
- Agent skills handle AI processing
- **Fail-fast validation** prevents hallucination at every step
- Quality validation ensures high-quality output

**No API Keys Required:**
- Uses `youtube-transcript-api` for direct transcript access
- No authentication needed for basic operation
- See `docs/API-KEY-DECISION.md` for rationale

---

## Integration

**Powerlevel:** This project uses [powerlevel](https://github.com/castrojo/powerlevel) for project management and epic tracking. Plans in `docs/plans/` are automatically converted to GitHub epics with trackable sub-tasks.

**Superpowers:** Development workflows leverage [superpowers](https://github.com/anomalyco/opencode) skills for planning (`writing-plans`), debugging (`systematic-debugging`), testing (`test-driven-development`), and verification (`verification-before-completion`).

**Configuration:**
- Powerlevel plugin: `.opencode/config.json`
- Superpowers location: `~/.config/opencode/skills/superpowers/`
- Project tracking: `~/.config/opencode/powerlevel/projects/casestudypilot/`

---

## Fail-Fast Validation Architecture

The agent includes comprehensive validation to prevent hallucination and ensure data quality:

### Validation Points

1. **Transcript Quality** (Step 2)
   - Ensures transcript exists and has sufficient content
   - Minimum: 1,000 characters, 50 segments, 100 words
   - Prevents the "empty transcript hallucination" bug

2. **Company Identification** (Step 3)
   - Validates company name is not generic placeholder
   - Requires confidence >= 0.7 for automated extraction
   - Detects: "Company", "Organization", "Unknown", etc.

3. **Analysis Output** (Step 6)
   - Verifies CNCF projects identified (minimum 1)
   - Checks all required sections present with sufficient content
   - Ensures minimum 100 characters per section

4. **Metric Fabrication Detection** (Step 8.5)
   - Cross-checks generated metrics against transcript
   - Uses fuzzy matching to allow for rephrasing
   - Flags metrics that don't appear in original content

5. **Company Consistency Check** (Step 8.5)
   - Prevents case studies about wrong company
   - Detects if generated content mentions different company
   - **Critical safeguard against "Spotify hallucination" bug**

### Severity Levels

- **CRITICAL**: Stops workflow immediately, posts error, closes issue
  - Empty transcript, wrong company, no CNCF projects
  
- **WARNING**: Continues with degraded quality, logs warning
  - Short transcript, only 1 project, possible fabricated metrics
  
- **INFO**: Informational only, no action needed
  - All validations passed, high quality data

### Manual Validation

Run validation commands manually for testing/debugging:

```bash
# Validate transcript quality
python -m casestudypilot validate-transcript video_data.json

# Validate company name
python -m casestudypilot validate-company "Intuit" "Video Title" --confidence 1.0

# Validate analysis output
python -m casestudypilot validate-analysis transcript_analysis.json

# Detect fabricated metrics
python -m casestudypilot validate-metrics case_study_sections.json video_data.json transcript_analysis.json

# Check company consistency
python -m casestudypilot validate-consistency case_study_sections.json video_data.json company_verification.json

# Run all validations
python -m casestudypilot validate-all video_data.json transcript_analysis.json case_study_sections.json company_verification.json
```

**Exit codes:**
- `0`: PASS (all checks passed)
- `1`: WARNING (has warnings, can continue)
- `2`: CRITICAL (fatal errors, must stop)

---

## 📐 Reference Architectures vs Case Studies

CaseStudyPilot generates two types of content from CNCF videos:

### Content Type Comparison

| Aspect | Case Study | Reference Architecture |
|--------|-----------|------------------------|
| **Length** | 500-1500 words | 2000-5000 words |
| **Sections** | 5 (Background, Challenge, Solution, Impact, Conclusion) | 13 (includes Architecture Overview, Diagrams, Integration Patterns, Security, Observability, etc.) |
| **CNCF Projects** | 2+ projects | 5+ projects (detailed usage) |
| **Technical Depth** | Score ≥0.60 | Score ≥0.70 |
| **Architecture Details** | Overview only | 3-layer architecture (Infrastructure, Platform, Application) |
| **Diagrams** | None | Textual diagram specifications (component + data flow) |
| **Audience** | Business leaders, executives | Engineers, architects, technical decision-makers |
| **Video Length** | 10-20 minutes | 15-40 minutes |
| **Output Directory** | `case-studies/` | `reference-architectures/` |
| **CNCF TAB Submission** | Not suitable | Designed for submission |
| **Agent** | `case-study-agent` | `reference-architecture-agent` |
| **Issue Label** | `case-study` | `reference-architecture` |

### When to Use Each Type

**Use Case Study when:**
- ✅ Video is 10-20 minutes long
- ✅ Single company story focused on business outcomes
- ✅ Mentions 2-3 CNCF projects
- ✅ Audience is business stakeholders
- ✅ Quick turnaround needed (simpler workflow)

**Use Reference Architecture when:**
- ✅ Video is 15-40 minutes with technical depth
- ✅ Discusses comprehensive architecture (5+ CNCF projects)
- ✅ Includes system diagrams or detailed demos
- ✅ Covers integration patterns and implementation details
- ✅ Audience is technical (engineers, architects)
- ✅ Intended for CNCF TAB submission

### Reference Architecture Features

**Enhanced Analysis:**
- Deep transcript analysis extracts 5+ CNCF projects with usage context
- 3-layer architecture breakdown (Infrastructure, Platform, Application)
- Integration patterns between components
- Technical metrics with transcript citations
- 6+ screenshot opportunities identified

**Comprehensive Content:**
- 13 sections covering all technical aspects:
  - Executive Summary
  - Background & Context
  - Technical Challenge
  - Architecture Overview (3 layers)
  - Architecture Diagrams (textual specifications)
  - CNCF Projects Deep Dive (5+ projects)
  - Integration Patterns
  - Implementation Details
  - Deployment Architecture
  - Security Considerations
  - Observability & Operations
  - Results & Impact
  - Lessons Learned & Best Practices
  - Conclusion

**Quality Standards:**
- **Technical Depth Score**: 5-dimensional scoring algorithm
  - CNCF Project Depth (25%): 5+ projects with detailed descriptions
  - Technical Specificity (20%): Concrete implementation details
  - Implementation Detail (20%): Version numbers, configurations
  - Metric Quality (20%): Quantifiable results with citations
  - Architecture Completeness (15%): All 3 layers documented
- **Threshold**: Must achieve ≥0.70 (vs 0.60 for case studies)
- **Word Count**: 2000-5000 words (vs 500-1500)

**Validation Checkpoints:**
1. Transcript quality (≥2000 characters for comprehensive content)
2. Deep analysis (5+ CNCF projects, 3 layers, 2+ integration patterns)
3. Metric fabrication detection (all metrics have transcript quotes)
4. Company consistency check
5. Final technical depth score (≥0.70)

### Requesting Generation

**Case Study:**
```markdown
Create GitHub issue with label: `case-study`
Include YouTube URL in issue body
```

**Reference Architecture:**
```markdown
Create GitHub issue with label: `reference-architecture`
Include YouTube URL in issue body

Optionally include:
- Expected CNCF projects
- Known architecture patterns
- Additional context
```

**Example Issue:**
```markdown
Title: Acme Corp Cloud-Native Platform

**YouTube URL**: https://www.youtube.com/watch?v=VIDEO_ID

**Expected CNCF Projects**: Kubernetes, Prometheus, Envoy, Helm, Flagger

**Architecture Context**: 
Multi-cluster Kubernetes platform with service mesh, 
distributed tracing, and progressive delivery.
```

### CLI Commands

**Case Study Validation:**
```bash
# Validate transcript (minimum 1000 chars)
python -m casestudypilot validate-transcript video_data.json

# Validate analysis (2+ projects)
python -m casestudypilot validate-analysis transcript_analysis.json

# Assemble case study
python -m casestudypilot assemble video.json analysis.json sections.json verification.json
```

**Reference Architecture Validation:**
```bash
# Validate deep analysis (5+ projects, 3 layers, integration patterns)
python -m casestudypilot validate-deep-analysis deep_analysis.json

# Validate technical depth score (≥0.70)
python -m casestudypilot validate-reference-architecture ref_arch.json

# Assemble reference architecture
python -m casestudypilot assemble-reference-architecture ref_arch.json screenshots/*.jpg --output output.md
```

**Presenter Profile Discovery:**
```bash
# Search CNCF YouTube channel for a presenter's videos
python -m casestudypilot search-presenter "Jeffrey Sica" \
  --github jeefy \
  --months 24 \
  --output presenter_videos.json

# Features:
# - Hybrid matching (strict + fuzzy) with confidence scoring
# - Searches past 24 months by default
# - GitHub username for cross-reference (optional)
# - Exit codes: 0 (2+ videos), 1 (1 video - warning), 2 (0 videos - critical)
```

### Output Examples

**Case Study Output:**
```
case-studies/
├── acme-corp.md                    # 800 words, 5 sections
└── images/
    └── acme-corp/
        ├── screenshot-1.jpg
        ├── screenshot-2.jpg
        └── screenshot-3.jpg
```

**Reference Architecture Output:**
```
reference-architectures/
├── acme-corp-cloud-native-platform.md    # 3500 words, 13 sections
└── images/
    └── acme-corp-cloud-native-platform/
        ├── screenshot-1.jpg          # Infrastructure overview
        ├── screenshot-2.jpg          # Platform services
        ├── screenshot-3.jpg          # Application layer
        ├── screenshot-4.jpg          # Service mesh diagram
        ├── screenshot-5.jpg          # Observability stack
        └── screenshot-6.jpg          # Deployment pipeline
```

### Migration Path

**Converting Case Study to Reference Architecture:**

If a case study was generated but the content warrants a reference architecture:

1. Re-label the issue: `case-study` → `reference-architecture`
2. Reference architecture agent will re-process with deeper analysis
3. Original case study remains in `case-studies/`
4. New reference architecture created in `reference-architectures/`

**Quality Indicators for Migration:**
- Case study technical depth score is high (0.65-0.69)
- Video contains 4+ CNCF projects
- Transcript has rich architectural details
- Community feedback requests more technical depth

### Documentation

- **User Guide**: `docs/REFERENCE-ARCHITECTURE-USER-GUIDE.md`
- **Comparison**: `docs/CASE-STUDY-VS-REFERENCE-ARCHITECTURE.md`
- **Agent Workflow**: `.github/agents/reference-architecture-agent.md`
- **Skills**: `.github/skills/transcript-deep-analysis/`, `architecture-diagram-specification/`, `reference-architecture-generation/`

---

## 🐋 Container Usage (Zero Host Dependencies)

**No Python installation required!** Run CaseStudyPilot entirely in containers using Podman or Docker.

### Prerequisites
- **Podman** (recommended) or **Docker**
- **Just** command runner: https://github.com/casey/just#installation

### Quick Start
```bash
# Build once
just build

# Generate case study
just case-study 'https://www.youtube.com/watch?v=VIDEO_ID'

# Develop with hot-reload
just dev
```

### Available Commands
- `just build` - Build the container image
- `just case-study <url>` - Generate case study from YouTube URL
- `just dev` - Open development shell with hot-reload
- `just publish` - Publish to GitHub Container Registry

See **[docs/CONTAINER-QUICK-START.md](docs/CONTAINER-QUICK-START.md)** for complete guide including:
- Individual CLI command usage in containers
- Publishing to GHCR
- Troubleshooting
- Full workflow examples

### Pull from Registry
```bash
podman pull ghcr.io/castrojo/casestudypilot:latest
```

### Benefits
- ✅ **Zero CVEs** - Using Chainguard Python (97.6% fewer vulnerabilities)
- ✅ **Minimal size** - ~50-70MB production image
- ✅ **No host dependencies** - Everything runs in container
- ✅ **Hot-reload dev mode** - Edit code, see changes instantly
- ✅ **Supply chain security** - Built-in SBOM and Sigstore signing

---

## Components (To Be Built)

### 1. Python CLI Tool: `casestudypilot`

Five commands for data operations:

```bash
# Fetch video transcript (no auth required!)
casestudypilot youtube-data <url>

# Verify company is CNCF end-user member
casestudypilot verify-company "Company Name"

# Extract and download screenshots from video
casestudypilot extract-screenshots video.json analysis.json sections.json \
  --download-dir case-studies/images/company/

# Assemble case study from components
casestudypilot assemble video.json analysis.json sections.json verification.json \
  --screenshots screenshots.json

# Validate quality
casestudypilot validate case-studies/company.md
```

### 2. GitHub Copilot Custom Agent

**Agent:** `@case-study-agent`  
**Location:** `.github/agents/case-study-agent.md`

Orchestrates 12-step workflow from issue to pull request.

### 3. Agent Skills (3)

1. **transcript-correction** - Fix common transcript errors
2. **transcript-analysis** - Extract structured data
3. **case-study-generation** - Generate polished markdown sections

**Location:** `.github/skills/*/SKILL.md`

### 4. Quality Validation

Multi-factor scoring across:
- Structure (30%): Required sections present
- Content Depth (40%): Word counts per section  
- CNCF Mentions (20%): Projects referenced
- Formatting (10%): Markdown quality

**Passing threshold:** 0.60

---

## Documentation

- **`AGENTS.md`**: Operational guide for LLM agents working with this framework
- **`CONTRIBUTING.md`**: How to extend with new skills, agents, and CLI tools
- **`.github/copilot-instructions.md`**: Copilot agent configuration
- **`docs/`**: Architecture decisions, API choices, and technical context

## 📚 Implementation Context

Major features are tracked via **epic issues** (label: `epic`) containing:
- Implementation plans and architecture
- Challenges and solutions
- Lessons learned
- Context for future development

**Find epics:**
```bash
# List all epics
gh issue list --label "epic" --state all

# Search by keyword
gh issue list --label "epic" --search "feature-name" --state all
```

**Before modifying code**, check related epics to understand design decisions and avoid past mistakes.

See [AGENTS.md](AGENTS.md#epic-issues-implementation-context-archive) for complete guide.

---

## Key Decisions

### ✅ Simplified: No API Key Required

**Decision:** Remove YouTube Data API requirement  
**Rationale:** User feedback - "seems overkill"  
**Impact:** Zero setup friction, works immediately  
**Trade-off:** Placeholder metadata (acceptable)

See `docs/API-KEY-DECISION.md` for full analysis.

### ✅ Agent-Centric Architecture

**Decision:** GitHub Copilot agent orchestrates everything  
**Rationale:** Leverages Copilot's strengths, minimal custom code  
**Impact:** Natural language workflow, easy to modify

### ✅ Approval-Required Implementation

**Decision:** No changes without explicit user approval  
**Rationale:** Prevent premature implementation  
**Impact:** User maintains control, no surprises

See `docs/CONSTRAINTS.md` for complete policy.

---

## Technology Stack

**Python Tools:**
- `youtube-transcript-api` - Transcript fetching (no auth!)
- `rapidfuzz` - Fuzzy company name matching
- `httpx` - HTTP client for CNCF API
- `jinja2` - Template rendering
- `typer` + `rich` - CLI framework with colors
- `pytest` - Testing

**GitHub Copilot:**
- Custom agents
- Agent skills
- GitHub Actions integration

**Total Dependencies:** 9 packages (all production-ready, permissive licenses)

---

## Implementation Status

### ✅ Completed
- Design reviewed and validated
- Architecture simplified (no API key)
- Complete planning documentation
- Implementation guide created
- Constraint policy documented

### 🔜 Next Steps
1. Implementing agent reads `docs/CONSTRAINTS.md`
2. Implementing agent reviews `docs/PLANNING.md`
3. Implementing agent requests approval to begin
4. Step-by-step implementation following `docs/IMPLEMENTATION-GUIDE.md`
5. Testing with real YouTube videos
6. First case study generated

---

## File Structure (Planned)

```
.
├── .github/
│   ├── agents/
│   │   └── case-study-agent.md          # Custom agent
│   ├── skills/
│   │   ├── transcript-correction/       # Skill 1
│   │   ├── transcript-analysis/         # Skill 2
│   │   └── case-study-generation/       # Skill 3
│   └── workflows/
│       └── copilot-setup-steps.yml      # Environment setup
│
├── casestudypilot/                      # Python package
│   ├── __main__.py                      # CLI entry point
│   └── tools/                           # 4 CLI tools
│       ├── youtube_client.py
│       ├── company_verifier.py
│       ├── assembler.py
│       └── validator.py
│
├── templates/
│   └── case_study.md.j2                 # Jinja2 template
│
├── case-studies/                        # Output directory
├── tests/                               # Test suite
│
├── docs/
│   ├── CONSTRAINTS.md                   # Approval policy ⚠️
│   ├── PLANNING.md                      # Specifications
│   ├── IMPLEMENTATION-GUIDE.md          # Step-by-step tasks
│   ├── API-KEY-DECISION.md              # Architecture decision
│   ├── GITHUB-ISSUE-WORKFLOW.md         # Issue workflow docs
│   └── plans/
│       └── 2026-02-09-design.md         # Original design
│
├── README.md                            # This file
└── requirements.txt                     # Dependencies
```

---

## Success Criteria

Implementation will be complete when:

- [ ] All 4 CLI commands work correctly
- [ ] Agent workflow executes end-to-end  
- [ ] Generated case studies pass validation (≥0.60)
- [ ] No API keys required for basic operation
- [ ] Complete documentation exists
- [ ] At least 1 successful case study generated
- [ ] Tests pass (≥80% coverage)

---

## References

- [GitHub Copilot Custom Agents](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-agents)
- [GitHub Copilot Skills](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [CNCF End User Community](https://www.cncf.io/enduser/)
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

---

## For Future Agents

**⚠️ CRITICAL: Read `docs/CONSTRAINTS.md` before doing ANYTHING**

This project has a strict approval policy. You MUST:
1. Read the constraints document
2. Understand the approval process
3. Request approval before creating files
4. Wait for explicit approval
5. Only do what was approved

**Do not implement without approval. Do not assume. Always ask.**

---

*This project is ready for implementation by a future agent following the documented process.*
