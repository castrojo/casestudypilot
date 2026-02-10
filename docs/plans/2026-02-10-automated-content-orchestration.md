# Automated Content Orchestration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Epic Issue:** #27

**Goal:** Enable users to tell an agent "ingest incoming requests" and have the system automatically discover, parse, route, and process case study and reference architecture requests from GitHub issues, delegating execution to specialized LLM agents.

**Architecture:** Three-layer system: (1) Issue parser CLI tool extracts YouTube URLs and metadata from GitHub issues, (2) Enhanced content-orchestrator agent discovers issues and spawns specialized LLM subagents via Task tool, (3) Specialized agents (case-study-agent, reference-architecture-agent) execute complete workflows silently and post results.

**Tech Stack:** Python (Typer, Rich), GitHub CLI (gh), OpenCode Task tool for subagent dispatch, existing casestudypilot CLI tools and skills

---

## Task 1: Issue Parser CLI Tool

**Goal:** Create `python -m casestudypilot parse-issue <issue_number>` command that extracts YouTube URLs and metadata from GitHub issues.

**Files:**
- Create: `casestudypilot/tools/issue_parser.py`
- Modify: `casestudypilot/__main__.py`
- Test: `tests/test_issue_parser.py`

### Step 1: Write failing test for basic issue parsing

**File:** `tests/test_issue_parser.py`

```python
"""Tests for GitHub issue parser."""

import json
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from casestudypilot.tools.issue_parser import parse_issue, extract_youtube_url


def test_extract_youtube_url_standard_format():
    """Test extracting standard YouTube URL."""
    body = """
    Please generate a case study for this video:
    https://www.youtube.com/watch?v=dQw4w9WgXcQ
    """
    url = extract_youtube_url(body)
    assert url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_extract_youtube_url_short_format():
    """Test extracting short YouTube URL."""
    body = "Check out https://youtu.be/dQw4w9WgXcQ for more info"
    url = extract_youtube_url(body)
    assert url == "https://youtu.be/dQw4w9WgXcQ"


def test_extract_youtube_url_not_found():
    """Test when no YouTube URL present."""
    body = "This is an issue without a YouTube link"
    url = extract_youtube_url(body)
    assert url is None


@patch('casestudypilot.tools.issue_parser.subprocess.run')
def test_parse_issue_case_study(mock_run):
    """Test parsing a case study issue."""
    # Mock gh CLI response
    mock_run.return_value = Mock(
        returncode=0,
        stdout=json.dumps({
            "number": 42,
            "title": "Generate case study for Intuit",
            "body": "YouTube URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ\n\nCompany: Intuit",
            "labels": [{"name": "case-study"}]
        })
    )
    
    result = parse_issue(42)
    
    assert result["issue_number"] == 42
    assert result["content_type"] == "case-study"
    assert result["video_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert result["company_name"] == "Intuit"


@patch('casestudypilot.tools.issue_parser.subprocess.run')
def test_parse_issue_reference_architecture(mock_run):
    """Test parsing a reference architecture issue."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout=json.dumps({
            "number": 43,
            "title": "Generate reference architecture for CERN",
            "body": "https://www.youtube.com/watch?v=xyz123abc",
            "labels": [{"name": "reference-architecture"}]
        })
    )
    
    result = parse_issue(43)
    
    assert result["issue_number"] == 43
    assert result["content_type"] == "reference-architecture"
    assert result["video_url"] == "https://www.youtube.com/watch?v=xyz123abc"


@patch('casestudypilot.tools.issue_parser.subprocess.run')
def test_parse_issue_no_url(mock_run):
    """Test parsing issue without YouTube URL."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout=json.dumps({
            "number": 44,
            "title": "Missing URL",
            "body": "No video link here",
            "labels": [{"name": "case-study"}]
        })
    )
    
    with pytest.raises(ValueError, match="No YouTube URL found"):
        parse_issue(44)


@patch('casestudypilot.tools.issue_parser.subprocess.run')
def test_parse_issue_gh_cli_error(mock_run):
    """Test handling gh CLI errors."""
    mock_run.return_value = Mock(returncode=1, stderr="Issue not found")
    
    with pytest.raises(RuntimeError, match="Failed to fetch issue"):
        parse_issue(999)
```

### Step 2: Run test to verify it fails

```bash
pytest tests/test_issue_parser.py -v
```

**Expected:** FAIL with "ModuleNotFoundError: No module named 'casestudypilot.tools.issue_parser'"

### Step 3: Implement issue parser module

**File:** `casestudypilot/tools/issue_parser.py`

```python
"""GitHub issue parser for extracting content generation metadata."""

import json
import re
import subprocess
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def extract_youtube_url(text: str) -> Optional[str]:
    """Extract YouTube URL from text.
    
    Args:
        text: Text containing potential YouTube URL
        
    Returns:
        YouTube URL if found, None otherwise
    """
    # Pattern matches:
    # - https://www.youtube.com/watch?v=VIDEO_ID
    # - https://youtu.be/VIDEO_ID
    # - http variants
    patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'https?://youtu\.be/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            # Reconstruct full URL from video ID
            video_id = match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}"
    
    return None


def extract_company_name(text: str) -> Optional[str]:
    """Extract company name from issue body.
    
    Looks for patterns like:
    - Company: Name
    - Company Name: Name
    - Company Name (Optional): Name
    
    Args:
        text: Issue body text
        
    Returns:
        Company name if found, None otherwise
    """
    patterns = [
        r'Company(?:\s+Name)?(?:\s+\(Optional\))?:\s*(.+)',
        r'company(?:\s+name)?(?:\s+\(optional\))?:\s*(.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            company = match.group(1).strip()
            # Ignore common placeholder values
            if company.lower() not in ['', 'n/a', 'none', 'unknown']:
                return company
    
    return None


def detect_content_type(labels: list) -> str:
    """Detect content type from issue labels.
    
    Args:
        labels: List of label dicts with "name" field
        
    Returns:
        Content type: "case-study", "reference-architecture", or "presenter-profile"
        
    Raises:
        ValueError: If no recognized content type label found
    """
    label_names = [label.get("name", "") for label in labels]
    
    if "case-study" in label_names:
        return "case-study"
    elif "reference-architecture" in label_names:
        return "reference-architecture"
    elif "presenter-profile" in label_names:
        return "presenter-profile"
    else:
        raise ValueError(
            f"No recognized content type label found. "
            f"Expected: case-study, reference-architecture, or presenter-profile. "
            f"Found: {label_names}"
        )


def parse_issue(issue_number: int) -> Dict[str, Any]:
    """Parse GitHub issue and extract content generation metadata.
    
    Args:
        issue_number: GitHub issue number
        
    Returns:
        Dict with extracted metadata:
        {
            "issue_number": int,
            "content_type": str,
            "video_url": str,
            "company_name": str | None,
            "title": str,
            "labels": list
        }
        
    Raises:
        RuntimeError: If gh CLI fails
        ValueError: If required data missing (URL, content type)
    """
    logger.info(f"Parsing issue #{issue_number}")
    
    # Fetch issue data via gh CLI
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number), "--json", "number,title,body,labels"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        error_msg = f"Failed to fetch issue #{issue_number}: {result.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    try:
        issue_data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse gh CLI output: {e}")
    
    # Extract fields
    body = issue_data.get("body", "")
    title = issue_data.get("title", "")
    labels = issue_data.get("labels", [])
    
    # Extract YouTube URL (required)
    video_url = extract_youtube_url(body)
    if not video_url:
        raise ValueError(
            f"No YouTube URL found in issue #{issue_number}. "
            f"Please provide a YouTube URL in the issue body."
        )
    
    # Detect content type from labels (required)
    content_type = detect_content_type(labels)
    
    # Extract optional company name
    company_name = extract_company_name(body)
    
    result = {
        "issue_number": issue_number,
        "content_type": content_type,
        "video_url": video_url,
        "company_name": company_name,
        "title": title,
        "labels": [label.get("name") for label in labels]
    }
    
    logger.info(f"Successfully parsed issue #{issue_number}")
    logger.info(f"  Content type: {content_type}")
    logger.info(f"  Video URL: {video_url}")
    logger.info(f"  Company: {company_name or 'Not specified'}")
    
    return result
```

### Step 4: Run tests to verify they pass

```bash
pytest tests/test_issue_parser.py -v
```

**Expected:** All tests PASS

### Step 5: Add CLI command for parse-issue

**File:** `casestudypilot/__main__.py`

Add import at top:
```python
from casestudypilot.tools.issue_parser import parse_issue
```

Add command before `def main()`:
```python
@app.command(name="parse-issue")
def parse_issue_cmd(
    issue_number: int = typer.Argument(..., help="GitHub issue number"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSON file path"),
):
    """Parse GitHub issue and extract content generation metadata.
    
    Extracts YouTube URL, content type, company name, and other metadata
    from GitHub issues created via content generation templates.
    
    Example:
        python -m casestudypilot parse-issue 42
        python -m casestudypilot parse-issue 42 --output issue_data.json
    """
    try:
        console.print(f"[cyan]Parsing issue:[/cyan] #{issue_number}")
        result = parse_issue(issue_number)
        
        # Write to file if specified
        if output:
            with open(output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            console.print(f"[green]✓ Issue data saved to:[/green] {output}")
        
        # Display result
        console.print(f"\n[bold]Issue #{result['issue_number']}[/bold]")
        console.print(f"[dim]Title:[/dim] {result['title']}")
        console.print(f"[dim]Content Type:[/dim] {result['content_type']}")
        console.print(f"[dim]Video URL:[/dim] {result['video_url']}")
        
        if result.get('company_name'):
            console.print(f"[dim]Company:[/dim] {result['company_name']}")
        else:
            console.print(f"[dim]Company:[/dim] [yellow]Not specified (will extract from video)[/yellow]")
        
        # Output JSON to stdout if no file specified
        if not output:
            console.print(f"\n[dim]JSON output:[/dim]")
            console.print(json.dumps(result, indent=2))
        
    except ValueError as e:
        console.print(f"[red]Validation Error:[/red] {e}")
        sys.exit(2)
    except RuntimeError as e:
        console.print(f"[red]Runtime Error:[/red] {e}")
        sys.exit(2)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)
```

### Step 6: Test CLI command manually

```bash
# Create a test issue first (or use existing one)
# Then test parsing
python -m casestudypilot parse-issue 42

# Test with output file
python -m casestudypilot parse-issue 42 --output /tmp/issue_data.json
cat /tmp/issue_data.json
```

**Expected:** Command outputs parsed issue data in JSON format

### Step 7: Commit Task 1

```bash
git add casestudypilot/tools/issue_parser.py
git add casestudypilot/__main__.py
git add tests/test_issue_parser.py
git commit -m "feat: add issue parser CLI tool for extracting YouTube URLs and metadata

- Create parse_issue() function to extract content generation metadata
- Support both standard and short YouTube URL formats
- Extract optional company name from issue body
- Detect content type from labels (case-study, reference-architecture)
- Add parse-issue CLI command with JSON output
- Add comprehensive test coverage"
```

---

## Task 2: Enhanced Content Orchestrator Agent

**Goal:** Update content-orchestrator agent to automatically spawn LLM subagents for processing issues.

**Files:**
- Modify: `.github/agents/content-orchestrator.md`

### Step 1: Update orchestrator to version 2.0.0

**File:** `.github/agents/content-orchestrator.md`

Update header:
```markdown
---
name: content-orchestrator
description: Discover and automatically process content generation requests by spawning specialized LLM agents
version: 2.0.0
trigger: Manual invocation via "ingest incoming requests" or `python -m casestudypilot orchestrate`
---
```

### Step 2: Replace Step 5 with automated subagent execution

**File:** `.github/agents/content-orchestrator.md`

Replace the entire "Step 5: Process Issues by Content Type" section with:

```markdown
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
```

### Step 3: Update Step 6 with simplified result aggregation

**File:** `.github/agents/content-orchestrator.md`

Replace "Step 6: Aggregate Results" section with:

```markdown
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
```

### Step 4: Update orchestrator overview and version history

**File:** `.github/agents/content-orchestrator.md`

Update the "Overview" section:

```markdown
## Overview

This agent serves as the **universal dispatcher/orchestrator** for all casestudypilot content generation requests. It:

1. **Discovers** open issues labeled with content type labels
2. **Validates** that issues are not already being processed
3. **Parses** issue data (YouTube URL, company name, content type)
4. **Spawns** LLM subagents via Task tool to execute specialized workflows
5. **Monitors** completion via issue labels and comments (posted by subagents)

**Execution Model (v2.0.0):** The orchestrator delegates execution to specialized LLM agents (case-study-agent, reference-architecture-agent) via OpenCode Task tool. Subagents execute workflows silently and post results to issues on completion.
```

Update the "Version History" section:

```markdown
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
```

### Step 5: Test updated orchestrator agent manually

```bash
# Read the updated orchestrator agent
cat .github/agents/content-orchestrator.md

# Verify it follows the new structure:
# - Version 2.0.0
# - Uses parse-issue CLI command
# - Spawns subagents via Task tool
# - Silent execution mode
```

**Expected:** Agent instructions are clear and complete

### Step 6: Commit Task 2

```bash
git add .github/agents/content-orchestrator.md
git commit -m "feat: update content-orchestrator to v2.0.0 with automated subagent dispatch

Breaking changes:
- Orchestrator now automatically spawns LLM subagents via Task tool
- Subagents execute workflows silently (no progress updates)
- Subagents post results directly to issues
- Uses new parse-issue CLI command for data extraction

New features:
- Automated issue parsing and data extraction
- LLM subagent spawning for case-study and reference-architecture agents
- Silent execution mode (no issue updates until completion)
- Simplified orchestrator logic (delegate and monitor)"
```

---

## Task 3: Orchestrate CLI Command

**Goal:** Create `python -m casestudypilot orchestrate` command that spawns the orchestrator agent.

**Files:**
- Modify: `casestudypilot/__main__.py`

### Step 1: Add orchestrate CLI command

**File:** `casestudypilot/__main__.py`

Add this command before `def main()`:

```python
@app.command(name="orchestrate")
def orchestrate_cmd():
    """Discover and process pending content generation requests.
    
    This command is designed to be executed by an LLM agent. It loads the
    content-orchestrator agent instructions and delegates execution.
    
    The orchestrator will:
    1. Discover open issues (case-study, reference-architecture, presenter-profile)
    2. Parse issue data to extract YouTube URLs and metadata
    3. Spawn specialized LLM agents to process each issue
    4. Monitor completion and post results to issues
    
    Usage (in OpenCode or similar LLM environment):
        Tell the agent: "ingest incoming requests"
        
        OR manually:
        python -m casestudypilot orchestrate
        
    Processing time:
    - Case studies: ~10-15 minutes per issue
    - Reference architectures: ~20-25 minutes per issue
    
    The orchestrator executes workflows silently. Check GitHub issues for
    completion status and PR links.
    """
    try:
        console.print("[cyan bold]Content Orchestrator v2.0.0[/cyan bold]")
        console.print("")
        
        # Check prerequisites
        console.print("[cyan]Checking prerequisites...[/cyan]")
        
        # Check gh CLI
        result = subprocess.run(["gh", "auth", "status"], capture_output=True)
        if result.returncode != 0:
            console.print("[red]✗ gh CLI not authenticated[/red]")
            console.print("[yellow]Run: gh auth login[/yellow]")
            sys.exit(2)
        console.print("[green]✓ gh CLI authenticated[/green]")
        
        # Check agent workflow file exists
        agent_file = Path(".github/agents/content-orchestrator.md")
        if not agent_file.exists():
            console.print(f"[red]✗ Agent workflow not found: {agent_file}[/red]")
            sys.exit(2)
        console.print(f"[green]✓ Agent workflow found[/green]")
        
        # Load agent instructions
        with open(agent_file, "r", encoding="utf-8") as f:
            agent_instructions = f.read()
        
        console.print("")
        console.print("[cyan bold]Orchestrator Instructions Loaded[/cyan bold]")
        console.print("")
        console.print("[yellow]EXECUTION MODE: This command is designed for LLM agent execution.[/yellow]")
        console.print("")
        console.print("The content-orchestrator agent will:")
        console.print("  1. Discover open GitHub issues (case-study, reference-architecture)")
        console.print("  2. Parse issue data and extract YouTube URLs")
        console.print("  3. Spawn specialized LLM agents for each issue")
        console.print("  4. Monitor completion and post results")
        console.print("")
        console.print("[dim]Agent workflow: .github/agents/content-orchestrator.md[/dim]")
        console.print("[dim]Version: 2.0.0[/dim]")
        console.print("")
        
        # In OpenCode environment, this would spawn the orchestrator agent
        # For now, provide instructions
        console.print("[cyan bold]To Execute:[/cyan bold]")
        console.print("")
        console.print("In an LLM agent environment (OpenCode, etc.):")
        console.print('  Tell the agent: "ingest incoming requests"')
        console.print("")
        console.print("The agent will read the orchestrator instructions from:")
        console.print(f"  {agent_file.absolute()}")
        console.print("")
        console.print("And execute the complete workflow autonomously.")
        console.print("")
        
        # Output agent instructions for debugging
        console.print("[dim]═══════════════════════════════════════════════════════════[/dim]")
        console.print("[dim]Agent Instructions Preview (first 500 chars):[/dim]")
        console.print("[dim]═══════════════════════════════════════════════════════════[/dim]")
        console.print("")
        console.print(agent_instructions[:500] + "...")
        console.print("")
        console.print("[dim]═══════════════════════════════════════════════════════════[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
        sys.exit(2)
```

Add import at top:
```python
import subprocess
```

### Step 2: Test orchestrate command

```bash
python -m casestudypilot orchestrate
```

**Expected:** 
- Command checks prerequisites (gh CLI authenticated)
- Loads orchestrator agent instructions
- Outputs guidance for execution
- Shows preview of agent instructions

### Step 3: Commit Task 3

```bash
git add casestudypilot/__main__.py
git commit -m "feat: add orchestrate CLI command for content orchestrator

- Add 'python -m casestudypilot orchestrate' command
- Checks prerequisites (gh CLI auth, agent workflow file)
- Loads content-orchestrator agent instructions
- Provides execution guidance for LLM agents
- Designed for 'ingest incoming requests' invocation"
```

---

## Task 4: Integration Testing

**Goal:** Test end-to-end workflow with real GitHub issues.

### Step 1: Create test case study issue

```bash
# Create a test issue via GitHub UI or gh CLI
gh issue create \
  --title "Test: Generate case study for Intuit" \
  --label "case-study" \
  --body "YouTube Video URL: https://www.youtube.com/watch?v=VIDEO_ID

Company Name (Optional): Intuit

Expected CNCF Projects (Optional):
- Kubernetes
- Argo CD

Requirements:
- [x] Video has captions/subtitles enabled
- [x] Video is at least 10 minutes long
- [ ] Company is a CNCF end-user member (if known)"

# Note the issue number
```

### Step 2: Test issue parser on test issue

```bash
# Replace 999 with actual issue number
python -m casestudypilot parse-issue 999
```

**Expected:**
- Extracts YouTube URL correctly
- Detects content_type as "case-study"
- Extracts company name "Intuit"
- Returns valid JSON

### Step 3: Test orchestrator discovery (manual)

```bash
# Check if orchestrator would discover the test issue
gh issue list --label "case-study" --state open --json number,title,labels
```

**Expected:** Test issue appears in list

### Step 4: Execute orchestrator agent (via LLM)

**In OpenCode or LLM environment:**

Tell the agent:
```
Read the instructions from .github/agents/content-orchestrator.md and execute the complete workflow. Process any open case-study or reference-architecture issues.
```

**Monitor:**
- Issue gets "in-progress" label
- Subagent spawns and executes case-study workflow
- After ~10-15 minutes, issue gets "case-study-generated" label
- Issue comment has PR link

### Step 5: Verify results

Check that:
- [ ] Case study markdown file created in `case-studies/`
- [ ] 3 screenshots extracted to `case-studies/images/`
- [ ] PR created and linked to issue
- [ ] Issue has correct labels (case-study-generated)
- [ ] No fabricated metrics (all from transcript)
- [ ] Correct company throughout document

### Step 6: Test error handling

Create issue with invalid data:
```bash
gh issue create \
  --title "Test: Invalid issue (no URL)" \
  --label "case-study" \
  --body "This issue has no YouTube URL"
```

Run orchestrator, verify:
- [ ] Parser fails with clear error
- [ ] Error comment posted to issue
- [ ] Issue not processed further

### Step 7: Document test results

Create file: `docs/testing/orchestration-integration-tests.md`

```markdown
# Orchestration Integration Tests

## Test Run: [Date]

### Test 1: Valid Case Study Issue
- Issue: #[number]
- Video: [URL]
- Result: ✅ SUCCESS
- PR: [URL]
- Time: [minutes]
- Notes: [any observations]

### Test 2: Valid Reference Architecture Issue
- Issue: #[number]
- Video: [URL]
- Result: ✅ SUCCESS / ❌ FAILED
- PR: [URL]
- Time: [minutes]
- Notes: [any observations]

### Test 3: Invalid Issue (No URL)
- Issue: #[number]
- Result: ✅ FAILED AS EXPECTED
- Error: [error message]
- Notes: [observations]

## Issues Found
- [List any bugs or unexpected behavior]

## Improvements Needed
- [List any improvements to be made]
```

### Step 8: Commit test documentation

```bash
git add docs/testing/orchestration-integration-tests.md
git commit -m "test: document orchestration integration test results"
```

---

## Task 5: Documentation

**Goal:** Update README and create orchestration guide.

**Files:**
- Modify: `README.md`
- Create: `docs/ORCHESTRATION-GUIDE.md`
- Modify: `AGENTS.md`

### Step 1: Add orchestration section to README

**File:** `README.md`

Add section after "Fail-Fast Validation Architecture":

```markdown
---

## Automated Content Orchestration

**Process all pending content generation requests automatically.**

### Quick Start

In an LLM agent environment (OpenCode, GitHub Copilot, etc.):

```
You: "ingest incoming requests"

Agent: [Executes content-orchestrator workflow]
       [Discovers 3 open issues]
       [Spawns specialized agents for each]
       [Posts results to issues]
       
       Summary: 2 successful, 1 failed
```

Or via CLI:

```bash
python -m casestudypilot orchestrate
# Follow instructions to execute in LLM environment
```

### How It Works

1. **Discovery**: Orchestrator finds open issues labeled `case-study` or `reference-architecture`
2. **Parsing**: Extracts YouTube URLs and metadata from issue bodies
3. **Routing**: Spawns appropriate specialized agent (case-study-agent or reference-architecture-agent)
4. **Execution**: Agent runs complete workflow silently (~10-25 minutes)
5. **Results**: Agent posts PR link (success) or error template (failure) to issue

### Supported Content Types

| Content Type | Label | Processing Time | Output |
|--------------|-------|-----------------|--------|
| Case Study | `case-study` | 10-15 minutes | 500-1500 words, 5 sections, 3 screenshots |
| Reference Architecture | `reference-architecture` | 20-25 minutes | 2000-5000 words, 13 sections, 6+ screenshots |
| Presenter Profile | `presenter-profile` | TBD | Not yet implemented (epic #17) |

### Manual Processing

You can also process individual issues manually:

```bash
# Parse issue data
python -m casestudypilot parse-issue 42

# Then manually run the specialized agent workflow
# See: .github/agents/case-study-agent.md
#      .github/agents/reference-architecture-agent.md
```

### Architecture

```
GitHub Issue (with YouTube URL)
         ↓
Content Orchestrator discovers issue
         ↓
parse-issue extracts metadata
         ↓
Orchestrator spawns LLM subagent
         ↓
   ┌─────────────────────────────────────┐
   │ Specialized Agent                   │
   │ (case-study or ref-arch)            │
   │                                     │
   │ - Fetches video data                │
   │ - Validates transcript              │
   │ - Analyzes content                  │
   │ - Generates document                │
   │ - Validates quality                 │
   │ - Creates PR                        │
   └─────────────────────────────────────┘
         ↓
   PR created and linked to issue
```

See [docs/ORCHESTRATION-GUIDE.md](docs/ORCHESTRATION-GUIDE.md) for complete documentation.

---
```

### Step 2: Create orchestration guide

**File:** `docs/ORCHESTRATION-GUIDE.md`

```markdown
# Content Orchestration Guide

Complete guide to automated content generation with casestudypilot.

## Overview

The content orchestration system automatically processes GitHub issues requesting case studies, reference architectures, and presenter profiles. It discovers open issues, extracts metadata, spawns specialized LLM agents, and posts results.

## Getting Started

### Prerequisites

1. **GitHub CLI authenticated:**
   ```bash
   gh auth login
   ```

2. **Python environment:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Repository cloned:**
   ```bash
   git clone https://github.com/cncf/casestudypilot
   cd casestudypilot
   ```

4. **LLM agent environment:**
   - OpenCode
   - GitHub Copilot
   - Claude Code
   - Or similar tool with Task tool support

### Basic Usage

**Method 1: Natural language (recommended)**

In your LLM environment:
```
You: "ingest incoming requests"

Agent: [Reads .github/agents/content-orchestrator.md]
       [Executes complete workflow]
       [Reports results]
```

**Method 2: Via CLI**
```bash
python -m casestudypilot orchestrate
# Follow instructions to spawn orchestrator agent
```

## Workflow Detail

### Phase 1: Discovery

Orchestrator discovers open issues:

```bash
gh issue list --label "case-study" --state open
gh issue list --label "reference-architecture" --state open
gh issue list --label "presenter-profile" --state open
```

Filters out already-processed issues:
- Has label: `*-generated` (completed)
- Has label: `in-progress` (currently processing)
- Has label: `validation-failed-*` (failed validation)

### Phase 2: Parsing

For each pending issue:

```bash
python -m casestudypilot parse-issue <issue_number>
```

Extracts:
- **YouTube URL** (required) - Pattern: `https://www.youtube.com/watch?v=...`
- **Company name** (optional) - From "Company Name (Optional): ..." field
- **Content type** - From issue labels
- **Issue title** - For context

Output: JSON with extracted metadata

### Phase 3: Agent Dispatch

Orchestrator spawns specialized LLM agent:

**For case studies:**
- Reads: `.github/agents/case-study-agent.md`
- Agent executes: 14-step workflow
- Duration: ~10-15 minutes
- Output: Markdown + 3 screenshots

**For reference architectures:**
- Reads: `.github/agents/reference-architecture-agent.md`
- Agent executes: 18-step workflow
- Duration: ~20-25 minutes
- Output: Markdown + 6+ screenshots

**Execution mode: Silent**
- No progress updates posted to issue during execution
- Only posts when complete (PR link) or failed (error)

### Phase 4: Completion

Subagent posts results to issue:

**On success:**
```markdown
✅ **Case Study Generated Successfully**

Your case study has been generated and is ready for review.

**Pull Request:** [#123](PR_URL)

The PR includes:
- Case study markdown file (case-studies/company.md)
- 3 contextual screenshots
- All validations passed (quality score: 0.75)

Please review and merge if acceptable.
```

Labels updated:
- Remove: `in-progress`
- Add: `case-study-generated`

**On failure:**
```markdown
❌ **Validation Failed: Transcript Quality**

The video transcript does not meet minimum quality requirements.

**Critical Issues:**
- Transcript too short: 450 characters (minimum: 1000)
- Insufficient segments: 12 (minimum: 50)

**Action Required:**
Please verify the video has captions enabled and is at least 10 minutes long.
```

Labels updated:
- Remove: `in-progress`
- Add: `validation-failed-transcript`

## Issue Parser Command

### Usage

```bash
# Output to stdout
python -m casestudypilot parse-issue 42

# Save to file
python -m casestudypilot parse-issue 42 --output issue_data.json
```

### Output Format

```json
{
  "issue_number": 42,
  "content_type": "case-study",
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "company_name": "Intuit",
  "title": "Generate case study for Intuit",
  "labels": ["case-study"]
}
```

### Error Handling

**No YouTube URL found:**
```
ValidationError: No YouTube URL found in issue #42.
Please provide a YouTube URL in the issue body.
```

**Invalid content type:**
```
ValueError: No recognized content type label found.
Expected: case-study, reference-architecture, or presenter-profile.
Found: ['bug', 'enhancement']
```

**GitHub API error:**
```
RuntimeError: Failed to fetch issue #42: Issue not found
```

## Specialized Agent Workflows

### Case Study Agent

**Workflow:** 14 steps with 5 validation checkpoints

1. Pre-flight validation
2. Fetch video data → **Validate transcript** (≥1000 chars)
3. Extract company name → **Validate company**
4. Verify CNCF membership
5. Correct transcript
6. Analyze transcript → **Validate analysis** (≥2 projects)
7. Extract 3 screenshots
8. Generate case study
9. **Validate metrics** (fabrication check)
10. **Validate company consistency** (prevent wrong company bug)
11. Assemble markdown
12. Validate quality (≥0.60 score)
13. Create branch and commit
14. Create PR

**Documentation:** [.github/agents/case-study-agent.md](.github/agents/case-study-agent.md)

### Reference Architecture Agent

**Workflow:** 18 steps with 7 validation checkpoints

1. Pre-flight validation
2. Fetch video data → **Validate transcript** (≥2000 chars)
3. Extract company name → **Validate company**
4. Verify CNCF membership
5. Correct transcript
6. Deep analysis → **Validate analysis** (≥5 projects, 3 layers)
7. Extract 6+ screenshots
8. Generate architecture diagram specs
9. Generate reference architecture
10. **Validate metrics** (with transcript quotes)
11. **Validate company consistency**
12. Assemble markdown
13. **Validate technical depth** (≥0.70 score)
14. Generate TAB submission guide
15. Create branch and commit
16. Create PR with TAB guide
17. Post to issue

**Documentation:** [.github/agents/reference-architecture-agent.md](.github/agents/reference-architecture-agent.md)

## Troubleshooting

### Orchestrator doesn't find issues

**Check:**
```bash
# Verify issues exist with correct labels
gh issue list --label "case-study" --state open

# Check if issues already processed
gh issue list --label "case-study-generated" --state all
```

### Parser fails to extract URL

**Issue body format:**

✅ **Good:**
```
YouTube Video URL: https://www.youtube.com/watch?v=VIDEO_ID

or

Video: https://www.youtube.com/watch?v=VIDEO_ID

or just:

https://www.youtube.com/watch?v=VIDEO_ID
```

❌ **Bad:**
```
Video ID: VIDEO_ID
(Parser looks for full URL, not just video ID)
```

### Subagent doesn't execute

**Check:**
1. Agent workflow file exists: `.github/agents/case-study-agent.md`
2. LLM environment supports Task tool (OpenCode, etc.)
3. Issue data parsed correctly (`parse-issue` worked)

### Validation checkpoint fails

Each checkpoint has detailed error templates. Check issue comments for:
- Which validation failed
- Specific error messages
- Action required to fix

Common failures:
- **Transcript quality:** Video too short or no captions
- **Company identification:** Video title unclear
- **Analysis:** Insufficient CNCF project mentions
- **Metrics:** Fabricated numbers not in transcript
- **Company consistency:** Wrong company hallucination

## Advanced Usage

### Process Specific Issue

```bash
# Parse issue
python -m casestudypilot parse-issue 42 --output issue_42.json

# Then tell LLM agent:
"Execute case-study-agent workflow for issue #42 using data from issue_42.json"
```

### Batch Processing

```bash
# Get all pending case study issues
gh issue list --label "case-study" --state open --json number | \
  jq -r '.[] | .number' | \
  while read issue_num; do
    python -m casestudypilot parse-issue "$issue_num" --output "issue_${issue_num}.json"
  done

# Then tell orchestrator to process all
```

### Monitor Progress

```bash
# Watch for completed issues
watch -n 60 'gh issue list --label "case-study-generated" --state all'

# Check in-progress issues
gh issue list --label "in-progress" --state open
```

## Label Reference

| Label | Meaning | Applied By |
|-------|---------|------------|
| `case-study` | Case study request | User (issue template) |
| `reference-architecture` | Reference architecture request | User (issue template) |
| `presenter-profile` | Presenter profile request | User (issue template) |
| `in-progress` | Currently processing | Orchestrator |
| `case-study-generated` | Case study completed | case-study-agent |
| `reference-architecture-generated` | Reference architecture completed | reference-architecture-agent |
| `presenter-profile-generated` | Presenter profile completed | people-agent (future) |
| `validation-failed-transcript` | Transcript quality check failed | Specialized agent |
| `validation-failed-company` | Company identification failed | Specialized agent |
| `validation-failed-analysis` | Analysis insufficient | Specialized agent |
| `validation-failed-metrics` | Fabricated metrics detected | Specialized agent |
| `validation-failed-company-mismatch` | Wrong company in content | Specialized agent |
| `validation-failed-quality` | Quality score too low | Specialized agent |
| `waiting-for-agent-implementation` | Agent not ready yet | Orchestrator |

## Architecture Diagrams

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│ GitHub Issues (Input)                                       │
│ - case-study label                                          │
│ - reference-architecture label                              │
│ - presenter-profile label                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Content Orchestrator (Layer 1)                              │
│ - Discovers open issues                                     │
│ - Filters processed issues                                  │
│ - Parses issue data (parse-issue CLI)                       │
│ - Routes to specialized agents                              │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ↓               ↓               ↓
┌────────────────┐ ┌──────────────┐ ┌──────────────┐
│ case-study-    │ │ ref-arch-    │ │ people-      │
│ agent          │ │ agent        │ │ agent        │
│ (14 steps)     │ │ (18 steps)   │ │ (future)     │
└────────┬───────┘ └──────┬───────┘ └──────┬───────┘
         │                │                │
         ↓                ↓                ↓
┌─────────────────────────────────────────────────────────────┐
│ Python CLI Tools (Layer 3)                                  │
│ - youtube-data, validate-transcript, verify-company         │
│ - validate-analysis, extract-screenshots, assemble          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Output                                                       │
│ - Markdown files (case-studies/, reference-architectures/)  │
│ - Screenshots (images/)                                      │
│ - Pull requests                                              │
│ - Issue comments                                             │
└─────────────────────────────────────────────────────────────┘
```

### Execution Flow

```
User creates issue
         ↓
Issue template captures:
- YouTube URL
- Optional company name
- Content type (label)
         ↓
User: "ingest incoming requests"
         ↓
Orchestrator discovers issue
         ↓
parse-issue extracts metadata
         ↓
Orchestrator marks issue "in-progress"
         ↓
Orchestrator spawns subagent via Task tool
         ↓
Subagent reads specialized agent workflow
         ↓
Subagent executes 14-18 steps silently
         ↓
   (10-25 minutes pass)
         ↓
Subagent completes workflow
         ↓
     SUCCESS path              FAILURE path
         ↓                          ↓
Subagent creates PR         Subagent posts error
         ↓                          ↓
Subagent posts PR link      Adds validation-failed-* label
         ↓                          ↓
Adds *-generated label      Removes in-progress label
         ↓                          ↓
Removes in-progress         User fixes issue
         ↓                          ↓
PR merged                   Retries
```

## Best Practices

### For Issue Creators

1. **Use issue templates** - Ensures proper labels and format
2. **Provide clear YouTube URL** - Full URL, not just video ID
3. **Specify company name** - Helps parser if video title unclear
4. **Verify video has captions** - Required for transcript extraction
5. **Check video length** - 10+ minutes for case studies, 15+ for ref archs

### For Orchestrator Operators

1. **Run regularly** - Check for new issues daily or weekly
2. **Monitor failures** - Review validation-failed-* labels
3. **Clean up completed issues** - Close issues after PRs merged
4. **Track metrics** - Success rate, processing time, failure reasons

### For Agent Developers

1. **Follow agent workflow format** - Markdown with clear steps
2. **Include validation checkpoints** - Fail-fast on bad data
3. **Post clear error messages** - Help users fix issues
4. **Test with real videos** - End-to-end integration tests
5. **Document exit codes** - 0=pass, 1=warning, 2=critical

## FAQ

**Q: How long does processing take?**
A: Case studies: 10-15 minutes. Reference architectures: 20-25 minutes.

**Q: Can I process multiple issues at once?**
A: Yes, the orchestrator processes all pending issues sequentially. Parallel processing planned for future version.

**Q: What if an issue fails validation?**
A: The agent posts an error template to the issue with details. Fix the issue and retry by telling the orchestrator to "ingest incoming requests" again.

**Q: Can I process issues manually?**
A: Yes, use `python -m casestudypilot parse-issue` to extract data, then follow the specialized agent workflow manually.

**Q: Does this work without an LLM agent?**
A: The specialized agents require an LLM to execute (they invoke skills for content generation). The parser works standalone.

**Q: How do I add a new content type?**
A: Create a new specialized agent workflow, add issue template, update orchestrator routing logic. See CONTRIBUTING.md for details.

## Related Documentation

- **Agent Workflows:**
  - [content-orchestrator.md](.github/agents/content-orchestrator.md)
  - [case-study-agent.md](.github/agents/case-study-agent.md)
  - [reference-architecture-agent.md](.github/agents/reference-architecture-agent.md)

- **Framework Documentation:**
  - [AGENTS.md](AGENTS.md) - Agent development guide
  - [README.md](README.md) - Project overview
  - [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guide

- **Issue Templates:**
  - [generate-case-study.yml](.github/ISSUE_TEMPLATE/generate-case-study.yml)
  - [generate-reference-architecture.yml](.github/ISSUE_TEMPLATE/generate-reference-architecture.yml)

## Support

- **Issues:** https://github.com/cncf/casestudypilot/issues
- **Discussions:** https://github.com/cncf/casestudypilot/discussions
- **Epic Tracking:** Check issues labeled `epic` for implementation status
```

### Step 3: Update AGENTS.md

**File:** `AGENTS.md`

Find the section "### 5. GitHub Communication: Use MCP or gh CLI" and add note after it:

```markdown
### 6. Issue Parsing and Data Extraction

**Pattern:** Extract metadata from GitHub issues for agent workflows.

The `parse-issue` CLI command extracts structured data from GitHub issues:

```bash
python -m casestudypilot parse-issue <issue_number> --output issue_data.json
```

**What it extracts:**
- YouTube URL (required)
- Content type from labels
- Optional company name
- Issue title and metadata

**Output format:**
```json
{
  "issue_number": 42,
  "content_type": "case-study",
  "video_url": "https://www.youtube.com/watch?v=...",
  "company_name": "Intuit",
  "title": "Generate case study for Intuit",
  "labels": ["case-study"]
}
```

**Usage in agent workflows:**

```bash
# In orchestrator or specialized agent
python -m casestudypilot parse-issue "$ISSUE_NUMBER" --output issue_data.json

# Load data
VIDEO_URL=$(jq -r '.video_url' issue_data.json)
COMPANY=$(jq -r '.company_name // "Not specified"' issue_data.json)

# Use in workflow
python -m casestudypilot youtube-data "$VIDEO_URL"
```

**Error handling:**
- Exit code 2: No YouTube URL found or invalid issue
- Posts error comment to issue with action required
```

### Step 4: Commit documentation

```bash
git add README.md docs/ORCHESTRATION-GUIDE.md AGENTS.md
git commit -m "docs: add comprehensive orchestration documentation

- Add orchestration section to README
- Create complete ORCHESTRATION-GUIDE.md
- Update AGENTS.md with issue parsing patterns
- Include architecture diagrams, troubleshooting, FAQ
- Document all CLI commands and workflows"
```

---

## Verification Checklist

After completing all tasks, verify:

### Core Functionality
- [ ] `python -m casestudypilot parse-issue <n>` extracts YouTube URLs
- [ ] `python -m casestudypilot parse-issue <n>` detects content types
- [ ] `python -m casestudypilot orchestrate` loads orchestrator instructions
- [ ] Orchestrator discovers open issues correctly
- [ ] Orchestrator filters already-processed issues
- [ ] Orchestrator spawns subagents via Task tool
- [ ] Subagents execute complete workflows
- [ ] Subagents post results to issues (PR link or error)
- [ ] Labels updated correctly (in-progress, *-generated, validation-failed-*)

### Error Handling
- [ ] Parse-issue fails gracefully on missing URL
- [ ] Parse-issue fails gracefully on invalid issue
- [ ] Orchestrator handles gh CLI auth errors
- [ ] Validation checkpoints stop on critical failures
- [ ] Error templates posted to issues are clear and actionable

### Documentation
- [ ] README has orchestration section
- [ ] ORCHESTRATION-GUIDE.md is complete
- [ ] AGENTS.md updated with new patterns
- [ ] All commands documented with examples
- [ ] Architecture diagrams included

### Testing
- [ ] Unit tests pass for issue_parser
- [ ] Integration test with real issue succeeds
- [ ] Error cases tested (invalid URL, etc.)
- [ ] Test results documented

### Code Quality
- [ ] Type hints added to new functions
- [ ] Docstrings complete
- [ ] No hardcoded values
- [ ] Logging added for debugging
- [ ] Exit codes correct (0=pass, 1=warn, 2=critical)

---

## Future Enhancements (Not in This Epic)

These will be tracked in separate epics:

1. **GitHub Actions Integration** - Scheduled orchestration every 6 hours
2. **Parallel Processing** - Process multiple issues concurrently
3. **Retry Logic** - Automatic retry on transient failures
4. **People Agent** - When epic #17 completes
5. **Progress Streaming** - Optional real-time updates during execution
6. **Metrics Dashboard** - Success rate, processing time analytics

---

## Success Criteria

This epic is complete when:

✅ User can say "ingest incoming requests" and system processes all pending issues
✅ System discovers issues labeled `case-study` and `reference-architecture`
✅ System extracts YouTube URLs and metadata from issue bodies
✅ System spawns appropriate LLM agent (case-study-agent or reference-architecture-agent)
✅ LLM agent executes complete workflow (fetch → analyze → generate → PR)
✅ System posts PR link on success, error template on failure
✅ System manages issue labels appropriately
✅ Multiple issues processed in single orchestrator run
✅ Documentation complete and clear
✅ Integration tests pass

---

**Epic Status:** Ready for implementation
**Estimated Time:** 13-17 hours (2-3 working days)
**Dependencies:** None (all required tools already exist)
**Version:** content-orchestrator v2.0.0
