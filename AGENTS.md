# Case Study Generation - Agent Workflow Guide

## Overview

This document codifies the workflow for generating CNCF case studies from YouTube videos. The primary workflow is defined in `.github/agents/case-study-agent.md` and agent skills in `.github/skills/`, but this document captures general best practices and operational guidelines.

## Primary Documentation

**ALWAYS refer to these as the source of truth:**
- **Agent Workflow:** `.github/agents/case-study-agent.md` (version 2.2.0+)
- **Agent Skills:** `.github/skills/*/SKILL.md`
  - `transcript-analysis` - Extract CNCF projects, metrics, sections
  - `case-study-generation` - Generate polished markdown content
  - `transcript-correction` - Clean up transcript text

**This document supplements but does NOT replace the agent workflow and skills.**

---

## Core Principles

### 1. Fail-Fast Validation

The framework implements 5 validation checkpoints to prevent hallucination:

| Step | Checkpoint | Command | Critical Failure Behavior |
|------|-----------|---------|---------------------------|
| 2 | Transcript Quality | `validate-transcript` | Stop, label issue, close |
| 3 | Company Identification | `validate-company` | Stop, label issue, close |
| 6 | Analysis Output | `validate-analysis` | Stop, label issue, close |
| 8.5 | Metric Fabrication | `validate-metrics` | Continue (WARNING only) |
| 8.5 | Company Consistency | `validate-consistency` | Stop if wrong company |
| 10 | Final Quality | `validate` | Stop if score < 0.60 |

**Exit Codes:**
- `0` = PASS (continue)
- `1` = WARNING (log and continue)
- `2` = CRITICAL (stop workflow immediately)

### 2. Always Use Real Metadata

```bash
# ✅ CORRECT - Fetches real YouTube title
python -m casestudypilot youtube-data "https://www.youtube.com/watch?v=VIDEO_ID"

# ❌ WRONG - Never use placeholder titles
title = "Video VIDEO_ID"
```

The youtube_client uses `yt-dlp` to fetch real video metadata including title, description, duration, and channel.

### 3. Slugified Filenames

Case study filenames MUST match the YouTube video title (slugified):

```python
# From utils.slugify()
title = "Supercharge Your Canary Deployments - Alex & Zach"
filename = "supercharge-your-canary-deployments.md"
```

**Rules:**
- Lowercase
- Hyphens as separators
- Remove special characters
- Strip speaker names (after " - ")
- Maximum readability

### 4. Always Include Screenshots

Screenshots provide visual context and improve case study quality:

```bash
python -m casestudypilot extract-screenshots \
  video_data.json \
  transcript_analysis.json \
  case_study_sections.json \
  --download-dir case-studies/images/<slugified-title>/ \
  --output screenshots.json
```

**Screenshot sections:**
- `challenge.jpg` - Problem visualization
- `solution.jpg` - Architecture/implementation
- `impact.jpg` - Results and metrics

**Pass to assembler:**
```bash
python -m casestudypilot assemble \
  video_data.json \
  transcript_analysis.json \
  case_study_sections.json \
  company_verification.json \
  --screenshots screenshots.json
```

### 5. Hyperlinks Are Mandatory

The template automatically adds hyperlinks for:

**Company names:**
- `[Intuit](https://www.intuit.com)` (from `hyperlinks.COMPANY_URLS`)

**CNCF projects:**
- `**[Kubernetes](https://kubernetes.io)**`
- `**[Argo CD](https://argoproj.github.io/cd/)**`

**Glossary terms:**
- `[GitOps](https://glossary.cncf.io/gitops/)`
- `[cloud-native](https://glossary.cncf.io/cloud-native-tech/)`

**To add new mappings:**
Edit `casestudypilot/hyperlinks.py`:
```python
COMPANY_URLS = {
    "NewCompany": "https://www.newcompany.com",
}

PROJECT_URLS = {
    "NewProject": "https://newproject.io",
}

GLOSSARY_TERMS = {
    "new term": "https://glossary.cncf.io/new-term/",
}
```

---

## Complete Workflow (Local Execution)

This is a reference implementation. **Always consult `.github/agents/case-study-agent.md` for the authoritative workflow.**

### Step 1: Fetch Video Data

```bash
python -m casestudypilot youtube-data "https://www.youtube.com/watch?v=VIDEO_ID"
# Creates: video_data.json
```

**Validation:**
```bash
python -m casestudypilot validate-transcript video_data.json
# Exit 0 = continue, Exit 2 = STOP
```

### Step 2: Extract Company Name

From issue body or video title:
```bash
COMPANY_NAME="Intuit"  # From issue or video metadata
```

**Validation:**
```bash
python -m casestudypilot validate-company "$COMPANY_NAME" "$VIDEO_TITLE" --confidence 1.0
# Exit 0 = continue, Exit 2 = STOP
```

### Step 3: Verify CNCF Membership

```bash
python -m casestudypilot verify-company "$COMPANY_NAME"
# Creates: company_verification.json
```

If API fails, manually create:
```json
{
  "query_name": "CompanyName",
  "matched_name": "CompanyName",
  "is_member": true,
  "confidence": 1.0,
  "landscape_url": "https://landscape.cncf.io",
  "category": "CNCF End User",
  "member_level": "End User Member"
}
```

### Step 4: Analyze Transcript

**Manual analysis following `.github/skills/transcript-analysis/SKILL.md`:**

Create `transcript_analysis.json`:
```json
{
  "cncf_projects": [
    {
      "name": "Kubernetes",
      "usage_context": "container orchestration"
    }
  ],
  "key_metrics": [
    {
      "value": "50%",
      "type": "percentage",
      "context": "deployment time reduction",
      "full_statement": "50% reduction in deployment time"
    }
  ],
  "sections": {
    "background": "...",
    "challenge": "...",
    "solution": "...",
    "impact": "..."
  }
}
```

**Validation:**
```bash
python -m casestudypilot validate-analysis transcript_analysis.json
# Exit 0 = continue, Exit 2 = STOP
```

### Step 5: Generate Case Study Sections

**Manual generation following `.github/skills/case-study-generation/SKILL.md`:**

Create `case_study_sections.json`:
```json
{
  "overview": "Markdown content with **bold CNCF projects**...",
  "challenge": "Markdown content with **bold metrics**...",
  "solution": "Markdown content...",
  "impact": "Markdown content...",
  "conclusion": "Markdown content..."
}
```

**Validation:**
```bash
# Validate metrics
python -m casestudypilot validate-metrics \
  case_study_sections.json \
  video_data.json \
  transcript_analysis.json
# Exit 0/1 = continue

# Validate company consistency
python -m casestudypilot validate-consistency \
  case_study_sections.json \
  video_data.json \
  company_verification.json
# Exit 0/1 = continue, Exit 2 = STOP (wrong company!)
```

### Step 6: Extract Screenshots

```bash
python -m casestudypilot extract-screenshots \
  video_data.json \
  transcript_analysis.json \
  case_study_sections.json \
  --download-dir case-studies/images/<slugified-title>/ \
  --output screenshots.json
# Creates: screenshots.json + 3 JPG files
```

### Step 7: Assemble Final Case Study

```bash
python -m casestudypilot assemble \
  video_data.json \
  transcript_analysis.json \
  case_study_sections.json \
  company_verification.json \
  --screenshots screenshots.json
# Creates: case-studies/<slugified-title>.md
```

### Step 8: Validate Quality

```bash
python -m casestudypilot validate "case-studies/<slugified-title>.md"
# Exit 0 = PASS (score >= 0.60), Exit 2 = STOP
```

---

## File Structure

### Input Files

```
video_data.json              # From youtube-data command
transcript_analysis.json     # Manual or AI-generated analysis
case_study_sections.json     # Manual or AI-generated content
company_verification.json    # From verify-company command
screenshots.json             # From extract-screenshots command
```

### Output Files

```
case-studies/
  <slugified-title>.md                    # Final case study
  images/<slugified-title>/
    challenge.jpg                          # Challenge screenshot
    solution.jpg                           # Solution screenshot
    impact.jpg                             # Impact screenshot
```

---

## Quality Standards

### Minimum Requirements (from validation.py)

- **Transcript:** >= 1000 chars, >= 50 segments, >= 100 words
- **Company Confidence:** >= 0.7 (WARNING at 0.5-0.7)
- **CNCF Projects:** >= 1 (WARNING if only 1)
- **Section Length:** >= 100 chars each
- **Quality Score:** >= 0.60 (target 0.70+)

### Style Requirements (from case-study-generation skill)

- **Word Count:** 500-1500 total
- **Tone:** Professional, technical, factual
- **Voice:** Third-person narrative
- **Tense:** Past for actions, present for current state
- **Metrics:** Always bold (`**50% reduction**`)
- **CNCF Projects:** Always bold and linked (`**[Kubernetes](https://kubernetes.io)**`)

---

## Common Pitfalls

### ❌ Don't Do This

1. **Skip validation checkpoints**
   ```bash
   # BAD - no validation
   python -m casestudypilot assemble ...
   ```

2. **Use placeholder titles**
   ```json
   {"title": "Video VIDEO_ID"}  // WRONG
   ```

3. **Forget screenshots**
   ```bash
   # BAD - no --screenshots flag
   python -m casestudypilot assemble ... 
   ```

4. **Ignore exit codes**
   ```bash
   validate-transcript video.json
   # Exit 2 but continue anyway - WRONG!
   ```

5. **Fabricate metrics**
   ```markdown
   **300% improvement** in performance  // Not in transcript!
   ```

### ✅ Do This

1. **Always validate at checkpoints**
   ```bash
   validate-transcript && validate-company && validate-analysis
   ```

2. **Use real metadata**
   ```bash
   python -m casestudypilot youtube-data URL  # Fetches real title
   ```

3. **Include screenshots**
   ```bash
   extract-screenshots ... && assemble ... --screenshots screenshots.json
   ```

4. **Check exit codes**
   ```bash
   if ! validate-transcript video.json; then
     echo "CRITICAL failure - stopping"
     exit 2
   fi
   ```

5. **Quote from transcript**
   ```markdown
   **100+ incidents prevented** per month  // Directly from speaker
   ```

---

## Troubleshooting

### Screenshots Fail to Extract

**Problem:** yt-dlp can't download frames

**Solution:** Falls back to YouTube thumbnails automatically
```bash
# Check screenshots.json for extraction_method
cat screenshots.json | jq '.screenshots[].extraction_method'
# "frame_extraction" (good) or "thumbnail_fallback" (acceptable)
```

### Metrics Validation Warnings

**Problem:** Metrics not found in transcript

**Solution:** Only use metrics explicitly stated by speaker
```bash
validate-metrics ... --json | jq '.checks[] | select(.passed == false)'
```

### Company Mismatch Detected

**Problem:** Generated content about wrong company (Spotify bug pattern)

**Solution:** CRITICAL failure - workflow stops automatically
```bash
# This should NEVER happen with validation
validate-consistency ...
# Exit 2 = wrong company detected
```

### Quality Score Too Low

**Problem:** Score < 0.60

**Solutions:**
1. Add more CNCF projects (check transcript)
2. Include more metrics (bold them: `**50%**`)
3. Ensure all 4 sections have >= 100 chars
4. Add glossary term hyperlinks

---

## Maintenance

### Adding New Companies

Edit `casestudypilot/hyperlinks.py`:
```python
COMPANY_URLS = {
    "NewCompany": "https://www.newcompany.com",
}
```

### Adding New CNCF Projects

Edit `casestudypilot/hyperlinks.py`:
```python
PROJECT_URLS = {
    "NewProject": "https://newproject.io",
}
```

Update `.github/skills/transcript-analysis/SKILL.md` to include new project in common list.

### Updating Validation Thresholds

Edit `casestudypilot/validation.py`:
```python
MIN_TRANSCRIPT_LENGTH = 1000      # Increase if quality issues
MIN_CONFIDENCE = 0.7              # Company identification threshold
MIN_QUALITY_SCORE = 0.60          # Final quality gate
```

Update tests in `tests/test_validation.py` to match new thresholds.

---

## Version History

- **v2.2.0** - Added fail-fast validation framework (current)
- **v2.0.0** - Original workflow (13 steps)
- **v1.x** - Initial implementation

---

## Support

For issues or questions:
1. Check `.github/agents/case-study-agent.md` (authoritative workflow)
2. Review `.github/skills/*/SKILL.md` (detailed task guidance)
3. Consult this document for best practices
4. Report bugs at https://github.com/castrojo/casestudypilot/issues

---

**Remember:** This document provides general guidance. **Always defer to the agent workflow and skills as the primary source of truth.**
