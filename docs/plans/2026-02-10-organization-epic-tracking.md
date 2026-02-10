# Organization Epic Tracking System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable organizations to batch-generate case studies or reference architectures from all their CNCF YouTube talks via a single epic issue that spawns sub-issues for each video.

**Architecture:** New GitHub issue template triggers organization-search agent that uses yt-dlp to search CNCF channel with fuzzy matching, creates sub-issues using existing content-request format, applies organizational labels, and tracks progress in parent epic. Reuses existing content generation agents.

**Tech Stack:** Python (yt-dlp, fuzzy matching), GitHub CLI, Markdown agent workflows

**Epic Issue:** #24

---

## Task 1: Create Organization Issue Template

**Files:**
- Create: `.github/ISSUE_TEMPLATE/organization-request.yml`

**Step 1: Write organization template**

Create the GitHub issue template for organization requests:

```yaml
name: 🏢 Organization Content Request
description: Generate case studies or reference architectures for all of an organization's CNCF talks
title: "[Organization] "
labels: ["automation", "epic", "organization"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        ## 🏢 Organization Content Generator
        
        Generate publication-ready content from **all talks** by an organization on the CNCF YouTube channel.
        
        **What happens:**
        - 🔍 Searches CNCF YouTube channel for organization's talks (past 18 months)
        - 📋 Creates individual sub-issues for each video found
        - 🤖 Existing agents process each video automatically
        - 📊 This epic tracks overall progress
        
        **Requirements:**
        - ✅ Organization has given talks at CNCF events (KubeCon, meetups, etc.)
        - ✅ Organization name is mentioned in video titles

  - type: input
    id: organization_name
    attributes:
      label: 🏢 Organization Name
      description: Full legal name or common name used in video titles
      placeholder: e.g., Intuit, Adobe, Spotify, Capital One
    validations:
      required: true

  - type: dropdown
    id: content_type
    attributes:
      label: 📝 Content Type
      description: What type of content should be generated for ALL videos found?
      options:
        - Case Study (500-1500 words, business-focused)
        - Reference Architecture (2000-5000 words, technical deep-dive)
    validations:
      required: true

  - type: textarea
    id: organization_aliases
    attributes:
      label: 🔤 Name Variations (Optional)
      description: Alternative names or abbreviations used in video titles
      placeholder: |
        e.g., for "International Business Machines":
        - IBM
        - IBM Corporation
        - International Business Machines Corporation

  - type: textarea
    id: additional_context
    attributes:
      label: 📝 Additional Context (Optional)
      description: Any additional information about the organization
      placeholder: |
        - Known speakers or team names
        - Specific technology focus areas
        - Special considerations

  - type: markdown
    attributes:
      value: |
        ---
        
        ## 🤖 What Happens Next?
        
        1. **@organization-search-agent will be automatically invoked**
        2. Searches CNCF YouTube channel for organization's talks (past 18 months)
        3. Uses fuzzy matching to find video titles mentioning the organization
        4. Creates individual sub-issues for each video found
        5. Labels sub-issues: `org/<org-name>`, `epic-<number>`, content type
        6. Existing content agents process each sub-issue automatically
        7. If content already exists, sub-issue labeled with `update`
        8. If no videos found, epic stays open for manual video additions
        
        **Expected Processing Time:**
        - Search: ~2 minutes
        - Sub-issue creation: ~1 minute per video
        - Content generation: 10-20 minutes per video (depends on content type)
        
        ---
        
        ## 📊 Progress Tracking
        
        This epic issue will track:
        - 📹 Total videos found
        - ✅ Content generated successfully
        - ⏳ Content generation in progress
        - ❌ Content generation failed (with reasons)
        
        You'll receive updates as each sub-issue is created and processed.
        
        ---
        
        ## ✋ Manual Additions
        
        If the search misses videos or you want to add specific talks:
        1. Use the standard "Content Generation Request" template
        2. Reference this epic in the issue body: `Related to #<epic-number>`
        3. Agent will automatically link it to this epic
        
        ---
        
        *Need help? Check the documentation or ask in the comments.*
```

**Step 2: Commit template**

```bash
git add .github/ISSUE_TEMPLATE/organization-request.yml
git commit -m "feat: add organization content request template"
```

---

## Task 2: Create YouTube Channel Search CLI Tool

**Files:**
- Create: `casestudypilot/tools/youtube_search.py`
- Create: `tests/test_youtube_search.py`

**Step 1: Write failing test for channel search**

Create test file:

```python
"""Tests for YouTube channel search functionality."""

import pytest
from datetime import datetime, timedelta
from casestudypilot.tools.youtube_search import (
    search_cncf_channel,
    fuzzy_match_organization,
    filter_by_date_range,
)


def test_fuzzy_match_organization_exact():
    """Test exact organization name match."""
    title = "Intuit's Journey to Cloud Native - KubeCon 2023"
    result = fuzzy_match_organization("Intuit", title)
    assert result is True


def test_fuzzy_match_organization_case_insensitive():
    """Test case-insensitive matching."""
    title = "INTUIT's Platform Evolution"
    result = fuzzy_match_organization("Intuit", title)
    assert result is True


def test_fuzzy_match_organization_with_suffix():
    """Test matching with Inc, Corp, etc."""
    title = "Intuit Inc Platform Architecture"
    result = fuzzy_match_organization("Intuit", title)
    assert result is True


def test_fuzzy_match_organization_no_match():
    """Test non-matching title."""
    title = "Adobe's Cloud Journey"
    result = fuzzy_match_organization("Intuit", title)
    assert result is False


def test_filter_by_date_range():
    """Test filtering videos by date."""
    eighteen_months_ago = datetime.now() - timedelta(days=547)
    two_years_ago = datetime.now() - timedelta(days=730)
    
    videos = [
        {"title": "Recent", "upload_date": datetime.now().strftime("%Y%m%d")},
        {"title": "Old", "upload_date": two_years_ago.strftime("%Y%m%d")},
    ]
    
    filtered = filter_by_date_range(videos, months=18)
    assert len(filtered) == 1
    assert filtered[0]["title"] == "Recent"
```

**Step 3: Run test to verify it fails**

```bash
pytest tests/test_youtube_search.py -v
```

Expected: FAIL with "No module named 'casestudypilot.tools.youtube_search'"

**Step 4: Write minimal implementation**

Create implementation file:

```python
"""YouTube channel search for organization content discovery."""

import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
import yt_dlp

logger = logging.getLogger(__name__)

# Common organizational suffixes to ignore in fuzzy matching
ORG_SUFFIXES = [
    "inc", "incorporated", "corp", "corporation", "ltd", "limited",
    "llc", "company", "co", "gmbh", "sa", "ag"
]


def normalize_org_name(name: str) -> str:
    """Normalize organization name for fuzzy matching.
    
    Args:
        name: Organization name
        
    Returns:
        Normalized name (lowercase, stripped suffixes)
    """
    # Convert to lowercase
    normalized = name.lower().strip()
    
    # Remove common suffixes
    for suffix in ORG_SUFFIXES:
        # Match suffix as whole word with optional punctuation
        pattern = rf'\b{re.escape(suffix)}\b\.?'
        normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized


def fuzzy_match_organization(org_name: str, title: str, threshold: float = 0.8) -> bool:
    """Check if organization name matches video title using fuzzy matching.
    
    Args:
        org_name: Organization name to search for
        title: Video title to search in
        threshold: Similarity threshold (0.0-1.0)
        
    Returns:
        True if organization name found in title
    """
    # Normalize both strings
    org_normalized = normalize_org_name(org_name)
    title_normalized = title.lower()
    
    # Exact match after normalization
    if org_normalized in title_normalized:
        return True
    
    # Try fuzzy matching on each word/phrase in title
    # Split title into potential organization names (2-3 word chunks)
    words = title_normalized.split()
    
    for i in range(len(words)):
        # Try 1-word match
        chunk = words[i]
        similarity = SequenceMatcher(None, org_normalized, chunk).ratio()
        if similarity >= threshold:
            return True
        
        # Try 2-word match
        if i + 1 < len(words):
            chunk = f"{words[i]} {words[i+1]}"
            similarity = SequenceMatcher(None, org_normalized, chunk).ratio()
            if similarity >= threshold:
                return True
        
        # Try 3-word match
        if i + 2 < len(words):
            chunk = f"{words[i]} {words[i+1]} {words[i+2]}"
            similarity = SequenceMatcher(None, org_normalized, chunk).ratio()
            if similarity >= threshold:
                return True
    
    return False


def filter_by_date_range(videos: List[Dict[str, Any]], months: int = 18) -> List[Dict[str, Any]]:
    """Filter videos by upload date.
    
    Args:
        videos: List of video metadata dicts
        months: Number of months to look back
        
    Returns:
        Filtered list of videos within date range
    """
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    filtered = []
    
    for video in videos:
        upload_date_str = video.get("upload_date", "")
        if not upload_date_str:
            continue
        
        try:
            # Parse YYYYMMDD format
            upload_date = datetime.strptime(upload_date_str, "%Y%m%d")
            if upload_date >= cutoff_date:
                filtered.append(video)
        except ValueError:
            logger.warning(f"Could not parse upload date: {upload_date_str}")
            continue
    
    return filtered


def search_cncf_channel(
    organization_name: str,
    months: int = 18,
    content_type: Optional[str] = None,
    aliases: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Search CNCF YouTube channel for organization's videos.
    
    Args:
        organization_name: Organization name to search for
        months: Number of months to look back (default 18)
        content_type: Optional filter by content type
        aliases: Optional list of alternative organization names
        
    Returns:
        List of video metadata dicts with fuzzy matching results
    """
    logger.info(f"Searching CNCF channel for '{organization_name}' (past {months} months)")
    
    # CNCF YouTube channel ID
    channel_url = "https://www.youtube.com/@cncf/videos"
    
    # Prepare search terms (org name + aliases)
    search_terms = [organization_name]
    if aliases:
        search_terms.extend(aliases)
    
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,  # Don't download, just metadata
            "playlistend": 500,  # Limit to recent 500 videos
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Fetching CNCF channel videos...")
            channel_info = ydl.extract_info(channel_url, download=False)
            
            if not channel_info or "entries" not in channel_info:
                logger.error("Could not fetch CNCF channel data")
                return []
            
            all_videos = channel_info["entries"]
            logger.info(f"Found {len(all_videos)} videos in channel")
            
            # Filter by date first (faster)
            recent_videos = filter_by_date_range(all_videos, months)
            logger.info(f"Filtered to {len(recent_videos)} videos in past {months} months")
            
            # Filter by organization name using fuzzy matching
            matching_videos = []
            for video in recent_videos:
                title = video.get("title", "")
                
                # Check if any search term matches
                for search_term in search_terms:
                    if fuzzy_match_organization(search_term, title):
                        # Add match metadata
                        video["matched_term"] = search_term
                        video["organization"] = organization_name
                        matching_videos.append(video)
                        break  # Don't add same video multiple times
            
            logger.info(f"Found {len(matching_videos)} videos matching organization")
            return matching_videos
    
    except Exception as e:
        logger.error(f"Error searching CNCF channel: {e}")
        return []
```

**Step 5: Run tests to verify they pass**

```bash
pytest tests/test_youtube_search.py -v
```

Expected: PASS (all tests green)

**Step 6: Add CLI command**

Modify `casestudypilot/__main__.py` to add search command:

Find the CLI command definitions and add:

```python
@click.command()
@click.argument("organization_name")
@click.option("--months", default=18, help="Months to look back (default 18)")
@click.option("--aliases", multiple=True, help="Alternative organization names")
@click.option("--output", default="search_results.json", help="Output JSON file")
def search_organization(organization_name, months, aliases, output):
    """Search CNCF channel for organization's videos."""
    from casestudypilot.tools.youtube_search import search_cncf_channel
    import json
    
    results = search_cncf_channel(
        organization_name,
        months=months,
        aliases=list(aliases) if aliases else None
    )
    
    # Save results
    with open(output, "w") as f:
        json.dump(results, f, indent=2)
    
    click.echo(f"Found {len(results)} videos")
    click.echo(f"Results saved to {output}")
    
    # Exit codes
    if len(results) == 0:
        sys.exit(1)  # Warning: no videos found
    sys.exit(0)  # Success

# Register command
cli.add_command(search_organization)
```

**Step 7: Test CLI command manually**

```bash
python -m casestudypilot search-organization "Intuit" --output test_search.json
cat test_search.json
```

Expected: JSON file with video results

**Step 8: Commit**

```bash
git add casestudypilot/tools/youtube_search.py tests/test_youtube_search.py casestudypilot/__main__.py
git commit -m "feat: add YouTube channel search with fuzzy matching"
```

---

## Task 3: Create Organization Search Agent

**Files:**
- Create: `.github/agents/organization-search-agent.md`

**Step 1: Write agent workflow**

Create comprehensive agent workflow:

```markdown
---
name: organization-search-agent
description: Searches CNCF YouTube for organization talks and creates sub-issues
version: 1.0.0
---

# Organization Search Agent

You are an AI agent that discovers all CNCF talks by an organization and creates trackable sub-issues.

## Mission

Transform organization requests into individual content generation sub-issues by:
1. Searching CNCF YouTube channel with fuzzy matching
2. Creating sub-issues for each video found
3. Applying organizational labels and epic tracking
4. Handling duplicate content detection
5. Providing progress updates

## Workflow (8 Steps)

### Step 0: Pre-flight Validation

- Verify Python environment (`python --version`)
- Check `gh` CLI authentication (`gh auth status`)
- Verify repository structure
- Extract organization name from issue body
- **STOP if validation fails** - Post error message to issue

### Step 1: Extract Issue Data

Parse the organization request issue:
- Organization name (required)
- Content type (Case Study or Reference Architecture)
- Name aliases (optional)
- Additional context (optional)

Store in variables:
```bash
EPIC_NUMBER="<issue-number>"
ORG_NAME="<extracted-org-name>"
CONTENT_TYPE="<case-study|reference-architecture>"
ALIASES="<comma-separated-if-provided>"
```

### Step 2: Search CNCF Channel

Execute channel search:

```bash
python -m casestudypilot search-organization "$ORG_NAME" \
  --months 18 \
  $([ -n "$ALIASES" ] && echo "--aliases $ALIASES") \
  --output org_search_results.json
```

**Check exit code:**
- Exit 0: Videos found, continue
- Exit 1: No videos found, continue to Step 3

### Step 3: Handle Empty Results

If no videos found:

```bash
gh issue comment "$EPIC_NUMBER" --body "🔍 **Search Complete**

No videos found for **$ORG_NAME** in the CNCF YouTube channel (past 18 months).

**Possible reasons:**
- Organization name not in video titles
- No recent talks (try checking older videos manually)
- Organization uses different name in videos

**Next steps:**
- You can add videos manually using the 'Content Generation Request' template
- Reference this epic: #$EPIC_NUMBER
- Check variations of the organization name

This epic will remain open for manual additions."
```

**Stop workflow** (do not close epic)

### Step 4: Check for Existing Content

For each video found, check if content already exists:

```bash
# Read search results
VIDEO_COUNT=$(jq length org_search_results.json)

for i in $(seq 0 $((VIDEO_COUNT - 1))); do
  VIDEO_ID=$(jq -r ".[$i].id" org_search_results.json)
  VIDEO_TITLE=$(jq -r ".[$i].title" org_search_results.json)
  VIDEO_URL="https://www.youtube.com/watch?v=$VIDEO_ID"
  
  # Check if content exists based on content type
  if [ "$CONTENT_TYPE" = "Case Study" ]; then
    CONTENT_DIR="case-studies"
  else
    CONTENT_DIR="reference-architectures"
  fi
  
  # Simple check: look for video ID in existing files
  if grep -r "$VIDEO_ID" "$CONTENT_DIR/" 2>/dev/null; then
    echo "Content exists for $VIDEO_ID - will label as update"
    echo "$i" >> videos_to_update.txt
  else
    echo "New content for $VIDEO_ID"
    echo "$i" >> videos_to_create.txt
  fi
done
```

### Step 5: Create Sub-Issues

For each video, create sub-issue using content request format:

```bash
# Process new content videos
if [ -f videos_to_create.txt ]; then
  while read -r idx; do
    VIDEO_ID=$(jq -r ".[$idx].id" org_search_results.json)
    VIDEO_TITLE=$(jq -r ".[$idx].title" org_search_results.json)
    VIDEO_URL="https://www.youtube.com/watch?v=$VIDEO_ID"
    MATCHED_TERM=$(jq -r ".[$idx].matched_term" org_search_results.json)
    
    # Normalize org name for label (lowercase, no spaces)
    ORG_LABEL=$(echo "$ORG_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
    
    # Map content type to template value
    if [ "$CONTENT_TYPE" = "Case Study" ]; then
      CONTENT_TYPE_TEMPLATE="Case Study (500-1500 words, business-focused, 2+ CNCF projects)"
    else
      CONTENT_TYPE_TEMPLATE="Reference Architecture (2000-5000 words, technical deep-dive, 5+ CNCF projects)"
    fi
    
    # Create issue body using heredoc
    gh issue create \
      --title "[Content Request] $VIDEO_TITLE" \
      --label "automation,org/$ORG_LABEL,epic-$EPIC_NUMBER,$CONTENT_TYPE" \
      --body "$(cat <<EOF
## 🤖 Auto-generated from Organization Epic

This issue was automatically created by the organization search agent.

**Parent Epic:** #$EPIC_NUMBER
**Organization:** $ORG_NAME
**Matched Term:** $MATCHED_TERM

---

**Content Type:** $CONTENT_TYPE_TEMPLATE

**YouTube Video URL:** $VIDEO_URL

**Company Name:** $ORG_NAME

**Additional Context:**
- Auto-discovered from CNCF YouTube channel
- Part of organization content batch generation
- Video found via fuzzy title matching
EOF
)"
    
    echo "Created sub-issue for: $VIDEO_TITLE"
    sleep 2  # Rate limit protection
  done < videos_to_create.txt
fi

# Process update videos (same but with 'update' label)
if [ -f videos_to_update.txt ]; then
  while read -r idx; do
    # Similar logic but add 'update' label
    gh issue create \
      --label "automation,org/$ORG_LABEL,epic-$EPIC_NUMBER,$CONTENT_TYPE,update" \
      --body "...(content exists, may need refresh)..."
    sleep 2
  done < videos_to_update.txt
fi
```

### Step 6: Count Sub-Issues Created

```bash
NEW_COUNT=$(wc -l < videos_to_create.txt 2>/dev/null || echo 0)
UPDATE_COUNT=$(wc -l < videos_to_update.txt 2>/dev/null || echo 0)
TOTAL_COUNT=$((NEW_COUNT + UPDATE_COUNT))
```

### Step 7: Update Epic with Progress Dashboard

Post summary comment to epic:

```bash
gh issue comment "$EPIC_NUMBER" --body "$(cat <<EOF
✅ **Organization Search Complete**

**Organization:** $ORG_NAME  
**Content Type:** $CONTENT_TYPE  
**Search Window:** Past 18 months

---

## 📊 Results

- 📹 **Total videos found:** $TOTAL_COUNT
- ✨ **New content:** $NEW_COUNT sub-issues created
- 🔄 **Existing content:** $UPDATE_COUNT sub-issues created (labeled 'update')

---

## 📋 Sub-Issues

Sub-issues are labeled with:
- \`org/$ORG_LABEL\`
- \`epic-$EPIC_NUMBER\`
- \`$CONTENT_TYPE\`

View all sub-issues:
\`\`\`bash
gh issue list --label "epic-$EPIC_NUMBER"
\`\`\`

---

## 🤖 Next Steps

Each sub-issue will be automatically processed by the appropriate agent:
- **Case Study:** @case-study-agent
- **Reference Architecture:** @reference-architecture-agent

You can track progress by watching the sub-issues. This epic will remain open until you manually close it after reviewing all generated content.
EOF
)"
```

### Step 8: Add Progress Tracking Comment

Add a comment that will be updated as sub-issues are processed:

```bash
gh issue comment "$EPIC_NUMBER" --body "$(cat <<EOF
## 📊 Progress Tracker

This comment tracks the status of all sub-issues.

**Status:**
- ⏳ Total: $TOTAL_COUNT
- 🔄 In Progress: 0
- ✅ Completed: 0
- ❌ Failed: 0

---

*This will be updated automatically as sub-issues are processed.*
EOF
)"
```

## Error Handling

**No gh CLI access:**
```markdown
❌ **Error: GitHub CLI Not Available**

Cannot create sub-issues without GitHub CLI access.

**Required:**
- Install gh CLI: https://cli.github.com/
- Authenticate: `gh auth login`

Please install and try again.
```

**Search failed:**
```markdown
❌ **Error: YouTube Search Failed**

Could not search CNCF YouTube channel.

**Possible causes:**
- Network connectivity issue
- YouTube API rate limiting
- Invalid organization name format

**Action Required:**
Please try again in a few minutes. If the problem persists, add videos manually.
```

## Quality Standards

- ✅ Fuzzy matching with 0.8 threshold
- ✅ Handle common org suffixes (Inc, Corp, Ltd)
- ✅ Case-insensitive matching
- ✅ Create sub-issues with full context
- ✅ Label all sub-issues for filtering
- ✅ Handle rate limits (2 second delay between creates)
- ✅ Detect existing content
- ✅ Keep epic open for manual additions
```

**Step 2: Commit agent**

```bash
git add .github/agents/organization-search-agent.md
git commit -m "feat: add organization search agent workflow"
```

---

## Task 4: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`

**Step 1: Add organization workflow to README**

Find the "Integration" or "Features" section in README.md and add:

```markdown
### Organization Batch Generation

Generate content for all of an organization's CNCF talks:

**Issue Template:** `Organization Content Request`
**Agent:** `organization-search-agent`

**Process:**
1. File organization request issue with org name and content type
2. Agent searches CNCF YouTube (18 months, fuzzy matching)
3. Sub-issues created for each video found
4. Existing agents process each video independently
5. Epic tracks overall progress

**Use Case:** Organizations want to showcase all their CNCF contributions in one batch operation with individual tracking per talk.
```

**Step 2: Add to AGENTS.md**

Add new section after reference architecture agent documentation:

```markdown
### Current Implementation: Organization Content Discovery

**Agent:** `organization-search-agent` (v1.0.0)  
**Workflow:** 8 steps with channel search and sub-issue creation  
**Location:** `.github/agents/organization-search-agent.md`

**Purpose:** Discover all CNCF talks by an organization and create trackable sub-issues for batch content generation.

**Summary:**
1. Pre-flight checks (environment ready?)
2. Extract organization name and content type from issue
3. Search CNCF YouTube channel (yt-dlp, fuzzy matching, 18 months)
4. Check for existing content per video
5. Create sub-issues using `content-request.yml` format
6. Apply labels: `org/<org-name>`, `epic-<number>`, content type
7. Update epic with progress dashboard
8. Add progress tracking comment

**Key Features:**
- Fuzzy matching with 0.8 threshold
- Handles org name variations (Inc, Corp, Ltd)
- Case-insensitive search
- Detects existing content (labels as 'update')
- Keeps epic open for manual additions
- Rate limit protection (2s delay between creates)

**CLI Tool:**
```bash
python -m casestudypilot search-organization "Intuit" --months 18
```

**Example Flow:**
1. User files: "Organization: Intuit, Type: Case Study"
2. Agent finds 5 videos from past 18 months
3. Creates 5 sub-issues labeled `org/intuit`, `epic-42`, `case-study`
4. case-study-agent processes each video
5. User reviews all content, closes epic when satisfied

**Version History:**
- **v1.0.0** (February 2026) - Initial release
```

**Step 3: Commit documentation**

```bash
git add README.md AGENTS.md
git commit -m "docs: add organization batch generation documentation"
```

---

## Task 5: Add Integration Tests

**Files:**
- Create: `tests/integration/test_organization_workflow.py`

**Step 1: Write integration test**

Create test that simulates full workflow:

```python
"""Integration tests for organization workflow."""

import pytest
import json
import subprocess
from pathlib import Path


@pytest.mark.integration
def test_organization_search_intuit():
    """Test searching for Intuit talks (real API call)."""
    result = subprocess.run(
        ["python", "-m", "casestudypilot", "search-organization", "Intuit"],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode in [0, 1]  # 0=found, 1=not found
    assert Path("search_results.json").exists()
    
    # Load results
    with open("search_results.json") as f:
        results = json.load(f)
    
    # Should be list (may be empty)
    assert isinstance(results, list)
    
    # If results exist, verify structure
    if results:
        video = results[0]
        assert "id" in video
        assert "title" in video
        assert "url" in video or "webpage_url" in video
        assert "organization" in video
        assert video["organization"] == "Intuit"


@pytest.mark.integration
def test_organization_search_with_aliases():
    """Test search with organization aliases."""
    result = subprocess.run(
        [
            "python", "-m", "casestudypilot", "search-organization", "IBM",
            "--aliases", "International Business Machines",
            "--aliases", "IBM Corporation",
        ],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode in [0, 1]
    assert Path("search_results.json").exists()


@pytest.mark.integration
def test_organization_search_nonexistent():
    """Test searching for organization with no videos."""
    result = subprocess.run(
        [
            "python", "-m", "casestudypilot", "search-organization",
            "NonexistentCompanyXYZ123",
        ],
        capture_output=True,
        text=True,
    )
    
    # Should exit with warning (no results)
    assert result.returncode == 1
    
    # Should still create empty results file
    assert Path("search_results.json").exists()
    
    with open("search_results.json") as f:
        results = json.load(f)
    assert results == []
```

**Step 2: Run integration tests**

```bash
pytest tests/integration/test_organization_workflow.py -v -m integration
```

Expected: PASS (may be slow due to real API calls)

**Step 3: Commit tests**

```bash
git add tests/integration/test_organization_workflow.py
git commit -m "test: add organization workflow integration tests"
```

---

## Task 6: Create Agent Invocation Instructions

**Files:**
- Create: `.github/AGENT_INVOCATION.md`

**Step 1: Write invocation guide**

Create instructions for how to trigger agents:

```markdown
# Agent Invocation Guide

## Organization Search Agent

**Trigger:** Issue filed with template "Organization Content Request"

**Manual Invocation:**

```bash
# In GitHub issue comments
@organization-search-agent

# Or via gh CLI
gh issue comment <issue-number> --body "@organization-search-agent"
```

**Expected Behavior:**
1. Agent reads issue body for organization name and content type
2. Searches CNCF YouTube channel
3. Creates sub-issues for each video found
4. Posts progress update to parent epic
5. Sub-issues automatically trigger content agents

**Required Labels:**
- `automation`
- `epic`
- `organization`

**Required Fields:**
- Organization name
- Content type (Case Study or Reference Architecture)

**Example Issue Body:**
```
Organization Name: Intuit
Content Type: Case Study
```

## Troubleshooting

**Agent doesn't respond:**
- Check issue has correct labels
- Verify organization name is provided
- Ensure gh CLI is authenticated

**No videos found:**
- Try adding name aliases
- Check spelling of organization name
- Search CNCF YouTube manually to verify videos exist

**Sub-issues not created:**
- Check gh CLI permissions
- Verify rate limits not exceeded
- Look for error comments in epic issue
```

**Step 2: Commit invocation guide**

```bash
git add .github/AGENT_INVOCATION.md
git commit -m "docs: add agent invocation guide"
```

---

## Task 7: Update Issue Template Config

**Files:**
- Modify: `.github/ISSUE_TEMPLATE/config.yml`

**Step 1: Add organization template to config**

Update config to include new template:

```yaml
blank_issues_enabled: false
contact_links:
  - name: 📚 Documentation
    url: https://github.com/cncf/casestudypilot/blob/main/README.md
    about: Read the full documentation
  - name: 💬 Discussions
    url: https://github.com/cncf/casestudypilot/discussions
    about: Ask questions and discuss features
```

**Step 2: Verify template ordering**

Ensure templates appear in logical order:
1. Content Generation Request (individual videos)
2. **Organization Content Request (NEW - batch operations)**
3. Epic Implementation (for development)

**Step 3: Commit config**

```bash
git add .github/ISSUE_TEMPLATE/config.yml
git commit -m "chore: update issue template config"
```

---

## Task 8: Create Example Epic

**Files:**
- Create: `docs/examples/organization-epic-example.md`

**Step 1: Write example walkthrough**

Create detailed example:

```markdown
# Organization Epic Example: Intuit

This document shows an example of the organization batch generation workflow.

## Initial Issue

**Title:** [Organization] Intuit  
**Labels:** `automation`, `epic`, `organization`

**Body:**
```
Organization Name: Intuit
Content Type: Case Study
Name Variations:
- Intuit Inc
- Intuit Software
```

## Agent Processing

**Step 1: Search CNCF Channel**
```bash
python -m casestudypilot search-organization "Intuit" --months 18
```

**Results:** 3 videos found
- "Intuit's Cloud Native Journey - KubeCon EU 2025"
- "How Intuit Uses Argo CD for GitOps - KubeCon NA 2024"  
- "Intuit Inc Platform Evolution - CloudNativeCon 2024"

**Step 2: Create Sub-Issues**

Sub-issue #101:
- Title: [Content Request] Intuit's Cloud Native Journey - KubeCon EU 2025
- Labels: `automation`, `org/intuit`, `epic-100`, `case-study`
- Body: Auto-generated with video URL

Sub-issue #102:
- Title: [Content Request] How Intuit Uses Argo CD for GitOps
- Labels: `automation`, `org/intuit`, `epic-100`, `case-study`

Sub-issue #103:
- Title: [Content Request] Intuit Inc Platform Evolution
- Labels: `automation`, `org/intuit`, `epic-100`, `case-study`

**Step 3: Update Epic**

Epic #100 receives comment:
```
✅ Organization Search Complete

Organization: Intuit
Content Type: Case Study
Search Window: Past 18 months

---

Results:
- Total videos found: 3
- New content: 3 sub-issues created
- Existing content: 0

Sub-issues: #101, #102, #103
```

## Content Generation

Each sub-issue processed independently by case-study-agent:

**Sub-issue #101 → PR #104**
- Creates `case-studies/intuit-cloud-native-journey.md`
- 3 screenshots extracted
- Validation passes (score 0.68)
- PR merged

**Sub-issue #102 → PR #105**
- Creates `case-studies/intuit-argo-cd-gitops.md`
- 3 screenshots
- PR merged

**Sub-issue #103 → PR #106**
- Creates `case-studies/intuit-platform-evolution.md`
- 3 screenshots
- PR merged

## Epic Completion

User reviews all content:
- ✅ intuit-cloud-native-journey.md
- ✅ intuit-argo-cd-gitops.md
- ✅ intuit-platform-evolution.md

User manually closes epic #100:
```
All Intuit case studies generated and reviewed. Content looks great! Closing epic.
```

## Result

- 3 case studies published
- All tagged with organization
- Trackable history in epic
- Individual PRs for review
```

**Step 2: Commit example**

```bash
git add docs/examples/organization-epic-example.md
git commit -m "docs: add organization epic example walkthrough"
```

---

## Testing & Verification

### Manual Testing Checklist

After implementation, manually test:

1. **Issue Template**
   - [ ] Template appears in GitHub issue creation UI
   - [ ] All fields render correctly
   - [ ] Dropdown has correct options
   - [ ] Required fields are enforced

2. **CLI Tool**
   - [ ] `python -m casestudypilot search-organization "Intuit"`
   - [ ] Verify fuzzy matching: "Intuit Inc" matches "Intuit"
   - [ ] Verify date filtering: only past 18 months
   - [ ] Verify output JSON structure

3. **Agent Workflow**
   - [ ] File test organization issue
   - [ ] Verify agent triggers
   - [ ] Check sub-issues created with correct labels
   - [ ] Verify progress comment posted
   - [ ] Check existing content detection

4. **Integration**
   - [ ] Verify sub-issues trigger content agents
   - [ ] Check PRs created correctly
   - [ ] Verify epic tracks all sub-issues
   - [ ] Test manual close of epic

### Automated Testing

```bash
# Run all tests
pytest tests/ -v

# Run only integration tests
pytest tests/integration/ -v -m integration

# Run specific test file
pytest tests/test_youtube_search.py -v
```

### Edge Cases to Test

1. Organization with no videos (empty results)
2. Organization name with special characters
3. Videos where content already exists
4. Very common organization names (avoid false positives)
5. Rate limiting (create many sub-issues)

---

## Deployment

### Pre-deployment Checklist

- [ ] All tests pass
- [ ] Documentation complete
- [ ] Example tested manually
- [ ] Agent workflow validated
- [ ] CLI tool works in production environment

### Deployment Steps

1. Merge all changes to main branch
2. Tag release: `git tag v2.3.0-org-tracking`
3. Push tag: `git push origin v2.3.0-org-tracking`
4. Update CHANGELOG.md
5. Announce feature in discussions

### Post-deployment

- Monitor first organization requests
- Watch for any issues with sub-issue creation
- Verify existing content agents handle org labels correctly
- Gather user feedback

---

## Future Enhancements

**Phase 2 (optional):**
- [ ] Auto-close epic when all sub-issues complete
- [ ] Progress tracker auto-updates
- [ ] Support for custom date ranges
- [ ] Support for other YouTube channels (not just CNCF)
- [ ] Better duplicate detection (check content similarity)
- [ ] Organization profile page (all content from org)

**Phase 3 (optional):**
- [ ] YouTube Data API integration (faster, quota-based)
- [ ] Speaker tracking across videos
- [ ] Technology trend analysis per org
- [ ] Automated org reports (meta-content)

---

## Skills & Tools Used

**Superpowers Skills:**
- @superpowers/brainstorming - Initial design
- @superpowers/writing-plans - This plan
- @superpowers/test-driven-development - TDD approach
- @superpowers/verification-before-completion - Pre-deployment checks

**Technologies:**
- Python 3.12+
- yt-dlp (YouTube metadata)
- GitHub CLI (gh)
- pytest (testing)
- difflib (fuzzy matching)

**Patterns:**
- Agent orchestration
- Issue template-driven workflows
- Epic-based tracking
- Fail-fast validation
- CLI-first design

---

## Success Criteria

✅ Users can file single issue for organization  
✅ Agent discovers all org videos (18 months)  
✅ Sub-issues created with correct labels  
✅ Existing content detected and labeled  
✅ Epic provides progress tracking  
✅ No API keys required (yt-dlp only)  
✅ Fuzzy matching handles name variations  
✅ Manual additions supported  
✅ Documentation complete  
✅ Tests pass  

---

**Ready for execution via @superpowers/executing-plans or @superpowers/subagent-driven-development**
