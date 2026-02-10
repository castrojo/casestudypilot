---
name: content-orchestrator
description: Discover and automatically process content generation requests by spawning specialized LLM agents
version: 2.0.0
trigger: Manual invocation via "ingest incoming requests" or `python -m casestudypilot orchestrate`
---

# Content Orchestrator Agent

## Mission

Automatically discover open GitHub issues requesting content generation and orchestrate the processing of each request by invoking the appropriate specialized agent.

## Overview

This agent serves as the **universal dispatcher/orchestrator** for all casestudypilot content generation requests. It:

1. **Discovers** open issues labeled with content type labels
2. **Validates** that issues are not already being processed
3. **Parses** issue data (YouTube URL, company name, content type)
4. **Spawns** LLM subagents via Task tool to execute specialized workflows
5. **Monitors** completion via issue labels and comments (posted by subagents)

**Execution Model (v2.0.0):** The orchestrator delegates execution to specialized LLM agents (case-study-agent, reference-architecture-agent) via OpenCode Task tool. Subagents execute workflows silently and post results to issues on completion.

**Supported Content Types:**

| Content Type | Label | Agent | Status |
|--------------|-------|-------|--------|
| Case Study | `case-study` | `case-study-agent` | ✅ v2.2.0 |
| Reference Architecture | `reference-architecture` | `reference-architecture-agent` | ✅ v1.0.0 |
| Presenter Profile | `presenter-profile` | `people-agent` | ⚠️ Not yet implemented (epic #17) |

**Key Responsibilities:**
- Multi-type issue discovery and filtering
- Preventing duplicate processing
- Sequential or parallel orchestration
- Error aggregation and reporting
- Content type routing

## Workflow (8 Steps)

### Step 1: Pre-Flight Checks

**Objective:** Verify environment and GitHub access.

```bash
# Check gh CLI is available
if ! command -v gh &> /dev/null; then
  echo "❌ Error: gh CLI not found"
  exit 2
fi

# Verify authentication
if ! gh auth status &> /dev/null; then
  echo "❌ Error: gh CLI not authenticated"
  exit 2
fi

# Verify repository access
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
echo "✅ Repository: $REPO"

# Verify Python environment
python -m casestudypilot --version || {
  echo "❌ Error: casestudypilot CLI not available"
  exit 2
}

echo "✅ Pre-flight checks passed"
```

---

### Step 2: Discover Open Issues by Content Type

**Objective:** Find all open issues for each content type that need processing.

```bash
echo "🔍 Discovering content generation requests..."
echo ""

# Fetch case study issues
CASE_STUDY_ISSUES=$(gh issue list \
  --label "case-study" \
  --state open \
  --json number,title,labels,createdAt,body \
  --limit 100)

CASE_STUDY_COUNT=$(echo "$CASE_STUDY_ISSUES" | jq 'length')
echo "📄 Case Studies: $CASE_STUDY_COUNT open request(s)"

# Fetch reference architecture issues
REF_ARCH_ISSUES=$(gh issue list \
  --label "reference-architecture" \
  --state open \
  --json number,title,labels,createdAt,body \
  --limit 100)

REF_ARCH_COUNT=$(echo "$REF_ARCH_ISSUES" | jq 'length')
echo "🏗️  Reference Architectures: $REF_ARCH_COUNT open request(s)"

# Fetch presenter profile issues
PRESENTER_ISSUES=$(gh issue list \
  --label "presenter-profile" \
  --state open \
  --json number,title,labels,createdAt,body \
  --limit 100)

PRESENTER_COUNT=$(echo "$PRESENTER_ISSUES" | jq 'length')
echo "👤 Presenter Profiles: $PRESENTER_COUNT open request(s)"

# Calculate total
TOTAL_COUNT=$((CASE_STUDY_COUNT + REF_ARCH_COUNT + PRESENTER_COUNT))

if [ $TOTAL_COUNT -eq 0 ]; then
  echo ""
  echo "ℹ️ No open content generation requests found"
  exit 0
fi

echo ""
echo "📋 Total: $TOTAL_COUNT open request(s) across all content types"
echo ""

# Save to files for processing
echo "$CASE_STUDY_ISSUES" > discovered_case_studies.json
echo "$REF_ARCH_ISSUES" > discovered_ref_archs.json
echo "$PRESENTER_ISSUES" > discovered_presenters.json
```

**Output:** 
- `discovered_case_studies.json`
- `discovered_ref_archs.json`
- `discovered_presenters.json`

---

### Step 3: Filter Already-Processed Issues

**Objective:** Exclude issues that are already being processed or completed.

```bash
echo "🔎 Filtering already-processed issues..."
echo ""

# Define filter function for processed/failed issues
filter_processed() {
  local input_file=$1
  jq '[.[] | select(
    (.labels | map(.name) | 
      (contains(["case-study-generated"]) or
       contains(["reference-architecture-generated"]) or
       contains(["presenter-profile-generated"]) or
       contains(["in-progress"]) or
       contains(["validation-failed-transcript"]) or
       contains(["validation-failed-company"]) or
       contains(["validation-failed-analysis"]) or
       contains(["validation-failed-presenter"]) or
       contains(["validation-failed-company-mismatch"]) or
       contains(["validation-failed-quality"])) | not
    )
  )]' "$input_file"
}

# Filter each content type
PENDING_CASE_STUDIES=$(filter_processed discovered_case_studies.json)
PENDING_REF_ARCHS=$(filter_processed discovered_ref_archs.json)
PENDING_PRESENTERS=$(filter_processed discovered_presenters.json)

# Count pending issues
PENDING_CS_COUNT=$(echo "$PENDING_CASE_STUDIES" | jq 'length')
PENDING_RA_COUNT=$(echo "$PENDING_REF_ARCHS" | jq 'length')
PENDING_PP_COUNT=$(echo "$PENDING_PRESENTERS" | jq 'length')
PENDING_TOTAL=$((PENDING_CS_COUNT + PENDING_RA_COUNT + PENDING_PP_COUNT))

if [ $PENDING_TOTAL -eq 0 ]; then
  echo "ℹ️ All discovered issues are already processed or in-progress"
  exit 0
fi

# Save pending issues
echo "$PENDING_CASE_STUDIES" > pending_case_studies.json
echo "$PENDING_REF_ARCHS" > pending_ref_archs.json
echo "$PENDING_PRESENTERS" > pending_presenters.json

echo "✅ Pending issues ready for processing:"
echo "   📄 Case Studies: $PENDING_CS_COUNT"
echo "   🏗️  Reference Architectures: $PENDING_RA_COUNT"
echo "   👤 Presenter Profiles: $PENDING_PP_COUNT"
echo "   📋 Total: $PENDING_TOTAL"
echo ""

# Display issue lists
if [ $PENDING_CS_COUNT -gt 0 ]; then
  echo "Case Study Requests:"
  echo "$PENDING_CASE_STUDIES" | jq -r '.[] | "  #\(.number): \(.title)"'
  echo ""
fi

if [ $PENDING_RA_COUNT -gt 0 ]; then
  echo "Reference Architecture Requests:"
  echo "$PENDING_REF_ARCHS" | jq -r '.[] | "  #\(.number): \(.title)"'
  echo ""
fi

if [ $PENDING_PP_COUNT -gt 0 ]; then
  echo "Presenter Profile Requests:"
  echo "$PENDING_PRESENTERS" | jq -r '.[] | "  #\(.number): \(.title)"'
  echo ""
fi
```

**Filter logic:**
- Exclude issues with label `*-generated` (already completed)
- Exclude issues with label `in-progress` (currently being processed)
- Exclude issues with any `validation-failed-*` label (already failed validation)

---

### Step 4: Determine Processing Strategy

**Objective:** Decide whether to process issues sequentially or in parallel.

```bash
# Check if parallel processing is requested (environment variable)
PARALLEL_PROCESSING=${PARALLEL_PROCESSING:-false}

if [ "$PARALLEL_PROCESSING" = "true" ]; then
  echo "🚀 Strategy: PARALLEL processing"
  STRATEGY="parallel"
else
  echo "📝 Strategy: SEQUENTIAL processing (default)"
  STRATEGY="sequential"
fi

# For initial implementation, always use sequential
if [ "$STRATEGY" = "parallel" ]; then
  echo "⚠️ Warning: Parallel processing not yet implemented, falling back to sequential"
  STRATEGY="sequential"
fi

echo ""
```

**Processing strategies:**
- **Sequential** (default): Process issues one at a time, safer, easier to debug
- **Parallel** (future): Process multiple issues concurrently, faster but more complex

---

### Step 5: Process Each Issue with LLM Subagent

**Objective:** For each pending issue, spawn an LLM subagent that executes the appropriate specialized agent workflow.

**Processing Pattern (Silent Mode):**

For each issue:
1. Parse issue data
2. Mark as in-progress
3. Spawn LLM subagent with specialized agent instructions
4. Subagent executes complete workflow silently
5. Subagent posts results (PR link or error) to issue on completion
6. Remove in-progress label, add result label
7. Log outcome

**Code:**

```bash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 PROCESSING CONTENT GENERATION REQUESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Initialize counters
PROCESSED_COUNT=0
SUCCESS_COUNT=0
ERROR_COUNT=0

# Process Case Studies
if [ $PENDING_CS_COUNT -gt 0 ]; then
  echo "━━━ CASE STUDIES ━━━"
  echo ""
  
  CASE_STUDY_NUMBERS=$(jq -r '.[] | .number' pending_case_studies.json)
  
  for ISSUE_NUMBER in $CASE_STUDY_NUMBERS; do
    echo "📄 Processing Case Study #$ISSUE_NUMBER"
    
    # Parse issue data
    echo "   → Parsing issue data..."
    python -m casestudypilot parse-issue "$ISSUE_NUMBER" --output "issue_${ISSUE_NUMBER}.json"
    
    if [ $? -ne 0 ]; then
      echo "   ✗ Failed to parse issue"
      gh issue comment "$ISSUE_NUMBER" --body "❌ **Processing Failed**

Failed to extract required data from issue.

**Action Required:**
Please ensure the issue contains:
- A valid YouTube URL (https://www.youtube.com/watch?v=...)
- Proper labels (case-study)

Then retry by telling an agent: 'ingest incoming requests'"
      
      echo "case-study #$ISSUE_NUMBER (parse-failed)" >> processing_errors.log
      ERROR_COUNT=$((ERROR_COUNT + 1))
      continue
    fi
    
    # Mark as in-progress
    gh issue edit "$ISSUE_NUMBER" --add-label "in-progress"
    
    # Load issue data
    ISSUE_DATA=$(cat "issue_${ISSUE_NUMBER}.json")
    VIDEO_URL=$(echo "$ISSUE_DATA" | jq -r '.video_url')
    COMPANY=$(echo "$ISSUE_DATA" | jq -r '.company_name // "Not specified"')
    
    echo "   → Video: $VIDEO_URL"
    echo "   → Company: $COMPANY"
    echo "   → Spawning case-study-agent subagent..."
    
    # Read case-study-agent instructions
    AGENT_INSTRUCTIONS=$(cat .github/agents/case-study-agent.md)
    
    # Spawn subagent via Task tool
    # NOTE: This uses OpenCode Task tool to spawn a fresh LLM agent
    # The subagent will execute the complete case-study workflow
    
    echo "   → Delegating to case-study-agent subagent (this may take 10-15 minutes)..."
    
    # Construct subagent prompt
    SUBAGENT_PROMPT="You are the case-study-agent.

Process GitHub issue #${ISSUE_NUMBER} with the following data:
- Video URL: ${VIDEO_URL}
- Company: ${COMPANY}
- Content Type: case-study

${AGENT_INSTRUCTIONS}

IMPORTANT EXECUTION NOTES:
1. Execute the complete workflow from Step 0 through Step 14
2. Run all CLI commands and invoke all required skills
3. Execute SILENTLY - do NOT post progress updates to the issue during execution
4. ONLY post to the issue when:
   - COMPLETE: Post PR link and success message, add 'case-study-generated' label, remove 'in-progress' label
   - FAILED: Post error template (from agent instructions), add appropriate 'validation-failed-*' label, remove 'in-progress' label
5. At validation checkpoints, check exit codes and stop on code 2 (critical)
6. Create atomic commit: 1 markdown file + 3 screenshot images
7. Create PR and link it in the issue comment

After completion, report back to me with:
- RESULT: success | failure
- If success: PR URL
- If failure: Which validation checkpoint failed"

    # Use Task tool to spawn subagent
    # (This is executed by the orchestrator LLM agent, not via CLI)
    # Task(
    #   prompt=SUBAGENT_PROMPT,
    #   subagent_type="general",
    #   description="Execute case-study-agent for issue $ISSUE_NUMBER"
    # )
    
    # TEMPORARY: For manual testing, output the prompt
    echo "$SUBAGENT_PROMPT" > "subagent_prompt_${ISSUE_NUMBER}.txt"
    echo "   ⚠️  Subagent prompt saved to: subagent_prompt_${ISSUE_NUMBER}.txt"
    echo "   ⚠️  Use Task tool to spawn subagent with this prompt"
    
    # Record processing attempt
    echo "case-study #$ISSUE_NUMBER (delegated)" >> processing_log.txt
    PROCESSED_COUNT=$((PROCESSED_COUNT + 1))
    
    echo ""
  done
fi

# Process Reference Architectures
if [ $PENDING_RA_COUNT -gt 0 ]; then
  echo "━━━ REFERENCE ARCHITECTURES ━━━"
  echo ""
  
  REF_ARCH_NUMBERS=$(jq -r '.[] | .number' pending_ref_archs.json)
  
  for ISSUE_NUMBER in $REF_ARCH_NUMBERS; do
    echo "🏗️  Processing Reference Architecture #$ISSUE_NUMBER"
    
    # Parse issue data
    echo "   → Parsing issue data..."
    python -m casestudypilot parse-issue "$ISSUE_NUMBER" --output "issue_${ISSUE_NUMBER}.json"
    
    if [ $? -ne 0 ]; then
      echo "   ✗ Failed to parse issue"
      gh issue comment "$ISSUE_NUMBER" --body "❌ **Processing Failed**

Failed to extract required data from issue.

**Action Required:**
Please ensure the issue contains:
- A valid YouTube URL (https://www.youtube.com/watch?v=...)
- Proper labels (reference-architecture)

Then retry by telling an agent: 'ingest incoming requests'"
      
      echo "reference-architecture #$ISSUE_NUMBER (parse-failed)" >> processing_errors.log
      ERROR_COUNT=$((ERROR_COUNT + 1))
      continue
    fi
    
    # Mark as in-progress
    gh issue edit "$ISSUE_NUMBER" --add-label "in-progress"
    
    # Load issue data
    ISSUE_DATA=$(cat "issue_${ISSUE_NUMBER}.json")
    VIDEO_URL=$(echo "$ISSUE_DATA" | jq -r '.video_url')
    COMPANY=$(echo "$ISSUE_DATA" | jq -r '.company_name // "Not specified"')
    
    echo "   → Video: $VIDEO_URL"
    echo "   → Company: $COMPANY"
    echo "   → Spawning reference-architecture-agent subagent..."
    
    # Read reference-architecture-agent instructions
    AGENT_INSTRUCTIONS=$(cat .github/agents/reference-architecture-agent.md)
    
    echo "   → Delegating to reference-architecture-agent subagent (this may take 20-25 minutes)..."
    
    # Construct subagent prompt
    SUBAGENT_PROMPT="You are the reference-architecture-agent.

Process GitHub issue #${ISSUE_NUMBER} with the following data:
- Video URL: ${VIDEO_URL}
- Company: ${COMPANY}
- Content Type: reference-architecture

${AGENT_INSTRUCTIONS}

IMPORTANT EXECUTION NOTES:
1. Execute the complete workflow from Step 0 through Step 18
2. Run all CLI commands and invoke all required skills
3. Execute SILENTLY - do NOT post progress updates to the issue during execution
4. ONLY post to the issue when:
   - COMPLETE: Post PR link with TAB submission guide, add 'reference-architecture-generated' label, remove 'in-progress' label
   - FAILED: Post error template (from agent instructions), add appropriate 'validation-failed-*' label, remove 'in-progress' label
5. At validation checkpoints, check exit codes and stop on code 2 (critical)
6. Create atomic commit: 1 markdown file + 6+ screenshot images
7. Create PR with TAB submission instructions and link it in the issue comment

After completion, report back to me with:
- RESULT: success | failure
- If success: PR URL
- If failure: Which validation checkpoint failed"

    # Use Task tool to spawn subagent
    echo "$SUBAGENT_PROMPT" > "subagent_prompt_${ISSUE_NUMBER}.txt"
    echo "   ⚠️  Subagent prompt saved to: subagent_prompt_${ISSUE_NUMBER}.txt"
    echo "   ⚠️  Use Task tool to spawn subagent with this prompt"
    
    # Record processing attempt
    echo "reference-architecture #$ISSUE_NUMBER (delegated)" >> processing_log.txt
    PROCESSED_COUNT=$((PROCESSED_COUNT + 1))
    
    echo ""
  done
fi

# Process Presenter Profiles
if [ $PENDING_PP_COUNT -gt 0 ]; then
  echo "━━━ PRESENTER PROFILES ━━━"
  echo ""
  
  PRESENTER_NUMBERS=$(jq -r '.[] | .number' pending_presenters.json)
  
  for ISSUE_NUMBER in $PRESENTER_NUMBERS; do
    echo "👤 Processing Presenter Profile #$ISSUE_NUMBER"
    
    # Mark issue as in-progress
    gh issue edit "$ISSUE_NUMBER" --add-label "in-progress"
    
    # Post comment about agent not ready
    gh issue comment "$ISSUE_NUMBER" --body "🤖 **Content Orchestrator**

Your presenter profile generation request has been identified.

**Status:** ⚠️ Agent not yet implemented
**Agent:** people-agent (in development, epic #17)
**Content type:** Presenter Profile (biography, talk aggregation, fun stats)

**Action Required:**
The people-agent is currently in development. Please check epic #17 for implementation status.

Once the agent is complete, your request will be processed automatically."
    
    # Record as error (agent not implemented)
    echo "presenter-profile #$ISSUE_NUMBER (agent not implemented)" >> processing_errors.log
    ERROR_COUNT=$((ERROR_COUNT + 1))
    
    # Remove in-progress label
    gh issue edit "$ISSUE_NUMBER" --remove-label "in-progress"
    
    # Add waiting label
    gh issue edit "$ISSUE_NUMBER" --add-label "waiting-for-agent-implementation"
    
    echo "   ⚠️ Agent not yet implemented (epic #17)"
    echo ""
  done
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

**Key changes from v1.0.0:**
- Parses issue data using new `parse-issue` CLI command
- Spawns LLM subagent via Task tool (not manual invocation)
- Subagent executes complete workflow silently
- Subagent handles all issue updates (PR link or error)
- Orchestrator only manages labels and logs results

---

### Step 6: Aggregate Results

**Objective:** Collect results from subagent executions and report summary.

**Note:** In v2.0.0, subagents execute asynchronously via Task tool. The orchestrator tracks which issues were delegated, but actual success/failure is determined by the subagent posting to the issue and updating labels.

```bash
echo ""
echo "📊 PROCESSING SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Count by content type
echo "Issues Delegated to Subagents:"
echo "  📄 Case Studies:              $PENDING_CS_COUNT"
echo "  🏗️  Reference Architectures:   $PENDING_RA_COUNT"
echo "  👤 Presenter Profiles:         $PENDING_PP_COUNT (agent not implemented)"
echo ""

# Overall totals
echo "Overall:"
echo "  Total discovered:             $TOTAL_COUNT"
echo "  Total pending:                $PENDING_TOTAL"
echo "  Total delegated to subagents: $PROCESSED_COUNT"
echo "  Total errors (parse failures): $ERROR_COUNT"
echo ""

# Show errors if any
if [ -f processing_errors.log ]; then
  echo "⚠️ Issues with errors:"
  cat processing_errors.log | sed 's/^/  /'
  echo ""
fi

# Agent implementation status
echo "Agent Status:"
echo "  ✅ case-study-agent (v2.2.0):              Ready"
echo "  ✅ reference-architecture-agent (v1.0.0):  Ready"
echo "  ⚠️ people-agent:                            Not yet implemented (epic #17)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "ℹ️  Subagents are processing issues asynchronously."
echo "ℹ️  Check GitHub issues for completion status and PR links."
echo "ℹ️  Case studies take ~10-15 minutes, reference architectures ~20-25 minutes."
```

---

### Step 7: Generate Orchestrator Report (Optional)

**Objective:** Create a summary report for logging/monitoring.

```bash
# Generate timestamped report
REPORT_FILE="orchestrator-report-$(date +%Y%m%d-%H%M%S).json"

jq -n \
  --argjson total_discovered "$TOTAL_COUNT" \
  --argjson total_pending "$PENDING_TOTAL" \
  --argjson total_processed "$PROCESSED_COUNT" \
  --argjson total_errors "$ERROR_COUNT" \
  --argjson case_studies "$PENDING_CS_COUNT" \
  --argjson ref_archs "$PENDING_RA_COUNT" \
  --argjson presenters "$PENDING_PP_COUNT" \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{
    timestamp: $timestamp,
    version: "1.0.0",
    summary: {
      total_discovered: $total_discovered,
      total_pending: $total_pending,
      total_processed: $total_processed,
      total_errors: $total_errors
    },
    by_content_type: {
      case_studies: $case_studies,
      reference_architectures: $ref_archs,
      presenter_profiles: $presenters
    },
    agent_status: {
      case_study_agent: "ready-manual",
      reference_architecture_agent: "ready-manual",
      people_agent: "not-implemented"
    }
  }' > "$REPORT_FILE"

echo "📄 Report saved: $REPORT_FILE"
```

---

### Step 8: Cleanup

**Objective:** Clean up temporary files.

```bash
rm -f discovered_case_studies.json discovered_ref_archs.json discovered_presenters.json
rm -f pending_case_studies.json pending_ref_archs.json pending_presenters.json
rm -f processed_issues.log processing_errors.log

echo "✅ Orchestrator workflow complete"
```

---

## Content Type Routing

### Routing Logic

The orchestrator routes issues to specialized agents based on labels:

```
Issue Label              → Agent                           → Output
──────────────────────────────────────────────────────────────────────
case-study              → case-study-agent v2.2.0         → case-studies/company.md
reference-architecture  → reference-architecture-agent    → reference-architectures/company.md
presenter-profile       → people-agent (not implemented)  → people/username.md
```

### Content Type Specifications

| Content Type | Sections | Word Count | Screenshots | CNCF Projects | Target Audience |
|--------------|----------|------------|-------------|---------------|-----------------|
| Case Study | 5 | 500-1500 | 3 | 2+ | Business leaders |
| Reference Architecture | 13 | 2000-5000 | 6+ | 5+ | Engineers, architects |
| Presenter Profile | 8 | 1000-2000 | 0 | N/A | Community members |

---

## Integration with Specialized Agents

### Architecture (v1.0.0 - Manual Invocation)

```
┌─────────────────────────────────────────┐
│ content-orchestrator                     │
│ - Discovers issues (3 types)             │
│ - Filters processed issues               │
│ - Routes by content type                 │
│ - Marks issues for processing            │
│ - Posts notifications                    │
└─────────────────┬───────────────────────┘
                  │
                  ├────────────────────────┬─────────────────────────┐
                  │ (Manual)               │ (Manual)                │ (Not ready)
                  ↓                        ↓                         ↓
┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│ case-study-agent         │  │ reference-architecture-  │  │ people-agent             │
│ v2.2.0                   │  │ agent v1.0.0             │  │ (epic #17)               │
│ - 14 steps               │  │ - 18 steps               │  │ - 16 steps (planned)     │
│ - 5 checkpoints          │  │ - 7 checkpoints          │  │ - 5 checkpoints          │
│ - 10 min processing      │  │ - 20 min processing      │  │ - TBD                    │
└──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘
```
---

## Usage

### Manual Invocation

```bash
# Run orchestrator to discover and prepare issues
bash .github/agents/content-orchestrator.sh

# Then manually process each discovered issue with appropriate agent
bash .github/agents/case-study-agent.sh 42
bash .github/agents/reference-architecture-agent.sh 43
# people-agent not yet ready
```

### Scheduled Execution (Future)

```yaml
# .github/workflows/orchestrator-schedule.yml
name: Content Orchestrator

on:
  schedule:
    - cron: "0 */6 * * *"  # Every 6 hours
  workflow_dispatch:       # Manual trigger

jobs:
  orchestrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run orchestrator
        run: bash .github/agents/content-orchestrator.sh
```

---

## Error Handling

### No Issues Found

```
ℹ️ No open content generation requests found
```

**Action:** None needed, orchestrator exits cleanly.

---

### All Issues Already Processed

```
ℹ️ All discovered issues are already processed or in-progress
```

**Action:** None needed, orchestrator exits cleanly.

---

### Agent Not Implemented

```
⚠️ Agent not yet implemented (epic #17)
```

**Action:** Wait for agent implementation, issue labeled `waiting-for-agent-implementation`.

---

### GitHub CLI Authentication Failed

```
❌ Error: gh CLI not authenticated
```

**Action:** Run `gh auth login` and retry.

---

## Label Conventions

The orchestrator relies on these labels to track issue state:

| Label | Meaning | Applied By |
|-------|---------|------------|
| `case-study` | Case study request | User (via issue template) |
| `reference-architecture` | Reference architecture request | User (via issue template) |
| `presenter-profile` | Presenter profile request | User (via issue template) |
| `in-progress` | Currently processing | Orchestrator or specialized agent |
| `case-study-generated` | Case study completed | case-study-agent |
| `reference-architecture-generated` | Reference architecture completed | reference-architecture-agent |
| `presenter-profile-generated` | Presenter profile completed | people-agent (future) |
| `validation-failed-*` | Failed validation checkpoint | Specialized agents |
| `waiting-for-agent-implementation` | Agent not ready | Orchestrator |

**Label lifecycle (example for case study):**

```
[case-study]
        ↓
    (orchestrator discovers)
        ↓
[case-study, in-progress]
        ↓
    (case-study-agent processes)
        ↓
[case-study, case-study-generated]  ← SUCCESS
        OR
[case-study, validation-failed-*]   ← FAILURE
```

---

## Quality Standards

### Orchestrator Responsibility

The orchestrator is responsible for:
- ✅ Discovering all open content generation requests across all types
- ✅ Filtering out already-processed issues
- ✅ Preventing duplicate processing (via `in-progress` label)
- ✅ Routing to appropriate specialized agent
- ✅ Posting status updates to issues
- ✅ Aggregating results across multiple issues and content types

### NOT Orchestrator Responsibility

The orchestrator does NOT:
- ❌ Validate video quality (handled by specialized agents)
- ❌ Generate content (handled by specialized agents)
- ❌ Create PRs (handled by specialized agents)
- ❌ Handle validation checkpoints (handled by specialized agents)

---

## Environment Requirements

### Required Tools

- `gh` CLI (GitHub CLI) with authentication
- `jq` (JSON processing)
- `bash` 4.0+ (for script execution)
- Python 3.8+ with casestudypilot installed

### Required Permissions

- Read access to repository issues
- Write access to issue labels and comments
- Ability to invoke workflows (for future automation)

---

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PARALLEL_PROCESSING` | `false` | Enable parallel issue processing (not yet implemented) |
| `MAX_CONCURRENT_ISSUES` | `3` | Maximum parallel issues (for future use) |
| `ISSUE_LIMIT` | `100` | Maximum issues to fetch per content type in one run |

**Example:**

```bash
# Enable parallel processing (future)
PARALLEL_PROCESSING=true bash content-orchestrator.sh

# Limit to 10 issues per content type per run
ISSUE_LIMIT=10 bash content-orchestrator.sh
```

---

## Version History

- **v2.0.0** (February 2026) - Automated subagent dispatch
  - Added issue parser integration (`parse-issue` CLI command)
  - Automated LLM subagent spawning via Task tool
  - Silent execution mode (no progress updates during processing)
  - Subagents post results directly to issues
  - Simplified orchestrator logic (delegate and monitor)
  
- **v1.0.0** (February 2026) - Initial release
  - Multi-content-type discovery (case studies, reference architectures, presenter profiles)
  - Filtering and routing logic
  - Sequential processing strategy
  - Manual invocation of specialized agents
  - Status tracking via labels
  - Basic error handling
  - Support for people-agent (queued until agent is implemented)

---

## Related Documentation

- **Specialized Agents:**
  - `.github/agents/case-study-agent.md` (v2.2.0)
  - `.github/agents/reference-architecture-agent.md` (v1.0.0)
  - `.github/agents/people-agent.md` (not yet implemented, epic #17)
- **Issue Templates:**
  - `.github/ISSUE_TEMPLATE/generate-case-study.yml`
  - `.github/ISSUE_TEMPLATE/generate-reference-architecture.yml`
  - `.github/ISSUE_TEMPLATE/presenter-profile-request.yml` (not yet created)
- **Framework Documentation:**
  - `AGENTS.md` - Agent development guide
  - `README.md` - Project overview

---

**Framework Status:** ✅ Ready for Manual Testing  
**Automation Status:** ⚠️ Manual invocation required for case-study and reference-architecture agents (v1.0.0)  
**People Agent Status:** ⚠️ Not yet implemented (epic #17)  
**Last Updated:** February 10, 2026
