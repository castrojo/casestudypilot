# Organizational Report Generation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Epic Issue:** #36

**Goal:** Generate comprehensive "End User Amazingness Reports" that aggregate all YouTube presentations where a specific organization (e.g., Intuit, Adobe) is the subject, creating executive summaries with technical appendices showcasing their cloud-native journey, CNCF project adoption, and community contributions.

**Architecture:** Three-layer design following casestudypilot framework: (1) Organization-agent orchestrates 20-step workflow with 7 validation checkpoints, (2) Three new LLM skills for multi-video organization analysis, executive summary generation, and technical appendix generation, (3) Six new CLI tools for organization video discovery, multi-video aggregation, timeline generation, metric aggregation, and quality validation with organizational report assembly.

**Tech Stack:** Python (Typer, Rich), youtube-transcript-api, yt-dlp, httpx, Jinja2, pytest, GitHub CLI (gh), existing casestudypilot CLI tools (multi_video_processor, company_verifier)

---

## Context: Learning from Previous Epics

**From Reference Architecture Epic (#15):**
- Deep technical analysis with 5+ CNCF projects
- Multi-dimensional quality scoring (5 weighted factors)
- TAB submission readiness
- Comprehensive validation checkpoints

**From Presenter Profile Epic (#17):**
- Multi-video aggregation patterns
- Profile update workflow (detecting existing content)
- Fun metadata stats with emojis
- Timeline construction from multiple sources

**Organizational Report Unique Requirements:**
- Aggregate by organization subject (not presenter affiliation)
- Executive summary + technical appendix format
- Track cloud-native journey evolution over time
- Cross-video metrics aggregation (deployment improvements, cost savings, etc.)
- Organization-level CNCF project portfolio view

---

## Design Decisions

**Aggregation Strategy:** Single organization theme - aggregate all videos where the organization is the **subject**, regardless of who presents. Example: All videos discussing "Intuit's cloud-native journey" even if different speakers.

**Output Format:** Executive summary (300-500 words) + Technical appendix (1500-3000 words) = Total 1800-3500 words. High-level insights for executives with detailed technical content for engineers.

**Quality Standards:**
- Minimum videos: 2 (prefer 3+)
- Minimum CNCF projects: 3 across all videos
- Quality score: ≥0.65
- Must verify organization is CNCF end-user member

**File Structure:**
```
organizational-reports/
├── intuit.md                    # Executive summary + appendix
├── adobe.md
└── metadata/
    ├── intuit.json             # Structured data + video list
    └── adobe.json
```

---

## Implementation Phases

### Phase 1: Core CLI Tools (8-10 hours)

#### Task 1: Organization Video Discovery CLI Tool

**Goal:** Create `python -m casestudypilot discover-organization-videos <organization_name>` command that searches for all YouTube videos where the organization is the subject.

**Files:**
- Create: `casestudypilot/tools/organization_discovery.py`
- Modify: `casestudypilot/__main__.py`
- Test: `tests/test_organization_discovery.py`

**Key Features:**
- Search video transcripts for organization mentions
- Calculate confidence score based on:
  - Mention count in transcript (capped at 10 mentions = 0.5 score)
  - Title match (adds 0.3 to score)
  - Video duration (10+ minutes adds 0.2)
- Filter by confidence threshold (default 0.70)
- Support GitHub issue or manual URL input
- Output JSON with filtered video list

**Test Coverage:**
- VideoMatch dataclass structure
- Confidence score calculation
- Transcript search with multiple mentions
- Filtering by confidence threshold
- GitHub issue URL extraction
- Manual URL input
- Error handling (no URLs, no mentions)

**CLI Command:**
```bash
python -m casestudypilot discover-organization-videos "Intuit" \
  --issue 42 \
  --min-confidence 0.70 \
  --output organization_videos.json
```

#### Task 2: Organization Data Aggregator CLI Tool

**Goal:** Create `python -m casestudypilot aggregate-organization-data <videos_json>` command that fetches and aggregates data from multiple videos.

**Files:**
- Create: `casestudypilot/tools/organization_aggregator.py`
- Modify: `casestudypilot/__main__.py`
- Test: `tests/test_organization_aggregator.py`

**Key Features:**
- Fetch all video data using existing `fetch_multi_video_data`
- Build chronological timeline (sorted by upload date)
- Calculate date range (first to latest video)
- Calculate total duration across all videos
- Prepare dataset for LLM analysis
- Output structured JSON

**Test Coverage:**
- OrganizationDataset dataclass
- Timeline building and sorting
- Date range calculation
- Total duration calculation
- Empty video handling
- Multi-video aggregation success path

**CLI Command:**
```bash
python -m casestudypilot aggregate-organization-data \
  organization_videos.json \
  --output organization_dataset.json
```

#### Task 3: Organization Dataset Validator CLI Tool

**Goal:** Create `python -m casestudypilot validate-organization-dataset <dataset_json>` command that validates aggregated data quality.

**Files:**
- Create: `casestudypilot/validation/organization_dataset.py`
- Modify: `casestudypilot/__main__.py`
- Test: `tests/test_validate_organization_dataset.py`

**Validation Checks:**
- Minimum 2 videos (WARNING if < 3, CRITICAL if < 2)
- Each video has transcript ≥ 1000 characters
- Timeline chronologically sorted
- Date range valid (start <= end)
- Total duration ≥ 20 minutes (WARNING if < 30 minutes)
- All videos mention organization name

**Exit Codes:**
- 0: PASS (≥3 videos, all high quality)
- 1: WARNING (2 videos or some quality issues)
- 2: CRITICAL (< 2 videos or major data issues)

**CLI Command:**
```bash
python -m casestudypilot validate-organization-dataset dataset.json
echo $?  # Check exit code
```

#### Task 4: Organization Report Validator CLI Tool

**Goal:** Create `python -m casestudypilot validate-organization-report <report_json>` command that validates final report quality.

**Files:**
- Create: `casestudypilot/validation/organization_report.py`
- Modify: `casestudypilot/__main__.py`
- Test: `tests/test_validate_organization_report.py`

**Quality Scoring (5 dimensions):**
1. **Executive Summary Quality (20%)**
   - Word count: 300-500 words
   - Contains key achievements
   - Clear business value proposition

2. **Technical Appendix Depth (30%)**
   - Word count: 1500-3000 words
   - ≥3 CNCF projects documented
   - Architecture evolution described

3. **Metric Quality (25%)**
   - ≥3 business metrics cited
   - Metrics have context and video sources
   - Quantifiable results

4. **Timeline Coherence (15%)**
   - Chronological progression
   - Clear evolution narrative
   - Date-stamped milestones

5. **Formatting & Structure (10%)**
   - All required sections present
   - Proper markdown formatting
   - Video links functional

**Exit Codes:**
- 0: PASS (score ≥ 0.65)
- 1: WARNING (score 0.55-0.64)
- 2: CRITICAL (score < 0.55)

**CLI Command:**
```bash
python -m casestudypilot validate-organization-report report.json
```

#### Task 5: Organization Report Assembler CLI Tool

**Goal:** Create `python -m casestudypilot assemble-organization-report <report_data_json>` command that assembles final markdown report.

**Files:**
- Create: `casestudypilot/tools/organization_report_assembler.py`
- Create: `templates/organization_report.md.j2`
- Modify: `casestudypilot/__main__.py`
- Test: `tests/test_organization_report_assembler.py`

**Template Sections:**
```markdown
---
title: "[Organization] Cloud-Native Journey"
organization: "Organization Name"
report_type: "organizational"
video_count: N
date_range: "YYYY-MM to YYYY-MM"
generation_date: "YYYY-MM-DD"
---

# [Organization] Cloud-Native Journey

## Executive Summary
[300-500 words: business value, key achievements, CNCF adoption]

## Cloud-Native Journey Timeline
[Chronological milestones from videos]

## CNCF Project Portfolio
[Table of projects with adoption context]

## Key Achievements
[Aggregated business metrics and outcomes]

---

## Technical Appendix

### Architecture Evolution
[How their architecture changed over time]

### CNCF Projects Deep Dive
[Detailed usage of each project across videos]

### Implementation Patterns
[Common patterns observed]

### Metrics & Results
[Detailed metrics with video citations]

### Video References
[Complete list of source videos with links]
```

**CLI Command:**
```bash
python -m casestudypilot assemble-organization-report \
  report_data.json \
  --output organizational-reports/intuit.md
```

#### Task 6: Company Verification Integration

**Goal:** Extend existing `verify-company` to support organizational reports.

**Files:**
- Modify: `casestudypilot/tools/company_verifier.py`
- Test: `tests/test_company_verifier.py` (add new tests)

**Enhancement:**
- Add `--report-type` flag to distinguish case-study vs organizational
- For organizational reports, verify org is CNCF member
- Return verification result with context

**No new CLI command** - extends existing:
```bash
python -m casestudypilot verify-company "Intuit" \
  --report-type organizational \
  --output company_verification.json
```

---

### Phase 2: LLM Skills (6-8 hours)

#### Task 7: Organization Analysis Skill

**Goal:** Create `.github/skills/organization-analysis/SKILL.md` that analyzes multiple videos to extract organization-level insights.

**File:** `.github/skills/organization-analysis/SKILL.md`

**Purpose:** Analyze aggregated video transcripts to identify CNCF projects, business metrics, architecture evolution, and key themes across an organization's cloud-native journey.

**Input Format:**
```json
{
  "organization": "Intuit",
  "videos_data": [
    {
      "video_id": "abc123",
      "title": "Intuit's Kubernetes Journey",
      "transcript": "...",
      "upload_date": "2023-06-20",
      "duration": 1200
    }
  ],
  "timeline": [
    {
      "video_id": "abc123",
      "title": "...",
      "upload_date": "2023-06-20"
    }
  ]
}
```

**Output Format:**
```json
{
  "organization": "Intuit",
  "cncf_projects": [
    {
      "name": "Kubernetes",
      "adoption_timeline": "First mentioned 2022, production 2023",
      "usage_contexts": ["Container orchestration", "Platform foundation"],
      "video_count": 3,
      "evolution": "Started with single cluster, now multi-cluster"
    }
  ],
  "aggregated_metrics": [
    {
      "metric": "Deployment frequency",
      "values": ["10x improvement", "Daily deploys"],
      "video_sources": ["abc123", "def456"],
      "context": "CI/CD pipeline improvements"
    }
  ],
  "architecture_evolution": {
    "starting_point": "Legacy VM-based infrastructure",
    "key_milestones": [
      {
        "date": "2022-Q3",
        "milestone": "Kubernetes adoption",
        "video_id": "abc123"
      }
    ],
    "current_state": "Cloud-native platform with service mesh"
  },
  "key_themes": [
    "Progressive migration strategy",
    "Developer productivity focus",
    "Cost optimization journey"
  ]
}
```

**Execution Instructions:**

1. **Read all video transcripts** - Understand the complete narrative across time
2. **Identify CNCF projects** - Extract all projects mentioned with usage context
3. **Track adoption timeline** - When each project was introduced/matured
4. **Aggregate business metrics** - Collect quantifiable results with video sources
5. **Map architecture evolution** - Identify starting point, milestones, current state
6. **Extract key themes** - Common threads across presentations
7. **Validate completeness** - Ensure minimum 3 CNCF projects identified

**Quality Guidelines:**
- Each CNCF project must have ≥1 usage context
- Metrics must cite specific video sources (video_id)
- Architecture evolution must be chronological
- Avoid fabricating metrics not in transcripts
- Preserve organization name consistency

#### Task 8: Executive Summary Generation Skill

**Goal:** Create `.github/skills/executive-summary-generation/SKILL.md` that generates business-focused 300-500 word summaries.

**File:** `.github/skills/executive-summary-generation/SKILL.md`

**Purpose:** Generate executive-level summary highlighting business value, key achievements, and CNCF adoption strategy for C-suite and business leaders.

**Input Format:**
```json
{
  "organization": "Intuit",
  "organization_analysis": {
    "cncf_projects": [...],
    "aggregated_metrics": [...],
    "architecture_evolution": {...},
    "key_themes": [...]
  },
  "company_verification": {
    "is_member": true,
    "matched_name": "Intuit"
  }
}
```

**Output Format:**
```json
{
  "executive_summary": {
    "opening": "Paragraph 1: Organization overview and cloud-native commitment",
    "achievements": "Paragraph 2: Key business outcomes and metrics",
    "technology": "Paragraph 3: CNCF projects adopted and why",
    "conclusion": "Paragraph 4: Future direction and community leadership",
    "word_count": 450
  }
}
```

**Execution Instructions:**

1. **Opening paragraph (100-150 words)**
   - Introduce organization and industry
   - State cloud-native adoption commitment
   - Mention CNCF end-user membership

2. **Achievements paragraph (100-150 words)**
   - Highlight top 3 business metrics
   - Quantify improvements (deployment frequency, cost savings, etc.)
   - Connect to business outcomes

3. **Technology paragraph (100-150 words)**
   - List key CNCF projects (3-5 max)
   - Explain adoption rationale
   - Describe architecture approach

4. **Conclusion paragraph (50-100 words)**
   - Future roadmap if mentioned
   - Community contributions
   - Call to action or lessons learned

**Quality Guidelines:**
- Target 300-500 words total
- Business-focused language (avoid deep technical jargon)
- Quantify value (use metrics from analysis)
- Maintain professional tone
- No fabricated metrics or claims

#### Task 9: Technical Appendix Generation Skill

**Goal:** Create `.github/skills/technical-appendix-generation/SKILL.md` that generates detailed 1500-3000 word technical content.

**File:** `.github/skills/technical-appendix-generation/SKILL.md`

**Purpose:** Generate comprehensive technical appendix with architecture details, CNCF project deep dives, implementation patterns, and detailed metrics for engineers and architects.

**Input Format:**
```json
{
  "organization": "Intuit",
  "organization_analysis": {
    "cncf_projects": [...],
    "aggregated_metrics": [...],
    "architecture_evolution": {...},
    "key_themes": [...]
  },
  "videos_data": [...]
}
```

**Output Format:**
```json
{
  "technical_appendix": {
    "architecture_evolution": "500-700 words: detailed architecture journey",
    "cncf_projects_deep_dive": "600-900 words: project-by-project analysis",
    "implementation_patterns": "300-500 words: common patterns observed",
    "metrics_and_results": "200-400 words: detailed metrics with citations",
    "video_references": [
      {
        "video_id": "abc123",
        "title": "Intuit Talk 1",
        "url": "https://youtube.com/watch?v=abc123",
        "date": "2023-06-20",
        "key_topics": ["Kubernetes", "Cost optimization"]
      }
    ],
    "word_count": 2100
  }
}
```

**Execution Instructions:**

1. **Architecture Evolution (500-700 words)**
   - Starting infrastructure (VMs, legacy systems)
   - Migration strategy and phases
   - Key architectural decisions
   - Current state and future plans

2. **CNCF Projects Deep Dive (600-900 words)**
   - One section per project (3-5 projects)
   - Adoption rationale
   - Implementation details
   - Integration with other projects
   - Lessons learned

3. **Implementation Patterns (300-500 words)**
   - Common patterns across projects
   - Progressive migration strategies
   - Testing and validation approaches
   - Operational practices

4. **Metrics & Results (200-400 words)**
   - Detailed metrics table with video citations
   - Before/after comparisons
   - Business impact analysis
   - ROI discussion if available

5. **Video References**
   - Complete list of source videos
   - Clickable links with timestamps
   - Key topics per video

**Quality Guidelines:**
- Target 1500-3000 words total
- Technical depth appropriate for engineers
- All metrics cite video sources (video_id)
- Include specific technologies, versions where mentioned
- Maintain factual accuracy (no fabrication)

---

### Phase 3: Organization Agent Workflow (6-8 hours)

#### Task 10: Create Organization Agent

**Goal:** Create `.github/agents/organization-agent.md` with 20-step workflow and 7 validation checkpoints.

**File:** `.github/agents/organization-agent.md`

**Agent Metadata:**
```yaml
---
name: organization-agent
description: Generate organizational reports from multiple YouTube videos
version: 1.0.0
trigger: GitHub issue with label "organizational-report" and YouTube URLs in body
---
```

**Workflow Overview (20 Steps):**

**Step 0: Pre-flight Validation**
- Verify Python environment
- Check repository structure (`organizational-reports/` directory)
- Validate issue contains organization name and ≥2 video URLs

**Step 1: Extract Organization and Video URLs from Issue**
- Parse organization name from issue title or body
- Extract all YouTube URLs from issue body
- Validate URL format

**Step 2: Discover Organization Videos**
```bash
python -m casestudypilot discover-organization-videos "$ORG_NAME" \
  --issue "$ISSUE_NUMBER" \
  --min-confidence 0.70 \
  --output organization_videos.json
```

**CHECKPOINT 1: Video Discovery Validation**
- Minimum 2 videos found (CRITICAL if < 2)
- Average confidence ≥ 0.70 (WARNING if 0.60-0.69)
- Exit code: 0=continue, 1=warn+continue, 2=stop+post error

**Step 3: Verify Company is CNCF Member**
```bash
python -m casestudypilot verify-company "$ORG_NAME" \
  --report-type organizational \
  --output company_verification.json
```

**CHECKPOINT 2: Company Verification**
- Organization must be CNCF end-user member (CRITICAL if not)
- Exit code: 0=member, 2=not member (stop workflow)

**Step 4: Aggregate Organization Data**
```bash
python -m casestudypilot aggregate-organization-data \
  organization_videos.json \
  --output organization_dataset.json
```

**CHECKPOINT 3: Dataset Validation**
```bash
python -m casestudypilot validate-organization-dataset \
  organization_dataset.json
```
- Exit code: 0=pass, 1=warn, 2=critical (stop)

**Step 5: Apply Transcript Correction Skill (Per Video)**
- For each video in dataset, apply existing `transcript-correction` skill
- Correct common transcription errors
- Save corrected transcripts

**Step 6: Apply Organization Analysis Skill**
- Use skill: `organization-analysis`
- Input: organization_dataset.json with corrected transcripts
- Output: organization_analysis.json
- Extracts CNCF projects, metrics, architecture evolution

**CHECKPOINT 4: Analysis Validation**
- Minimum 3 CNCF projects (WARNING if 2, CRITICAL if < 2)
- Minimum 3 business metrics (WARNING if < 3)
- Architecture evolution described (CRITICAL if missing)
- Exit code: 0=pass, 1=warn, 2=critical

**Step 7: Apply Executive Summary Generation Skill**
- Use skill: `executive-summary-generation`
- Input: organization_analysis.json + company_verification.json
- Output: executive_summary.json
- Generates 300-500 word business-focused summary

**Step 8: Apply Technical Appendix Generation Skill**
- Use skill: `technical-appendix-generation`
- Input: organization_analysis.json + videos_data
- Output: technical_appendix.json
- Generates 1500-3000 word technical content

**Step 9: Combine Summary + Appendix**
- Merge executive_summary.json and technical_appendix.json
- Create unified report_data.json
- Validate total word count (1800-3500 words)

**CHECKPOINT 5: Content Completeness**
- Executive summary: 300-500 words (CRITICAL if out of range)
- Technical appendix: 1500-3000 words (WARNING if 1200-1500)
- Total: 1800-3500 words (CRITICAL if < 1800)

**Step 10: Validate Metrics and Company Consistency**
```bash
# Use existing validation tools adapted for multi-video
python -m casestudypilot validate-metrics \
  report_data.json organization_dataset.json

python -m casestudypilot validate-consistency \
  report_data.json company_verification.json
```

**CHECKPOINT 6: Quality Validation**
- All metrics cite video sources (CRITICAL if fabricated)
- Organization name consistent (CRITICAL if wrong org mentioned)
- Exit code: 0=pass, 2=critical (stop)

**Step 11: Assemble Final Report**
```bash
python -m casestudypilot assemble-organization-report \
  report_data.json \
  --output organizational-reports/$ORG_SLUG.md
```

**Step 12: Validate Final Quality Score**
```bash
python -m casestudypilot validate-organization-report \
  report_data.json
```

**CHECKPOINT 7: Final Quality Score**
- Score ≥ 0.65 (PASS)
- Score 0.55-0.64 (WARNING - continue but flag)
- Score < 0.55 (CRITICAL - stop)

**Step 13: Create Branch**
```bash
BRANCH="organizational-report/$ORG_SLUG"
git checkout -b "$BRANCH"
```

**Step 14: Commit Report**
```bash
git add organizational-reports/$ORG_SLUG.md
git add organizational-reports/metadata/$ORG_SLUG.json
git commit -m "Add organizational report for $ORG_NAME"
```

**Step 15: Create Pull Request**
```bash
gh pr create \
  --title "Add organizational report for $ORG_NAME" \
  --body "..." \
  --base main
```

**Step 16: Post Success to Issue**
- Post PR link to original issue
- Include report summary statistics
- Thank contributor

**Error Templates:**
- 7 error templates (one per checkpoint)
- Each includes: what failed, critical issues, possible causes, action required

---

### Phase 4: Templates & Infrastructure (3-4 hours)

#### Task 11: Create Jinja2 Template

**Goal:** Create `templates/organization_report.md.j2` for report assembly.

**File:** `templates/organization_report.md.j2`

**Template Structure:**
- YAML frontmatter with metadata
- Executive Summary section
- Journey Timeline section
- CNCF Project Portfolio table
- Key Achievements section
- Technical Appendix (collapsible or separate)
- Video References section

**Variables:**
- `organization`, `video_count`, `date_range`
- `executive_summary` (object with paragraphs)
- `timeline` (list of milestones)
- `cncf_projects` (list with details)
- `aggregated_metrics` (list with citations)
- `technical_appendix` (object with sections)
- `video_references` (list with links)

#### Task 12: Create Directory Structure

```bash
mkdir -p organizational-reports/metadata
mkdir -p organizational-reports/images  # For future screenshots
```

#### Task 13: Create GitHub Issue Template

**Goal:** Create `.github/ISSUE_TEMPLATE/generate-organizational-report.yml`

**Template Fields:**
- Organization name (required)
- Video URLs (required, minimum 2)
- Expected CNCF projects (optional)
- Known business outcomes (optional)
- Additional context (optional)

**Template Content:**
```yaml
name: Generate an Organizational Report
description: Generate a comprehensive organizational report (1800-3500 words) aggregating multiple presentations
labels: ["organizational-report"]
body:
  - type: markdown
    attributes:
      value: |
        Generate an executive summary + technical appendix showcasing an organization's cloud-native journey.
        
        **Output:** 1800-3500 word report with executive summary (300-500w) and technical appendix (1500-3000w)
        
        **Requirements:**
        - Minimum 2 videos (prefer 3+)
        - Organization must be CNCF end-user member
        - Videos discuss organization's CNCF adoption
        - Minimum 3 CNCF projects across all videos

  - type: input
    id: organization
    attributes:
      label: Organization Name
      description: Full organization name
      placeholder: e.g., Intuit, Adobe, Capital One
    validations:
      required: true

  - type: textarea
    id: video_urls
    attributes:
      label: Video URLs
      description: YouTube URLs (minimum 2, one per line)
      placeholder: |
        https://www.youtube.com/watch?v=VIDEO_ID_1
        https://www.youtube.com/watch?v=VIDEO_ID_2
        https://www.youtube.com/watch?v=VIDEO_ID_3
    validations:
      required: true

  - type: textarea
    id: cncf_projects
    attributes:
      label: Expected CNCF Projects (Optional)
      placeholder: |
        - Kubernetes
        - Prometheus
        - Envoy

  - type: textarea
    id: business_outcomes
    attributes:
      label: Known Business Outcomes (Optional)
      placeholder: |
        - 10x deployment frequency improvement
        - 30% cost reduction
        - 50% faster incident response
```

---

### Phase 5: Documentation Updates (3-4 hours)

#### Task 14: Update README.md

**Sections to Add:**

1. **Content Types** - Add organizational reports to comparison table
2. **Organizational Reports** - New section with:
   - Purpose and audience
   - When to use vs case studies vs reference architectures
   - Output structure
   - Example organizations

3. **CLI Commands** - Add new commands:
   - `discover-organization-videos`
   - `aggregate-organization-data`
   - `validate-organization-dataset`
   - `validate-organization-report`
   - `assemble-organization-report`

#### Task 15: Update AGENTS.md

**Sections to Add:**

1. **Current Implementation: Organizational Report Generation**
   - Agent overview
   - 20-step workflow summary
   - 7 validation checkpoints
   - Skills used (3)
   - CLI tools used (6)

2. **Multi-Video Aggregation Patterns**
   - Video discovery by organization mention
   - Confidence scoring
   - Timeline construction
   - Cross-video metric aggregation

#### Task 16: Update CONTRIBUTING.md

**If Needed:** Add guidance for extending with organizational report features.

---

### Phase 6: Integration Testing (4-6 hours)

#### Task 17: End-to-End Test with Intuit

**Goal:** Generate complete organizational report for Intuit using real YouTube videos.

**Test Videos:** (Find 2-3 real Intuit CNCF videos)

**Success Criteria:**
- All 7 validation checkpoints pass
- Executive summary: 300-500 words
- Technical appendix: 1500-3000 words
- Quality score ≥ 0.65
- Report generated in `organizational-reports/intuit.md`
- PR created successfully

#### Task 18: Test Validation Checkpoints

**Goal:** Test each validation checkpoint with bad data to ensure fail-fast works.

**Test Scenarios:**
1. Only 1 video provided (should CRITICAL stop at checkpoint 1)
2. Non-CNCF member organization (should CRITICAL stop at checkpoint 2)
3. Videos with very short transcripts (should warn/stop at checkpoint 3)
4. Only 1 CNCF project found (should CRITICAL stop at checkpoint 4)
5. Executive summary too short (should CRITICAL stop at checkpoint 5)
6. Fabricated metrics (should CRITICAL stop at checkpoint 6)
7. Quality score < 0.55 (should CRITICAL stop at checkpoint 7)

#### Task 19: Test Error Recovery

**Goal:** Verify error messages are helpful and issues get properly updated.

**Test Scenarios:**
- Video discovery finds 0 videos
- Company verification fails
- Dataset validation fails
- GitHub API errors

#### Task 20: Achieve Test Coverage ≥80%

**Goal:** Write comprehensive unit and integration tests.

**Test Files:**
- All CLI tool test files (6)
- All validation test files (2)
- Integration tests for full workflow

---

## Quick Reference

### New CLI Commands

```bash
# Discover videos for organization
python -m casestudypilot discover-organization-videos "Intuit" \
  --issue 42 \
  --min-confidence 0.70 \
  --output organization_videos.json

# Aggregate data from discovered videos
python -m casestudypilot aggregate-organization-data \
  organization_videos.json \
  --output organization_dataset.json

# Validate organization dataset
python -m casestudypilot validate-organization-dataset \
  organization_dataset.json

# Validate organizational report quality
python -m casestudypilot validate-organization-report \
  report_data.json

# Assemble final report
python -m casestudypilot assemble-organization-report \
  report_data.json \
  --output organizational-reports/intuit.md

# Verify company (extended)
python -m casestudypilot verify-company "Intuit" \
  --report-type organizational \
  --output company_verification.json
```

### Exit Code Convention

- **0**: PASS (continue workflow)
- **1**: WARNING (log warning, continue with degraded quality)
- **2**: CRITICAL (stop workflow immediately, post error to issue)

### Quality Thresholds

- **Minimum videos**: 2 (prefer 3+)
- **Minimum CNCF projects**: 3 across all videos
- **Executive summary**: 300-500 words
- **Technical appendix**: 1500-3000 words
- **Total word count**: 1800-3500 words
- **Quality score**: ≥0.65

### Validation Checkpoints

1. **Video Discovery** (Step 2) - Minimum 2 videos with confidence ≥ 0.70
2. **Company Verification** (Step 3) - Must be CNCF end-user member
3. **Dataset Validation** (Step 4) - Data quality and completeness
4. **Analysis Validation** (Step 6) - Minimum 3 CNCF projects, 3 metrics
5. **Content Completeness** (Step 9) - Word counts in range
6. **Quality Validation** (Step 10) - No fabrication, consistency check
7. **Final Quality Score** (Step 12) - Overall score ≥ 0.65

---

## Success Criteria

Implementation complete when:

- ✅ All 6 CLI tools implemented with tests
- ✅ All 3 LLM skills created
- ✅ Organization-agent workflow complete (20 steps)
- ✅ Jinja2 template created
- ✅ GitHub issue template created
- ✅ Documentation updated (README, AGENTS, CONTRIBUTING)
- ✅ End-to-end test with real organization succeeds
- ✅ All 7 validation checkpoints tested
- ✅ Test coverage ≥80%
- ✅ At least 1 organizational report generated and merged

---

## Estimated Timeline

- **Phase 1: Core CLI Tools** - 8-10 hours
- **Phase 2: LLM Skills** - 6-8 hours
- **Phase 3: Organization Agent** - 6-8 hours
- **Phase 4: Templates & Infrastructure** - 3-4 hours
- **Phase 5: Documentation** - 3-4 hours
- **Phase 6: Integration Testing** - 4-6 hours

**Total Estimated Time:** 30-40 hours

---

## Notes for Implementing Agent

**Reuse Existing Components:**
- `multi_video_processor.py` - Already handles batch video fetching
- `company_verifier.py` - Extend for organizational reports
- `transcript-correction` skill - Apply per-video
- `validate-metrics` and `validate-consistency` - Adapt for multi-video

**New Patterns:**
- Video discovery by organization mentions (confidence scoring)
- Multi-video timeline construction
- Cross-video metric aggregation
- Executive + appendix two-part structure

**Critical Success Factors:**
- Fail-fast validation at each checkpoint
- Clear error messages for users
- No metric fabrication (cite video sources)
- Organization name consistency throughout
- Quality score transparency

**Testing Strategy:**
- TDD for all CLI tools (write tests first)
- Mock external APIs (YouTube, GitHub)
- Test happy path and error paths
- Validate all exit codes
- Test with real data (Intuit example)

---

**Status:** 🟡 Ready for Implementation

**Version:** 1.0.0

**Created:** 2026-02-10
