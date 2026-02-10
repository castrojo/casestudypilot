# Changelog

All notable changes to the Skill-Driven LLM Automation Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- **v2.2.0** (Current): Fail-fast validation + LLM-optimized documentation
- **v2.1.0**: Screenshot integration + hyperlink automation
- **v2.0.0**: Initial production release with core features
- **v1.x**: Planning and design phase

---

## Upgrade Guide

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

[2.2.0]: https://github.com/castrojo/casestudypilot/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/castrojo/casestudypilot/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/castrojo/casestudypilot/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/castrojo/casestudypilot/releases/tag/v1.0.0
