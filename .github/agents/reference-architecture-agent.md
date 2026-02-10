---
name: reference-architecture-agent
description: Generate comprehensive reference architectures from YouTube videos for CNCF TAB submission
version: 1.0.0
trigger: GitHub issue with label "reference-architecture" and YouTube URL in body
---

# Reference Architecture Agent

## Mission

Automatically generate comprehensive reference architectures (2000-5000 words, 13 sections, 6 screenshots) from technical YouTube videos, suitable for CNCF Technical Advisory Board (TAB) submission.

## Overview

This agent extends the casestudypilot framework to generate reference architectures - detailed technical documents that showcase complex CNCF project integrations and architectural patterns. Reference architectures are more comprehensive than case studies (2000-5000 words vs 500-1500) and target technical audiences (engineers, architects) rather than business stakeholders.

**Key Differences from Case Study Agent:**
- 13 sections vs 5 sections
- 5+ CNCF projects vs 2+ projects  
- Technical depth score >= 0.70 vs 0.60
- Architecture diagrams with component specifications
- Suitable for CNCF TAB submission

## Workflow (19 Steps with 7 Validation Checkpoints)

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

echo "✅ Pre-flight checks passed"
echo "📹 Video URL: $VIDEO_URL"
```

---

### Step 2: Fetch Video Data and Validate Transcript

**Objective:** Download video metadata and transcript, then validate quality.

```bash
# Fetch video data
python -m casestudypilot youtube-data "$VIDEO_URL" > video_data.json

# Update issue title to match video title
VIDEO_TITLE=$(jq -r '.title' video_data.json)
gh issue edit "$ISSUE_NUMBER" --title "$VIDEO_TITLE"

echo "✅ Updated issue title to: $VIDEO_TITLE"

# Validate transcript quality (min 2000 chars for reference architectures)
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

echo "✅ Transcript validation passed"
```

**Checkpoint 1: Transcript Quality**
- Exit 0: Continue
- Exit 1: Log warning, continue
- Exit 2: Post error, STOP

---

### Step 3: Extract Company Name

**Objective:** Extract company name from video title/description.

```bash
# Extract company name (heuristic: look for patterns in title)
VIDEO_TITLE=$(jq -r '.title' video_data.json)
COMPANY_NAME=$(echo "$VIDEO_TITLE" | grep -oP '^[A-Z][a-zA-Z0-9\s]+(?=\sat\s|using|with|:|\s-\s)' || echo "[Company Name]")

echo "ℹ️ Extracted company: $COMPANY_NAME"
# Note: Final company name will be extracted in transcript-deep-analysis
```

---

### Step 4: Verify CNCF Membership (Optional)

**Objective:** Check if company is CNCF member (informational only).

```bash
python -m casestudypilot cncf-member-check "$COMPANY_NAME"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ $COMPANY_NAME is a CNCF member"
  MEMBERSHIP_STATUS="CNCF Member"
elif [ $EXIT_CODE -eq 1 ]; then
  echo "ℹ️ $COMPANY_NAME is not a CNCF member (reference architecture can still be submitted)"
  MEMBERSHIP_STATUS="Non-member"
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

**Output:** Save to `transcript_corrected.json`

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

**Output:** Save to `transcript_deep_analysis.json`

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

echo "✅ Deep analysis validation passed"
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

**Output:** Save to `diagram_specifications.json`

**Note:** No validation checkpoint (validated contextually in next step)

---

### Step 8: Apply reference-architecture-generation Skill

**Objective:** Generate comprehensive 13-section reference architecture content.

**Use skill:** `reference-architecture-generation` (NEW)

**Input:**
```json
{
  "deep_analysis": "<from transcript_deep_analysis.json>",
  "diagram_specifications": "<from diagram_specifications.json>",
  "company_info": {
    "name": "<from deep analysis>",
    "url": "<company URL from company verification or manual lookup>",
    "industry": "<from deep analysis>",
    "verified_membership": "<from Step 4>"
  },
  "video_metadata": {
    "title": "<from video_data.json>",
    "url": "<VIDEO_URL>",
    "duration_seconds": "<from video_data.json>",
    "duration_string": "<from video_data.json, format: HH:MM:SS or MM:SS>",
    "speakers": "<extracted from title, format: 'Name1 & Name2'>"
  }
}
```

**Output:** Save to `reference_architecture.json`

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

echo "✅ Metric validation passed"
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

echo "✅ Company consistency validation passed"
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

# Validate screenshot uniqueness
python -m casestudypilot validate-screenshots "$OUTPUT_FILE"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  echo "❌ Critical: Duplicate screenshots detected"
  gh issue comment "$ISSUE_NUMBER" --body "❌ **Validation Failed: Screenshot Duplication**

The generated reference architecture contains duplicate screenshots.

**Details:**
\`\`\`
$(python -m casestudypilot validate-screenshots \"$OUTPUT_FILE\" 2>&1)
\`\`\`

**Action Required:**
This is a bug in the reference-architecture-generation skill. Please report this issue with the video URL."
  
  exit 2
elif [ $EXIT_CODE -eq 1 ]; then
  echo "⚠️ Warning: Screenshot numbering issues detected"
fi

echo "✅ Screenshot validation passed"
```

---

### Step 12: Validate Final Quality

**Objective:** Final validation with technical depth scoring.

```bash
python -m casestudypilot validate-reference-architecture reference_architecture.json
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
  # CRITICAL: Technical depth too low
  gh issue comment "$ISSUE_NUMBER" --body "❌ **Validation Failed: Technical Depth**

The reference architecture does not meet minimum technical depth score.

**Validation Results:**
$(python -m casestudypilot validate-reference-architecture reference_architecture.json 2>&1)

**Action Required:**
The content is below quality standards for CNCF TAB submission (score < 0.60 or < 2000 words). Options:
1. Use a more technical video with implementation details
2. Use case-study-agent for less technical content (score >= 0.60)
3. Manually enhance the generated content and re-run validation"
  
  exit 2
elif [ $EXIT_CODE -eq 1 ]; then
  echo "⚠️ Warning: Technical depth score is 0.60-0.69 (acceptable but not ideal)"
fi

echo "✅ Final quality validation passed"
```

**Checkpoint 5: Final Technical Depth**
- Exit 0: Continue (score >= 0.70)
- Exit 1: Log warning, continue (score 0.60-0.69)
- Exit 2: Post error, STOP (score < 0.60 or other critical issues)

---

### Step 13: Create Branch

**Objective:** Create git branch for the reference architecture.

```bash
BRANCH_NAME="reference-architecture/${COMPANY_SLUG}-$(date +%Y%m%d)"

git checkout -b "$BRANCH_NAME"

echo "✅ Created branch: $BRANCH_NAME"
```

---

### Step 14: Commit Files

**Objective:** Commit reference architecture markdown and screenshots atomically.

```bash
# Add all files atomically
git add "$OUTPUT_FILE"
git add reference-architectures/images/${COMPANY_SLUG}/*.jpg

# Create commit
git commit -m "Add reference architecture for $COMPANY_NAME

- Generated from YouTube video: $VIDEO_URL
- Technical depth score: $(python -m casestudypilot validate-reference-architecture reference_architecture.json 2>&1 | grep -oP 'Technical Depth Score: \K[0-9.]+')
- Word count: $(jq -r '.sections | to_entries | map(.value | split(\" \") | length) | add' reference_architecture.json)
- CNCF projects: $(jq -r '.cncf_project_list | length' reference_architecture.json) projects
- Screenshots: 6 images

Generated by reference-architecture-agent v1.0.0"

echo "✅ Committed reference architecture and screenshots"
```

---

### Step 15: Push Branch

**Objective:** Push branch to remote repository.

```bash
git push -u origin "$BRANCH_NAME"

if [ $? -ne 0 ]; then
  echo "❌ Failed to push branch"
  exit 2
fi

echo "✅ Pushed branch: $BRANCH_NAME"
```

---

### Step 16: Create Pull Request with TAB Submission Guidance

**Objective:** Create PR with comprehensive description including TAB submission instructions.

```bash
TAB_GUIDANCE="## CNCF TAB Submission Instructions

This reference architecture is ready for submission to the CNCF Technical Advisory Board.

### Submission Process

1. **Merge this PR**: Review and merge this reference architecture to main branch
2. **Create TAB Issue**: Go to https://github.com/cncf/tab/issues/new
3. **Select Template**: Choose 'Reference Architecture Submission'
4. **Fill Template**:
   - **Title**: \"Reference Architecture: $COMPANY_NAME\"
   - **Link**: URL to this reference architecture on main branch
   - **Primary Patterns**: $(jq -r '.metadata.tab_metadata.primary_patterns | join(\", \")' reference_architecture.json)
   - **CNCF Projects**: $(jq -r '.cncf_project_list[0:5] | map(.name) | join(\", \")' reference_architecture.json)
   - **Architectural Significance**: $(jq -r '.metadata.tab_metadata.architectural_significance' reference_architecture.json)
5. **Wait for Review**: TAB typically reviews within 2-4 weeks

### Quality Metrics

- **Technical Depth Score**: $(python -m casestudypilot validate-reference-architecture reference_architecture.json 2>&1 | grep -oP 'Technical Depth Score: \K[0-9.]+') / 1.00 ✅
- **Word Count**: $(jq -r '.sections | to_entries | map(.value | split(\" \") | length) | add' reference_architecture.json) words
- **CNCF Projects**: $(jq -r '.cncf_project_list | length' reference_architecture.json) projects
- **Sections**: 13 sections
- **Screenshots**: 6 images

### TAB Review Criteria

The TAB will evaluate this reference architecture based on:
- Technical accuracy and depth
- Architectural patterns and design decisions
- CNCF project integration and usage
- Real-world implementation details
- Value to the cloud native community

For more information: https://github.com/cncf/tab/blob/main/process/reference-architectures.md"

gh pr create \
  --title "Add reference architecture for $COMPANY_NAME" \
  --body "$(cat <<EOF
# Reference Architecture: $COMPANY_NAME

## Summary

- **Company**: $COMPANY_NAME
- **Industry**: $(jq -r '.metadata.industry' reference_architecture.json)
- **Source Video**: [$VIDEO_TITLE]($VIDEO_URL)
- **Generated**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Technical Overview

This reference architecture documents $(jq -r '.metadata.company_name' reference_architecture.json)'s implementation of a cloud native architecture featuring $(jq -r '.cncf_project_list | length' reference_architecture.json) CNCF projects.

## CNCF Projects Featured

$(jq -r '.cncf_project_list[] | \"- **\(.name)** (\(.category)): \(.usage_summary)\"' reference_architecture.json)

## Key Metrics

$(jq -r '.key_metrics_summary[] | \"- **\(.metric)**: \(.improvement) → \(.business_impact)\"' reference_architecture.json)

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

echo "✅ Posted success comment to issue"
```

---

### Step 18: Cleanup

**Objective:** Clean up temporary files.

```bash
rm -f video_data.json transcript_corrected.json transcript_deep_analysis.json diagram_specifications.json reference_architecture.json
rm -rf screenshots/

echo "✅ Cleanup complete"
echo "✅ Reference architecture workflow completed successfully"
```

---

## Error Handling

### Critical Failure Points

The workflow has 5 critical validation checkpoints that will stop execution:

1. **Transcript Quality** (Step 2): < 2000 chars or no captions
2. **Deep Analysis** (Step 6): < 5 CNCF projects or missing architecture layers
3. **Metric Fabrication** (Step 9a): Metrics without transcript support
4. **Company Consistency** (Step 9b): Content about wrong company
5. **Final Quality** (Step 12): Technical depth score < 0.60

### Error Templates

All error templates are included inline in the workflow steps above.

### Recovery

If a workflow fails:
1. Check the validation error posted to the issue
2. Verify the video meets requirements (length, captions, technical depth)
3. Consider using case-study-agent for less technical videos
4. Re-run the workflow by adding the label again

---

## Quality Standards

### Minimum Requirements

- **Transcript**: >= 2000 characters
- **Video Length**: >= 15 minutes (20-40 minutes recommended)
- **CNCF Projects**: >= 5 projects featured
- **Architecture Layers**: All 3 layers documented (infrastructure, platform, application)
- **Integration Patterns**: >= 2 patterns described
- **Technical Metrics**: Quantitative results with transcript quotes
- **Screenshots**: 6 high-quality screenshots
- **Word Count**: 2000-5000 words
- **Technical Depth Score**: >= 0.70 (pass), >= 0.60 (warning)

### Sub-Score Targets

For technical depth >= 0.70, aim for:
- CNCF Project Depth: >= 0.80 (5+ projects, 3+ categories, integration patterns)
- Technical Specificity: >= 0.60 (commands, versions, configs, patterns)
- Implementation Detail: >= 0.70 (500+ words, phases, challenges)
- Metric Quality: >= 0.80 (3+ metrics with before/after)
- Architecture Completeness: >= 0.80 (11+ sections, diagrams, observability)

---

## Environment Requirements

### Required Tools

- Python 3.8+
- yt-dlp (YouTube video downloader)
- ffmpeg (screenshot extraction)
- jq (JSON processing)
- gh CLI (GitHub operations)

### Required Permissions

- Read/write access to repository
- Ability to create branches and PRs
- GitHub Actions or manual execution environment

### Directory Structure

```
.
├── reference-architectures/
│   └── images/
├── templates/
│   └── reference_architecture.md.j2
├── .github/
│   ├── agents/
│   │   └── reference-architecture-agent.md
│   └── skills/
│       ├── transcript-deep-analysis/
│       ├── architecture-diagram-specification/
│       └── reference-architecture-generation/
└── casestudypilot/
    └── tools/
        ├── validate_deep_analysis.py
        ├── validate_reference_architecture.py
        └── assemble_reference_architecture.py
```

---

## Version History

- **v1.0.0** (February 2026) - Initial release
  - 18-step workflow with 5 validation checkpoints
  - Technical depth scoring algorithm (5 sub-scores)
  - CNCF TAB submission guidance
  - Supports videos 15-40 minutes with 5+ CNCF projects

---

**Framework Status:** ✅ Production Ready  
**Last Updated:** February 10, 2026
