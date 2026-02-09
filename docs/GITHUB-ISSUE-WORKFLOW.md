# GitHub Issue Workflow for Case Study Generation

## Overview

This document describes the automated GitHub issue workflow that allows users to request case study generation by simply creating an issue. The workflow automatically invokes the `@case-study-agent` to process the request without any manual intervention.

## Architecture

```
User creates issue with YouTube URL
    ↓
GitHub Issue Form (case-study-request.yml)
    ↓
Auto-applies "case-study" + "automation" labels
    ↓
GitHub Actions Workflow (auto-assign-case-study.yml)
    ↓
Workflow posts comment: "@case-study-agent please generate..."
    ↓
@case-study-agent processes the request
    ↓
Agent creates Pull Request with case study
    ↓
Agent posts results to the issue
```

## Components

### 1. Issue Template (`.github/ISSUE_TEMPLATE/case-study-request.yml`)

**Purpose:** Provides a structured form interface for users to submit case study requests.

**Features:**
- ✅ Form-based input (no markdown knowledge required)
- ✅ Required YouTube URL field with validation
- ✅ Optional company name field
- ✅ Optional additional context textarea
- ✅ Validation checkboxes for requirements
- ✅ Embedded instructions and examples
- ✅ Auto-applies `case-study` and `automation` labels

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| YouTube Video URL | Input | Yes | Full YouTube URL from CNCF channel |
| Company Name | Input | No | Optional if not clear from video title |
| Additional Context | Textarea | No | Any helpful information for the agent |
| Checklist | Checkboxes | Partial | Confirms CNCF requirements |

**Template Location:** `.github/ISSUE_TEMPLATE/case-study-request.yml`

**Example Issue Body (Generated):**
```markdown
### 📹 YouTube Video URL
https://www.youtube.com/watch?v=V6L-xOUdoRQ

### 🏢 Company Name (Optional)
Intuit

### 📝 Additional Context (Optional)
Video discusses GitOps adoption with Kubernetes and Argo CD.

### ✅ Checklist
- [x] This video is from the official CNCF YouTube channel
- [x] I understand the case study will be auto-generated and may require human review
- [x] The company featured is (to the best of my knowledge) a CNCF member
```

---

### 2. Template Configuration (`.github/ISSUE_TEMPLATE/config.yml`)

**Purpose:** Configures issue template behavior and provides helpful links.

**Features:**
- Enables blank issues alongside the template
- Provides links to documentation
- Provides link for bug reports

**Contact Links:**
- 📖 **Documentation** → `.github/copilot-instructions.md`
- 🐛 **Bug Report** → Standard issue creation

**Template Location:** `.github/ISSUE_TEMPLATE/config.yml`

---

### 3. Auto-Assignment Workflow (`.github/workflows/auto-assign-case-study.yml`)

**Purpose:** Automatically invokes `@case-study-agent` when case study issues are created.

**Trigger:**
```yaml
on:
  issues:
    types: [opened]
```

**Conditions:**
- Only runs if issue has `case-study` label
- Requires `issues: write` permission

**Actions:**
1. Detects new issue creation
2. Checks for `case-study` label
3. Posts comment using GitHub Script API:
   ```
   @case-study-agent please generate this case study based on the information provided above.
   ```

**Workflow Location:** `.github/workflows/auto-assign-case-study.yml`

**Expected Runtime:** ~5-10 seconds from issue creation to comment posted

---

## User Journey

### Step 1: Access Issue Templates

Users navigate to: `https://github.com/[owner]/[repo]/issues/new/choose`

They see the template selector with:
- **🎬 Case Study Request** - Main template for case study generation
- **📖 Documentation** - Link to full docs
- **🐛 Bug Report** - Link for reporting issues

### Step 2: Fill Out the Form

The form-based interface guides users through:

1. **YouTube Video URL** (required)
   - Placeholder: `https://www.youtube.com/watch?v=V6L-xOUdoRQ`
   - Must be from official CNCF YouTube channel

2. **Company Name** (optional)
   - Only needed if not clear from video title
   - Example: `Intuit, Adobe, Spotify`

3. **Additional Context** (optional)
   - Specific CNCF projects mentioned
   - Key metrics or outcomes discussed
   - Any special considerations

4. **Checklist** (required)
   - Confirm video is from CNCF channel
   - Understand case study is auto-generated
   - Optionally confirm company is CNCF member

### Step 3: Submit Issue

When user clicks "Submit new issue":
- Issue is created with structured body
- Labels `case-study` and `automation` are automatically applied
- Title format: `[Case Study] <user-provided-title>`

### Step 4: Automatic Workflow Execution

Within ~10 seconds:
1. GitHub Actions detects the new issue
2. Workflow verifies `case-study` label is present
3. Workflow posts comment mentioning `@case-study-agent`
4. Agent begins processing automatically

### Step 5: Agent Processing

The `@case-study-agent` executes its 12-step workflow (see `PLANNING.md` for details):
1. Extracts video ID from URL
2. Fetches video transcript
3. Identifies company name
4. Verifies CNCF membership
5. Applies transcript correction skill
6. Applies transcript analysis skill
7. Applies case study generation skill
8. Assembles case study from sections
9. Validates quality (score ≥ 0.60)
10. Creates branch `case-study-<company>-<video-id>`
11. Creates pull request
12. Posts results to issue

**Expected processing time:** 3-5 minutes

### Step 6: Results Posted

The agent posts a comment to the issue with:
- ✅ Success message with PR link
- Company name identified
- CNCF projects detected
- Quality score achieved
- Branch name created

**Example:**
```markdown
✅ Case study generated! Please review: #123

**Company:** Intuit
**Projects:** Kubernetes, Argo CD, Helm
**Quality Score:** 0.78
**Branch:** case-study-intuit-V6L-xOUdoRQ

The case study is ready for your review at case-studies/intuit.md
```

---

## Labels

### case-study
- **Color:** `#0E8A16` (green)
- **Description:** Automated case study generation request
- **Purpose:** Triggers the auto-assignment workflow
- **Auto-applied:** Yes (by issue template)

### automation
- **Color:** `#1D76DB` (blue)
- **Description:** Automated workflow processes
- **Purpose:** Categorizes automated tasks
- **Auto-applied:** Yes (by issue template)

---

## Error Handling

The workflow handles various error scenarios gracefully:

### Workflow Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| Workflow doesn't trigger | Label not applied | Manually add `case-study` label |
| Comment not posted | Permissions issue | Check `issues: write` permission |
| Workflow queued indefinitely | GitHub Actions limit | Wait for queue to clear |

### Agent Errors

| Error | Cause | Agent Response |
|-------|-------|----------------|
| Video not found | Invalid URL or private video | Comment + close issue |
| Not CNCF channel | Video from wrong channel | Comment with error + close |
| Company not member | Company not in CNCF landscape | Comment with suggestions + close |
| Quality too low | Insufficient content in video | Comment with issues + close |
| Transcript unavailable | Captions disabled | Comment with error + close |

---

## Testing

### Test Case 1: Valid CNCF Member Video

**Setup:**
1. Create issue via template
2. Use URL: `https://www.youtube.com/watch?v=V6L-xOUdoRQ`
3. Leave company name blank

**Expected Results:**
- ✅ Workflow triggers within 10 seconds
- ✅ Comment posted with `@case-study-agent` mention
- ✅ Agent identifies company as "Intuit"
- ✅ Verifies Intuit is CNCF member
- ✅ Generates case study with quality score ~0.78
- ✅ Creates PR successfully
- ✅ Posts success message to issue

**Test Duration:** ~4 minutes total

---

### Test Case 2: Non-CNCF Member Company

**Setup:**
1. Create issue via template
2. Use video URL from company not in CNCF landscape

**Expected Results:**
- ✅ Workflow triggers normally
- ✅ Agent processes video
- ❌ Verification fails at step 4
- ✅ Agent posts error message with suggestions
- ✅ Issue is closed automatically

---

### Test Case 3: Invalid YouTube URL

**Setup:**
1. Create issue via template
2. Use invalid or non-YouTube URL

**Expected Results:**
- ✅ Workflow triggers normally
- ❌ Video data extraction fails at step 2
- ✅ Agent posts error message
- ✅ Issue is closed automatically

---

## Debugging

### Check Workflow Execution

```bash
# List recent workflow runs
gh run list --workflow=auto-assign-case-study.yml --limit 5

# View specific workflow run
gh run view <run-id>

# View workflow logs
gh run view <run-id> --log
```

### Check Issue Details

```bash
# View issue with comments
gh issue view <issue-number> --comments

# Check issue labels
gh issue view <issue-number> --json labels

# View issue timeline
gh issue view <issue-number> --json timelineItems
```

### Common Debug Scenarios

**Workflow didn't trigger:**
```bash
# Check if labels were applied
gh issue view <issue-number> --json labels

# Manually trigger by adding comment
gh issue comment <issue-number> --body "@case-study-agent please generate this case study"
```

**Agent didn't respond:**
```bash
# Check if agent is properly configured
cat .github/agents/case-study-agent.md

# Verify GitHub Copilot is enabled for the repository
gh api repos/:owner/:repo/copilot
```

---

## Maintenance

### Updating the Template

To modify the issue template:

1. Edit `.github/ISSUE_TEMPLATE/case-study-request.yml`
2. Commit and push changes
3. Template updates appear immediately (no restart required)

**Example: Add a new field**
```yaml
  - type: input
    id: video_duration
    attributes:
      label: ⏱️ Video Duration (Optional)
      description: Approximate length of the video
      placeholder: e.g., 30 minutes
```

### Updating the Workflow

To modify the auto-assignment behavior:

1. Edit `.github/workflows/auto-assign-case-study.yml`
2. Commit and push changes
3. New workflow version applies to future issues only

**Example: Change comment message**
```yaml
body: '@case-study-agent please process this case study request with high priority.'
```

### Creating Additional Labels

```bash
# Create new label
gh label create "priority-high" \
  --description "High priority case study request" \
  --color "D73A4A"

# Add to issue template
# Edit case-study-request.yml:
labels: ["case-study", "automation", "priority-high"]
```

---

## Best Practices

### For Users

✅ **DO:**
- Use videos from the official CNCF YouTube channel
- Verify company is a CNCF member before submitting
- Provide additional context if the video is complex
- Check if a case study already exists for the company

❌ **DON'T:**
- Submit multiple videos in one issue (create separate issues)
- Submit videos without transcripts/captions
- Submit non-technical marketing videos
- Resubmit immediately if agent fails (wait for error message)

### For Maintainers

✅ **DO:**
- Monitor workflow execution for failures
- Review generated case studies for quality
- Update quality thresholds based on results
- Keep documentation in sync with template changes
- Test template changes in a fork first

❌ **DON'T:**
- Disable the workflow without notifying users
- Change label names without updating the workflow
- Remove required fields from the template
- Skip testing after major workflow changes

---

## Metrics and Monitoring

### Success Metrics

Track these metrics to measure workflow effectiveness:

| Metric | Description | Target |
|--------|-------------|--------|
| **Workflow Success Rate** | % of issues where workflow posts comment | > 95% |
| **Agent Success Rate** | % of issues where agent creates PR | > 60% |
| **Average Processing Time** | Time from issue creation to PR | < 5 minutes |
| **Quality Score Average** | Average quality score of generated case studies | > 0.70 |
| **Manual Intervention Rate** | % of issues requiring manual help | < 10% |

### Monitoring Commands

```bash
# Count case study issues
gh issue list --label "case-study" --state all --json number,state | jq 'length'

# Count successful PRs
gh pr list --search "case-study" --json number | jq 'length'

# View recent workflow runs
gh run list --workflow=auto-assign-case-study.yml --limit 10 --json conclusion | jq '[.[] | .conclusion] | group_by(.) | map({status: .[0], count: length})'
```

---

## Security Considerations

### Permissions

The workflow requires minimal permissions:
- **issues: write** - To post comments on issues
- **No repository write access** - Agent creates PRs, doesn't commit directly
- **No secrets required** - Uses `GITHUB_TOKEN` automatically provided

### Input Validation

The agent performs validation at multiple steps:
1. YouTube URL format validation
2. CNCF channel verification
3. Company membership verification
4. Content quality validation

### Rate Limiting

GitHub Actions has rate limits:
- **Workflow runs:** 1000 API requests per hour per repo
- **Issue comments:** Unlimited
- **Copilot agent:** Subject to Copilot usage limits

**Recommendation:** Monitor usage if processing > 20 case studies per hour

---

## Troubleshooting Guide

### Issue: Template doesn't appear in issue creation

**Symptoms:**
- Users don't see "🎬 Case Study Request" option
- Only blank issue option appears

**Solutions:**
1. Verify files exist:
   ```bash
   ls .github/ISSUE_TEMPLATE/
   ```
2. Check YAML syntax:
   ```bash
   yamllint .github/ISSUE_TEMPLATE/case-study-request.yml
   ```
3. Ensure files are committed and pushed to default branch

---

### Issue: Workflow doesn't trigger

**Symptoms:**
- Issue created but no comment appears
- Workflow run doesn't show in Actions tab

**Solutions:**
1. Verify `case-study` label was applied:
   ```bash
   gh issue view <number> --json labels
   ```
2. Check workflow exists on default branch:
   ```bash
   gh workflow view auto-assign-case-study.yml
   ```
3. Manually trigger workflow:
   ```bash
   gh issue comment <number> --body "@case-study-agent please generate this case study"
   ```

---

### Issue: Agent doesn't respond

**Symptoms:**
- Comment posted but agent doesn't process
- No follow-up comments from agent

**Solutions:**
1. Verify agent configuration exists:
   ```bash
   cat .github/agents/case-study-agent.md
   ```
2. Check GitHub Copilot is enabled for the repository
3. Verify agent skills are present:
   ```bash
   ls .github/skills/
   ```
4. Check if agent is processing other issues (may be rate limited)

---

## Future Enhancements

### Planned Improvements

1. **Priority Queue**
   - Add `priority` field to template
   - Agent processes high-priority requests first

2. **Status Updates**
   - Agent posts progress updates as it processes
   - Shows current step (e.g., "Analyzing transcript...")

3. **Batch Processing**
   - Allow multiple video URLs in one issue
   - Agent creates separate PRs for each

4. **Quality Previews**
   - Agent posts preview of generated sections
   - User can approve/reject before PR creation

5. **Custom Templates**
   - Allow users to specify case study template style
   - Support different output formats (blog post, whitepaper, etc.)

---

## Related Documentation

- **Agent Workflow:** `.github/agents/case-study-agent.md`
- **Skills Documentation:** `.github/skills/*/SKILL.md`
- **Planning Document:** `docs/PLANNING.md`
- **Implementation Guide:** `docs/IMPLEMENTATION-GUIDE.md`
- **Copilot Instructions:** `.github/copilot-instructions.md`

---

## Support

### For Users

If you encounter issues with the workflow:
1. Check this documentation first
2. Review error messages in issue comments
3. Create a bug report issue if problem persists
4. Tag `@case-study-agent` with specific questions

### For Contributors

To contribute improvements:
1. Fork the repository
2. Test changes thoroughly
3. Update documentation
4. Submit PR with clear description

---

## Changelog

### 2026-02-09 - Initial Release

**Added:**
- Form-based issue template for case study requests
- Auto-assignment workflow with GitHub Actions
- Template configuration with helpful links
- Automatic label application
- Comprehensive documentation

**Features:**
- ✅ Zero-setup workflow for users
- ✅ Automatic agent invocation
- ✅ Structured data collection
- ✅ Built-in validation and examples
- ✅ Complete error handling

---

*Last updated: 2026-02-09*
