---
name: epic-creation
description: Create GitHub epic issue from any implementation plan file
version: 1.0.0
---

# Epic Creation

## Purpose

Create a GitHub epic issue from an implementation plan file, regardless of format or structure.

## When to Use

- When `writing-plans` completes (automatic)
- When user says "create an epic for plan X" (manual)
- When asked to create epics for existing plans

**Announce at start:** "I'm using the epic-creation skill to create an epic issue."

## Input Requirements

- **Plan file path** (required)
- **Force create** (optional, default false) - create even if plan already has epic reference

## Execution Instructions

### Step 1: Read and Understand the Plan

Read the plan file completely. Use your understanding to identify:

- **Title/Feature name** - What is being implemented?
- **Goal** - What does it accomplish? (aim for 1 sentence)
- **Architecture** - How does it work? (aim for 2-3 sentences)
- **Tech Stack** - What technologies are used?
- **Tasks** - Major implementation tasks (for checklist)

**Flexible reading:** Plans may have different formats:
- Superpowers standard format with headers
- Simple numbered lists
- Prose descriptions
- Bullet points
- Other structures

**Your job:** Extract the essence regardless of format.

### Step 2: Check for Existing Epic

```bash
PLAN_FILE="<plan-file-path>"

# Check if plan already references an epic
if grep -q "Epic Issue:" "$PLAN_FILE" || grep -q "epic.*#[0-9]" "$PLAN_FILE"; then
  EXISTING_EPIC=$(grep -oP '(?:Epic Issue:|epic).*#\K\d+' "$PLAN_FILE" | head -1)
  echo "⚠️ Plan already linked to epic #$EXISTING_EPIC"
  
  # If not forcing, stop here
  if [ "$FORCE" != "true" ]; then
    echo "Use force=true to create new epic anyway"
    exit 0
  fi
fi
```

### Step 3: Build Epic Body

Create the epic issue body with extracted information:

```bash
cat > epic_body.md <<EOF
## 📋 Plan File

\`$PLAN_FILE\`

## 🎯 Goal

$GOAL

## 🏗️ Architecture

$ARCH

## 🛠️ Tech Stack

$TECH

## ✅ Tasks

$TASKS

---

**Status:** 🟡 In Progress

---

## 📚 Implementation Journey

<!-- JOURNEY_START -->

*Journey documentation will be added upon completion.*

<!-- JOURNEY_END -->
EOF
```

**Handling missing information:**
- If goal not found: Use "Implementation of [Title]"
- If architecture not found: Use "See plan file for details"
- If tech stack not found: Use "See plan file for details"
- If tasks not found: Use "- [ ] See plan file for task breakdown"

**Be practical:** Some plans won't have all information clearly labeled. That's okay - extract what you can.

### Step 4: Create Epic Issue

```bash
# Create the issue
gh issue create \
  --title "$TITLE" \
  --label "epic,planning" \
  --body "$(cat epic_body.md)"

# Capture the issue number
EPIC_NUMBER=$(gh issue list --label "epic" --limit 1 --json number --jq '.[0].number')
echo "Created epic issue: #$EPIC_NUMBER"
```

### Step 5: Update Plan with Epic Reference

Add epic reference to the plan file:

```bash
# Add epic reference near the top of the plan (after tech stack if present)
# Find a good insertion point
if grep -q "^\*\*Tech Stack:\*\*" "$PLAN_FILE"; then
  # Insert after tech stack
  sed -i "/^\*\*Tech Stack:\*\*/a\\n**Epic Issue:** #$EPIC_NUMBER" "$PLAN_FILE"
elif grep -q "^---" "$PLAN_FILE"; then
  # Insert after first separator
  sed -i "0,/^---/s/^---/---\n\n**Epic Issue:** #$EPIC_NUMBER/" "$PLAN_FILE"
else
  # Insert after first paragraph/section
  sed -i "4a\\n**Epic Issue:** #$EPIC_NUMBER" "$PLAN_FILE"
fi

# Commit the update
git add "$PLAN_FILE"
git commit -m "docs: link plan to epic issue #$EPIC_NUMBER"
```

### Step 6: Announce

Tell the user:

```
✅ Epic issue created: #$EPIC_NUMBER
✅ Plan updated with epic reference

Epic URL: https://github.com/<owner>/<repo>/issues/$EPIC_NUMBER
```

## Quality Guidelines

**Epic creation should be:**
- ✅ **Fast** - Don't overthink extraction, use common sense
- ✅ **Flexible** - Handle any reasonable plan format
- ✅ **Practical** - Missing info? Use sensible defaults
- ✅ **Linked** - Always update plan with epic reference

**Avoid:**
- ❌ Rigid format requirements
- ❌ Failing if plan structure is non-standard
- ❌ Over-engineering the extraction logic

## Examples

### Example 1: Standard Superpowers Plan

**Plan structure:**
```markdown
# Feature Implementation Plan

**Goal:** Build the feature
**Architecture:** Uses X and Y
**Tech Stack:** Python, JavaScript

### Task 1: Do thing
### Task 2: Do other thing
```

**Extraction:**
- Title: "Feature"
- Goal: "Build the feature"
- Architecture: "Uses X and Y"
- Tech Stack: "Python, JavaScript"
- Tasks: "Task 1: Do thing", "Task 2: Do other thing"

### Example 2: Non-Standard Plan

**Plan structure:**
```markdown
# Adding Dark Mode

We need to add dark mode to the app. This will involve:

1. Create theme context
2. Add theme toggle
3. Update all components

Technologies: React, CSS-in-JS
```

**Extraction (intelligent reading):**
- Title: "Dark Mode"
- Goal: "Add dark mode to the app"
- Architecture: "Create theme context and update all components with dark mode support"
- Tech Stack: "React, CSS-in-JS"
- Tasks: "Create theme context", "Add theme toggle", "Update all components"

### Example 3: Minimal Plan

**Plan structure:**
```markdown
# Fix Bug #123

Update validation logic to handle edge case.
```

**Extraction (with defaults):**
- Title: "Fix Bug #123"
- Goal: "Update validation logic to handle edge case"
- Architecture: "See plan file for details"
- Tech Stack: "See plan file for details"
- Tasks: "- [ ] See plan file for implementation details"

**Still useful:** Future agents can find this epic and see the linked plan for full context.

## Integration

**Called by:**
- `writing-plans` skill - After plan is saved
- Manual agent invocation - When user requests epic creation
- Batch operations - When processing multiple plans
