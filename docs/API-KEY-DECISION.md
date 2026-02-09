# Architecture Decision Record: API-Key-Free Design

**Decision Date:** February 9, 2026  
**Status:** Accepted  
**Deciders:** User, Assistant

---

## Context

The original design for the CNCF Case Study Automation system required a YouTube Data API v3 key from Google Cloud Platform to fetch video metadata (title, description, duration, publish date).

During planning review, the user questioned: **"do I need a google cloud key and integration to get the transcripts from youtube? seems overkill"**

This prompted a re-evaluation of the YouTube API requirement.

---

## Decision

**We will NOT require a YouTube API key for basic operation.**

Instead, we will:
1. Use `youtube-transcript-api` library to fetch transcripts (no authentication required)
2. Use placeholder metadata for title/description
3. Calculate video duration from transcript timing
4. Make rich metadata optional for future enhancement

---

## Rationale

### Why Remove the API Key Requirement?

#### User Experience Benefits

1. **Zero Setup Friction**
   - No Google Cloud account needed
   - No API key generation
   - No secret management
   - Works immediately after `pip install`

2. **Faster Testing**
   - Developers can test instantly
   - No credential configuration
   - No rate limiting concerns (10K requests/day)
   - No cost tracking needed

3. **Simpler Documentation**
   - No GCP setup instructions
   - No secret management guide
   - No API quota explanations
   - Fewer failure points

#### Technical Benefits

1. **Reduced Dependencies**
   - Remove `google-api-python-client` (~20MB package)
   - One less external service dependency
   - Fewer potential authentication failures

2. **Better Reliability**
   - No API quota issues
   - No authentication failures
   - No rate limiting
   - One less point of failure

3. **Adequate Functionality**
   - Transcript contains all critical information
   - Agent can infer company name from content
   - Duration can be calculated from transcript
   - Title/description are not essential for case study generation

### What We Lose

1. **Rich Metadata**
   - Video title → Placeholder: "YouTube Video {video_id}"
   - Description → Empty string
   - Channel name → Empty string
   - Publish date → Empty string
   - Exact duration → Calculated from transcript (close enough)

2. **User-Facing Impact**
   - Agent must infer company name from issue title or transcript
   - Case study metadata section has less info
   - Cannot verify video details programmatically

**Assessment:** These losses are acceptable. The transcript contains all necessary information for case study generation.

---

## Technical Implementation

### Before (With API Key)

```python
def fetch_video_data(url: str, api_key: str) -> Dict[str, Any]:
    video_id = extract_video_id(url)
    
    # Requires API key
    youtube = build("youtube", "v3", developerKey=api_key)
    response = youtube.videos().list(part="snippet,contentDetails", id=video_id).execute()
    
    # Extract metadata
    title = response["items"][0]["snippet"]["title"]
    description = response["items"][0]["snippet"]["description"]
    duration = parse_iso8601_duration(response["items"][0]["contentDetails"]["duration"])
    
    # Fetch transcript (no auth)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    return {
        "video_id": video_id,
        "title": title,
        "description": description,
        "duration_seconds": duration,
        "transcript": transcript
    }
```

### After (No API Key)

```python
def fetch_video_data(url: str) -> Dict[str, Any]:
    video_id = extract_video_id(url)
    
    # Fetch transcript (no auth)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    # Calculate duration from transcript
    duration = int(transcript[-1]["start"] + transcript[-1]["duration"])
    
    return {
        "video_id": video_id,
        "url": url,
        "title": f"YouTube Video {video_id}",  # Placeholder
        "description": "",                      # Placeholder
        "duration_seconds": duration,           # Calculated
        "transcript": transcript                # Complete data
    }
```

**Key Change:** Single external API call instead of two, no authentication needed.

---

## Consequences

### Positive

1. ✅ **Instant Setup**
   - Clone repo → `pip install -r requirements.txt` → Done
   - No credential configuration step
   - New contributors can start immediately

2. ✅ **Reduced Complexity**
   - Fewer dependencies
   - Simpler error handling (no auth failures)
   - Less documentation needed

3. ✅ **Better Reliability**
   - No API quota limits
   - No authentication token expiration
   - No rate limiting issues

4. ✅ **Adequate Functionality**
   - Transcript has all info needed for case studies
   - Company name in issue title or transcript
   - Duration calculated accurately enough

### Negative

1. ❌ **Placeholder Metadata**
   - Title not automatically extracted
   - Description not available
   - Channel name unknown
   - Publish date missing

2. ❌ **Manual Company Name Extraction**
   - Agent must infer company name from issue title
   - Or extract from transcript content
   - Slightly more complex agent logic

3. ❌ **Less Rich Output**
   - Case study metadata section has less info
   - Cannot programmatically verify video details
   - Missing publish date context

**Assessment:** Negative consequences are minor and acceptable for a planning/prototype phase.

---

## Alternatives Considered

### Alternative 1: Make API Key Optional

**Approach:**
```python
def fetch_video_data(url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    if api_key:
        return fetch_with_rich_metadata(url, api_key)
    else:
        return fetch_with_basic_metadata(url)
```

**Pros:**
- Best of both worlds
- Users can choose setup complexity vs. functionality
- Easy upgrade path

**Cons:**
- More complex implementation
- Two code paths to maintain
- API key still needed for full functionality

**Decision:** Good future enhancement, but not for initial implementation.

### Alternative 2: Scrape YouTube Page

**Approach:** Parse YouTube video HTML to extract title/description

**Pros:**
- No API key needed
- Rich metadata available

**Cons:**
- Fragile (HTML structure changes)
- Against YouTube TOS
- Rate limiting risk
- More complex parsing

**Decision:** Rejected - violates TOS, too fragile.

### Alternative 3: Require API Key (Original Design)

**Approach:** Stick with original plan requiring YouTube Data API v3 key

**Pros:**
- Rich metadata available
- Proper authentication
- Within YouTube TOS
- Accurate video details

**Cons:**
- User feedback: "seems overkill"
- Setup friction
- Credential management
- Additional failure point

**Decision:** Rejected based on user feedback and cost/benefit analysis.

---

## Future Enhancements

### Enhancement: Optional API Key Support

**When to add:**
- After initial implementation proves the concept
- If users request richer metadata
- If company name inference proves problematic

**How to add:**
1. Add optional `api_key` parameter to `fetch_video_data()`
2. If provided: call YouTube Data API
3. If not provided: use current placeholder approach
4. Update documentation with API setup instructions
5. Add environment variable support: `YOUTUBE_API_KEY`

**Effort:** Low (1-2 days)

**Example:**
```python
def fetch_video_data(url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    video_id = extract_video_id(url)
    
    if api_key:
        metadata = fetch_rich_metadata(video_id, api_key)
    else:
        metadata = extract_basic_metadata(url, video_id)
    
    transcript = fetch_transcript(video_id)
    
    # Calculate duration from transcript if not available
    if metadata["duration_seconds"] == 0 and transcript:
        metadata["duration_seconds"] = calculate_duration(transcript)
    
    return {**metadata, "transcript": transcript}
```

---

## Lessons Learned

### For Future Architecture Decisions

1. **Question Assumptions**
   - Original design assumed API key was necessary
   - User question revealed it wasn't for core functionality
   - Always ask: "What's the simplest solution?"

2. **Prioritize Setup Simplicity**
   - Fewer setup steps = more users willing to try
   - External dependencies should be optional when possible
   - Authentication adds complexity - justify it

3. **Distinguish Must-Have vs. Nice-To-Have**
   - Transcript: Must-have (contains case study content)
   - Title/Description: Nice-to-have (not essential)
   - Focus on must-haves first

4. **Listen to User Feedback**
   - User questioning design can reveal improvements
   - "Seems overkill" is valid technical feedback
   - Re-evaluate when concerns are raised

---

## References

- [youtube-transcript-api Documentation](https://github.com/jdepoix/youtube-transcript-api)
- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [YouTube Terms of Service](https://www.youtube.com/static?template=terms)

---

## Approval

**User:** Approved simplification by questioning API key necessity  
**Assistant:** Implemented API-key-free design based on user feedback  
**Status:** Accepted and documented  

---

*This decision can be revisited in the future if richer metadata proves necessary.*
