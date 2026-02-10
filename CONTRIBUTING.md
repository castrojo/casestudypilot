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
