# Implementation Guide
## Step-by-Step Tasks for Future Agent

**Status:** Planning Phase - Ready for Implementation  
**Date:** February 9, 2026

---

## ⚠️ Before You Begin

1. **Read `docs/CONSTRAINTS.md` first** - Critical approval policy
2. **Read `docs/PLANNING.md`** - Understand what to build
3. **Read `docs/API-KEY-DECISION.md`** - Understand architecture choice
4. **Request approval before creating ANY file**

---

## Implementation Checklist

### Phase 1: Foundation Setup

#### Task 1.1: Create Directory Structure
**Request approval to create these directories:**
```
casestudypilot/
casestudypilot/tools/
templates/
tests/
case-studies/
.github/agents/
.github/skills/transcript-correction/
.github/skills/transcript-analysis/
.github/skills/case-study-generation/
.github/workflows/
```

**Verification:** Run `tree -L 2` to confirm structure

---

#### Task 1.2: Create Python Package Markers
**Request approval to create these files:**
- `casestudypilot/__init__.py` (empty)
- `casestudypilot/tools/__init__.py` (empty)
- `tests/__init__.py` (empty)

**Verification:** Run `python -c "import casestudypilot"` (should not error)

---

#### Task 1.3: Create requirements.txt
**Request approval with this content:**
```
# Core Dependencies
youtube-transcript-api==0.6.2
rapidfuzz==3.6.1
pyyaml==6.0.1
httpx==0.26.0
jinja2==3.1.3
pydantic==2.6.1
typer==0.9.0
rich==13.7.0

# Development Dependencies
pytest==8.0.0
pytest-cov==4.1.0
```

**Verification:** Run `pip install -r requirements.txt` (in venv)

---

#### Task 1.4: Create .gitignore
**Request approval with this content:**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# Generated data
video_data.json
company_verification.json
transcript_analysis.json
case_study_sections.json
validation_results.json

# Logs
*.log
```

**Verification:** Git should ignore __pycache__ directories

---

#### Task 1.5: Create case-studies/.gitkeep
**Request approval to create empty .gitkeep file**

**Verification:** `git add case-studies/` should work

---

### Phase 2: Python CLI Tool - youtube_client.py

#### Task 2.1: Create youtube_client.py skeleton
**Request approval for file:** `casestudypilot/tools/youtube_client.py`

**Functions to implement:**
1. `extract_video_id(url: str) -> str`
   - Parse YouTube URL (youtube.com/watch?v=, youtu.be/, etc.)
   - Return video ID
   - Raise ValueError if invalid

2. `fetch_transcript(video_id: str) -> List[Dict[str, Any]]`
   - Use `YouTubeTranscriptApi.get_transcript(video_id)`
   - Return list of segments with text, start, duration
   - Raise exception if transcript unavailable

3. `format_duration(seconds: int) -> str`
   - Convert seconds to HH:MM:SS or MM:SS format
   - Example: 3665 → "1:01:05"

4. `extract_basic_metadata(url: str, video_id: str) -> Dict[str, Any]`
   - Return dict with video_id, url, placeholder title/description
   - Set duration to 0 (will be calculated later)

5. `fetch_video_data(url: str) -> Dict[str, Any]`
   - Call extract_video_id()
   - Call extract_basic_metadata()
   - Call fetch_transcript()
   - Calculate duration from last transcript segment
   - Return combined dict

**Test manually after creation:**
```bash
python -c "from casestudypilot.tools.youtube_client import fetch_video_data; \
           print(fetch_video_data('https://www.youtube.com/watch?v=V6L-xOUdoRQ'))"
```

---

### Phase 3: Python CLI Tool - company_verifier.py

#### Task 3.1: Create company_verifier.py
**Request approval for file:** `casestudypilot/tools/company_verifier.py`

**Functions to implement:**
1. `fetch_landscape_data() -> Dict[str, Any]`
   - GET `https://landscape.cncf.io/api/data.json`
   - Use httpx with 30s timeout
   - Return JSON response

2. `extract_enduser_members(landscape_data: Dict) -> List[str]`
   - Navigate: data → categories → "CNCF Members" → subcategories → "End User" → items
   - Extract company names
   - Return list

3. `find_best_match(company_name: str, member_list: List[str]) -> Dict[str, Any]`
   - Use `rapidfuzz.fuzz.token_sort_ratio()` for matching
   - Find highest scoring match
   - Return: matched_name, confidence, is_member (confidence >= 0.70)

4. `verify_company(company_name: str) -> Dict[str, Any]`
   - Fetch landscape data
   - Extract members
   - Find best match
   - Return verification results

**Test manually:**
```bash
python -c "from casestudypilot.tools.company_verifier import verify_company; \
           print(verify_company('Intuit'))"
```

Expected: `{"is_member": true, "confidence": 1.0, ...}`

---

### Phase 4: Python CLI Tool - assembler.py

#### Task 4.1: Create assembler.py
**Request approval for file:** `casestudypilot/tools/assembler.py`

**Functions to implement:**
1. `load_json_file(file_path: Path) -> Dict[str, Any]`
   - Check file exists
   - Load and parse JSON
   - Raise FileNotFoundError if missing

2. `create_jinja_env() -> Environment`
   - Load templates from `templates/` directory
   - Configure Jinja2 with autoescape, trim_blocks, lstrip_blocks

3. `assemble_case_study(...) -> Dict[str, Any]`
   - Parameters: 4 JSON file paths, optional output path
   - Load all JSON files
   - Verify company is_member == true
   - Merge into context dict
   - Render template
   - Save to case-studies/{company}.md
   - Return output_path, company_name, cncf_projects

**Test manually:** (requires template and JSON files)
```bash
# Create test JSON files first, then:
python -c "from casestudypilot.tools.assembler import assemble_case_study; \
           print(assemble_case_study(...))"
```

---

### Phase 5: Python CLI Tool - validator.py

#### Task 5.1: Create validator.py
**Request approval for file:** `casestudypilot/tools/validator.py`

**Constants to define:**
```python
WEIGHTS = {
    "structure": 0.30,
    "content_depth": 0.40,
    "cncf_mentions": 0.20,
    "formatting": 0.10,
}

REQUIRED_SECTIONS = ["Overview", "Challenge", "Solution", "Impact", "Conclusion"]

MIN_WORDS_PER_SECTION = {
    "Overview": 50,
    "Challenge": 100,
    "Solution": 150,
    "Impact": 100,
    "Conclusion": 50,
}
```

**Functions to implement:**
1. `read_case_study(file_path: Path) -> str`
2. `extract_sections(content: str) -> Dict[str, str]`
3. `count_words(text: str) -> int`
4. `validate_structure(sections: Dict) -> Dict[str, Any]`
5. `validate_content_depth(sections: Dict) -> Dict[str, Any]`
6. `validate_cncf_mentions(content: str) -> Dict[str, Any]`
7. `validate_formatting(content: str) -> Dict[str, Any]`
8. `calculate_quality_score(...) -> float`
9. `generate_warnings(...) -> List[str]`
10. `validate_case_study(file_path: Path, threshold: float) -> Dict[str, Any]`

**Test manually:**
```bash
# Create test markdown file first, then:
python -c "from casestudypilot.tools.validator import validate_case_study; \
           print(validate_case_study('test.md', 0.60))"
```

---

### Phase 6: Python CLI Entry Point

#### Task 6.1: Create __main__.py
**Request approval for file:** `casestudypilot/__main__.py`

**Structure:**
```python
import typer
from rich.console import Console

app = typer.Typer(name="casestudypilot", ...)
console = Console()

@app.command()
def youtube_data(url: str, output: Path): ...

@app.command()
def verify_company(company_name: str, output: Path): ...

@app.command()
def assemble(...): ...

@app.command()
def validate(case_study_path: Path, output: Path, threshold: float): ...

def main():
    app()

if __name__ == "__main__":
    main()
```

**Test all commands:**
```bash
python -m casestudypilot --help
python -m casestudypilot youtube-data --help
python -m casestudypilot verify-company --help
python -m casestudypilot assemble --help
python -m casestudypilot validate --help
```

---

### Phase 7: Jinja2 Template

#### Task 7.1: Create case_study.md.j2
**Request approval for file:** `templates/case_study.md.j2`

**Template structure:**
```jinja2
# {{ company }} Case Study

> **Source:** [{{ video.title }}]({{ video.url }})  
> **Duration:** {{ video.duration_formatted }}

---

{{ sections.overview }}

---

{{ sections.challenge }}

---

{{ sections.solution }}

---

{{ sections.impact }}

---

{{ sections.conclusion }}

---

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

**Video Source:**
- **Title:** {{ video.title }}
- **URL:** {{ video.url }}
- **Duration:** {{ video.duration_formatted }}

---

*This case study was automatically generated from the video interview.*
```

**Test:** Render with sample data

---

### Phase 8: GitHub Copilot Custom Agent

#### Task 8.1: Create case-study-agent.md
**Request approval for file:** `.github/agents/case-study-agent.md`

**Required YAML frontmatter:**
```yaml
---
name: case-study-agent
description: CNCF Case Study Automation Agent
version: 1.0.0
---
```

**Content to include:**
- Mission statement
- 12-step workflow (see PLANNING.md)
- Environment setup info
- Error handling instructions
- Quality standards
- Communication style
- Example issue/response

**Reference:** See PLANNING.md Section 2 for detailed content

---

### Phase 9: GitHub Copilot Skills

#### Task 9.1: Create transcript-correction skill
**Request approval for file:** `.github/skills/transcript-correction/SKILL.md`

**Required YAML frontmatter:**
```yaml
---
name: transcript-correction
description: Corrects common errors in YouTube auto-generated transcripts
version: 1.0.0
---
```

**Content to include:**
- Purpose
- Correction strategy (CNCF projects, technical terms, acronyms)
- Processing rules
- Input/output format
- Examples
- Quality checklist

---

#### Task 9.2: Create transcript-analysis skill
**Request approval for file:** `.github/skills/transcript-analysis/SKILL.md`

**Required YAML frontmatter:**
```yaml
---
name: transcript-analysis
description: Analyzes transcripts to extract structured data
version: 1.0.0
---
```

**Content to include:**
- Purpose
- Analysis tasks (identify projects, extract challenges/solutions/impact)
- Output schema
- Processing guidelines
- Quality checklist

---

#### Task 9.3: Create case-study-generation skill
**Request approval for file:** `.github/skills/case-study-generation/SKILL.md`

**Required YAML frontmatter:**
```yaml
---
name: case-study-generation
description: Generates polished case study sections
version: 1.0.0
---
```

**Content to include:**
- Purpose
- Section requirements (Overview, Challenge, Solution, Impact, Conclusion)
- Word count minimums
- Style guidelines
- Markdown formatting rules
- Quality checklist

---

### Phase 10: GitHub Actions Workflow

#### Task 10.1: Create copilot-setup-steps.yml
**Request approval for file:** `.github/workflows/copilot-setup-steps.yml`

**Required structure:**
```yaml
name: copilot-setup-steps  # Must be this exact name

on:
  workflow_dispatch:

jobs:
  copilot-setup-steps:      # Must be this exact name
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Verify installation
        run: python -m casestudypilot --help
```

**Test:** Push to GitHub and trigger workflow manually

---

#### Task 10.2: Create copilot-instructions.md
**Request approval for file:** `.github/copilot-instructions.md`

**Content to include:**
- Repository overview
- Custom agent usage
- Available skills
- Python tools documentation
- Environment setup info
- No secrets required note
- Repository structure
- Example issue

---

### Phase 11: Testing

#### Task 11.1: Create test files
**Request approval for these files:**
- `tests/test_youtube_client.py`
- `tests/test_company_verifier.py`
- `tests/test_assembler.py`
- `tests/test_validator.py`

**Each test file should:**
- Import pytest
- Import the module to test
- Create test fixtures
- Mock external API calls
- Test happy path
- Test error cases
- Test edge cases

**Example structure:**
```python
import pytest
from casestudypilot.tools.youtube_client import extract_video_id

def test_extract_video_id_watch_url():
    url = "https://www.youtube.com/watch?v=VIDEO_ID"
    assert extract_video_id(url) == "VIDEO_ID"

def test_extract_video_id_short_url():
    url = "https://youtu.be/VIDEO_ID"
    assert extract_video_id(url) == "VIDEO_ID"

def test_extract_video_id_invalid():
    with pytest.raises(ValueError):
        extract_video_id("https://not-youtube.com")
```

**Run tests:**
```bash
pytest tests/ -v
```

---

### Phase 12: Documentation

#### Task 12.1: Create README.md
**Request approval for file:** `README.md`

**Sections to include:**
1. Project title and overview
2. Features
3. Architecture diagram (ASCII art acceptable)
4. Setup instructions (no API key required!)
5. Usage examples
6. Testing instructions
7. Contributing guidelines
8. Technology stack
9. References

**Keep it concise** - Link to detailed docs in docs/

---

### Phase 13: Integration Testing

#### Task 13.1: Test with real YouTube video
**Steps:**
1. Choose test video (e.g., Intuit GitOps talk)
2. Run: `python -m casestudypilot youtube-data "<url>"`
3. Verify output JSON is correct
4. Check transcript is populated
5. Verify duration calculation

---

#### Task 13.2: Test company verification
**Steps:**
1. Run: `python -m casestudypilot verify-company "Intuit"`
2. Verify it finds the company
3. Test with misspelling: "Intuitt"
4. Verify fuzzy matching works
5. Test with non-member company
6. Verify is_member == false

---

#### Task 13.3: Test end-to-end workflow
**Steps:**
1. Create GitHub issue with YouTube URL
2. Mention @case-study-agent
3. Observe agent executing workflow
4. Verify each step completes
5. Check PR is created
6. Review generated case study

---

### Phase 14: Validation & Quality

#### Task 14.1: Create sample good case study
**Steps:**
1. Manually create a high-quality case study
2. Ensure it meets all validation criteria
3. Run validator: should score ≥ 0.80
4. Use as reference for expected output

---

#### Task 14.2: Create sample poor case study
**Steps:**
1. Create case study with issues (missing sections, short content)
2. Run validator: should score < 0.60
3. Verify warnings are helpful
4. Use for testing validation logic

---

### Phase 15: Deployment

#### Task 15.1: Final verification checklist
- [ ] All CLI commands work
- [ ] Tests pass
- [ ] Documentation complete
- [ ] GitHub Actions workflow configured
- [ ] Agent and skills created
- [ ] Template renders correctly
- [ ] Validation scores correctly
- [ ] At least one successful case study generated

---

#### Task 15.2: Create release documentation
**Request approval to create:** `docs/RELEASE-NOTES.md`

**Content:**
- Version number
- What's included
- What's working
- Known limitations
- Setup instructions
- Quick start guide

---

## Testing Commands Reference

### Unit Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_youtube_client.py -v

# Run with coverage
pytest tests/ --cov=casestudypilot --cov-report=html
```

### Manual Testing
```bash
# Test YouTube data fetching
python -m casestudypilot youtube-data "https://www.youtube.com/watch?v=V6L-xOUdoRQ"

# Test company verification
python -m casestudypilot verify-company "Intuit"

# Test assembly (after creating JSON files)
python -m casestudypilot assemble video_data.json analysis.json sections.json verification.json

# Test validation (after creating case study)
python -m casestudypilot validate case-studies/intuit.md
```

---

## Troubleshooting Guide

### Issue: Import errors
**Solution:** Verify `__init__.py` files exist, run `pip install -r requirements.txt`

### Issue: YouTube transcript not found
**Solution:** Check video has captions, try different video

### Issue: CNCF API timeout
**Solution:** Increase timeout in httpx call, check internet connection

### Issue: Template rendering fails
**Solution:** Verify all expected variables are in context dict

### Issue: Validation always fails
**Solution:** Check threshold, review validation logic, test with known good case study

---

## Completion Criteria

Implementation is complete when:

1. ✅ All files listed in PLANNING.md exist
2. ✅ All 4 CLI commands work correctly
3. ✅ Tests pass (at least 80% coverage)
4. ✅ Agent workflow executes end-to-end
5. ✅ At least 1 case study generated successfully
6. ✅ Validation scores correctly
7. ✅ Documentation is complete
8. ✅ GitHub Actions workflow configured
9. ✅ No API keys required for basic operation
10. ✅ User approval obtained for all implementation steps

---

## Post-Implementation

### What to do after implementation:
1. Generate 3-5 case studies from real videos
2. Collect feedback on quality
3. Refine validation thresholds
4. Update documentation based on learnings
5. Consider optional enhancements (YouTube API key, etc.)

---

*Follow this guide step-by-step. Request approval before creating each file. Test thoroughly at each phase.*
