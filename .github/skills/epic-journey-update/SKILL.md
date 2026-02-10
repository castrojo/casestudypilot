---
name: epic-journey-update
description: Update epic issue with implementation journey and lessons learned after work completes
version: 1.0.0
---

# Epic Journey Update

## Purpose

Update epic issue with comprehensive implementation journey documenting challenges, solutions, learnings, and context for future agents.

## When to Use

- After merging epic-related branch to main
- After PR merge for epic work
- When user requests "update epic #N with journey"

**Announce at start:** "I'm using the epic-journey-update skill to document the implementation journey."

## Input Requirements

- **Epic issue number** (required)
- **Branch name** OR **PR number** (at least one)
- **Base branch** (default: main)

## Execution Instructions

### Step 1: Gather Context

**If working from branch:**
```bash
BRANCH_NAME="<feature-branch>"
BASE_BRANCH="main"

# Get commits
git log $BASE_BRANCH..$BRANCH_NAME --oneline --no-merges

# Get files changed
git diff $BASE_BRANCH...$BRANCH_NAME --name-only
```

**If working from PR:**
```bash
PR_NUMBER="<pr-number>"

# Get PR details
gh pr view $PR_NUMBER --json title,body,commits,comments

# Get commit messages
gh pr view $PR_NUMBER --json commits --jq '.commits[].commit.message'

# Get files changed
gh pr view $PR_NUMBER --json files --jq '.files[].path'
```

### Step 2: Analyze Implementation

Review the commits, PR discussion, and code changes to understand:

**Challenges (2-4 items):**
- Look for "fix", "debug", "resolve", "workaround", "bug" in commits
- PR comments discussing problems
- Technical obstacles, unexpected issues

**Solutions (2-4 items):**
- Look for "implement", "add", "refactor", "improve" in commits
- Key design decisions
- Tradeoffs made and why

**Learnings (2-3 items):**
- What worked well
- What to do differently next time
- Patterns to reuse or avoid

**Artifacts:**
- Count files modified/created
- List top 10 key files
- Count test files
- List related PRs

### Step 3: Write Context for Future Agents

**This is the most important section.** Write 2-4 sentences covering:

**Design Rationale:**
- Why this approach over alternatives
- What constraints influenced decisions
- What assumptions were made

**Integration Points:**
- What depends on this work
- What must remain stable
- What can be safely changed

**Dependencies:**
- External requirements
- Configuration needs
- Version constraints

**Follow-up Work:**
- Known limitations
- Suggested improvements
- Related work needed

**Warnings:**
- What NOT to do
- What breaks if changed incorrectly
- Performance/security considerations

### Step 4: Generate Journey Log

Create journey content:

```markdown
---

## 📊 Status

✅ **Completed**

**Completed:** <date>
**Branch:** `<branch-name>`
**PR:** #<pr-number> (if applicable)

---

## 📚 Implementation Journey

### Summary

<2-3 sentences: what was accomplished, key deliverables>

### Challenges Encountered

- **<Challenge 1>**: <Description and impact>
- **<Challenge 2>**: <Description and impact>

### Solutions Applied

- **<Solution 1>**: <How solved and why>
- **<Solution 2>**: <Decision and rationale>

### Key Learnings

- <Learning 1>
- <Learning 2>

### Artifacts Created

- **Files Modified:** <count> files (key: file1, file2, ...)
- **Tests Added:** <count> test files
- **Related PRs:** #<pr1>

### Context for Future Agents

**Design Rationale:** <Why this approach>

**Integration Points:** <What depends on this>

**Dependencies:** <Requirements>

**Follow-up Work:** <Limitations and improvements>

**Warnings:** <What not to do>

---
```

### Step 5: Update Epic Issue

Get current issue body and update the journey section:

```bash
EPIC_NUMBER="<epic-number>"

# Get current body
CURRENT_BODY=$(gh issue view $EPIC_NUMBER --json body --jq '.body')

# Replace content between JOURNEY_START and JOURNEY_END markers
# Option 1: In-place update (complex text manipulation)
# Option 2: Append as comment (simpler)

# Simpler approach - post journey as comment
gh issue comment $EPIC_NUMBER --body "$(cat journey_log.md)"
```

**Alternative - update in place:**
```bash
# Save current body
echo "$CURRENT_BODY" > temp_body.md

# Use sed or awk to replace section between JOURNEY_START and JOURNEY_END
# with new journey content

# Update issue
gh issue edit $EPIC_NUMBER --body "$(cat updated_body.md)"
```

### Step 6: Update Labels

```bash
# Add completion labels
gh issue edit $EPIC_NUMBER --add-label "completed,documented"

# Note: Do NOT close the issue (per user preference)
```

### Step 7: Confirm

```bash
gh issue comment $EPIC_NUMBER --body "✅ Epic journey documented. Implementation complete and lessons learned captured for future reference."
```

## Quality Guidelines

Journey logs must be:
- ✅ **Factual** - Based on actual work, not assumptions
- ✅ **Specific** - Concrete examples, not vague statements
- ✅ **Concise** - 500-800 words total
- ✅ **Actionable** - Future agents can apply learnings

**Bad:** "We improved performance"
**Good:** "MCP stdio connection had 2s startup delay causing test timeouts. Added retry logic with 3 attempts. Reduced test failures from 30% to 0%."

## Example Journey Entry

### Summary

Integrated CNCF Landscape MCP server to replace direct API calls, providing real-time project and member data with validated quality.

### Challenges Encountered

- **MCP Connection Stability**: Initial stdio connection had timeout issues with Docker container startup (2s delay)
- **Fuzzy Matching Edge Cases**: Company name variations (e.g., "Intuit Inc." vs "Intuit") required threshold tuning

### Solutions Applied

- **Connection Pooling**: Implemented context manager with retry logic (3 attempts, 2s delay between retries)
- **Calibrated Threshold**: Tested with 50 company names, set fuzzy match threshold to 85 for optimal precision/recall balance

### Key Learnings

- MCP stdio transport requires explicit connection verification before tool calls
- Fuzzy matching threshold should be data-driven (test with real examples, not guesswork)
- Docker container startup time impacts test suite (add warmup step to reduce flaky tests)

### Artifacts Created

- **Files Modified:** 12 files (mcp_client.py, validate_company.py, test_mcp_client.py, hyperlinks.py, transcript_analysis skill)
- **Tests Added:** 24 tests (18 unit, 6 integration)
- **Related PRs:** #123
- **Documentation:** Updated AGENTS.md with MCP integration patterns

### Context for Future Agents

**Design Rationale:** MCP client uses stdio transport (not HTTP) because landscape-mcp-server only supports stdio currently. Chose context manager pattern for automatic cleanup after API errors to prevent leaked Docker processes.

**Integration Points:** All company verification flows through validate_company.py → mcp_client.query_members(). Project validation uses transcript-analysis skill → validate_analysis.py → mcp_client.query_projects(). Do not bypass mcp_client or you'll have stale data from old landscape.json cache.

**Dependencies:** Requires Docker and mcp Python package (0.1.0+). Landscape data URL is configurable but defaults to https://landscape.cncf.io/data/full.json. Connection fails silently if Docker not running - check stderr logs for "connection refused".

**Follow-up Work:** Consider adding connection pooling for multiple concurrent requests (currently serial). HTTP transport would be more reliable but requires upstream changes to landscape-mcp-server. Caching layer could reduce Docker startup overhead in tests (currently 2s per test).

**Warnings:** Do not remove retry logic in connect() method - Docker startup is genuinely slow (2s). Do not lower fuzzy match threshold below 85 - causes false positives (tested: "Adobe" matched "Abode" at 80%). Do not cache query results longer than 1 hour - landscape data updates multiple times daily.

## Integration

**Called by:**
- `finishing-a-development-branch` skill - After Option 1 (local merge) when epic detected
- Manual agent invocation - When user requests journey update
- After PR merge notification - When observing epic-related work complete
