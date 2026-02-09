# CNCF Case Study Automation - Planning Document

**Status:** Planning Phase  
**Date:** February 9, 2026  
**Version:** 1.0

---

## ⚠️ CRITICAL CONSTRAINTS

### Implementation Approval Policy

**UNDER NO CIRCUMSTANCE should any implementation changes be made without EXPLICIT approval from the user.**

This means:
- ❌ No code files created
- ❌ No configuration files modified
- ❌ No dependencies installed
- ❌ No scripts executed
- ❌ No "helpful" changes

**Before ANY implementation action:**
1. Present the proposed change to the user
2. Wait for explicit approval (user must say "approved" or equivalent)
3. Only then proceed

**Violations of this policy are unacceptable.**

See `docs/CONSTRAINTS.md` for complete policy details.

---

## Project Overview

### What This System Will Do

Automate the creation of CNCF end-user case studies from YouTube video interviews using GitHub Copilot custom agents.

**Input:** GitHub issue with YouTube URL  
**Output:** Pull request with publication-ready case study

**Key Decision:** No YouTube API key required - uses `youtube-transcript-api` for direct transcript access.

### Architecture Approach

**Agent-Centric Design:**
- GitHub Copilot custom agent orchestrates entire workflow
- Agent invokes Python CLI tools for data operations
- Agent applies specialized skills for AI processing
- Agent creates pull request with final result

**Components:**
1. **Custom Agent** - Workflow orchestrator
2. **Agent Skills** (3) - AI processing tasks
3. **Python CLI Tools** (4) - Data operations
4. **Quality Validation** - Automated checks

---

## Component Specifications

### 1. Python CLI Tool: `casestudypilot`

**Purpose:** Provide command-line tools for data fetching, verification, assembly, and validation.

**Commands to Implement:**

#### Command 1: `youtube-data`
```bash
python -m casestudypilot youtube-data <url> --output video_data.json
```

**Functionality:**
- Extract video ID from YouTube URL
- Fetch transcript using `youtube-transcript-api` (no auth!)
- Calculate duration from transcript timing
- Output JSON with: video_id, url, transcript, duration_seconds, duration_formatted

**Dependencies:**
- `youtube-transcript-api==0.6.2`
- Standard library: `urllib.parse`, `json`, `pathlib`

**Output Format:**
```json
{
  "video_id": "V6L-xOUdoRQ",
  "url": "https://youtube.com/...",
  "title": "YouTube Video V6L-xOUdoRQ",
  "description": "",
  "transcript": [
    {"text": "...", "start": 0.0, "duration": 3.5}
  ],
  "duration_seconds": 1800,
  "duration_formatted": "30:00"
}
```

#### Command 2: `verify-company`
```bash
python -m casestudypilot verify-company "Company Name" --output company_verification.json
```

**Functionality:**
- Fetch CNCF Landscape data from `landscape.cncf.io/api/data.json`
- Extract end-user member companies
- Perform fuzzy matching using `rapidfuzz` (token_sort_ratio)
- Return match with confidence score

**Dependencies:**
- `httpx==0.26.0`
- `rapidfuzz==3.6.1`

**Output Format:**
```json
{
  "is_member": true,
  "matched_name": "Intuit",
  "confidence": 1.0,
  "query": "intuit",
  "threshold": 0.70,
  "total_members": 150
}
```

#### Command 3: `assemble`
```bash
python -m casestudypilot assemble video_data.json analysis.json sections.json verification.json --output case-studies/company.md
```

**Functionality:**
- Load 4 JSON input files
- Verify company is CNCF member
- Render Jinja2 template with combined data
- Save markdown file to case-studies/ directory

**Dependencies:**
- `jinja2==3.1.3`
- `pyyaml==6.0.1`

**Template Location:** `templates/case_study.md.j2`

#### Command 4: `validate`
```bash
python -m casestudypilot validate case-studies/company.md --threshold 0.60 --output validation_results.json
```

**Functionality:**
- Parse markdown file
- Extract sections and content
- Calculate quality score (0.0-1.0) across 4 dimensions:
  - Structure (30%): Required sections present
  - Content Depth (40%): Word counts per section
  - CNCF Mentions (20%): Projects referenced
  - Formatting (10%): Markdown quality
- Compare to threshold
- Return pass/fail with warnings

**Output Format:**
```json
{
  "quality_score": 0.82,
  "passed": true,
  "threshold": 0.60,
  "warnings": [],
  "details": {
    "structure": {"score": 1.0, "missing_sections": []},
    "content_depth": {"score": 0.85, "shallow_sections": []},
    "cncf_mentions": {"score": 1.0, "projects_mentioned": ["Kubernetes", "Argo CD"]},
    "formatting": {"score": 0.8, "issues": []}
  }
}
```

**CLI Framework:**
- Use `typer==0.9.0` for command structure
- Use `rich==13.7.0` for colored terminal output
- Proper error handling with exit codes

---

### 2. GitHub Copilot Custom Agent

**File:** `.github/agents/case-study-agent.md`

**Structure:**
```markdown
---
name: case-study-agent
description: CNCF Case Study Automation Agent
version: 1.0.0
---

# Workflow Instructions

[Detailed 12-step workflow for agent to follow]
```

**Agent Responsibilities:**
1. Extract YouTube URL from issue
2. Run `youtube-data` tool
3. Extract company name from issue/transcript
4. Run `verify-company` tool
5. Apply `transcript-correction` skill
6. Apply `transcript-analysis` skill
7. Apply `case-study-generation` skill
8. Run `assemble` tool
9. Run `validate` tool
10. Create branch
11. Commit case study file
12. Create pull request

**Error Handling:**
- If no transcript: Comment and close issue
- If not CNCF member: Comment with suggestions and close
- If validation fails: Comment with warnings and request review
- If any tool fails: Comment with error details

---

### 3. Agent Skills

#### Skill 1: Transcript Correction

**File:** `.github/skills/transcript-correction/SKILL.md`

**Purpose:** Fix common errors in auto-generated YouTube transcripts

**YAML Frontmatter Required:**
```yaml
---
name: transcript-correction
description: Corrects common errors in YouTube auto-generated transcripts
version: 1.0.0
---
```

**Task:**
- Fix CNCF project names (kubernetes → Kubernetes, argo cd → Argo CD)
- Fix technical terms (get ops → GitOps, dev ops → DevOps)
- Fix acronyms (api → API, yaml → YAML, json → JSON)
- Fix company names (proper capitalization)
- Add sentence capitalization and basic punctuation
- Preserve timing data exactly

**Input:** `video_data.json` transcript array  
**Output:** Corrected transcript array (save back to `video_data.json`)

#### Skill 2: Transcript Analysis

**File:** `.github/skills/transcript-analysis/SKILL.md`

**Purpose:** Extract structured data from corrected transcript

**Task:**
- Identify all CNCF projects mentioned
- Extract challenges (problems before adoption)
- Extract solutions (what they implemented)
- Extract impact/outcomes (metrics, results)
- Classify content into case study sections
- Extract notable quotes
- Identify key metrics

**Input:** Corrected transcript from `video_data.json`  
**Output:** `transcript_analysis.json` with structured data

**Output Schema:**
```json
{
  "cncf_projects": [
    {"name": "Kubernetes", "usage_context": "...", "key_details": "..."}
  ],
  "challenges": [
    {"category": "scalability", "description": "...", "transcript_segment": "..."}
  ],
  "solutions": [
    {"category": "automation", "description": "...", "technologies": [...]}
  ],
  "impact": [
    {"category": "performance", "metric": "80% reduction", "description": "..."}
  ],
  "sections": {
    "overview": {"summary": "...", "transcript_segments": [...]},
    "challenge": {...},
    "solution": {...},
    "impact": {...},
    "conclusion": {...}
  },
  "quotes": [
    {"text": "...", "speaker": "...", "context": "..."}
  ],
  "key_metrics": ["80% reduction in deployment time", ...]
}
```

#### Skill 3: Case Study Generation

**File:** `.github/skills/case-study-generation/SKILL.md`

**Purpose:** Generate polished markdown sections following CNCF format

**Task:**
Generate 5 sections with specific requirements:

1. **Overview** (50-100 words)
   - Company name, industry, scale
   - What they accomplished
   - CNCF projects used

2. **Challenge** (100-200 words)
   - Problems before adoption
   - Business/technical impact
   - Why change was needed

3. **Solution** (150-300 words)
   - Technologies adopted
   - Implementation approach
   - How technologies work together
   - Include code examples

4. **Impact** (100-200 words)
   - Key metrics (bulleted)
   - Before/after comparisons
   - Business benefits
   - Include quotes

5. **Conclusion** (50-100 words)
   - Transformation summary
   - Future plans
   - Recommendation

**Input:** `transcript_analysis.json` + `video_data.json`  
**Output:** `case_study_sections.json` with markdown sections

**Style Guidelines:**
- Professional but accessible
- Active voice
- Specific over vague
- Story-driven (problem → solution → results)
- Use proper markdown formatting
- Bold key metrics
- Include code blocks where relevant

---

### 4. Jinja2 Template

**File:** `templates/case_study.md.j2`

**Purpose:** Combine all components into final case study

**Structure:**
```jinja2
# {{ company }} Case Study

> **Source:** [{{ video.title }}]({{ video.url }})

{{ sections.overview }}

{{ sections.challenge }}

{{ sections.solution }}

{{ sections.impact }}

{{ sections.conclusion }}

## Metadata

**Company:** {{ company }}

**CNCF Projects Used:**
{% for project in analysis.cncf_projects %}
- **{{ project.name }}**: {{ project.usage_context }}
{% endfor %}

**Key Metrics:**
{% for metric in analysis.key_metrics %}
- {{ metric }}
{% endfor %}
```

---

### 5. GitHub Actions Workflow

**File:** `.github/workflows/copilot-setup-steps.yml`

**Purpose:** Configure Python environment for Copilot agent

**Job name MUST be:** `copilot-setup-steps` (GitHub Copilot requirement)

**Steps:**
1. Checkout repository
2. Set up Python 3.11
3. Install dependencies from `requirements.txt`
4. Verify CLI installation

**No secrets required** - all tools work without authentication

---

### 6. Quality Validation System

**Validation Dimensions:**

#### Structure (30% weight)
- Check for required sections: Overview, Challenge, Solution, Impact, Conclusion
- Score = (sections present / total required)

#### Content Depth (40% weight)
- Minimum word counts:
  - Overview: 50 words
  - Challenge: 100 words
  - Solution: 150 words
  - Impact: 100 words
  - Conclusion: 50 words
- Score = average(section_word_count / minimum)

#### CNCF Mentions (20% weight)
- Count unique CNCF projects mentioned
- 0 projects = 0.0
- 1 project = 0.5
- 2 projects = 0.8
- 3+ projects = 1.0

#### Formatting (10% weight)
- Check for code blocks
- Check for lists
- Check for links
- Check for proper headers
- Deduct points for missing elements

**Passing Threshold:** 0.60 (configurable)

---

## Dependencies

**All pinned versions for reproducibility:**

```
youtube-transcript-api==0.6.2    # Transcript fetching (no auth)
rapidfuzz==3.6.1                 # Fuzzy string matching
pyyaml==6.0.1                    # YAML parsing
httpx==0.26.0                    # HTTP client
jinja2==3.1.3                    # Template rendering
pydantic==2.6.1                  # Data validation
typer==0.9.0                     # CLI framework
rich==13.7.0                     # Terminal formatting

# Development
pytest==8.0.0                    # Testing
pytest-cov==4.1.0                # Coverage
```

**All dependencies:**
- Production-ready
- Actively maintained
- Permissive licenses (MIT/BSD)
- No authentication required

---

## File Structure to Create

```
.
├── .github/
│   ├── agents/
│   │   └── case-study-agent.md
│   ├── skills/
│   │   ├── transcript-correction/
│   │   │   └── SKILL.md
│   │   ├── transcript-analysis/
│   │   │   └── SKILL.md
│   │   └── case-study-generation/
│   │       └── SKILL.md
│   ├── workflows/
│   │   └── copilot-setup-steps.yml
│   └── copilot-instructions.md
│
├── casestudypilot/
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   └── tools/
│       ├── __init__.py
│       ├── youtube_client.py    # youtube-data command
│       ├── company_verifier.py  # verify-company command
│       ├── assembler.py         # assemble command
│       └── validator.py         # validate command
│
├── templates/
│   └── case_study.md.j2
│
├── case-studies/                # Output directory
│   └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   ├── test_youtube_client.py
│   ├── test_company_verifier.py
│   ├── test_assembler.py
│   └── test_validator.py
│
├── docs/
│   ├── plans/
│   │   └── 2026-02-09-design.md
│   ├── PLANNING.md              # This file
│   ├── IMPLEMENTATION-GUIDE.md
│   ├── CONSTRAINTS.md
│   └── API-KEY-DECISION.md
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Implementation Phases

### Phase 1: Foundation (Days 1-3)
- Create directory structure
- Set up Python package skeleton
- Create requirements.txt
- Set up pytest configuration
- Create .gitignore

### Phase 2: Python CLI Tools (Days 4-7)
- Implement youtube_client.py
- Implement company_verifier.py
- Implement assembler.py
- Implement validator.py
- Create CLI entry point (__main__.py)
- Write unit tests for each tool

### Phase 3: GitHub Copilot Configuration (Days 8-10)
- Create custom agent definition
- Create 3 agent skills with YAML frontmatter
- Create GitHub Actions workflow
- Create copilot-instructions.md

### Phase 4: Templates & Documentation (Days 11-12)
- Create Jinja2 template
- Write comprehensive README
- Create usage examples
- Document testing approach

### Phase 5: Integration Testing (Days 13-14)
- Test with real YouTube videos
- Test agent workflow end-to-end
- Test validation with sample case studies
- Fix bugs and edge cases

### Phase 6: Finalization (Day 15)
- Complete documentation
- Create deployment guide
- Final quality review
- Ready for production use

---

## Success Criteria

### Must Have (MVP)
- [ ] All 4 CLI commands work correctly
- [ ] Agent workflow executes end-to-end
- [ ] Generated case studies pass validation (≥0.60)
- [ ] No API keys required
- [ ] Complete documentation exists
- [ ] At least 1 successful case study generated

### Should Have
- [ ] Integration tests for all tools
- [ ] Error handling for common failures
- [ ] Clear error messages to users
- [ ] Validation warnings are actionable
- [ ] Agent provides progress updates

### Nice to Have
- [ ] Support for non-English transcripts
- [ ] Custom validation rules
- [ ] Batch processing
- [ ] Metrics dashboard

---

## Testing Strategy

### Unit Tests
- Test each CLI command independently
- Mock external API calls (YouTube, CNCF Landscape)
- Test edge cases (missing transcript, invalid URL, non-member company)
- Test validation scoring logic

### Integration Tests
- Test with real YouTube videos
- Test company verification against real CNCF data
- Test template rendering with sample data
- Test validation with known good/bad case studies

### Manual Testing
- Test agent skills in GitHub web UI
- Test complete workflow from issue → PR
- Test error handling and recovery
- Test with various video types

**No automated skill testing** - GitHub Copilot skills cannot be unit tested, only manually validated.

---

## Known Limitations

1. **Placeholder Metadata**
   - Title, description, channel are placeholders
   - Agent must infer company name from transcript
   - Duration calculated from transcript timing

2. **No Automated Skill Testing**
   - Skills must be manually tested in GitHub
   - Cannot unit test AI processing

3. **CNCF Landscape Dependency**
   - Relies on public API structure
   - Changes to API could break verification
   - Mitigation: Graceful error handling

4. **English Transcripts Only**
   - youtube-transcript-api fetches default language
   - Non-English videos may fail or produce poor results

---

## Future Enhancements

### Optional YouTube API Integration
If rich metadata is needed later:
- Make API key optional parameter
- If provided: fetch title, description, channel, publish date
- If not provided: use current placeholder approach
- Update documentation with API setup instructions

### Other Enhancements
- Multi-language support
- Custom CNCF project dictionary
- Batch processing (multiple videos)
- Export to PDF/HTML
- Web UI for testing
- Metrics dashboard

---

## Risk Mitigation

### Risk: Transcript Not Available
- **Mitigation:** Check early in workflow, fail fast with clear message
- **User Action:** Request manual transcript or different video

### Risk: Company Not CNCF Member
- **Mitigation:** Use fuzzy matching with confidence threshold
- **User Action:** Review suggestions, correct company name, or cancel

### Risk: Poor Quality Case Study
- **Mitigation:** Validation scoring with configurable threshold
- **User Action:** Review warnings, regenerate sections, or edit manually

### Risk: CNCF API Changes
- **Mitigation:** Version pin, error handling, fallback logic
- **User Action:** Update company verification logic if API changes

### Risk: Agent Misunderstands Workflow
- **Mitigation:** Detailed agent instructions with error handling
- **User Action:** Review agent output at each phase, provide feedback

---

## References

- [GitHub Copilot Custom Agents Documentation](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-agents)
- [GitHub Copilot Skills Documentation](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [CNCF End User Community](https://www.cncf.io/enduser/)
- [youtube-transcript-api Documentation](https://github.com/jdepoix/youtube-transcript-api)
- [CNCF Landscape API](https://landscape.cncf.io/api/data.json)

---

## Next Steps

**For the implementing agent:**

1. Read `docs/CONSTRAINTS.md` first
2. Read `docs/API-KEY-DECISION.md` for architecture context
3. Follow `docs/IMPLEMENTATION-GUIDE.md` step-by-step
4. **Request approval before creating ANY files**
5. Test each component as you build
6. Document any deviations or issues

**Remember:** No changes without explicit user approval.

---

*This planning document is complete and ready for implementation by a future agent.*
