# Skill-Driven Agent Development Guide

## Overview

This document provides operational guidance for **LLM agents** working with this skill-driven automation framework. The framework implements a three-layer architecture where agents orchestrate workflows by combining CLI tools (Python) with LLM skills.

**Primary Audience:** AI agents (GitHub Copilot, Claude, GPT-4, etc.)

## Foundation: Superpowers Skills

**IMPORTANT:** This framework builds on top of **superpowers**, a universal skill system for LLM-driven development. Before working with casestudypilot, familiarize yourself with these foundational skills:

### Universal Development Skills (Superpowers)

Located at: `~/.config/opencode/skills/superpowers/`

**Planning & Design:**
- `brainstorming`: Design exploration before implementation (REQUIRED for new features)
- `writing-plans`: Structured planning for multi-step tasks
- `executing-plans`: Plan execution with review checkpoints

**Development Discipline:**
- `test-driven-development`: Write tests before implementation
- `systematic-debugging`: Root cause analysis for failures
- `verification-before-completion`: Run checks before claiming work complete

**Workflow Management:**
- `using-git-worktrees`: Isolated development environments
- `finishing-a-development-branch`: Merge decision workflows
- `requesting-code-review`: Review request automation
- `receiving-code-review`: Review feedback processing

**Orchestration:**
- `dispatching-parallel-agents`: Independent task parallelism
- `subagent-driven-development`: Task delegation patterns

**Meta Skills:**
- `writing-skills`: Skill creation and editing
- `using-superpowers`: How to access and invoke skills

### When to Use Superpowers vs. CaseStudyPilot Skills

| Situation | Use Superpowers | Use CaseStudyPilot Skills |
|-----------|-----------------|---------------------------|
| Planning new feature | ✅ `writing-plans` | After plan: domain agents |
| Debugging validation failure | ✅ `systematic-debugging` | Understand validation logic |
| Implementing new agent | ✅ `brainstorming`, `test-driven-development` | Reference existing agents |
| Creating new skill | ✅ `writing-skills` | Follow `.github/skills/` patterns |
| Generating case study | Domain workflow | ✅ `case-study-agent` |
| Generating reference architecture | Domain workflow | ✅ `reference-architecture-agent` |
| Analyzing transcript | Domain task | ✅ `transcript-analysis` or `transcript-deep-analysis` skill |

**Integration Point:** CaseStudyPilot agents and skills follow superpowers patterns but are specialized for CNCF content generation.

## Framework Mental Model

### Three-Layer Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ LAYER 1: AGENTS (You are here)                              │
│ - Orchestrate workflows                                      │
│ - Make decisions based on exit codes                         │
│ - Invoke skills and CLI tools                                │
│ - Handle errors and communicate with users                   │
└──────────────────────────────────────────────────────────────┘
                            │
                            ├─────────────────┐
                            ↓                 ↓
┌────────────────────────────────┐  ┌───────────────────────────┐
│ LAYER 2: SKILLS                │  │ LAYER 3: CLI TOOLS        │
│ - LLM-powered tasks            │  │ - Python validation       │
│ - Content generation           │  │ - Data fetching           │
│ - Analysis and extraction      │  │ - File assembly           │
│ - Structured input/output      │  │ - Quality scoring         │
└────────────────────────────────┘  └───────────────────────────┘
```

### Your Role as an Agent

You are the **orchestrator**. Your job is to:

1. **Read agent workflow files** (`.github/agents/*.md`) to understand the complete workflow
2. **Invoke CLI tools** for validation and data operations (check exit codes!)
3. **Invoke LLM skills** for content generation and analysis (prepare structured inputs)
4. **Make decisions** based on validation results (continue, warn, or stop)
5. **Communicate** with users (post errors, create PRs, thank contributors)

## Core Operating Principles

### 1. Always Check Exit Codes

Every CLI validation command returns an exit code:

| Code | Meaning | Action |
|------|---------|--------|
| 0 | PASS | Continue to next step |
| 1 | WARNING | Log warning, continue workflow |
| 2 | CRITICAL | Post error to issue, stop immediately |

**Pattern:**
```bash
python -m casestudypilot validate-transcript video_data.json
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  # CRITICAL failure - post error template and STOP
  echo "❌ Validation Failed: Transcript Quality"
  exit 2
elif [ $EXIT_CODE -eq 1 ]; then
  # WARNING - log and continue
  echo "⚠️ Warning: Transcript quality below optimal"
fi
# Exit code 0: continue silently
```

**Never proceed after exit code 2.** This is the framework's primary hallucination prevention mechanism.

### 2. Skills Have Structured Inputs/Outputs

When invoking an LLM skill:

1. **Read the skill file** (`.github/skills/<skill-name>/SKILL.md`)
2. **Prepare the input** in the exact JSON/text format specified
3. **Execute the skill instructions** step-by-step
4. **Produce the output** in the exact JSON/text format specified
5. **Validate the output** (if validation command exists)

**Example: transcript-analysis skill**

Input format (from skill file):
```json
{
  "transcript": "text from video_data.json",
  "video_title": "from video_data.json",
  "duration": 1234
}
```

Output format (from skill file):
```json
{
  "cncf_projects": [
    {"name": "Kubernetes", "usage_context": "container orchestration"}
  ],
  "key_metrics": [...],
  "sections": {
    "background": "...",
    "challenge": "...",
    "solution": "...",
    "impact": "..."
  }
}
```

Then validate:
```bash
python -m casestudypilot validate-analysis transcript_analysis.json
# Check exit code!
```

### 3. Fail-Fast Validation Architecture

The framework includes **validation checkpoints** at critical decision points. The case study agent has 5 checkpoints:

| Step | Checkpoint | CLI Command | Stop on Code 2? |
|------|-----------|-------------|-----------------|
| 2 | Transcript Quality | `validate-transcript` | YES |
| 3 | Company Identification | `validate-company` | YES |
| 6 | Analysis Output | `validate-analysis` | YES |
| 8.5a | Metric Fabrication | `validate-metrics` | NO (warn only) |
| 8.5b | Company Consistency | `validate-consistency` | YES |
| 10 | Final Quality | `validate` | YES (score < 0.60) |

**Why fail-fast?**
- Prevents wasting compute on bad inputs
- Catches hallucination early (empty transcript, wrong company)
- Saves you from generating invalid content

### 4. CLI for Data, Skills for Content

**Use CLI tools when:**
- ✅ Fetching data (YouTube transcripts, CNCF API)
- ✅ Validating data (transcript quality, company names)
- ✅ Assembling files (Jinja2 templates)
- ✅ Scoring quality (multi-factor metrics)
- ✅ Any deterministic operation

**Use LLM skills when:**
- ✅ Analyzing content (extracting CNCF projects)
- ✅ Generating text (writing case study sections)
- ✅ Correcting errors (fixing transcript mistakes)
- ✅ Any creative/interpretive task

**Why this separation?**
- CLI tools are testable and deterministic
- LLM skills leverage your strengths (understanding, generation)
- Validation in Python prevents hallucination

### 5. GitHub Communication: Use MCP or gh CLI

**CRITICAL:** Always use GitHub MCP tools or `gh` CLI for GitHub operations. Never use `curl`, web scraping, or manual API calls.

**Available GitHub Integration Methods:**

1. **GitHub MCP (Model Context Protocol)** - Preferred when available
2. **gh CLI** - Universal fallback for all GitHub operations

**Why this matters:**
- ✅ Efficient: Direct API access with authentication
- ✅ Reliable: Official GitHub tooling with error handling
- ✅ Maintainable: Consistent interface across workflows
- ✅ Secure: Built-in authentication and token management
- ❌ Never use `curl` or HTTP requests manually
- ❌ Never scrape GitHub web pages for data

#### GitHub MCP Tools (Preferred)

If GitHub MCP is available in your environment, use these tools:

| Operation | MCP Tool | Example |
|-----------|----------|---------|
| Create Issue | `create_issue` | `create_issue(owner, repo, title, body)` |
| Update Issue | `update_issue` | `update_issue(owner, repo, issue_number, state, body)` |
| Add Comment | `create_issue_comment` | `create_issue_comment(owner, repo, issue_number, body)` |
| Create PR | `create_pull_request` | `create_pull_request(owner, repo, title, body, head, base)` |
| Get Issue | `get_issue` | `get_issue(owner, repo, issue_number)` |
| List PRs | `list_pull_requests` | `list_pull_requests(owner, repo, state)` |
| Search | `search_code` | `search_code(query, repo)` |

**Example: Post validation error to issue**
```python
# Use GitHub MCP to post error
create_issue_comment(
    owner="cncf",
    repo="casestudypilot",
    issue_number=42,
    body="""❌ **Validation Failed: Transcript Quality**

The transcript is too short or empty.

**Action Required:** Please verify the YouTube video has captions enabled."""
)
```

#### gh CLI (Universal Fallback)

When GitHub MCP is not available, use `gh` CLI for all GitHub operations:

| Operation | gh Command | Example |
|-----------|------------|---------|
| Create Issue | `gh issue create` | `gh issue create --title "..." --body "..."` |
| Update Issue | `gh issue edit` | `gh issue edit 42 --add-label "validated"` |
| Add Comment | `gh issue comment` | `gh issue comment 42 --body "..."` |
| Create PR | `gh pr create` | `gh pr create --title "..." --body "..." --base main` |
| Get Issue | `gh issue view` | `gh issue view 42 --json title,body,labels` |
| List PRs | `gh pr list` | `gh pr list --state open --json number,title` |
| Search | `gh api` | `gh api repos/:owner/:repo/search/code -q "..."` |

**Example: Post validation error using gh CLI**
```bash
# Use gh CLI to post error
gh issue comment 42 --body "❌ **Validation Failed: Transcript Quality**

The transcript is too short or empty.

**Action Required:** Please verify the YouTube video has captions enabled."
```

#### GitHub Communication Patterns

**Pattern 1: Post error to issue (validation failure)**
```bash
# When validation returns exit code 2
if [ $EXIT_CODE -eq 2 ]; then
  # Use gh CLI to post error template
  gh issue comment "$ISSUE_NUMBER" --body "$(cat error_template.md)"
  exit 2
fi
```

**Pattern 2: Create PR with results**
```bash
# After successful workflow completion
gh pr create \
  --title "Add case study for $COMPANY" \
  --body "$(cat pr_description.md)" \
  --base main \
  --head "$BRANCH_NAME"
```

**Pattern 3: Fetch issue data for workflow input**
```bash
# Extract video URL from issue body
ISSUE_DATA=$(gh issue view "$ISSUE_NUMBER" --json body --jq '.body')
VIDEO_URL=$(echo "$ISSUE_DATA" | grep -oP 'https://www\.youtube\.com/watch\?v=[^[:space:]]+' | head -1)
```

**Pattern 4: Update issue labels based on workflow state**
```bash
# Add label when workflow starts
gh issue edit "$ISSUE_NUMBER" --add-label "in-progress"

# Update label when validation passes
gh issue edit "$ISSUE_NUMBER" --remove-label "in-progress" --add-label "validated"

# Add label when PR is created
gh issue edit "$ISSUE_NUMBER" --add-label "pr-created"
```

**Pattern 5: Link PR to issue**
```bash
# Reference issue in PR body
gh pr create \
  --title "Add case study for $COMPANY" \
  --body "Closes #$ISSUE_NUMBER

## Summary
- Generated case study from video analysis
- Extracted 3 screenshots
- Validated all quality checkpoints" \
  --base main
```

#### Common Pitfalls (DON'T DO THIS)

**❌ Using curl for GitHub API**
```bash
# BAD - manual API calls
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo/issues/42/comments \
  -d '{"body": "..."}'
```

**FIX:** Use `gh issue comment 42 --body "..."`

**❌ Scraping GitHub web pages**
```bash
# BAD - parsing HTML
wget https://github.com/owner/repo/issues/42
grep '<title>' index.html
```

**FIX:** Use `gh issue view 42 --json title`

**❌ Manual token management**
```bash
# BAD - hardcoded tokens
GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```

**FIX:** Use `gh auth login` or GitHub MCP authentication

**❌ Ignoring gh CLI JSON output**
```bash
# BAD - parsing human-readable output
gh issue view 42 | grep "title:"
```

**FIX:** Use `gh issue view 42 --json title --jq '.title'`

#### Environment Setup

**Check if GitHub MCP is available:**
```python
# In Python CLI tools
try:
    import github_mcp
    USE_MCP = True
except ImportError:
    USE_MCP = False
```

**Check if gh CLI is available:**
```bash
if ! command -v gh &> /dev/null; then
  echo "❌ Error: gh CLI not found"
  exit 2
fi

# Verify authentication
if ! gh auth status &> /dev/null; then
  echo "❌ Error: gh CLI not authenticated"
  exit 2
fi
```

**Agent workflow requirement:**
All agent workflows that interact with GitHub must include authentication checks in their pre-flight steps.

## Operational Workflows

### Current Implementation: Case Study Generation

**Agent:** `case-study-agent` (v2.2.0)  
**Workflow:** 14 steps with 5 validation checkpoints  
**Location:** `.github/agents/case-study-agent.md`

**Summary:**
1. Pre-flight checks (environment ready?)
2. Fetch video data → Validate transcript quality
3. Extract company name → Validate company
4. Verify CNCF membership
5. **Skill:** Correct transcript (transcript-correction)
6. **Skill:** Analyze transcript (transcript-analysis) → Validate analysis
7. Extract 3 screenshots
8. **Skill:** Generate case study (case-study-generation)
9. Validate metrics (fabrication check) + company consistency
10. Assemble markdown with screenshots
11. Validate final quality
12. Create branch
13. Commit (atomic: 1 markdown + 3 images)
14. Create PR and post to issue

**This is your template for creating new agent workflows.**

### Current Implementation: Reference Architecture Generation

**Agent:** `reference-architecture-agent` (v1.0.0)  
**Workflow:** 18 steps with 7 validation checkpoints (5 critical)  
**Location:** `.github/agents/reference-architecture-agent.md`

**Purpose:** Generate comprehensive CNCF reference architectures (2000-5000 words, 13 sections, 5+ CNCF projects) suitable for Technical Advisory Board (TAB) submission. Designed for technical audiences (engineers, architects).

**Summary:**
1. Pre-flight checks (environment ready?)
2. Fetch video data → Validate transcript quality (≥2000 chars)
3. Extract company name → Validate company
4. Verify CNCF membership
5. **Skill:** Correct transcript (transcript-correction)
6. **Skill:** Deep analysis (transcript-deep-analysis) → Validate deep analysis (5+ projects, 3 layers, 2+ patterns) **[CRITICAL]**
7. Extract 6+ screenshots
8. **Skill:** Architecture diagram specification (architecture-diagram-specification)
9. **Skill:** Generate reference architecture (reference-architecture-generation)
10. Validate metrics (fabrication check with transcript quotes) **[CRITICAL]**
11. Validate company consistency **[CRITICAL]**
12. Assemble markdown with screenshots
13. Validate technical depth score (≥0.70) **[CRITICAL]**
14. Generate TAB submission guidance
15. Create branch
16. Commit (atomic: 1 markdown + 6+ images)
17. Create PR with TAB submission instructions
18. Post to issue and notify

**Key Differences from Case Study Agent:**

| Aspect | Case Study Agent | Reference Architecture Agent |
|--------|------------------|------------------------------|
| Content Depth | 500-1500 words, 5 sections | 2000-5000 words, 13 sections |
| CNCF Projects | 2+ projects | 5+ projects with detailed usage |
| Architecture | Overview only | 3-layer breakdown + integration patterns |
| Diagrams | None | Textual component + data flow specs |
| Screenshots | 3 screenshots | 6+ screenshots (architecture-focused) |
| Screenshot Placement | Grouped together (usually at end) | **Distributed contextually** across document |
| Screenshots Per Section | ~1 section with all images | **3-4 major sections** with topical images |
| Technical Depth | Score ≥0.60 | Score ≥0.70 (5-dimensional scoring) |
| Skills Used | 3 skills | 3 specialized skills (deep-analysis, diagram-spec, generation) |
| Validation Checkpoints | 5 checkpoints | 7 checkpoints (5 critical fail-fast) |
| Target Audience | Business leaders | Engineers, architects |
| CNCF TAB Submission | Not designed for | Explicitly designed for submission |
| Transcript Minimum | ≥1000 chars | ≥2000 chars (more content needed) |

**Technical Depth Scoring Algorithm:**

The reference architecture agent uses a **5-dimensional scoring system** with weighted components:

```python
technical_depth_score = (
    0.25 * cncf_project_depth +      # 5+ projects, detailed descriptions
    0.20 * technical_specificity +    # Concrete implementation details
    0.20 * implementation_detail +    # Version numbers, configurations
    0.20 * metric_quality +           # Quantifiable results with citations
    0.15 * architecture_completeness  # All 3 layers documented
)
```

**Threshold:** ≥0.70 (PASS), 0.60-0.69 (WARNING), <0.60 (CRITICAL)

**When to Use:**
- ✅ Video is 15-40 minutes with technical depth
- ✅ Discusses comprehensive architecture (5+ CNCF projects)
- ✅ Includes system diagrams or detailed demos
- ✅ Covers integration patterns and implementation details
- ✅ Target audience is engineers/architects
- ✅ Content intended for CNCF TAB submission

**Critical Validation Checkpoints:**

1. **Deep Analysis (Step 6):** Exit code 2 if <5 CNCF projects, missing architecture layers, or <2 integration patterns
2. **Metric Fabrication (Step 10):** Exit code 2 if metrics lack transcript quotes
3. **Company Consistency (Step 11):** Exit code 2 if content mentions wrong company
4. **Technical Depth Score (Step 13):** Exit code 2 if score <0.60, exit code 1 if 0.60-0.69
5. **Transcript Quality (Step 2):** Exit code 2 if <2000 characters

**Screenshot Placement Requirements:**

Reference architectures require **6+ screenshots distributed contextually** across 3-4 major sections (approximately double the screenshots compared to case studies which use 3 screenshots grouped together).

**Key Principle:** Screenshots must be **topical to the paragraph content** where they appear. Each screenshot should reinforce the main technical point being discussed in that section.

**Distribution Pattern:**

| Section | Screenshot Topics | Example (CERN Architecture) |
|---------|-------------------|------------------------------|
| Background | Legacy architecture, current pain points | VM-based legacy architecture diagram |
| Architecture Overview | New architecture design, key components | Kubernetes multi-cluster architecture |
| Architecture Diagrams | Component diagrams, data flows | Component diagram, data flow diagram |
| Integration Patterns | Specific patterns (cache separation, GitOps) | Cache separation diagram, GitOps workflow |
| Implementation Details | Testing results, deployment steps | Load testing performance comparison |
| Observability/Results | Production metrics, usage statistics | Usage dashboard showing scale |

**Anti-Pattern (DO NOT DO THIS):**
```markdown
## Architecture Overview
[Content about architecture...]

![Screenshot 1](...)
![Screenshot 2](...)
![Screenshot 3](...)
![Screenshot 4](...)
![Screenshot 5](...)
![Screenshot 6](...)  ← All screenshots dumped in one place

## Next Section
[Content continues...]
```

**Correct Pattern (DO THIS):**
```markdown
## Background
[Content about legacy architecture...]

![Legacy VM-based architecture](...)  ← Screenshot 1 placed contextually

[More content...]

## Architecture Overview
[Content about new Kubernetes architecture...]

![New Kubernetes architecture](...)  ← Screenshot 2 placed contextually

[More content...]

## Integration Patterns
[Content about cache separation pattern...]

![Cache separation diagram](...)  ← Screenshot 3 placed contextually

[Content about GitOps pattern...]

![GitOps workflow](...)  ← Screenshot 4 placed contextually

## Implementation Details
[Content about load testing...]

![Load testing results](...)  ← Screenshot 5 placed contextually

## Results
[Content about production metrics...]

![Usage statistics dashboard](...)  ← Screenshot 6 placed contextually
```

**Guidelines for Screenshot Placement:**

1. **Place screenshot immediately after** the paragraph that describes what it shows
2. **Use descriptive alt text** that explains what the screenshot depicts (not generic "Figure 1")
3. **Add caption** with context (e.g., "*Load testing results presented at 19:00 demonstrating 4x improvement*")
4. **Spread across document** - aim for 1-2 screenshots per major section
5. **Match content to image** - if discussing cache architecture, place cache diagram there

**Assembly Script Responsibility:**

The assembly script (`assemble_reference_architecture.py`) should be updated to:
- Accept screenshot placement hints from the generation skill JSON
- Place screenshots in specified sections based on topical relevance
- Default to contextual distribution if no hints provided
- NEVER dump all screenshots in one location

**Output Structure:**

```markdown
---
title: "Reference Architecture: Company Cloud-Native Platform"
subtitle: "Multi-cluster Kubernetes with Service Mesh and Progressive Delivery"
company: "Company Name"
industry: "Technology"
video_url: "https://youtube.com/..."
publication_date: "2026-02-XX"
tab_status: "ready_for_submission"
primary_patterns:
  - "Multi-cluster orchestration"
  - "Service mesh architecture"
  - "Progressive delivery"
---

## Executive Summary
[100-200 words]

## Background & Context
[300-500 words]

## Technical Challenge
[300-500 words]

## Architecture Overview
[400-600 words - 3 layers breakdown]

## Architecture Diagrams
[200-400 words - textual specifications]

## CNCF Projects Deep Dive
[600-1000 words - 5+ projects]

## Integration Patterns
[300-500 words]

## Implementation Details
[400-600 words]

## Deployment Architecture
[200-400 words]

## Security Considerations
[200-400 words]

## Observability & Operations
[300-500 words]

## Results & Impact
[200-400 words]

## Lessons Learned & Best Practices
[200-400 words]

## Conclusion
[100-200 words]
```

**Skills Used:**

1. **transcript-deep-analysis** (38KB)
   - Extracts 5+ CNCF projects with usage context
   - Identifies 3-layer architecture (Infrastructure, Platform, Application)
   - Finds integration patterns between components
   - Extracts technical metrics with transcript quotes
   - Identifies 6+ screenshot opportunities

2. **architecture-diagram-specification** (37KB)
   - Generates textual diagram descriptions (NOT code)
   - Component diagrams (services, data stores, boundaries)
   - Data flow diagrams (request paths, data pipelines)
   - No Mermaid/PlantUML to avoid hallucination

3. **reference-architecture-generation** (~1000 lines)
   - 18-step execution process
   - Generates all 13 sections
   - Ensures technical depth and completeness
   - Maintains company consistency throughout
   - Cites transcript for all metrics

**CLI Tools:**

```bash
# Validate deep analysis output
python -m casestudypilot validate-deep-analysis deep_analysis.json
# Exit 0: 5+ projects, 3 layers, 2+ patterns ✅
# Exit 1: 4 projects or 1 pattern ⚠️
# Exit 2: <4 projects or missing layers ❌

# Validate technical depth score
python -m casestudypilot validate-reference-architecture ref_arch.json
# Exit 0: score ≥0.70 ✅
# Exit 1: score 0.60-0.69 ⚠️
# Exit 2: score <0.60 ❌

# Assemble reference architecture
python -m casestudypilot assemble-reference-architecture \
  ref_arch.json screenshots/*.jpg --output output.md
```

**Error Templates:**

All error templates are embedded in the agent workflow file. Critical checkpoints include detailed error messages with:
- What went wrong
- Critical issues list
- Possible causes
- Action required from user

**CNCF TAB Submission:**

The agent generates a TAB submission guide in the PR description:

```markdown
## 📋 CNCF TAB Submission Guide

This reference architecture is ready for submission to the CNCF Technical Advisory Board.

### Submission Checklist
- ✅ Technical depth score: X.XX (≥0.70 required)
- ✅ CNCF projects: N projects documented
- ✅ Architecture: 3 layers complete
- ✅ Word count: XXXX words (2000-5000 range)
- ✅ Metrics cited: All metrics have transcript quotes
- ✅ Company verified: CNCF end-user member

### Next Steps
1. Review the generated content in `reference-architectures/company.md`
2. Verify technical accuracy
3. Optionally add diagrams (Mermaid/PlantUML)
4. Create issue in cncf/toc repository
5. Link to this reference architecture
```

**Version History:**
- **v1.0.0** (February 2026) - Initial release with 18-step workflow

## Common Patterns and Best Practices

### Pattern 1: Fetch-Validate-Process

Most workflows follow this pattern:

```
1. Fetch data (CLI tool)
2. Validate data (CLI tool with exit code)
3. If valid, process data (skill or CLI)
4. Validate output (CLI tool with exit code)
5. If valid, continue
```

**Example:**
```bash
# 1. Fetch
python -m casestudypilot youtube-data "$URL"

# 2. Validate
python -m casestudypilot validate-transcript video_data.json
if [ $? -eq 2 ]; then exit 2; fi

# 3. Process (skill invocation)
# [Apply transcript-analysis skill]

# 4. Validate
python -m casestudypilot validate-analysis transcript_analysis.json
if [ $? -eq 2 ]; then exit 2; fi

# 5. Continue...
```

### Pattern 2: Structured JSON for Skills

All skill inputs and outputs use JSON:

```json
{
  "input_field_1": "value",
  "input_field_2": ["list", "of", "items"],
  "input_field_3": {"nested": "object"}
}
```

**Why JSON?**
- Unambiguous format
- Easy to validate
- Self-documenting
- No parsing errors

### Pattern 3: Error Templates for Users

When validation fails (exit code 2), post a helpful error to the GitHub issue:

```markdown
❌ **Validation Failed: [Checkpoint Name]**

[What went wrong]

**Critical Issues:**
- [Issue 1]
- [Issue 2]

**Possible Causes:**
- [Cause 1]
- [Cause 2]

**Action Required:**
[What user should do]
```

Templates are in agent workflow files. Use them verbatim.

### Pattern 4: Atomic Commits

When committing files, always commit all related files in a single atomic commit:

```bash
# Case study workflow: 1 markdown + 3 images
git add case-studies/company.md
git add case-studies/images/company/*.jpg
git commit -m "Add case study for Company with screenshots"
```

**Why atomic?**
- Ensures markdown and images are always in sync
- Easy to revert if needed
- Clean git history

## Common Pitfalls (DON'T DO THIS)

### ❌ Ignoring Exit Codes

```bash
# BAD - no exit code check
python -m casestudypilot validate-transcript video.json
python -m casestudypilot validate-company "Company" "Title"
# Continue regardless of validation results
```

**Result:** Hallucination, bad data propagates through workflow

**FIX:** Always check exit codes and stop on code 2

### ❌ Skipping Validation Checkpoints

```bash
# BAD - skip validation for speed
python -m casestudypilot youtube-data "$URL"
# [Apply skills immediately without validation]
```

**Result:** Generate content from empty/bad transcript

**FIX:** Validate at every checkpoint

### ❌ Using Placeholder Data

```json
{
  "title": "Video VIDEO_ID",
  "company": "Company",
  "projects": ["CNCF Project"]
}
```

**Result:** Generic, useless output

**FIX:** Always use real data from CLI tools (youtube-data uses yt-dlp for real metadata)

### ❌ Fabricating Metrics

```markdown
The company achieved **300% improvement** in performance.
```

**Result:** False claims not supported by transcript

**FIX:** Only use metrics from transcript, validate with `validate-metrics`

### ❌ Wrong Company Hallucination (Spotify Bug)

```json
{
  "company_verification": {"matched_name": "Intuit"},
  "case_study_content": "Spotify uses Kubernetes..." // WRONG COMPANY!
}
```

**Result:** Case study about wrong company

**FIX:** Use `validate-consistency` to catch this (exit code 2 stops workflow)

### ❌ Separate Commits for Related Files

```bash
# BAD - separate commits
git add case-studies/company.md
git commit -m "Add case study"

git add case-studies/images/company/*.jpg
git commit -m "Add screenshots"
```

**Result:** Broken state between commits (markdown references non-existent images)

**FIX:** Single atomic commit for all related files

## Adding New Skills and Agents

### Creating a New LLM Skill

**When to create a skill:**
- Task requires natural language understanding
- Task is creative/generative (not deterministic)
- Task can be reused across multiple agents
- Task has clear input/output boundaries

**Steps:**
1. Create `.github/skills/<skill-name>/SKILL.md`
2. Define the skill purpose (1-2 sentences)
3. Specify input format (JSON structure with types)
4. Specify output format (JSON structure with types)
5. Write execution instructions (step-by-step for LLMs)
6. Add 2-3 examples (input → output)
7. Reference skill from agent workflow

**Template:**
```markdown
# Skill: skill-name

## Purpose
[What this skill does in 1-2 sentences]

## Input Format
```json
{
  "field1": "type and description",
  "field2": ["type and description"]
}
```

## Output Format
```json
{
  "result_field1": "type and description",
  "result_field2": ["type and description"]
}
```

## Execution Instructions

1. [Step 1: What to do]
2. [Step 2: What to do]
3. [Step 3: What to do]

## Examples

### Example 1: [Description]

**Input:**
```json
{...}
```

**Output:**
```json
{...}
```

## Quality Guidelines

- [Guideline 1]
- [Guideline 2]
```

### Creating a New Agent Workflow

**When to create an agent:**
- You have a complete end-to-end workflow
- Workflow combines multiple CLI tools and skills
- Workflow needs orchestration logic (decision trees)
- Workflow is triggered by user action (GitHub issue, PR, etc.)

**Steps:**
1. Create `.github/agents/<agent-name>.md`
2. Define agent metadata (name, version, description)
3. List workflow steps (numbered, imperative)
4. Specify CLI tool invocations
5. Specify skill invocations
6. Add validation checkpoints (with exit code handling)
7. Create error templates
8. Document environment requirements

**Template:**
```markdown
---
name: agent-name
description: [What this agent does]
version: 1.0.0
---

# Agent Name

## Mission
[What this agent automates]

## Workflow (N Steps)

### Step 1: [Action]
[Description]

```bash
# CLI command if applicable
```

**Validation (if applicable):**
```bash
python -m casestudypilot validate-something data.json
```

**Check exit code:**
- Exit 0: Continue
- Exit 1: Log warning, continue
- Exit 2: Post error, STOP

**Error Template:**
```markdown
❌ **Error: [Description]**
[Details]
```

### Step 2: Apply [Skill Name] Skill
- Use skill: `skill-name`
- Input: [Prepare from previous step]
- Output: [Save to file]

[Repeat for all steps]

## Error Handling
[List all error scenarios with templates]

## Quality Standards
[Define quality requirements]
```

### Adding a New CLI Tool

**When to create a CLI tool:**
- Operation is deterministic (same input → same output)
- Operation requires validation logic
- Operation involves file I/O or API calls
- Operation needs to be testable

**Steps:**
1. Add Python module: `casestudypilot/tools/<tool_name>.py`
2. Implement function with clear input/output
3. Add CLI command in `casestudypilot/__main__.py`
4. Return exit code: 0 (success), 1 (warning), 2 (critical)
5. Write tests: `tests/test_<tool_name>.py`
6. Update README CLI commands section
7. Reference from agent workflows

**Exit Code Convention:**
```python
import sys

def main():
    try:
        result = do_work()
        if result.is_critical_failure:
            print("❌ Critical error", file=sys.stderr)
            sys.exit(2)
        elif result.has_warnings:
            print("⚠️ Warning", file=sys.stderr)
            sys.exit(1)
        else:
            print("✅ Success")
            sys.exit(0)
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(2)
```

## Framework Extension Examples

### Example 1: Blog Post Generation

**New skill:** `blog-post-generation`

```markdown
# Skill: blog-post-generation

## Purpose
Generate technical blog posts from meeting transcripts or design documents.

## Input Format
```json
{
  "source_content": "raw text",
  "target_audience": "developers|managers|general",
  "tone": "casual|professional|technical",
  "length": 500-2000 (words)
}
```

## Output Format
```json
{
  "title": "Blog post title",
  "subtitle": "Optional subtitle",
  "content": "Markdown content with sections",
  "tags": ["tag1", "tag2"],
  "estimated_read_time": 8
}
```
```

**New CLI tool:** `validate-blog-post`

```bash
python -m casestudypilot validate-blog-post blog.json
# Checks: length, structure, tone, formatting
# Exit codes: 0=pass, 1=warn, 2=critical
```

**New agent:** `blog-post-agent`

```markdown
# Blog Post Agent

## Workflow (8 Steps)

1. Extract source content from issue
2. Validate source quality → validate-source
3. Apply blog-post-generation skill
4. Validate blog post → validate-blog-post
5. Assemble final markdown
6. Create branch
7. Commit blog post
8. Create PR
```

### Example 2: Documentation Auditor

**New skill:** `documentation-analysis`

```markdown
# Skill: documentation-analysis

## Purpose
Analyze documentation for completeness, clarity, and accuracy.

## Input Format
```json
{
  "docs_directory": "path/to/docs",
  "file_list": ["file1.md", "file2.md"],
  "check_types": ["links", "spelling", "structure"]
}
```

## Output Format
```json
{
  "issues": [
    {
      "file": "path/to/file.md",
      "line": 42,
      "type": "broken_link",
      "severity": "critical",
      "message": "Link to /api/v2 is broken"
    }
  ],
  "summary": {
    "total_issues": 15,
    "critical": 3,
    "warnings": 12
  }
}
```
```

**New CLI tool:** `check-doc-links`

```bash
python -m casestudypilot check-doc-links docs/
# Validates all links in markdown files
# Exit codes: 0=all valid, 1=some broken, 2=many broken
```

**New agent:** `documentation-auditor-agent`

```markdown
# Documentation Auditor Agent

## Workflow (7 Steps)

1. Scan repository for markdown files
2. Apply documentation-analysis skill
3. Check all links → check-doc-links
4. Generate issue report
5. Create branch with fixes (if possible)
6. Commit fixes
7. Create PR with audit results
```

## Maintenance and Updates

### Keeping Documentation in Sync

**Critical rule:** Documentation must always match reality.

**When you make changes:**
1. ✅ Update README.md if architecture changes
2. ✅ Update AGENTS.md if patterns change
3. ✅ Update agent workflows if steps change
4. ✅ Update skills if input/output formats change
5. ✅ Update CONTRIBUTING.md if extension process changes

**Why?**
- Future LLM agents will read these docs
- Outdated docs cause confusion and errors
- You are writing for your future self

### Version Control

**Agent workflows use semantic versioning:**
- `1.0.0` - Initial release
- `1.1.0` - Minor changes (new features, backward compatible)
- `2.0.0` - Major changes (breaking changes to workflow)

**Update version in agent file header:**
```markdown
---
name: case-study-agent
version: 2.3.0  # Increment when workflow changes
---
```

**Document changes in CHANGELOG.md** (create if doesn't exist)

### Testing Your Changes

**Before committing:**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_validation.py -v

# Check test coverage
pytest tests/ --cov=casestudypilot --cov-report=html
```

**For CLI tools:**
- Write unit tests in `tests/`
- Test all exit codes (0, 1, 2)
- Test edge cases (empty input, malformed JSON, etc.)

**For skills:**
- Manually test with real examples
- Verify JSON output is valid
- Check output meets quality guidelines

**For agents:**
- Test end-to-end workflow manually
- Verify all validation checkpoints work
- Test error paths (what happens on failures?)

## Epic Issues: Implementation Context Archive

### Overview

Major feature implementations are tracked via **epic issues** (label: `epic`). These serve as the **source of truth** for implementation history and context for future agents.

**Why epic issues matter:**
- 📋 Implementation plan link
- 🧭 Architecture decisions and rationale
- 🐛 Challenges encountered
- ✅ Solutions applied
- 🎓 Lessons learned
- 🔗 Related PRs
- 📝 Context for future work

### When to Search Epic Issues

**Always check epics when:**
1. Working on existing features
2. Debugging problems
3. Planning related work
4. Refactoring code
5. Adding tests

**Search commands:**
```bash
# List all epics
gh issue list --label "epic" --state all

# Search by keyword
gh issue list --label "epic" --search "MCP server" --state all

# View specific epic
gh issue view 42
```

### Creating Epics

**Automatic creation:**
- `writing-plans` skill creates epic when plan is saved

**Manual creation:**
- User says "create an epic for plan X"
- Use `epic-creation` skill with plan file path
- Works with any plan format (flexible parsing)

**For existing plans without epics:**
```bash
# Find plans missing epics
for plan in docs/plans/*.md; do
  if ! grep -q "Epic Issue:" "$plan"; then
    echo "Missing epic: $plan"
    # Use epic-creation skill
  fi
done
```

### Epic Structure

```markdown
## 🎯 Goal
[One sentence]

## 🏗️ Architecture
[2-3 sentences]

## 🛠️ Tech Stack
[Technologies]

## 📋 Plan File
`docs/plans/filename.md`

## ✅ Tasks
- [ ] Task 1
- [ ] Task 2

---
Status: ✅ Completed

## 📚 Implementation Journey
[Added after completion]
```

### Discovery Pattern

Before changing unfamiliar code:

1. Identify the feature/component
2. Search epic issues
3. Read epic for context
4. Check plan file for details
5. Review related PRs

**Example:**
```bash
# Working on MCP client
gh issue list --label "epic" --search "MCP" --state all
gh issue view 42
cat docs/plans/2026-02-09-integrate-mcp.md
```

### Epic Lifecycle

- **Created:** When plan is written
- **Updated:** When work completes
- **Status:** Left open for reference
- **Labels:** `epic`, `planning`, `completed`, `documented`

---

## Support and Resources

### Documentation Hierarchy

1. **README.md** - Framework architecture (read first)
2. **AGENTS.md** - This file (operational guide)
3. **CONTRIBUTING.md** - Extension procedures (read when adding components)
4. **`.github/agents/*.md`** - Individual agent workflows
5. **`.github/skills/*/SKILL.md`** - Individual skill definitions
6. **`docs/`** - Technical details and design decisions

### Key Concepts

**Skill:** LLM-powered task with structured input/output (Layer 2)  
**Agent:** Orchestrator combining skills and CLI tools (Layer 1)  
**CLI Tool:** Python command for deterministic operations (Layer 3)  
**Validation:** Checkpoint with exit codes to prevent hallucination  
**Fail-Fast:** Stop immediately on critical errors (exit code 2)

### Questions to Ask Yourself

**Before adding a skill:**
- Is this task creative/interpretive? (If no, use CLI tool)
- Does it have clear input/output boundaries? (If no, refine)
- Can it be reused across agents? (If no, might be too specific)

**Before adding an agent:**
- Do I have a complete end-to-end workflow? (If no, plan more)
- Do I need multiple steps? (If no, might be single skill)
- Do I need validation checkpoints? (Usually yes)

**Before adding a CLI tool:**
- Is this deterministic? (If no, use skill)
- Can I write tests for it? (If no, rethink design)
- Does it need validation logic? (If yes, return exit codes)

## Version History

- **v2.2.0** (February 2026) - Added fail-fast validation framework
- **v2.0.0** (February 2026) - Initial production release with case study agent
- **v1.x** (February 2026) - Development and planning phase

---

**Remember:** You are the orchestrator. Skills and CLI tools are your instruments. Validation is your safety net. Documentation is your memory.

**Framework Status:** ✅ Production Ready - Ready for Skill Expansion  
**Version:** 2.2.0  
**Last Updated:** February 9, 2026
