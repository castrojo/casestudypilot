# Agent Workflow Validation Updates

## Overview

This document describes the validation checkpoints to add to `.github/agents/case-study-agent.md`.

## Updated Steps

### Step 2: Fetch Video Data and Validate Transcript (UPDATED)

**After running:**
```bash
python -m casestudypilot youtube-data "<youtube-url>"
```

**ADD VALIDATION:**
```bash
python -m casestudypilot validate-transcript video_data.json
```

**Check exit code and decide:**
- Exit code 0 (PASS) → Continue to Step 3
- Exit code 1 (WARNING) → Log warning in issue comment, continue to Step 3
- Exit code 2 (CRITICAL) → Post error to issue, close issue with label `validation-failed-transcript`, STOP

**Error Post Template (CRITICAL):**
```markdown
❌ **Validation Failed: Transcript Quality**

The video transcript does not meet minimum quality requirements:

**Critical Issues:**
[List issues from validation output]

**Possible Causes:**
- Video may not have captions enabled
- Video may be too short for case study generation
- YouTube API may have failed to fetch transcript

**Action Required:**
Please verify:
1. Video has captions/subtitles enabled on YouTube
2. Video is at least 10 minutes long
3. Video URL is correct and accessible

If the video meets these requirements, please try again or report an issue.
```

---

### Step 3: Extract Company Name and Validate (UPDATED)

**Extraction priority:**
1. Check issue body for user-provided company name (confidence = 1.0)
2. Parse video title for company name
3. Parse video description

**ADD VALIDATION:**
```bash
python -m casestudypilot validate-company "<company-name>" "<video-title>" --confidence <score>
```

**Check exit code and decide:**
- Exit code 0 (PASS) → Continue to Step 4
- Exit code 1 (WARNING) → Log warning, continue to Step 4
- Exit code 2 (CRITICAL) → Post error to issue, close issue with label `validation-failed-company`, STOP

**Error Post Template (CRITICAL):**
```markdown
❌ **Validation Failed: Company Identification**

Cannot identify valid company name from video.

**Details:**
- Video Title: "{title}"
- Extracted Name: "{extracted}" (confidence: {score})
- Issue: {validation_error}

**Action Required:**
Please edit the issue and provide the company name in the "Company Name (Optional)" field, then re-run the agent.
```

---

### Step 6: Apply Transcript Analysis Skill and Validate Output (NEW)

**After using the `transcript-analysis` skill:**

**ADD VALIDATION:**
```bash
python -m casestudypilot validate-analysis transcript_analysis.json
```

**Check exit code and decide:**
- Exit code 0 (PASS) → Continue to Step 7
- Exit code 1 (WARNING) → Log warning, continue to Step 7
- Exit code 2 (CRITICAL) → Post error to issue, close issue with label `validation-failed-analysis`, STOP

**Error Post Template (CRITICAL):**
```markdown
❌ **Validation Failed: Transcript Analysis**

The transcript analysis does not meet minimum requirements for case study generation.

**Critical Issues:**
[List issues from validation output]

**Possible Causes:**
- Video may not be about CNCF technologies
- Transcript may lack technical content
- Video may be introductory/overview only

**Action Required:**
This video may not be suitable for automated case study generation. Please verify:
1. Video discusses specific CNCF project usage (Kubernetes, Prometheus, etc.)
2. Speaker provides technical details about implementation
3. Video is from a CNCF end-user, not a vendor pitch

Consider trying a different video or manually creating the case study.
```

---

### NEW Step 8.5: Validate Generated Case Study Content

**After Step 8 (case-study-generation skill), ADD NEW STEP:**

#### Validation 1: Metric Fabrication Detection

```bash
python -m casestudypilot validate-metrics case_study_sections.json video_data.json transcript_analysis.json
```

**Check exit code:**
- Exit code 0 (PASS) → Continue to validation 2
- Exit code 1 (WARNING) → Log warning with list of suspicious metrics, continue to validation 2

**Warning Log:**
```markdown
⚠️ **Warning: Potential Metric Fabrication**

Found {count} metric(s) in generated case study that don't appear in transcript:
- {metric1}
- {metric2}

These metrics should be reviewed for accuracy before merging.
```

#### Validation 2: Company Consistency Check

```bash
python -m casestudypilot validate-consistency case_study_sections.json video_data.json company_verification.json
```

**Check exit code:**
- Exit code 0 (PASS) → Continue to Step 9 (Assembly)
- Exit code 1 (WARNING) → Log warning, continue
- Exit code 2 (CRITICAL) → Post critical error, close issue with label `validation-failed-company-mismatch`, STOP

**Error Post Template (CRITICAL):**
```markdown
❌ **CRITICAL ERROR: Company Mismatch Detected**

The generated case study appears to be about the WRONG COMPANY!

**Expected Company:** {expected}
**Generated Case Study About:** {detected}

**Details:**
- Expected company mentioned: {expected_count} times
- Other company mentioned: {other_count} times

**This is the same bug that caused the Spotify hallucination incident.**

**Action:**
Workflow stopped to prevent generating incorrect case study. This is likely an LLM hallucination issue.

**Manual Review Required:**
1. Review `case_study_sections.json` manually
2. Verify transcript content in `video_data.json`
3. Check if video is actually about {expected} or {detected}
4. Report this incident if it's a regression of the transcript API bug

**DO NOT MERGE** any output from this workflow run.
```

---

### Step 10: Validate Quality (ENHANCED)

**After running:**
```bash
python -m casestudypilot validate case-studies/<company>.md
```

**The validation output now includes warnings from all previous validation steps.**

**Enhanced PR description should include:**
```markdown
## Validation Summary

**Transcript Quality:** ✅ PASS / ⚠️ WARNING / ❌ CRITICAL
[Details]

**Company Identification:** ✅ PASS / ⚠️ WARNING / ❌ CRITICAL
[Details]

**Analysis Quality:** ✅ PASS / ⚠️ WARNING / ❌ CRITICAL
[Details]

**Content Validation:** ✅ PASS / ⚠️ WARNING
- Metric verification: [status]
- Company consistency: [status]

**Overall Quality Score:** {score}

**Validation Warnings (if any):**
- [List all warnings from validation steps]
```

---

## New Issue Labels

Add these labels to the repository:
- `validation-failed-transcript`: Empty/bad transcript
- `validation-failed-company`: Can't identify company
- `validation-failed-analysis`: No CNCF projects found
- `validation-failed-company-mismatch`: Wrong company detected (Spotify bug)
- `validation-failed-quality`: Quality score too low
- `validation-warning`: Has warnings but continued

---

## Stop Points Summary

**Agent MUST STOP at these points:**

1. **Step 2**: Empty/insufficient transcript (< 1000 chars or < 50 segments)
2. **Step 3**: Cannot identify company name (generic/empty/low confidence)
3. **Step 6**: No CNCF projects in analysis OR missing required sections
4. **Step 8.5**: Company mismatch detected (wrong company in generated content)
5. **Step 10**: Quality score < 0.60

**Agent CONTINUES WITH WARNING at these points:**

1. **Step 2**: Short transcript (< 5000 chars)
2. **Step 3**: Medium confidence company extraction (0.5-0.7)
3. **Step 6**: Only 1 CNCF project OR no quantitative metrics
4. **Step 8.5**: Metrics not found in transcript (possible fabrication)
5. **Step 8.5**: Other companies mentioned (partners/competitors)

---

## Agent Version Update

Update agent version from `2.0.0` to `2.2.0` (major feature: fail-fast validation)

---

## CLI Commands Reference

For manual testing/debugging, these commands are now available:

```bash
# Validate transcript
python -m casestudypilot validate-transcript video_data.json

# Validate company name
python -m casestudypilot validate-company "Intuit" "Intuit's Journey" --confidence 1.0

# Validate analysis
python -m casestudypilot validate-analysis transcript_analysis.json

# Validate metrics
python -m casestudypilot validate-metrics case_study_sections.json video_data.json transcript_analysis.json

# Validate company consistency
python -m casestudypilot validate-consistency case_study_sections.json video_data.json company_verification.json

# Run all validations
python -m casestudypilot validate-all video_data.json transcript_analysis.json case_study_sections.json company_verification.json
```

**Exit codes:**
- 0: PASS (all checks passed)
- 1: WARNING (some warnings, can continue)
- 2: CRITICAL (fatal errors, must stop)
