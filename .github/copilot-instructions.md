# Repository Instructions for GitHub Copilot

## Project Overview

This repository automates the creation of CNCF end-user case studies from YouTube video interviews using GitHub Copilot custom agents and Python CLI tools.

## Custom Agent

**Agent Name:** `@case-study-agent`
**Location:** `.github/agents/case-study-agent.md`

**Usage:**
```markdown
Create an issue with a YouTube URL and assign it to @case-study-agent:

Title: Generate case study for Intuit GitOps talk
Body: https://www.youtube.com/watch?v=V6L-xOUdoRQ

@case-study-agent please generate this case study
```

## Agent Skills

Three skills available for AI processing:

1. **transcript-correction** (`.github/skills/transcript-correction/SKILL.md`)
   - Fixes speech-to-text errors in YouTube captions
   - Corrects CNCF project capitalization
   - Fixes common technical term errors

2. **transcript-analysis** (`.github/skills/transcript-analysis/SKILL.md`)
   - Extracts structured data from transcripts
   - Identifies CNCF projects and usage
   - Extracts quantitative metrics
   - Classifies content into sections

3. **case-study-generation** (`.github/skills/case-study-generation/SKILL.md`)
   - Generates publication-ready markdown
   - Follows CNCF case study style guidelines
   - Creates Overview, Challenge, Solution, Impact, Conclusion sections

## Python CLI Tools

The `casestudypilot` package provides four commands:

### 1. Fetch YouTube Data
```bash
python -m casestudypilot youtube-data "<youtube-url>"
```
- Extracts video ID from URL
- Fetches transcript (no API key required!)
- Outputs: `video_data.json`

### 2. Verify Company
```bash
python -m casestudypilot verify-company "Company Name"
```
- Checks if company is CNCF end-user member
- Uses fuzzy matching for name variations
- Outputs: `company_verification.json`
- **Exits with error if not a member**

### 3. Assemble Case Study
```bash
python -m casestudypilot assemble video_data.json analysis.json sections.json verification.json
```
- Merges all component JSON files
- Renders Jinja2 template
- Outputs: `case-studies/<company>.md`

### 4. Validate Quality
```bash
python -m casestudypilot validate case-studies/<company>.md
```
- Checks structure, content depth, CNCF mentions, formatting
- Calculates quality score (0.0-1.0)
- **Exits with error if score < 0.60**
- Outputs: `validation_results.json`

## Environment Setup

Python environment is configured via GitHub Actions:
- Workflow: `.github/workflows/copilot-setup-steps.yml`
- Python 3.11
- Dependencies: `requirements.txt`

**No API keys required!** Uses `youtube-transcript-api` which accesses transcripts directly.

## Repository Structure

```
.
├── .github/
│   ├── agents/case-study-agent.md          # Custom agent
│   ├── skills/                             # 3 AI processing skills
│   └── workflows/copilot-setup-steps.yml   # Environment setup
├── casestudypilot/                         # Python package
│   ├── __main__.py                         # CLI entry point
│   └── tools/                              # 4 CLI tools
├── templates/case_study.md.j2             # Jinja2 template
├── case-studies/                           # Output directory
└── requirements.txt                        # Python dependencies
```

## Critical Workflow Rules

When the agent processes a case study request:

1. **Always verify company first** - Stop if not CNCF member
2. **Apply skills in order** - correction → analysis → generation
3. **Validate before PR** - Stop if quality score < 0.60
4. **Include quality score in PR** - Transparency for reviewers
5. **Fail fast** - Don't waste processing on invalid inputs

## Quality Thresholds

- **Company verification confidence:** ≥ 0.70
- **Case study quality score:** ≥ 0.60 (target: 0.70+)
- **Minimum CNCF projects:** 2
- **Minimum metrics:** 1
- **Word count range:** 500-1500

## Test Video

Use this video for testing:
- **URL:** https://www.youtube.com/watch?v=V6L-xOUdoRQ
- **Company:** Intuit (verified CNCF member)
- **Projects:** Kubernetes, Argo CD, Helm
- **Expected Quality:** ≥ 0.75

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Test CLI
python -m casestudypilot --help

# Run full workflow manually
python -m casestudypilot youtube-data "https://www.youtube.com/watch?v=VIDEO_ID"
python -m casestudypilot verify-company "Company Name"
# (Apply skills manually via Copilot)
python -m casestudypilot assemble video_data.json analysis.json sections.json verification.json
python -m casestudypilot validate case-studies/company.md

# Run tests
pytest tests/ -v
```

## Implementation Notes

- **Zero setup friction** - No API keys required for basic operation
- **Agent-centric design** - GitHub Copilot orchestrates everything
- **Fail-fast validation** - Early errors prevent wasted processing
- **Quality first** - Don't create PRs for low-quality output
- **Incremental processing** - JSON files for intermediate data

## Documentation

- `docs/PLANNING.md` - Complete specifications
- `docs/IMPLEMENTATION-GUIDE.md` - Step-by-step implementation tasks
- `docs/API-KEY-DECISION.md` - Architecture rationale
- `docs/plans/2026-02-09-design.md` - Original design document
- `docs/CONSTRAINTS.md` - Development constraints and approval policy
