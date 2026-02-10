# Contributing to Skill-Driven LLM Automation Framework

## Overview

This framework is designed for **skill-driven development** where LLM agents are the primary developers. This guide explains how to extend the framework with new skills, agents, and CLI tools.

**Target Audience:** LLM agents (GitHub Copilot, Claude, GPT-4, etc.)

---

## Understanding the Framework

Before contributing, understand the three-layer architecture:

```
AGENTS → Orchestrate workflows (decision trees, error handling)
   ↓
SKILLS → LLM-powered tasks (analysis, generation, correction)
   ↓
CLI TOOLS → Deterministic operations (validation, data fetching)
```

**Read these first:**
1. `README.md` - Framework architecture
2. `AGENTS.md` - Operational guidelines

---

## Finding Implementation Context

Before modifying existing features, **check epic issues** for implementation history.

### Quick Search

```bash
# Search epics by keyword
gh issue list --label "epic" --search "keyword" --state all

# View epic
gh issue view <number>
```

### What Epics Contain

- Architecture decisions and rationale
- Challenges and solutions
- Lessons learned
- Related PRs and docs

**Example:** Before modifying company verification, search for "company" or "MCP" in epics to understand why current approach exists.

See [AGENTS.md - Epic Issues](AGENTS.md#epic-issues-implementation-context-archive) for details.

---

## Adding a New Skill

### When to Add a Skill

Create a new skill when:
- Task requires natural language understanding or generation
- Task is creative/interpretive (not deterministic)
- Task has clear input/output boundaries
- Task can be reused across multiple agents

**Examples:**
- `transcript-analysis` - Extract structured data from text
- `case-study-generation` - Generate polished markdown content
- `blog-post-generation` - Create technical blog posts
- `documentation-analysis` - Audit docs for quality

### Step-by-Step Guide

#### 1. Create Skill Directory

```bash
mkdir -p .github/skills/<skill-name>
```

**Naming conventions:**
- Use kebab-case: `blog-post-generation`, `code-review-analysis`
- Be specific: `transcript-analysis` not just `analysis`
- Use verbs: `generation`, `correction`, `analysis`

#### 2. Create Skill File

Create `.github/skills/<skill-name>/SKILL.md` with this structure:

```markdown
# Skill: skill-name

## Purpose

[1-2 sentence description of what this skill does]

## Input Format

```json
{
  "field1": "type: description",
  "field2": ["array", "of", "items"],
  "field3": {
    "nested": "object"
  }
}
```

## Output Format

```json
{
  "result_field1": "type: description",
  "result_field2": ["type: description"]
}
```

## Execution Instructions

LLM agents will follow these steps to execute this skill:

1. **[Step 1 Name]**
   - What to do
   - How to do it
   - What to avoid

2. **[Step 2 Name]**
   - What to do
   - How to do it
   - What to avoid

3. **[Step 3 Name]**
   - What to do
   - How to do it
   - What to avoid

## Examples

### Example 1: [Description]

**Input:**
```json
{
  "field1": "sample value",
  "field2": ["item1", "item2"]
}
```

**Output:**
```json
{
  "result_field1": "processed value",
  "result_field2": ["result1", "result2"]
}
```

### Example 2: [Description]

[Another example with different input/output]

## Quality Guidelines

- [Guideline 1: e.g., Minimum word count]
- [Guideline 2: e.g., Required sections]
- [Guideline 3: e.g., Formatting requirements]
- [Guideline 4: e.g., Tone and style]

## Common Pitfalls

- ❌ [Don't do this]
- ❌ [Avoid this mistake]
- ✅ [Do this instead]
```

#### 3. Test the Skill Manually

Before integrating with an agent:

1. Create sample input JSON
2. Execute the skill instructions manually
3. Verify output format matches specification
4. Check quality guidelines are met

#### 4. Add Validation (Optional but Recommended)

If the skill output needs validation, create a CLI tool:

**Create:** `casestudypilot/tools/validate_<skill_output>.py`

```python
import sys
import json
from pathlib import Path

def validate_skill_output(output_file: str) -> int:
    """
    Validate output from <skill-name> skill.
    
    Returns:
        0 - PASS (all checks passed)
        1 - WARNING (has warnings, can continue)
        2 - CRITICAL (fatal errors, must stop)
    """
    try:
        data = json.loads(Path(output_file).read_text())
        
        # Check required fields
        if "result_field1" not in data:
            print("❌ CRITICAL: Missing required field 'result_field1'", file=sys.stderr)
            return 2
        
        # Check quality requirements
        if len(data["result_field1"]) < 100:
            print("⚠️ WARNING: result_field1 is short", file=sys.stderr)
            return 1
        
        print("✅ Validation passed")
        return 0
        
    except Exception as e:
        print(f"❌ CRITICAL: {e}", file=sys.stderr)
        return 2
```

**Register in `casestudypilot/__main__.py`:**

```python
@app.command()
def validate_skill_output(
    output_file: str,
):
    """Validate output from <skill-name> skill."""
    exit_code = validate_skill_output(output_file)
    sys.exit(exit_code)
```

#### 5. Document the Skill

Update `README.md`:

```markdown
### Layer 2: Skills (LLM-Powered)

| Skill | Input | Output | Purpose |
|-------|-------|--------|---------|
| ... existing skills ... |
| `<skill-name>` | <description> | <description> | <purpose> |
```

#### 6. Reference from Agent

Add skill invocation to relevant agent workflow:

```markdown
### Step N: Apply <Skill Name> Skill

- Use skill: `<skill-name>`
- Input: [Prepare from previous step]
- Output: [Save to file]

**Validation (if applicable):**
```bash
python -m casestudypilot validate-<skill-output> output.json
```

**Check exit code:**
- Exit 0: Continue
- Exit 1: Log warning, continue
- Exit 2: Post error, STOP
```

---

## Adding a New Agent

### When to Add an Agent

Create a new agent when:
- You have a complete end-to-end workflow
- Workflow combines multiple CLI tools and skills
- Workflow needs orchestration logic (decision trees)
- Workflow is triggered by user action (issue, PR, etc.)

**Examples:**
- `case-study-agent` - Generate case studies from videos
- `blog-post-agent` - Create blog posts from transcripts
- `documentation-agent` - Audit and fix documentation
- `code-review-agent` - Analyze PRs for quality

### Step-by-Step Guide

#### 1. Plan the Workflow

Before writing anything, answer:

1. **What triggers this agent?** (GitHub issue label? PR comment?)
2. **What are the inputs?** (YouTube URL? Code files? Text?)
3. **What are the outputs?** (Markdown file? PR? Issue comment?)
4. **What skills will you use?** (Existing or new?)
5. **What CLI tools will you need?** (Existing or new?)
6. **What can go wrong?** (Empty input? API failures? Validation failures?)

#### 2. Create Agent File

Create `.github/agents/<agent-name>.md`:

```markdown
---
name: agent-name
description: [One-line description of what this agent does]
version: 1.0.0
---

# Agent Name

## Mission

[2-3 sentences explaining what this agent automates]

## Workflow (N Steps)

### Step 0: Pre-flight Validation (Optional but Recommended)

- Verify environment is ready
- Validate trigger conditions
- Check required inputs exist
- **STOP if any validation fails**

### Step 1: [Action Name]

[Description of what happens in this step]

```bash
# CLI command if applicable
python -m casestudypilot <command> <args>
```

**Validation (if applicable):**
```bash
python -m casestudypilot validate-<something> data.json
```

**Check exit code:**
- Exit 0: Continue to Step 2
- Exit 1: Log warning, continue to Step 2
- Exit 2: Post error, close issue with label `validation-failed-<type>`, STOP

**Error Template (if CRITICAL):**
```markdown
❌ **Validation Failed: [Description]**

[What went wrong]

**Critical Issues:**
- [Issue 1]
- [Issue 2]

**Action Required:**
[What user should do]
```

### Step 2: Apply [Skill Name] Skill

- Use skill: `<skill-name>`
- Input: [Prepare from Step 1 output]
  ```json
  {
    "field1": "from step 1",
    "field2": "from step 1"
  }
  ```
- Output: [Save to `<filename>.json`]

### Step 3: [Continue with more steps...]

[Repeat for all steps]

### Step N: Create Pull Request

- Create PR from branch
- PR title: `[Type]: [Description]`
- PR description should include:
  - Source information
  - Validation summary
  - Quality metrics
  - Review checklist

PR Description Template:
```markdown
# [Title]

Generated from: [source]

## Validation Summary

**[Checkpoint 1]:** ✅ PASS / ⚠️ WARNING / ❌ CRITICAL
[Details]

**[Checkpoint 2]:** ✅ PASS / ⚠️ WARNING / ❌ CRITICAL
[Details]

## Review Checklist

- [ ] [Item 1]
- [ ] [Item 2]
```

## Error Handling

[List all error scenarios with templates]

### [Error Type 1]

```markdown
❌ Error: [Description]
[Details]
[Action Required]
```

### [Error Type 2]

[Continue for all error types]

## Environment Setup

The Python environment is configured via GitHub Actions workflow: `.github/workflows/<setup-file>.yml`

Required files:
- [List required files and dependencies]

## Quality Standards

- **[Standard 1]:** [Description and threshold]
- **[Standard 2]:** [Description and threshold]
- **[Standard 3]:** [Description and threshold]

## Communication Style

- [How to communicate with users]
- [Tone and formatting]
```

#### 3. Create GitHub Workflow (Optional)

If the agent should trigger automatically:

Create `.github/workflows/<agent-name>-trigger.yml`:

```yaml
name: Auto-invoke <Agent Name>

on:
  issues:
    types: [opened, labeled]

jobs:
  invoke-agent:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, '<trigger-label>')
    
    permissions:
      issues: write
      pull-requests: write
      contents: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Invoke Agent
        run: |
          gh issue comment ${{ github.event.issue.number }} --body "@<agent-name> please process this request"
        env:
          GH_TOKEN: ${{ github.token }}
```

#### 4. Test the Agent End-to-End

1. Create a test issue with appropriate trigger
2. Invoke the agent manually
3. Verify each step executes correctly
4. Check validation checkpoints work
5. Verify error handling works
6. Confirm PR is created correctly

#### 5. Document the Agent

Update `README.md`:

```markdown
### Layer 1: Agents (Orchestration)

| Agent | Version | Workflow | Validation Checkpoints |
|-------|---------|----------|------------------------|
| ... existing agents ... |
| `<agent-name>` | 1.0.0 | N steps | M fail-fast validations |
```

Update `AGENTS.md` with a workflow summary if it's substantially different from existing patterns.

---

## Adding a New CLI Tool

### When to Add a CLI Tool

Create a new CLI tool when:
- Operation is deterministic (same input → same output)
- Operation requires validation logic
- Operation involves file I/O or API calls
- Operation needs to be independently testable

**Examples:**
- `youtube-data` - Fetch video transcripts
- `validate-transcript` - Check transcript quality
- `extract-screenshots` - Download video frames
- `assemble` - Render Jinja2 template

### Step-by-Step Guide

#### 1. Create Tool Module

Create `casestudypilot/tools/<tool_name>.py`:

```python
"""
<Tool Name>

Description of what this tool does.
"""

import sys
import json
from pathlib import Path
from typing import Optional

def main(
    input_arg: str,
    optional_arg: Optional[str] = None,
    output: str = "output.json"
) -> int:
    """
    [Description of what this function does]
    
    Args:
        input_arg: [Description]
        optional_arg: [Description]
        output: [Description]
    
    Returns:
        0 - Success (operation completed)
        1 - Warning (operation completed with warnings)
        2 - Critical (operation failed, cannot continue)
    """
    try:
        # 1. Load/process input
        input_data = load_input(input_arg)
        
        # 2. Validate input (CRITICAL failures)
        if not validate_input(input_data):
            print("❌ CRITICAL: Invalid input", file=sys.stderr)
            return 2
        
        # 3. Perform operation
        result = process_data(input_data, optional_arg)
        
        # 4. Check for warnings
        if has_warnings(result):
            print("⚠️ WARNING: Operation completed with warnings", file=sys.stderr)
            print(f"Details: {result.warnings}", file=sys.stderr)
            
        # 5. Save output
        Path(output).write_text(json.dumps(result.data, indent=2))
        print(f"✅ Success: Output written to {output}")
        
        return 1 if has_warnings(result) else 0
        
    except Exception as e:
        print(f"❌ CRITICAL: {e}", file=sys.stderr)
        return 2


def load_input(input_arg: str):
    """Helper function to load input"""
    pass


def validate_input(data) -> bool:
    """Helper function to validate input"""
    pass


def process_data(data, optional_arg):
    """Helper function to process data"""
    pass


def has_warnings(result) -> bool:
    """Helper function to check for warnings"""
    pass
```

#### 2. Register CLI Command

Edit `casestudypilot/__main__.py`:

```python
from casestudypilot.tools import <tool_name>

@app.command()
def <command_name>(
    input_arg: str = typer.Argument(..., help="Description"),
    optional_arg: str = typer.Option(None, help="Description"),
    output: str = typer.Option("output.json", "--output", "-o", help="Output file path"),
):
    """
    [Description of what this command does]
    
    Exit codes:
        0 - Success
        1 - Warning (check stderr for details)
        2 - Critical failure (workflow should stop)
    """
    exit_code = <tool_name>.main(input_arg, optional_arg, output)
    sys.exit(exit_code)
```

#### 3. Write Tests

Create `tests/test_<tool_name>.py`:

```python
"""
Tests for <tool_name>
"""

import pytest
from pathlib import Path
from casestudypilot.tools import <tool_name>

def test_success_case(tmp_path):
    """Test successful operation"""
    output = tmp_path / "output.json"
    result = <tool_name>.main("valid_input", output=str(output))
    
    assert result == 0
    assert output.exists()
    data = json.loads(output.read_text())
    assert "expected_field" in data


def test_warning_case(tmp_path):
    """Test operation with warnings"""
    output = tmp_path / "output.json"
    result = <tool_name>.main("warning_input", output=str(output))
    
    assert result == 1  # Warning exit code
    assert output.exists()


def test_critical_failure(tmp_path):
    """Test critical failure"""
    output = tmp_path / "output.json"
    result = <tool_name>.main("invalid_input", output=str(output))
    
    assert result == 2  # Critical exit code
    assert not output.exists()  # No output on failure


def test_edge_cases(tmp_path):
    """Test edge cases"""
    # Empty input
    result = <tool_name>.main("", output=str(tmp_path / "output.json"))
    assert result == 2
    
    # Malformed input
    result = <tool_name>.main("malformed", output=str(tmp_path / "output.json"))
    assert result == 2
```

#### 4. Run Tests

```bash
# Run tests for your new tool
pytest tests/test_<tool_name>.py -v

# Run all tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=casestudypilot --cov-report=html
```

#### 5. Document the CLI Command

Update `README.md`:

```markdown
#### Data Operations (N commands)

```bash
# [Description of what this command does]
python -m casestudypilot <command-name> <input> [--optional-arg value] [--output file.json]
```
```

Or if it's a validation command:

```markdown
#### Validation Commands (N commands - Fail-Fast Architecture)

```bash
# [Description of what this validates]
python -m casestudypilot <command-name> <input> [--optional-arg value]
# Exit: 0=pass, 1=warning, 2=critical
```
```

#### 6. Reference from Agent Workflows

Add the CLI command to relevant agent workflows:

```markdown
### Step N: [Action]

```bash
python -m casestudypilot <command-name> <input>
```

**Validation:**
```bash
python -m casestudypilot validate-<output> output.json
```

**Check exit code:**
- Exit 0: Continue
- Exit 1: Log warning, continue
- Exit 2: Post error, STOP
```

---

## Modifying Reference Architecture System

### Overview

The reference architecture system has unique components that may need modification:

1. **5-Dimensional Technical Depth Scoring** - Algorithm in `validate_reference_architecture.py`
2. **Deep Analysis Validation** - Checks for CNCF projects, layers, patterns in `validate_deep_analysis.py`
3. **Jinja2 Template** - 13-section structure in `templates/reference_architecture.md.j2`
4. **LLM Skills** - 3 specialized skills for deep analysis, diagrams, and generation

### Modifying the Technical Depth Scoring Algorithm

**File:** `casestudypilot/tools/validate_reference_architecture.py`

The scoring algorithm uses 5 weighted components:

```python
technical_depth_score = (
    0.25 * cncf_project_depth +      # 25% weight
    0.20 * technical_specificity +    # 20% weight
    0.20 * implementation_detail +    # 20% weight
    0.20 * metric_quality +           # 20% weight
    0.15 * architecture_completeness  # 15% weight
)
```

#### Changing Score Weights

To adjust the importance of each dimension:

1. Locate the `calculate_technical_depth_score()` function
2. Modify the weights (must sum to 1.0):
   ```python
   score = (
       0.30 * cncf_project_depth +      # Increased importance
       0.15 * technical_specificity +    # Decreased
       0.20 * implementation_detail +    
       0.20 * metric_quality +           
       0.15 * architecture_completeness
   )
   ```
3. Update the docstring to document the new weights
4. Run tests: `pytest tests/test_validate_reference_architecture.py -v`

#### Adding a New Scoring Dimension

To add a 6th dimension (e.g., "observability_depth"):

1. Create scoring function:
   ```python
   def score_observability_depth(data: dict) -> float:
       """
       Score observability implementation depth.
       
       Returns: 0.0-1.0
       """
       score = 0.0
       
       # Check for observability section
       if "observability_operations" in data.get("sections", {}):
           score += 0.3
       
       # Check for monitoring stack details
       obs_text = data.get("sections", {}).get("observability_operations", "")
       if "Prometheus" in obs_text or "Grafana" in obs_text:
           score += 0.3
       
       # Check for alerting details
       if "alert" in obs_text.lower():
           score += 0.2
       
       # Check for SLO/SLI mentions
       if "SLO" in obs_text or "SLI" in obs_text:
           score += 0.2
       
       return min(score, 1.0)
   ```

2. Update main scoring function:
   ```python
   score = (
       0.20 * cncf_project_depth +          # Rebalanced
       0.15 * technical_specificity +
       0.15 * implementation_detail +
       0.15 * metric_quality +
       0.15 * architecture_completeness +
       0.20 * score_observability_depth(data)  # New dimension
   )
   ```

3. Add test cases in `tests/test_validate_reference_architecture.py`

4. Update `AGENTS.md` documentation with new scoring dimensions

#### Changing Score Thresholds

Current thresholds:
- **≥0.70**: PASS (exit code 0)
- **0.60-0.69**: WARNING (exit code 1)
- **<0.60**: CRITICAL (exit code 2)

To change thresholds:

1. Locate threshold constants in `validate_reference_architecture.py`:
   ```python
   THRESHOLD_PASS = 0.70
   THRESHOLD_WARN = 0.60
   ```

2. Modify values:
   ```python
   THRESHOLD_PASS = 0.75  # More stringent
   THRESHOLD_WARN = 0.65
   ```

3. Update error messages to reflect new thresholds

4. Update `README.md` and `AGENTS.md` documentation

5. Test with existing reference architectures to ensure reasonable pass rates

### Modifying Deep Analysis Validation

**File:** `casestudypilot/tools/validate_deep_analysis.py`

Current validation checks:

| Check | Pass | Warn | Critical |
|-------|------|------|----------|
| CNCF Projects | 5+ | 4 | <4 |
| Architecture Layers | All 3 | - | <3 |
| Integration Patterns | 2+ | 1 | 0 |
| Screenshots | 6+ | 4-5 | <4 |
| Sections | All 6 required | - | Missing any |
| Word Counts | 200-800 per section | - | <200 or >800 |

#### Changing Validation Thresholds

To require more CNCF projects:

```python
# Change from 5+ to 7+ required
if num_projects >= 7:
    print("✅ CNCF projects: {num_projects} (pass)")
    return 0
elif num_projects >= 5:
    print(f"⚠️ CNCF projects: {num_projects} (warning, 7+ recommended)")
    return 1
else:
    print(f"❌ CNCF projects: {num_projects} (critical, 5+ required)")
    return 2
```

#### Adding New Validation Checks

To add a check for "security patterns":

```python
def validate_security_patterns(data: dict) -> int:
    """
    Validate security patterns are documented.
    
    Returns: 0=pass, 1=warn, 2=critical
    """
    patterns = data.get("security_patterns", [])
    
    if len(patterns) >= 3:
        print(f"✅ Security patterns: {len(patterns)}")
        return 0
    elif len(patterns) >= 1:
        print(f"⚠️ Security patterns: {len(patterns)} (3+ recommended)")
        return 1
    else:
        print("❌ No security patterns documented (critical)")
        return 2
```

Then call in main validation function and combine exit codes appropriately.

### Modifying the Jinja2 Template

**File:** `templates/reference_architecture.md.j2`

The template defines the 13-section structure and formatting.

#### Adding a New Section

To add a "Cost Optimization" section:

1. Update the template after "Deployment Architecture":
   ```jinja2
   ## Cost Optimization
   
   {{ sections.cost_optimization }}
   
   {% if screenshots_by_section.cost_optimization %}
   ### Visual Reference
   {% for screenshot in screenshots_by_section.cost_optimization %}
   ![{{ screenshot.caption }}](images/{{ company_slug }}/{{ screenshot.filename }})
   *{{ screenshot.caption }}*
   {% endfor %}
   {% endif %}
   ```

2. Update `reference-architecture-generation` skill to generate the new section

3. Update validation in `validate_reference_architecture.py` to expect the section

4. Test template rendering with sample data

#### Changing Section Order

Rearrange sections in the template file - the order in the template determines output order.

#### Modifying YAML Frontmatter

To add new metadata fields:

```jinja2
---
title: "{{ title }}"
subtitle: "{{ subtitle }}"
company: "{{ company }}"
industry: "{{ industry }}"
video_url: "{{ video_url }}"
publication_date: "{{ publication_date }}"
tab_status: "{{ tab_status }}"
primary_patterns: {{ primary_patterns | tojson }}
complexity_level: "{{ complexity_level }}"  # NEW FIELD
estimated_read_time: {{ estimated_read_time }}  # NEW FIELD
---
```

Then update `assemble_reference_architecture.py` to provide these values.

### Modifying LLM Skills

#### Transcript Deep Analysis Skill

**File:** `.github/skills/transcript-deep-analysis/SKILL.md`

**When to modify:**
- Change required CNCF project count
- Add new analysis dimensions (e.g., cost data, carbon footprint)
- Modify screenshot identification logic

**Process:**
1. Update input/output format if needed
2. Modify execution instructions
3. Update examples to reflect changes
4. Test manually with real transcripts

#### Architecture Diagram Specification Skill

**File:** `.github/skills/architecture-diagram-specification/SKILL.md`

**When to modify:**
- Add new diagram types (sequence, deployment)
- Change component identification logic
- Modify textual description format

**Process:**
1. Update output format
2. Add new diagram type instructions
3. Provide examples of new diagram types
4. Test with diverse architectures

#### Reference Architecture Generation Skill

**File:** `.github/skills/reference-architecture-generation/SKILL.md`

**When to modify:**
- Change section structure (add/remove/reorder)
- Modify writing style or tone
- Adjust word count targets
- Add new quality guidelines

**Process:**
1. Update output format with new sections
2. Modify step-by-step execution instructions
3. Update quality guidelines
4. Test with multiple transcript types

### Testing Reference Architecture Changes

#### Unit Tests

```bash
# Test deep analysis validation
pytest tests/test_validate_deep_analysis.py -v

# Test technical depth scoring
pytest tests/test_validate_reference_architecture.py -v

# Test assembly
pytest tests/test_assemble_reference_architecture.py -v

# All reference architecture tests
pytest tests/test_*reference*.py -v
```

#### Integration Testing

1. **Find test video**: 15-40 min, 5+ CNCF projects, detailed architecture
2. **Run agent workflow**: Follow all 18 steps manually
3. **Check validation**: Verify all checkpoints pass/warn/fail as expected
4. **Inspect output**: Review generated markdown for quality
5. **Test edge cases**: Short video, few projects, missing diagrams

#### Validation Testing

Create test fixtures with various scores:

```python
# tests/test_validate_reference_architecture.py

def test_scoring_high_quality():
    """Test with high-quality reference architecture (score ≥0.70)"""
    data = {
        "cncf_projects": [
            {"name": "Kubernetes", "description": "...detailed..."},
            # 5+ projects total
        ],
        "sections": {
            "executive_summary": "..." * 200,  # Good length
            # All sections with quality content
        },
        # High-quality architecture data
    }
    
    score = calculate_technical_depth_score(data)
    assert score >= 0.70

def test_scoring_borderline():
    """Test borderline quality (0.60-0.69)"""
    # Less detailed content
    score = calculate_technical_depth_score(data)
    assert 0.60 <= score < 0.70

def test_scoring_insufficient():
    """Test insufficient quality (<0.60)"""
    # Minimal content
    score = calculate_technical_depth_score(data)
    assert score < 0.60
```

### Updating Documentation After Changes

When you modify the reference architecture system:

1. **README.md**: Update comparison table, quality thresholds, CLI commands
2. **AGENTS.md**: Update technical depth scoring section, validation checkpoints
3. **CONTRIBUTING.md**: This file - document new modification patterns
4. **Agent workflow**: `.github/agents/reference-architecture-agent.md` - update steps
5. **Skills**: Update relevant skill files if input/output changes

### Common Modification Scenarios

#### Scenario 1: Make Scoring More Stringent

**Goal:** Increase quality bar for TAB submissions

**Changes:**
1. Increase PASS threshold from 0.70 to 0.75
2. Increase WARN threshold from 0.60 to 0.65
3. Increase CNCF project requirement from 5+ to 7+
4. Increase word count minimum from 2000 to 2500

**Testing:** Run against existing passing reference architectures, expect some to move to WARNING.

#### Scenario 2: Add Security Focus

**Goal:** Emphasize security in reference architectures

**Changes:**
1. Add 6th scoring dimension: "security_depth" (15% weight)
2. Add security validation in `validate_deep_analysis.py`
3. Make "Security Considerations" section longer (400-600 words)
4. Add security patterns to deep analysis skill

**Testing:** Test with security-focused and non-security videos.

#### Scenario 3: Support Shorter Videos

**Goal:** Allow 10-15 minute videos to generate reference architectures

**Changes:**
1. Lower transcript minimum from 2000 to 1500 characters
2. Lower CNCF project requirement from 5+ to 4+
3. Allow 1500-4000 word output range
4. Adjust scoring for shorter content

**Testing:** Test with 10-15 min videos that have good technical depth.

---

## Best Practices

### For Skills

1. **Be Specific:** Clear, unambiguous instructions for LLMs
2. **Use Examples:** Provide 2-3 input/output examples
3. **Define Quality:** Explicit quality guidelines
4. **Structured Output:** Always use JSON for complex outputs
5. **Avoid Ambiguity:** Don't leave room for interpretation

### For Agents

1. **Fail-Fast:** Validate early and stop on critical errors
2. **Clear Errors:** Provide actionable error messages for users
3. **Exit Codes:** Always check CLI tool exit codes
4. **Atomic Commits:** Commit related files together
5. **Document Steps:** Number steps, use imperative language

### For CLI Tools

1. **Return Exit Codes:** 0=success, 1=warning, 2=critical
2. **Meaningful Output:** Use stderr for errors, stdout for results
3. **Test Edge Cases:** Empty input, malformed data, API failures
4. **Handle Exceptions:** Catch exceptions, return exit code 2
5. **Clear Help Text:** Document what the command does

---

## Testing Guidelines

### Manual Testing Workflow

1. **Test in isolation:** Each component separately
2. **Test integration:** Components working together
3. **Test error paths:** What happens when things fail?
4. **Test edge cases:** Empty input, large input, malformed input
5. **Test end-to-end:** Full workflow from trigger to PR

### Automated Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=casestudypilot --cov-report=html

# Run specific test file
pytest tests/test_<name>.py -v

# Run specific test function
pytest tests/test_<name>.py::test_function -v
```

### Test Coverage Goals

- **CLI Tools:** 100% coverage (deterministic, testable)
- **Validation:** 100% coverage (critical for quality)
- **Skills:** Manual testing only (LLM-generated content)
- **Agents:** Manual end-to-end testing

---

## Documentation Standards

### Keep These Updated

When you add or modify components:

1. **README.md** - Framework overview, CLI commands, agent/skill tables
2. **AGENTS.md** - Operational guidelines, patterns, examples
3. **CONTRIBUTING.md** - This file, if extension process changes
4. **Agent files** - `.github/agents/<agent>.md` version numbers and steps
5. **Skill files** - `.github/skills/<skill>/SKILL.md` input/output formats

### Documentation Style

- **For LLMs:** Imperative language, decision trees, structured tables
- **For Humans:** Conversational, examples, quick start guides
- **For Both:** Clear hierarchies, consistent formatting, comprehensive examples

---

## Getting Help

### Resources

1. **README.md** - Understand framework architecture
2. **AGENTS.md** - Learn operational patterns
3. **Existing skills** - Study `.github/skills/*/SKILL.md` as templates
4. **Existing agents** - Study `.github/agents/*.md` as templates
5. **Test files** - See `tests/` for testing patterns

### Common Questions

**Q: Should this be a skill or a CLI tool?**  
A: If it requires natural language understanding/generation → Skill. If it's deterministic (testable) → CLI tool.

**Q: When do I need validation?**  
A: At every critical decision point where bad data could cause hallucination or workflow failure.

**Q: What exit code should I return?**  
A: 0 (success, continue), 1 (warning, continue), 2 (critical, stop workflow immediately).

**Q: How do I test LLM skills?**  
A: Manually execute the skill instructions with sample inputs, verify output format and quality.

**Q: Should I update docs before or after implementing?**  
A: After implementation, immediately before committing. Keep docs and reality in sync.

---

## Contribution Checklist

Before submitting changes:

- [ ] New skill has SKILL.md file with complete documentation
- [ ] New agent has workflow file with all steps and error templates
- [ ] New CLI tool has implementation, tests, and CLI registration
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] README.md updated with new components
- [ ] AGENTS.md updated if new patterns introduced
- [ ] Documentation reflects reality (no outdated information)
- [ ] Tested end-to-end manually
- [ ] Version numbers updated if modifying existing components

---

**Framework Status:** ✅ Production Ready - Ready for Skill Expansion  
**Version:** 2.2.0  
**Last Updated:** February 9, 2026
