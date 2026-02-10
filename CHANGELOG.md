# Changelog

All notable changes to the Skill-Driven LLM Automation Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-02-10

### Added

**🏗️ Major Feature: Reference Architecture Generation**

This release introduces comprehensive reference architecture generation, expanding the framework from case studies to include detailed technical documentation suitable for CNCF Technical Advisory Board (TAB) submission.

**New Agents:**
- **`reference-architecture-agent` (v1.0.0)**: 18-step workflow with 7 validation checkpoints (5 critical fail-fast)
  - Generates 2000-5000 word technical documents
  - Requires 5+ CNCF projects (vs 2+ for case studies)
  - Technical depth score threshold: ≥0.70 (vs ≥0.60 for case studies)
  - Produces 13 sections vs 5 for case studies
  - Designed for engineers/architects (vs business leaders)

**New LLM Skills (3):**
- **`transcript-deep-analysis`**: Extracts 5+ CNCF projects, 3-layer architecture (Infrastructure, Platform, Application), integration patterns, technical metrics with transcript quotes, 6+ screenshot opportunities
- **`architecture-diagram-specification`**: Generates textual specifications for component diagrams and data flow diagrams (no code generation to avoid hallucination)
- **`reference-architecture-generation`**: Produces 13-section comprehensive architecture documentation with 18-step execution process

**New CLI Tools (3):**
- **`validate-deep-analysis`**: Validates deep analysis output (7 checks: 5+ CNCF projects, 3 architecture layers, 2+ integration patterns, 6+ screenshots, 6 sections, word counts 200-800)
  - Exit codes: 0 (pass), 1 (warning), 2 (critical)
- **`validate-reference-architecture`**: 5-dimensional technical depth scoring algorithm
  - **Scoring dimensions** (weighted):
    - 25% CNCF project depth (5+ projects with detailed descriptions)
    - 20% Technical specificity (concrete implementation details)
    - 20% Implementation detail (version numbers, configurations)
    - 20% Metric quality (quantifiable results with citations)
    - 15% Architecture completeness (all 3 layers documented)
  - **Thresholds**: ≥0.70 (pass), 0.60-0.69 (warning), <0.60 (critical)
- **`assemble-reference-architecture`**: Jinja2 template rendering for 13-section reference architectures with 6+ screenshots

**New Templates:**
- **`templates/reference_architecture.md.j2`** (190 lines): 13-section structure with YAML frontmatter, CNCF project tables, metrics tables, diagram specifications, TAB submission guidance

**Content Type Comparison:**
| Aspect | Case Study | Reference Architecture |
|--------|-----------|----------------------|
| Length | 500-1500 words | 2000-5000 words |
| Sections | 5 | 13 |
| CNCF Projects | 2+ | 5+ |
| Technical Depth | ≥0.60 | ≥0.70 |
| Audience | Business leaders | Engineers, architects |
| TAB Submission | Not suitable | Explicitly designed |

**Documentation (6 new/updated files):**
- **`README.md`**: Added 150-line reference architecture section with comparison table, decision guide, feature highlights
- **`AGENTS.md`**: Added detailed reference-architecture-agent entry with 18-step workflow, comparison table, 5-dimensional scoring algorithm
- **`CONTRIBUTING.md`**: Added 400-line section on modifying reference architecture system (scoring, validation, templates, skills)
- **`docs/REFERENCE-ARCHITECTURE-USER-GUIDE.md`** (550 lines): Comprehensive user guide with validation explanations, output structure, TAB submission process, FAQ, troubleshooting
- **`docs/CASE-STUDY-VS-REFERENCE-ARCHITECTURE.md`** (400 lines): Detailed comparison with decision tree, 6 scenarios, migration paths, recommendation matrix
- **`docs/INTEGRATION-TEST-PLAN.md`**: Testing plan for reference architecture workflow validation

**GitHub Issue Template:**
- **Updated `.github/ISSUE_TEMPLATE/content-request.yml`**: Renamed from `case-study-request.yml`, added dropdown with 3 options:
  - "Case Study (500-1500 words, business-focused, 2+ CNCF projects)"
  - "Reference Architecture (2000-5000 words, technical deep-dive, 5+ CNCF projects)"
  - "Both (generate both case study and reference architecture)"

**Directory Structure:**
```
reference-architectures/          # New output directory
├── company-platform.md           # 2000-5000 word reference architecture
└── images/
    └── company-platform/
        └── [6+ screenshots]      # Architecture-focused screenshots
```

### Changed

**Architecture Improvements:**
- **Dual-mode operation**: Framework now supports both case studies (business-focused) and reference architectures (technical-focused)
- **Validation framework extended**: Case study checkpoints (5) vs reference architecture checkpoints (7, with 5 critical)
- **Quality thresholds differentiated**: Case study (≥0.60) vs reference architecture (≥0.70)
- **Screenshot requirements**: Case study (3) vs reference architecture (6+)

**CLI Enhancements:**
- Added `validate-deep-analysis` with 7 validation checks
- Added `validate-reference-architecture` with 5-dimensional scoring
- Added `assemble-reference-architecture` with new template system

**Agent Workflow:**
- Case study agent remains 14 steps (unchanged)
- Reference architecture agent: 18 steps with enhanced validation

**Documentation:**
- All documentation updated to reflect dual-mode capability
- Issue template streamlined to single template with dropdown
- Added comprehensive comparison and decision guides

### Technical Improvements

**Validation Architecture:**
- **5-dimensional technical depth scoring** for reference architectures:
  ```python
  score = 0.25 * cncf_project_depth +
          0.20 * technical_specificity +
          0.20 * implementation_detail +
          0.20 * metric_quality +
          0.15 * architecture_completeness
  ```
- **Deep analysis validation**: Checks CNCF project count (5+), architecture layers (3), integration patterns (2+), screenshot opportunities (6+)
- **Enhanced fail-fast**: 7 checkpoints for reference architectures vs 5 for case studies

**Quality Standards:**
- Reference architectures require higher technical depth (0.70 vs 0.60)
- More stringent CNCF project requirements (5+ vs 2+)
- Architecture completeness validation (all 3 layers required)
- Integration pattern documentation (2+ patterns required)

**CNCF TAB Submission:**
- Reference architectures include TAB submission guidance
- Generated PR includes TAB submission checklist
- Quality score breakdown included in PR description
- Meets CNCF TAB technical depth requirements

### Breaking Changes

**None** - This is a feature addition, not a breaking change. All existing case study functionality remains unchanged.

### Migration Guide

**For existing case study users:**
- No changes required - case study generation works exactly as before
- New issue template provides dropdown to select content type
- Can continue using `case-study` label for GitHub issues

**To start using reference architectures:**
1. Use new dropdown in issue template, select "Reference Architecture"
2. Ensure video is 15-40 minutes with 5+ CNCF projects
3. Agent will automatically use reference-architecture-agent workflow
4. Review generated content in `reference-architectures/` directory

**To generate both:**
1. Select "Both" in dropdown or add both labels to issue
2. Both agents run independently
3. Outputs in separate directories: `case-studies/` and `reference-architectures/`

### Known Limitations

- Reference architectures require longer videos (15-40 min vs 10-20 min)
- Higher technical depth requirement may exclude some videos
- Textual diagram specifications require manual conversion to visual diagrams for publication
- TAB submission is manual process (not automated)

### Future Enhancements

Planned for future releases:
- Automatic Mermaid diagram generation from textual specifications
- Automated CNCF TAB submission workflow
- Support for multi-video reference architectures
- Reference architecture versioning and updates
- Community contribution workflow for reference architectures

## [2.2.0] - 2026-02-09

### Added
- **Fail-Fast Validation Framework**: 5 validation checkpoints with exit codes (0=pass, 1=warning, 2=critical)
  - `validate-transcript`: Check transcript quality (min 1000 chars, 50 segments)
  - `validate-company`: Validate company identification (confidence >= 0.7)
  - `validate-analysis`: Verify analysis output (min 1 CNCF project, all sections)
  - `validate-metrics`: Detect fabricated metrics (fuzzy match against transcript)
  - `validate-consistency`: Check company consistency (prevent "Spotify bug")
  - `validate-all`: Run all validations comprehensively
- **Documentation overhaul**: Optimized all documentation for LLM consumption
  - README.md refactored to emphasize skill-driven framework
  - AGENTS.md updated with extensible skill system guidance
  - CONTRIBUTING.md created for adding new skills/agents
  - Documentation structure focused on three-layer architecture
- **Packaging improvements**:
  - Added `pyproject.toml` for pip installability
  - Added `CHANGELOG.md` for version tracking
  - Package now installable with `pip install -e .`

### Changed
- Agent workflow updated from 13 to 14 steps (added Step 8.5 validation)
- Documentation now emphasizes framework extensibility over specific use case
- All docs restructured for skill-driven development approach

### Fixed
- Documentation inconsistencies between README and implementation
- Archived outdated planning documents to `docs/archive/`

## [2.1.0] - 2026-02-08

### Added
- **Screenshot Integration**: Automatic screenshot extraction and embedding
  - `extract-screenshots` command for downloading video frames
  - 3 screenshots per case study (challenge, solution, impact)
  - Intelligent timestamp selection from transcript analysis
  - Fallback to YouTube thumbnails if frame extraction fails
- **Hyperlink System**: Automatic URL injection for markdown
  - Company URLs (6 companies mapped in `hyperlinks.py`)
  - CNCF project URLs (19 projects mapped)
  - CNCF glossary terms (11 terms mapped)
- **Validation enhancements**:
  - Quality validation includes screenshot check
  - Relative path handling for images

### Changed
- `assemble` command now accepts `--screenshots` parameter
- Template updated to embed images with captions
- Agent workflow updated to 13 steps (added Step 7 for screenshots)

## [2.0.0] - 2026-02-07

### Added
- **Initial Production Release**: Complete case study automation system
- **CLI Tools** (5 commands):
  - `youtube-data`: Fetch video transcripts and metadata
  - `verify-company`: Check CNCF membership
  - `assemble`: Render case study from components
  - `validate`: Multi-factor quality scoring
- **Agent Skills** (3 LLM-powered skills):
  - `transcript-correction`: Fix common transcript errors
  - `transcript-analysis`: Extract structured data
  - `case-study-generation`: Generate polished markdown
- **Agent Workflow**:
  - 12-step workflow from issue to PR
  - GitHub Copilot custom agent
  - Automated issue-to-PR process
- **Quality System**:
  - Multi-factor scoring (structure, content, CNCF mentions, formatting)
  - Minimum threshold: 0.60
  - Comprehensive validation
- **Documentation**:
  - Complete planning documentation
  - Implementation guide
  - API key decision rationale
  - GitHub issue workflow guide

### Features
- Zero API keys required (uses `youtube-transcript-api` + `yt-dlp`)
- Real metadata fetching (no placeholders)
- Jinja2 template system
- Comprehensive test suite
- Agent-centric architecture

## [1.0.0] - 2026-02-06

### Added
- Initial repository structure
- Planning phase documentation
- Design documents
- Architecture decisions

---

## Version History Summary

- **v3.0.0** (Current): Reference Architecture Generation + Dual-Mode Framework
- **v2.2.0**: Fail-fast validation + LLM-optimized documentation
- **v2.1.0**: Screenshot integration + hyperlink automation
- **v2.0.0**: Initial production release with core features
- **v1.x**: Planning and design phase

---

## Upgrade Guide

### Upgrading from 2.2.0 to 3.0.0

**What's New:**
- Reference architecture generation capability
- 3 new CLI commands: `validate-deep-analysis`, `validate-reference-architecture`, `assemble-reference-architecture`
- 3 new LLM skills for deep analysis and architecture generation
- New reference-architecture-agent with 18-step workflow
- Comprehensive documentation for dual-mode operation

**New CLI Commands:**
```bash
# Validate deep analysis output
python -m casestudypilot validate-deep-analysis deep_analysis.json

# Validate reference architecture quality
python -m casestudypilot validate-reference-architecture ref_arch.json

# Assemble reference architecture
python -m casestudypilot assemble-reference-architecture ref_arch.json screenshots/*.jpg --output output.md
```

**GitHub Issue Workflow:**
- Updated issue template now has dropdown for content type selection
- Old behavior: Select "Case Study" to maintain existing workflow
- New behavior: Select "Reference Architecture" for comprehensive technical documentation
- Can select "Both" to generate both types

**Documentation:**
- Review `docs/REFERENCE-ARCHITECTURE-USER-GUIDE.md` for user guide
- Review `docs/CASE-STUDY-VS-REFERENCE-ARCHITECTURE.md` for comparison
- Review `CONTRIBUTING.md` for architecture modification guidelines

**No Breaking Changes**: 
- All existing case study functionality unchanged
- Case study agent remains 14 steps (no modifications)
- All existing CLI commands work exactly as before
- Existing issue workflows continue to work

**Recommended Actions:**
1. Update issue template in your fork/deployment
2. Review new documentation to understand reference architecture capabilities
3. Try reference architecture with a technical deep-dive video (15+ min, 5+ CNCF projects)

### Upgrading from 2.1.0 to 2.2.0

**New CLI Commands:**
- Add 6 new validation commands to your workflows
- Update agent workflow to check exit codes at each validation point

**Documentation Changes:**
- Review updated README.md for framework architecture emphasis
- Review AGENTS.md for skill-driven development guidance
- Review CONTRIBUTING.md for extension procedures

**No Breaking Changes**: All existing commands and workflows continue to work.

### Upgrading from 2.0.0 to 2.1.0

**New CLI Command:**
- `extract-screenshots` command added
- Update `assemble` calls to include `--screenshots screenshots.json`

**Agent Workflow Changes:**
- Add Step 7 (screenshot extraction) before assembly
- Update agent to 13-step workflow

**No Breaking Changes**: Screenshots are optional, old workflows work without them.

---

[3.0.0]: https://github.com/castrojo/casestudypilot/compare/v2.2.0...v3.0.0
[2.2.0]: https://github.com/castrojo/casestudypilot/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/castrojo/casestudypilot/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/castrojo/casestudypilot/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/castrojo/casestudypilot/releases/tag/v1.0.0
