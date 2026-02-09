# Screenshot Integration Plan

**Status:** 📋 Ready for Implementation  
**Created:** 2026-02-09  
**Purpose:** Add contextual video screenshots to case study reports

---

## Overview

Add capability to insert 2 contextual screenshots from YouTube videos into case study reports, capturing key moments during the Challenge and Solution sections to provide visual variety and context.

---

## Architecture Decisions

### Screenshot Source: YouTube Thumbnail API

**Decision:** Use YouTube's built-in thumbnail URLs for MVP

- **URLs:** `https://img.youtube.com/vi/{VIDEO_ID}/{quality}.jpg`
- **Available qualities:**
  - `maxresdefault.jpg` (1920x1080) - best quality
  - `sddefault.jpg` (640x480) - good balance
  - `hqdefault.jpg` (480x360) - smaller
  - `mqdefault.jpg` (320x180) - thumbnail

**Pros:**
- No video download required
- Instant access, reliable
- Officially supported by YouTube
- Zero additional dependencies

**Cons:**
- Static video thumbnails (typically title card), not timestamp-specific
- Same image if used multiple times

**Note:** YouTube thumbnail API provides video-level thumbnails, NOT frame-by-frame extraction. For timestamp-specific frames, future enhancement would require yt-dlp integration.

### Storage Location: `case-studies/images/{company-slug}/`

Each company gets a subdirectory for their screenshots:
- Example: `case-studies/images/intuit/challenge.jpg`
- Keeps related assets together
- Easy to maintain and delete

### Placement Strategy: 2 Screenshots

1. **Challenge section** - captures the problem being described
2. **Solution section** - shows the implementation or results

### Selection Strategy: Transcript Analysis

Analyze transcript for high-impact moments:
- Architecture diagrams mentioned ("as you can see here", "this diagram shows")
- Metrics/numbers being discussed ("here are our results")
- Demo moments ("let me show you")
- Visual aids referenced ("on this slide")

Use timestamp detection to identify when speakers reference visuals.

**Fallback:** If no clear visual moments detected, use static thumbnails with generic captions.

---

## Implementation Components

### 1. New CLI Command: `extract-screenshots`

**Location:** `casestudypilot/__main__.py`

**Usage:**
```bash
casestudypilot extract-screenshots \
  --video-data video_data.json \
  --analysis transcript_analysis.json \
  --output screenshots.json \
  --download-dir case-studies/images/intuit/
```

**Output:** `screenshots.json`

**Format:**
```json
{
  "company_slug": "intuit",
  "screenshots": [
    {
      "section": "challenge",
      "timestamp": 325,
      "timestamp_formatted": "5:25",
      "reason": "Speaker discussing deployment pain points",
      "youtube_url": "https://img.youtube.com/vi/V6L-xOUdoRQ/sddefault.jpg",
      "local_path": "case-studies/images/intuit/challenge.jpg",
      "caption": "Traditional deployment pipeline challenges"
    },
    {
      "section": "solution",
      "timestamp": 892,
      "timestamp_formatted": "14:52",
      "reason": "GitOps architecture explanation",
      "youtube_url": "https://img.youtube.com/vi/V6L-xOUdoRQ/sddefault.jpg",
      "local_path": "case-studies/images/intuit/solution.jpg",
      "caption": "Argo CD GitOps workflow architecture"
    }
  ]
}
```

### 2. New Tool Module: `screenshot_extractor.py`

**Location:** `casestudypilot/tools/screenshot_extractor.py`

**Core Functions:**

```python
def analyze_transcript_for_visual_moments(
    transcript_segments: List[Dict],
    analysis: Dict
) -> List[Dict]:
    """Find moments where visuals are likely shown."""

def select_optimal_timestamps(
    visual_moments: List[Dict],
    target_sections: List[str] = ["challenge", "solution"]
) -> List[Dict]:
    """Select best timestamps for each target section."""

def generate_screenshot_urls(
    video_id: str,
    quality: str = "sddefault"
) -> str:
    """Generate YouTube thumbnail URL."""

def download_screenshot(
    url: str,
    output_path: Path
) -> Dict:
    """Download screenshot from URL to local path."""

def generate_caption(
    section: str,
    sections_content: Dict,
    timestamp: int
) -> str:
    """Generate contextual caption for screenshot."""

def extract_screenshots(
    video_data_path: Path,
    analysis_path: Path,
    sections_path: Path,
    output_path: Path,
    download_dir: Path
) -> Dict:
    """Main function: orchestrate screenshot extraction."""
```

### 3. Update Jinja2 Template

**File:** `templates/case_study.md.j2`

**Add screenshot rendering to Challenge and Solution sections:**

```jinja2
## Challenge

{{ sections.challenge }}

{% if screenshots and screenshots.challenge %}

![{{ screenshots.challenge.caption }}]({{ screenshots.challenge.local_path }})
*{{ screenshots.challenge.caption }}* {% if screenshots.challenge.timestamp_formatted %}*({{ screenshots.challenge.timestamp_formatted }})*{% endif %}
{% endif %}

---

## Solution

{{ sections.solution }}

{% if screenshots and screenshots.solution %}

![{{ screenshots.solution.caption }}]({{ screenshots.solution.local_path }})
*{{ screenshots.solution.caption }}* {% if screenshots.solution.timestamp_formatted %}*({{ screenshots.solution.timestamp_formatted }})*{% endif %}
{% endif %}
```

### 4. Update Assembler

**File:** `casestudypilot/tools/assembler.py`

**Changes:**
- Add optional `screenshots_path` parameter
- Load screenshots JSON if provided
- Pass to template context

```python
def assemble_case_study(
    video_data_path: Path,
    analysis_path: Path,
    sections_path: Path,
    verification_path: Path,
    screenshots_path: Path = None,  # NEW
    output_path: Path = None,
) -> Dict[str, Any]:
    # ... existing code ...
    
    # NEW: Load screenshots if provided
    screenshots = None
    if screenshots_path and screenshots_path.exists():
        screenshots_data = load_json_file(screenshots_path)
        # Convert list to dict keyed by section
        screenshots = {
            s["section"]: s 
            for s in screenshots_data.get("screenshots", [])
        }
    
    context = {
        "company": ...,
        "video": ...,
        "analysis": ...,
        "sections": ...,
        "verification": ...,
        "screenshots": screenshots,  # NEW
    }
```

### 5. Update Agent Workflow

**File:** `.github/agents/case-study-agent.md`

**Add step 9.5 between analysis and assembly:**

```markdown
### Step 9.5: Extract Screenshots

**Command:**
```bash
casestudypilot extract-screenshots \
  --video-data video_data.json \
  --analysis transcript_analysis.json \
  --sections case_study_sections.json \
  --output screenshots.json \
  --download-dir case-studies/images/{company-slug}/
```

**Purpose:**
1. Analyze transcript for visual reference moments
2. Select optimal timestamps for Challenge and Solution sections
3. Generate YouTube thumbnail URLs
4. Download screenshots to local directory
5. Create contextual captions based on section content

**Output:** `screenshots.json`

**Success Criteria:**
- 2 screenshots identified (one per section)
- Files downloaded successfully
- Captions generated for each screenshot
- JSON contains all metadata
```

### 6. Update Validation

**File:** `casestudypilot/tools/validator.py`

**Add screenshot validation checks:**

```python
def validate_screenshots(content: str) -> Dict:
    """Check for screenshot presence and validity."""
    
    # Check for markdown images
    images = re.findall(r'!\[.*?\]\(.*?\)', content)
    
    return {
        "has_images": len(images) > 0,
        "image_count": len(images),
        "expected_count": 2,
        "score": min(len(images) / 2, 1.0)  # Expect 2 images
    }
```

---

## Data Flow

```
1. YouTube URL → youtube_client.py → video_data.json (with video_id)
                                     ↓
2. Transcript → transcript-analysis → transcript_analysis.json (visual moments)
                                     ↓
3. Sections generated → case_study_sections.json (Challenge/Solution content)
                        ↓
4. All inputs → screenshot_extractor.py → screenshots.json + downloaded images
                                         ↓
5. All JSON files → assembler.py → case-studies/{company}.md (with images)
```

---

## Visual Moment Detection

**Phrases indicating visual content:**

- "as you can see"
- "this slide shows"
- "here's a diagram"
- "let me show you"
- "looking at this chart"
- "on this screen"
- "this architecture"
- "these metrics"
- "here are the results"
- "this graph illustrates"

**Scoring logic:**

1. Count visual indicator phrases near timestamp
2. Check if timestamp aligns with section boundaries
3. Prefer moments in first 2/3 of video (actual content vs Q&A)
4. Select highest-scoring moment per section

---

## File Changes Summary

### New Files
- `casestudypilot/tools/screenshot_extractor.py` - Core implementation
- `tests/test_screenshot_extractor.py` - Unit tests
- `docs/SCREENSHOT-INTEGRATION-PLAN.md` - This document

### Modified Files
- `casestudypilot/__main__.py` - Add CLI command
- `casestudypilot/tools/assembler.py` - Add screenshots parameter
- `templates/case_study.md.j2` - Add image rendering
- `.github/agents/case-study-agent.md` - Add workflow step
- `casestudypilot/tools/validator.py` - Add image validation

### New Directories
- `case-studies/images/` - Base directory
- `case-studies/images/{company-slug}/` - Per-company subdirectories

---

## Testing Requirements

### Unit Tests (`tests/test_screenshot_extractor.py`)

```python
def test_analyze_visual_moments()
    """Test detection of visual indicator phrases."""

def test_select_optimal_timestamps()
    """Test timestamp selection for sections."""

def test_generate_screenshot_urls()
    """Test YouTube URL generation."""

def test_download_screenshot()
    """Test image download (mocked)."""

def test_generate_caption()
    """Test caption generation from context."""

def test_extract_screenshots_integration()
    """Test full workflow."""
```

### Integration Test

Run full workflow with Intuit case study:
```bash
casestudypilot extract-screenshots \
  --video-data video_data.json \
  --analysis transcript_analysis.json \
  --sections case_study_sections.json \
  --output screenshots.json \
  --download-dir case-studies/images/intuit/

casestudypilot assemble \
  video_data.json \
  transcript_analysis.json \
  case_study_sections.json \
  company_verification.json \
  --screenshots screenshots.json \
  --output case-studies/intuit.md
```

---

## Dependencies

### Already Available
- `httpx>=0.24.0` - HTTP client for downloads
- `jinja2>=3.1.0` - Template rendering

### New (Optional)
- `Pillow>=10.0.0` - Image validation/manipulation (optional enhancement)

---

## Risk Mitigation

### Risk 1: YouTube thumbnail unavailable
- **Fallback:** Skip screenshots, text-only case study
- **Validation:** Check HTTP 200 before rendering

### Risk 2: Image directories not created
- **Solution:** `Path.mkdir(parents=True, exist_ok=True)`
- **Validation:** Verify directory exists before download

### Risk 3: Large file sizes
- **Solution:** Use `sddefault.jpg` (640x480) instead of maxres
- **Validation:** Warn if file >500KB

### Risk 4: Broken paths in markdown
- **Solution:** Use repository-root-relative paths
- **Validation:** Test GitHub markdown preview

---

## Implementation Phases

### Phase 1: Core Implementation (MVP)
- [ ] Implement `screenshot_extractor.py`
- [ ] Add `extract-screenshots` CLI command
- [ ] Update template with image rendering
- [ ] Update assembler to accept screenshots
- [ ] Basic unit tests

### Phase 2: Integration
- [ ] Update agent workflow
- [ ] Update validator
- [ ] Integration tests
- [ ] Documentation updates

### Phase 3: Enhancement (Future)
- [ ] Add yt-dlp for timestamp-specific frames
- [ ] ML-based scene detection
- [ ] Screenshot galleries
- [ ] Animated GIFs

---

## Success Criteria

Implementation complete when:

- [x] Planning document created
- [ ] `screenshot_extractor.py` implemented
- [ ] `extract-screenshots` CLI command works
- [ ] Template renders images correctly
- [ ] Assembler accepts screenshots parameter
- [ ] Tests pass for all functions
- [ ] Integration test successful with Intuit case study
- [ ] Documentation updated
- [ ] At least one case study generated with screenshots

---

## Future Enhancements

### 1. Timestamp-Specific Frame Extraction (yt-dlp)

Replace static thumbnails with exact frames:

```python
def extract_frame_at_timestamp(
    video_url: str, 
    timestamp: int, 
    output: Path
):
    """Extract specific frame using yt-dlp."""
    import subprocess
    
    cmd = [
        "yt-dlp",
        "--skip-download",
        f"--external-downloader=ffmpeg",
        f"--external-downloader-args=-ss {timestamp} -frames:v 1",
        f"--output={output}",
        video_url
    ]
    subprocess.run(cmd, check=True)
```

**Pros:** Exact presentation slides, diagrams, metrics
**Cons:** Video download, slower, additional dependency

### 2. Screenshot Galleries

Multiple images per section with thumbnails and lightbox.

### 3. AI-Generated Captions

Use vision model to analyze extracted frames and generate descriptive captions.

### 4. User-Specified Timestamps

Allow issue creators to specify exact timestamps:
```
@case-study-agent generate case study
Screenshots at: 5:23, 12:45
```

### 5. Batch Processing

Pre-extract screenshots for all CNCF videos in library.

---

## Example Output

**Generated markdown:**

```markdown
## Challenge

Before adopting cloud-native technologies, Intuit struggled with slow, manual 
deployment processes that created bottlenecks in software delivery...

![Traditional deployment pipeline challenges](case-studies/images/intuit/challenge.jpg)
*Traditional deployment pipeline challenges (5:25)*

---

## Solution

Intuit adopted **Kubernetes** as its standard container orchestration platform...

![Argo CD GitOps workflow architecture](case-studies/images/intuit/solution.jpg)
*Argo CD GitOps workflow architecture (14:52)*
```

**Rendered HTML:**
- Images appear inline within Challenge and Solution sections
- Captions provide context
- Timestamps link back to video moments
- Visual variety breaks up text-heavy content

---

## References

- YouTube Thumbnail API: `https://img.youtube.com/vi/{VIDEO_ID}/{quality}.jpg`
- YouTube Video Format: `https://www.youtube.com/watch?v={VIDEO_ID}`
- yt-dlp documentation: https://github.com/yt-dlp/yt-dlp
- Pillow (PIL) documentation: https://pillow.readthedocs.io/

---

*This plan provides a complete approach to adding contextual video screenshots to case study reports while maintaining system simplicity and reliability.*
