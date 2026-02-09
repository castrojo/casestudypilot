# CNCF Case Study Automation

**Status:** 📋 Planning Phase  
**Ready for Implementation:** Yes

Automate the creation of CNCF end-user case studies from YouTube video interviews using GitHub Copilot custom agents.

---

## What This Will Do

**Input:** GitHub issue with YouTube URL  
**Output:** Pull request with publication-ready case study

**Example:**
```
Issue: "Case Study Request: Intuit GitOps Journey"
URL: https://www.youtube.com/watch?v=V6L-xOUdoRQ

@case-study-agent please generate this case study

→ Agent processes video
→ Agent creates PR with case-studies/intuit.md
```

---

## Architecture

**Agent-Centric Design:**
- GitHub Copilot custom agent orchestrates entire workflow
- Python CLI tools handle data operations
- Agent skills handle AI processing
- Quality validation ensures high-quality output

**No API Keys Required:**
- Uses `youtube-transcript-api` for direct transcript access
- No authentication needed for basic operation
- See `docs/API-KEY-DECISION.md` for rationale

---

## Components (To Be Built)

### 1. Python CLI Tool: `casestudypilot`

Four commands for data operations:

```bash
# Fetch video transcript (no auth required!)
casestudypilot youtube-data <url>

# Verify company is CNCF end-user member
casestudypilot verify-company "Company Name"

# Assemble case study from components
casestudypilot assemble video.json analysis.json sections.json verification.json

# Validate quality
casestudypilot validate case-studies/company.md
```

### 2. GitHub Copilot Custom Agent

**Agent:** `@case-study-agent`  
**Location:** `.github/agents/case-study-agent.md`

Orchestrates 12-step workflow from issue to pull request.

### 3. Agent Skills (3)

1. **transcript-correction** - Fix common transcript errors
2. **transcript-analysis** - Extract structured data
3. **case-study-generation** - Generate polished markdown sections

**Location:** `.github/skills/*/SKILL.md`

### 4. Quality Validation

Multi-factor scoring across:
- Structure (30%): Required sections present
- Content Depth (40%): Word counts per section  
- CNCF Mentions (20%): Projects referenced
- Formatting (10%): Markdown quality

**Passing threshold:** 0.60

---

## Documentation

### For Implementing Agents

📘 **Start here:** `docs/CONSTRAINTS.md` - Critical approval policy  
📋 **Planning:** `docs/PLANNING.md` - Complete specifications  
🔧 **Implementation:** `docs/IMPLEMENTATION-GUIDE.md` - Step-by-step tasks  
🏗️ **Architecture:** `docs/API-KEY-DECISION.md` - Design rationale  
📐 **Design:** `docs/plans/2026-02-09-design.md` - Original design document

### Quick Start for Implementers

1. Read `docs/CONSTRAINTS.md` (mandatory)
2. Read `docs/PLANNING.md` (understand what to build)
3. Follow `docs/IMPLEMENTATION-GUIDE.md` (step-by-step)
4. **Request approval before creating any files**

---

## Key Decisions

### ✅ Simplified: No API Key Required

**Decision:** Remove YouTube Data API requirement  
**Rationale:** User feedback - "seems overkill"  
**Impact:** Zero setup friction, works immediately  
**Trade-off:** Placeholder metadata (acceptable)

See `docs/API-KEY-DECISION.md` for full analysis.

### ✅ Agent-Centric Architecture

**Decision:** GitHub Copilot agent orchestrates everything  
**Rationale:** Leverages Copilot's strengths, minimal custom code  
**Impact:** Natural language workflow, easy to modify

### ✅ Approval-Required Implementation

**Decision:** No changes without explicit user approval  
**Rationale:** Prevent premature implementation  
**Impact:** User maintains control, no surprises

See `docs/CONSTRAINTS.md` for complete policy.

---

## Technology Stack

**Python Tools:**
- `youtube-transcript-api` - Transcript fetching (no auth!)
- `rapidfuzz` - Fuzzy company name matching
- `httpx` - HTTP client for CNCF API
- `jinja2` - Template rendering
- `typer` + `rich` - CLI framework with colors
- `pytest` - Testing

**GitHub Copilot:**
- Custom agents
- Agent skills
- GitHub Actions integration

**Total Dependencies:** 9 packages (all production-ready, permissive licenses)

---

## Implementation Status

### ✅ Completed
- Design reviewed and validated
- Architecture simplified (no API key)
- Complete planning documentation
- Implementation guide created
- Constraint policy documented

### 🔜 Next Steps
1. Implementing agent reads `docs/CONSTRAINTS.md`
2. Implementing agent reviews `docs/PLANNING.md`
3. Implementing agent requests approval to begin
4. Step-by-step implementation following `docs/IMPLEMENTATION-GUIDE.md`
5. Testing with real YouTube videos
6. First case study generated

---

## File Structure (Planned)

```
.
├── .github/
│   ├── agents/
│   │   └── case-study-agent.md          # Custom agent
│   ├── skills/
│   │   ├── transcript-correction/       # Skill 1
│   │   ├── transcript-analysis/         # Skill 2
│   │   └── case-study-generation/       # Skill 3
│   └── workflows/
│       └── copilot-setup-steps.yml      # Environment setup
│
├── casestudypilot/                      # Python package
│   ├── __main__.py                      # CLI entry point
│   └── tools/                           # 4 CLI tools
│       ├── youtube_client.py
│       ├── company_verifier.py
│       ├── assembler.py
│       └── validator.py
│
├── templates/
│   └── case_study.md.j2                 # Jinja2 template
│
├── case-studies/                        # Output directory
├── tests/                               # Test suite
│
├── docs/
│   ├── CONSTRAINTS.md                   # Approval policy ⚠️
│   ├── PLANNING.md                      # Specifications
│   ├── IMPLEMENTATION-GUIDE.md          # Step-by-step tasks
│   ├── API-KEY-DECISION.md              # Architecture decision
│   └── plans/
│       └── 2026-02-09-design.md         # Original design
│
├── README.md                            # This file
└── requirements.txt                     # Dependencies
```

---

## Success Criteria

Implementation will be complete when:

- [ ] All 4 CLI commands work correctly
- [ ] Agent workflow executes end-to-end  
- [ ] Generated case studies pass validation (≥0.60)
- [ ] No API keys required for basic operation
- [ ] Complete documentation exists
- [ ] At least 1 successful case study generated
- [ ] Tests pass (≥80% coverage)

---

## References

- [GitHub Copilot Custom Agents](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-agents)
- [GitHub Copilot Skills](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [CNCF End User Community](https://www.cncf.io/enduser/)
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

---

## For Future Agents

**⚠️ CRITICAL: Read `docs/CONSTRAINTS.md` before doing ANYTHING**

This project has a strict approval policy. You MUST:
1. Read the constraints document
2. Understand the approval process
3. Request approval before creating files
4. Wait for explicit approval
5. Only do what was approved

**Do not implement without approval. Do not assume. Always ask.**

---

*This project is ready for implementation by a future agent following the documented process.*
