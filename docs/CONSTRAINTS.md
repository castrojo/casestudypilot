# Project Constraints and Policies

**Project:** CNCF Case Study Automation  
**Status:** Planning Phase  
**Date:** February 9, 2026

---

## 🚨 CRITICAL: Implementation Approval Policy

### The Rule

**UNDER NO CIRCUMSTANCE shall any implementation changes be made without EXPLICIT approval from the user.**

This is non-negotiable. This is mandatory. This cannot be overridden.

---

## What Requires Approval

### ❌ Prohibited Without Approval

The following actions are **absolutely forbidden** without explicit user approval:

1. **File Operations**
   - Creating new files
   - Modifying existing files
   - Deleting files
   - Renaming files
   - Moving files

2. **Code Changes**
   - Writing any Python code
   - Writing any configuration files
   - Writing any YAML/JSON/MD files
   - Making "quick fixes"
   - Adding "helpful" comments

3. **System Operations**
   - Installing dependencies
   - Running scripts
   - Executing commands (beyond read-only operations)
   - Modifying git state
   - Changing permissions

4. **Configuration Changes**
   - Updating .gitignore
   - Modifying requirements.txt
   - Changing GitHub Actions workflows
   - Adding environment variables

5. **"Helpful" Actions**
   - "I'll just add this while I'm here"
   - "This is obviously what they meant"
   - "It's just a small change"
   - "I'm sure they'll want this"

### ✅ Allowed Without Approval

The following are permitted:

1. **Read-Only Operations**
   - Reading files
   - Listing directories
   - Checking git status
   - Viewing file contents
   - Searching code

2. **Planning Activities**
   - Creating documentation (in docs/)
   - Writing planning documents
   - Designing architecture
   - Proposing solutions

3. **Communication**
   - Asking clarifying questions
   - Presenting options
   - Explaining trade-offs
   - Requesting approval

---

## Approval Process

### Step 1: Present Proposal

Before making ANY change, present:

1. **What** you want to change
2. **Why** it needs to change
3. **How** you will change it
4. **What** the impact/risks are
5. **Alternatives** considered

**Example:**
```
I propose creating the following file:

File: casestudypilot/__init__.py
Content: Empty file (Python package marker)
Reason: Required for Python to recognize directory as package
Impact: Enables import statements to work
Alternatives: Could use namespace package, but standard practice is __init__.py

Request: May I create this file?
```

### Step 2: Wait for Approval

The user must respond with:
- ✅ **"Approved"** - Proceed with the change
- ✅ **"Yes"** - Proceed with the change
- ✅ **"Go ahead"** - Proceed with the change
- ✅ **"Approved with changes: [details]"** - Modify proposal and proceed
- ❌ **"Not approved"** - Do not proceed
- ❌ **"No"** - Do not proceed
- ❌ **"Wait"** - Do not proceed yet

**Silence is NOT approval.** If unclear, ask again.

### Step 3: Execute Only What Was Approved

- Do exactly what was approved
- No "extras"
- No "improvements"
- No "while I'm here" additions

If you think of something else during implementation, **STOP** and request additional approval.

---

## Why This Policy Exists

### The Incident: February 9, 2026

**What happened:**
- User asked to "finish the plan and document everything"
- Agent interpreted this as permission to implement
- Agent created 19 files with ~900 lines of code
- Agent built the entire system without explicit approval

**What should have happened:**
- Agent should have asked: "Should I implement this plan, or just document it?"
- Agent should have presented implementation proposal
- Agent should have waited for explicit approval
- Agent should have only created planning documents

**Lesson learned:**
Instructions to "continue" or "finish" do NOT imply permission to implement.  
Always clarify. Always ask. Always wait for approval.

---

## Exceptions

There are **NO EXCEPTIONS** to this policy.

Even if:
- It seems obvious
- It's just documentation
- It's a small change
- You've done it before
- The user is busy
- You want to be helpful

**STOP. ASK. WAIT FOR APPROVAL.**

---

## Violation Consequences

If this policy is violated:

1. **Stop immediately** when violation is discovered
2. **Acknowledge the violation** explicitly
3. **Present what was done** without approval
4. **Ask for guidance** on how to proceed:
   - Keep the changes?
   - Revert the changes?
   - Modify the changes?
5. **Document the violation** so future agents learn from it

**Do not:**
- Pretend it didn't happen
- Justify why it was okay
- Minimize the violation
- Continue with more changes

---

## Implementation Mode vs. Planning Mode

### Planning Mode (Current)

**Allowed:**
- Create documentation in docs/
- Write specifications
- Design architecture
- Propose solutions
- Create task lists

**Not Allowed:**
- Create implementation files
- Write actual code
- Install dependencies
- Run tests
- Modify configuration

### Implementation Mode

Can only be entered with explicit approval:

**User says:** "Start implementing" or "Create the files" or "Approved to begin implementation"

**Then allowed:**
- Create implementation files
- Write code
- Install dependencies
- Run tests
- Modify configuration

**Still required:**
- Request approval for significant decisions
- Ask when unclear
- Present options for user choice

---

## How to Check for Approval

### Before ANY action, ask yourself:

1. ❓ Did the user explicitly approve this specific action?
2. ❓ Am I in planning mode or implementation mode?
3. ❓ Is this a read-only operation?
4. ❓ Could this change affect the project state?
5. ❓ Am I making assumptions about what the user wants?

**If any answer is unclear → ASK FOR APPROVAL**

### Red Flags (Signs you're about to violate policy):

- "I'll just..."
- "While I'm here..."
- "They probably want..."
- "This is standard practice..."
- "It's just a small..."
- "I'm sure they meant..."

**When you catch yourself with these thoughts → STOP AND ASK**

---

## Communication Templates

### Template 1: Seeking Approval for File Creation

```
I need to create the following file:

**File:** path/to/file.py
**Purpose:** What this file does
**Content Summary:** Brief description of what will be in it
**Dependencies:** What it requires
**Impact:** How it affects the system

**Request:** May I create this file?
```

### Template 2: Seeking Approval for Change

```
I need to modify the following:

**Current State:** What exists now
**Proposed Change:** What I want to change
**Reason:** Why this change is needed
**Impact:** What this affects
**Risks:** What could go wrong

**Request:** May I make this change?
```

### Template 3: Seeking Clarification

```
I'm unclear about the instruction: "[quote user instruction]"

This could mean:
1. [Interpretation A]
2. [Interpretation B]
3. [Interpretation C]

**Question:** Which interpretation is correct, or is it something else?
```

---

## Success Criteria

This policy is being followed successfully when:

- ✅ No files are created without approval
- ✅ No code is written without approval
- ✅ User is asked before every significant action
- ✅ Proposals are clear and detailed
- ✅ Approval is waited for before proceeding
- ✅ Only approved actions are executed
- ✅ No "extras" or "improvements" without approval

---

## Summary

**The Golden Rule:**

> When in doubt, ask.  
> When not in doubt, ask anyway.  
> Always ask before implementation.  
> Always wait for explicit approval.  
> Always do only what was approved.

**Remember:**
- Asking slows things down temporarily
- Not asking causes major problems
- User approval is REQUIRED, not OPTIONAL
- This policy protects both user and agent

---

*This policy is in effect for the entire project lifecycle.*  
*All agents working on this project must read and follow this document.*  
*This policy supersedes all other instructions if there is a conflict.*
