# CNCF Case Study Automation System - Python Implementation Design

# Milestone 2: Component Specifications

**Previous:** [Milestone 1: Executive Summary & Architecture](./2026-02-09-python-design-m1-overview.md)  
**Next:** [Milestone 3: Implementation Roadmap & Testing](./2026-02-09-python-design-m3-implementation.md)

---

## Table of Contents

1. [YouTube API Client](#1-youtube-api-client)
2. [Transcript Corrector](#2-transcript-corrector)
3. [Company Verifier](#3-company-verifier)
4. [NLP Engine (spaCy)](#4-nlp-engine-spacy)
5. [AI Content Generator](#5-ai-content-generator)
6. [Case Study Assembler](#6-case-study-assembler)
7. [GitHub Integration](#7-github-integration)

---

## 1. YouTube API Client

**Responsibility:** Interact with YouTube Data API v3 to retrieve video metadata and transcripts.

### Interface

```python
# casestudypilot/youtube/client.py
from typing import Optional
from casestudypilot.models.video import VideoMetadata, Transcript


class YouTubeClient:
    """Async YouTube API client."""
    
    async def get_metadata(self, video_id: str) -> VideoMetadata:
        """
        Fetch video metadata from YouTube API.
        
        Args:
            video_id: YouTube video ID (11 characters)
            
        Returns:
            VideoMetadata with title, channel, speakers, etc.
            
        Raises:
            VideoNotFoundError: Video doesn't exist
            PrivateVideoError: Video is private
            WrongChannelError: Video not from CNCF channel
        """
        ...
    
    async def get_transcript(self, video_id: str, language: str = "en") -> Transcript:
        """
        Fetch video transcript/captions.
        
        Priority order:
        1. Manual captions (if available)
        2. Auto-generated captions
        
        Args:
            video_id: YouTube video ID
            language: Preferred language code (default: "en")
            
        Returns:
            Transcript with full text and metadata
            
        Raises:
            NoTranscriptAvailableError: No captions found
        """
        ...
    
    async def validate_video(self, video_id: str) -> bool:
        """
        Quick validation: exists, public, CNCF channel.
        
        Returns:
            True if valid, False otherwise
        """
        ...
```

### Implementation Details

#### Metadata Extraction

```python
# casestudypilot/youtube/metadata_extractor.py
import re
from datetime import datetime
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from casestudypilot.models.video import VideoMetadata, CaptionTrack


class MetadataExtractor:
    """Extract video metadata from YouTube API."""
    
    # CNCF Channel ID
    CNCF_CHANNEL_ID = "UCvqbFHwN-nwalWPjPUKpvTA"
    
    def __init__(self, api_key: str):
        self.youtube = build("youtube", "v3", developerKey=api_key)
    
    async def extract(self, video_id: str) -> VideoMetadata:
        """Extract metadata from video."""
        try:
            # Fetch video details
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            
            if not response["items"]:
                raise VideoNotFoundError(f"Video {video_id} not found")
            
            item = response["items"][0]
            snippet = item["snippet"]
            
            # Validate CNCF channel
            if snippet["channelId"] != self.CNCF_CHANNEL_ID:
                raise WrongChannelError(
                    f"Video is not from CNCF channel (found: {snippet['channelTitle']})"
                )
            
            # Extract speakers and company from title
            speakers, company = self._parse_speakers_from_title(snippet["title"])
            
            # If not in title, try description
            if not speakers:
                speakers, company = self._parse_speakers_from_description(
                    snippet["description"]
                )
            
            # Get caption tracks
            captions = await self._get_caption_tracks(video_id)
            
            return VideoMetadata(
                video_id=video_id,
                url=f"https://www.youtube.com/watch?v={video_id}",
                title=snippet["title"],
                description=snippet["description"],
                channel_id=snippet["channelId"],
                channel_name=snippet["channelTitle"],
                published_at=datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")),
                duration_seconds=self._parse_duration(item["contentDetails"]["duration"]),
                speakers=speakers,
                company=company,
                caption_tracks=captions
            )
            
        except HttpError as e:
            if e.resp.status == 404:
                raise VideoNotFoundError(f"Video {video_id} not found")
            raise
    
    def _parse_speakers_from_title(self, title: str) -> tuple[list[str], Optional[str]]:
        """
        Parse speaker names and company from video title.
        
        Common KubeCon formats:
        - "Topic - Speaker1 & Speaker2, Company"
        - "Topic - Speaker1, Company1 & Speaker2, Company2"
        - "Topic | Speaker Name, Company"
        """
        speakers = []
        company = None
        
        # Pattern: " - Name1 & Name2, Company"
        pattern1 = re.compile(
            r'\s-\s([A-Z][a-z]+(?:\s[A-Z][a-z]+)?(?:\s&\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)?)?),\s*([^|]+)'
        )
        match = pattern1.search(title)
        if match:
            speaker_str = match.group(1)
            company = match.group(2).strip()
            speakers = [s.strip() for s in re.split(r'\s&\s', speaker_str)]
            return speakers, company
        
        # Pattern: " | Name, Company"
        pattern2 = re.compile(r'\|\s*([A-Z][a-z]+\s[A-Z][a-z]+),\s*([^|]+)')
        match = pattern2.search(title)
        if match:
            speakers = [match.group(1).strip()]
            company = match.group(2).strip()
            return speakers, company
        
        return [], None
    
    def _parse_speakers_from_description(self, description: str) -> tuple[list[str], Optional[str]]:
        """
        Parse speakers from video description as fallback.
        
        Look for:
        - "Speakers:\\nName1, Company\\nName2, Company"
        - "Presented by Name1 and Name2 from Company"
        """
        # Pattern: "Speakers:" section
        speakers_section = re.search(
            r'Speakers?:\s*\n((?:[A-Z][a-z]+\s[A-Z][a-z]+,\s[^\n]+\n?)+)',
            description,
            re.MULTILINE
        )
        if speakers_section:
            lines = speakers_section.group(1).strip().split('\n')
            speakers = []
            company = None
            for line in lines:
                match = re.match(r'([A-Z][a-z]+\s[A-Z][a-z]+),\s*([^,]+)', line)
                if match:
                    speakers.append(match.group(1).strip())
                    if not company:
                        company = match.group(2).strip()
            return speakers, company
        
        # Pattern: "Presented by X and Y from Company"
        presented = re.search(
            r'[Pp]resented by\s+([A-Z][a-z]+\s[A-Z][a-z]+)(?:\s+and\s+([A-Z][a-z]+\s[A-Z][a-z]+))?\s+from\s+([^.]+)',
            description
        )
        if presented:
            speakers = [presented.group(1)]
            if presented.group(2):
                speakers.append(presented.group(2))
            company = presented.group(3).strip()
            return speakers, company
        
        return [], None
    
    async def _get_caption_tracks(self, video_id: str) -> list[CaptionTrack]:
        """Get available caption tracks."""
        try:
            request = self.youtube.captions().list(
                part="snippet",
                videoId=video_id
            )
            response = request.execute()
            
            tracks = []
            for item in response.get("items", []):
                snippet = item["snippet"]
                tracks.append(CaptionTrack(
                    language=snippet["language"],
                    language_name=snippet.get("name", snippet["language"]),
                    is_auto_generated=snippet["trackKind"] == "asr"
                ))
            return tracks
            
        except HttpError:
            return []  # Captions API not accessible, will use transcript-api
    
    @staticmethod
    def _parse_duration(duration: str) -> int:
        """
        Parse ISO 8601 duration to seconds.
        
        Example: "PT4M13S" -> 253 seconds
        """
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration)
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
```

#### Transcript Fetching

```python
# casestudypilot/youtube/transcript_fetcher.py
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

from casestudypilot.models.video import Transcript, CaptionType


class TranscriptFetcher:
    """Fetch video transcripts."""
    
    async def fetch(self, video_id: str, language: str = "en") -> Transcript:
        """
        Fetch transcript from YouTube.
        
        Uses youtube-transcript-api (no API quota consumption).
        """
        try:
            # Get all available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try manual captions first
            try:
                transcript_data = transcript_list.find_manually_created_transcript([language])
                caption_type = CaptionType.MANUAL
            except NoTranscriptFound:
                # Fall back to auto-generated
                transcript_data = transcript_list.find_generated_transcript([language])
                caption_type = CaptionType.AUTO_GENERATED
            
            # Fetch the transcript
            entries = transcript_data.fetch()
            
            # Combine all text entries
            full_text = " ".join(entry["text"] for entry in entries)
            
            # Clean up transcript
            full_text = self._clean_transcript(full_text)
            
            word_count = len(full_text.split())
            
            return Transcript(
                video_id=video_id,
                content=full_text,
                language=language,
                caption_type=caption_type,
                word_count=word_count
            )
            
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
            raise NoTranscriptAvailableError(
                f"No transcript available for video {video_id}: {str(e)}"
            )
    
    @staticmethod
    def _clean_transcript(text: str) -> str:
        """Clean up transcript text."""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove [Music], [Applause], etc.
        text = re.sub(r'\[[\w\s]+\]', '', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
```

### Error Handling

```python
# casestudypilot/utils/errors.py
class YouTubeError(Exception):
    """Base YouTube error."""
    pass


class VideoNotFoundError(YouTubeError):
    """Video doesn't exist."""
    pass


class PrivateVideoError(YouTubeError):
    """Video is private or restricted."""
    pass


class WrongChannelError(YouTubeError):
    """Video not from CNCF channel."""
    pass


class NoTranscriptAvailableError(YouTubeError):
    """No captions/transcript available."""
    pass
```

---

## 2. Transcript Corrector

**Responsibility:** Correct speech-to-text errors using CNCF glossary, spell checking, and pattern matching.

### Interface

```python
# casestudypilot/transcript/corrector.py
from casestudypilot.models.correction import CorrectionResult


class TranscriptCorrector:
    """Multi-layered transcript correction."""
    
    async def correct(self, text: str) -> CorrectionResult:
        """
        Correct transcript errors.
        
        Correction pipeline:
        1. Glossary corrections (CNCF terms)
        2. Pattern-based corrections (known errors)
        3. Context analysis (preserve proper nouns, code)
        4. Spell checking (Levenshtein distance)
        5. Confidence scoring
        
        Args:
            text: Raw transcript text
            
        Returns:
            CorrectionResult with corrected text and metadata
        """
        ...
```

### Implementation Layers

#### 1. Glossary Corrector

```python
# casestudypilot/transcript/glossary_corrector.py
from casestudypilot.models.correction import Correction, CorrectionMethod


class GlossaryCorrector:
    """Correct using CNCF glossary terms."""
    
    # CNCF canonical terms
    GLOSSARY_TERMS = {
        "kubernetes": "Kubernetes",
        "prometheus": "Prometheus",
        "envoy": "Envoy",
        "istio": "Istio",
        "helm": "Helm",
        "etcd": "etcd",
        "containerd": "containerd",
        "kubectl": "kubectl",
        "argo": "Argo",
        "argo cd": "Argo CD",
        "argocd": "Argo CD",
        "flux": "Flux",
        "fluentd": "Fluentd",
        "jaeger": "Jaeger",
        "cilium": "Cilium",
        "linkerd": "Linkerd",
        "vitess": "Vitess",
        "harbor": "Harbor",
        "gitops": "GitOps",
        "devsecops": "DevSecOps",
        "microservices": "microservices",
        "containerization": "containerization",
        "orchestration": "orchestration",
    }
    
    def correct(self, text: str) -> tuple[str, list[Correction]]:
        """
        Apply glossary corrections.
        
        Returns:
            (corrected_text, list_of_corrections)
        """
        corrections = []
        result_text = text
        
        # Process each term
        for incorrect, correct in self.GLOSSARY_TERMS.items():
            pattern = re.compile(r'\b' + re.escape(incorrect) + r'\b', re.IGNORECASE)
            
            for match in pattern.finditer(text):
                # Only correct if not already correct case
                if match.group(0) != correct:
                    position = match.start()
                    original = match.group(0)
                    
                    # Get context (50 chars before/after)
                    context_start = max(0, position - 50)
                    context_end = min(len(text), position + len(original) + 50)
                    context = text[context_start:context_end]
                    
                    corrections.append(Correction(
                        position=position,
                        original=original,
                        corrected=correct,
                        method=CorrectionMethod.GLOSSARY,
                        confidence=1.0,  # Glossary = 100% confidence
                        context=context
                    ))
                    
                    # Apply correction
                    result_text = result_text[:position] + correct + result_text[position + len(original):]
        
        return result_text, corrections
```

#### 2. Pattern Corrector

```python
# casestudypilot/transcript/pattern_corrector.py
import re
from dataclasses import dataclass


@dataclass
class CorrectionPattern:
    """Pattern-based correction rule."""
    pattern: re.Pattern
    replacement: str
    confidence: float
    description: str


class PatternCorrector:
    """Apply known error patterns."""
    
    PATTERNS = [
        # Spacing errors
        CorrectionPattern(
            pattern=re.compile(r'\bmicro\s+services\b', re.IGNORECASE),
            replacement="microservices",
            confidence=0.95,
            description="Fix 'micro services' spacing"
        ),
        CorrectionPattern(
            pattern=re.compile(r'\bcloud\s+native\b', re.IGNORECASE),
            replacement="cloud native",
            confidence=0.90,
            description="Standardize 'cloud native'"
        ),
        
        # Homophone errors
        CorrectionPattern(
            pattern=re.compile(r'\bcueectl\b', re.IGNORECASE),
            replacement="kubectl",
            confidence=0.99,
            description="Fix 'cueectl' -> 'kubectl'"
        ),
        CorrectionPattern(
            pattern=re.compile(r'\bprom\s*etheus\b', re.IGNORECASE),
            replacement="Prometheus",
            confidence=0.95,
            description="Fix spacing in Prometheus"
        ),
        
        # Common mispellings
        CorrectionPattern(
            pattern=re.compile(r'\bkubernetes\s+cluster\b', re.IGNORECASE),
            replacement="Kubernetes cluster",
            confidence=0.90,
            description="Capitalize Kubernetes"
        ),
    ]
    
    def correct(self, text: str) -> tuple[str, list[Correction]]:
        """Apply pattern-based corrections."""
        corrections = []
        result_text = text
        
        for pattern_rule in self.PATTERNS:
            for match in pattern_rule.pattern.finditer(text):
                position = match.start()
                original = match.group(0)
                
                corrections.append(Correction(
                    position=position,
                    original=original,
                    corrected=pattern_rule.replacement,
                    method=CorrectionMethod.PATTERN,
                    confidence=pattern_rule.confidence,
                    context=text[max(0, position-50):min(len(text), position+100)]
                ))
                
                result_text = pattern_rule.pattern.sub(pattern_rule.replacement, result_text)
        
        return result_text, corrections
```

#### 3. Context Analyzer

```python
# casestudypilot/transcript/context_analyzer.py
import re


class ContextAnalyzer:
    """
    Analyze context to determine if correction should be applied.
    
    Preserves:
    - Code blocks (backticks)
    - Quoted text
    - Acronyms (all caps)
    - URLs
    """
    
    def should_preserve(self, text: str, position: int, word: str) -> bool:
        """
        Check if word at position should be preserved (not corrected).
        
        Args:
            text: Full text
            position: Position of word
            word: Word to check
            
        Returns:
            True if should preserve, False if can correct
        """
        # Preserve acronyms (2+ uppercase letters)
        if len(word) >= 2 and word.isupper():
            return True
        
        # Check if in code block (backticks)
        if self._is_in_code_block(text, position):
            return True
        
        # Check if in quotes
        if self._is_in_quotes(text, position):
            return True
        
        # Check if part of URL
        if self._is_in_url(text, position):
            return True
        
        return False
    
    @staticmethod
    def _is_in_code_block(text: str, position: int) -> bool:
        """Check if position is inside backtick code block."""
        # Count backticks before position
        before = text[:position]
        single_backticks = before.count('`') - before.count('```') * 3
        triple_backticks = before.count('```')
        
        # Inside triple backticks?
        if triple_backticks % 2 == 1:
            return True
        
        # Inside single backticks?
        if single_backticks % 2 == 1:
            return True
        
        return False
    
    @staticmethod
    def _is_in_quotes(text: str, position: int) -> bool:
        """Check if position is inside quotes."""
        before = text[:position]
        
        # Check double quotes
        if before.count('"') % 2 == 1:
            return True
        
        # Check single quotes (but not apostrophes)
        single_quotes = re.findall(r"(?<!\w)'|'(?!\w)", before)
        if len(single_quotes) % 2 == 1:
            return True
        
        return False
    
    @staticmethod
    def _is_in_url(text: str, position: int) -> bool:
        """Check if position is part of URL."""
        # Look for http:// or https:// before position
        url_pattern = re.compile(r'https?://[^\s]+')
        for match in url_pattern.finditer(text):
            if match.start() <= position <= match.end():
                return True
        return False
```

#### 4. Spell Corrector

```python
# casestudypilot/transcript/spell_corrector.py
from spellchecker import SpellChecker
from rapidfuzz import fuzz


class SpellCorrector:
    """Spell check with Levenshtein distance."""
    
    def __init__(self):
        self.spell = SpellChecker()
        
        # Add CNCF terms to dictionary (don't flag as misspelled)
        cncf_terms = [
            "kubernetes", "kubectl", "helm", "prometheus",
            "grafana", "envoy", "istio", "linkerd", "cilium",
            "etcd", "containerd", "fluentd", "jaeger",
            "gitops", "devsecops", "microservices"
        ]
        self.spell.word_frequency.load_words(cncf_terms)
    
    def correct(self, text: str, min_confidence: float = 0.50) -> tuple[str, list[Correction]]:
        """
        Apply spell corrections.
        
        Only applies corrections with confidence >= min_confidence.
        """
        corrections = []
        words = text.split()
        result_words = []
        position = 0
        
        for word in words:
            # Clean word (remove punctuation for checking)
            clean_word = re.sub(r'[^\w]', '', word)
            
            if not clean_word:
                result_words.append(word)
                position += len(word) + 1
                continue
            
            # Check if misspelled
            if clean_word.lower() not in self.spell:
                # Get correction candidates
                candidates = self.spell.candidates(clean_word.lower())
                
                if candidates:
                    # Find best match
                    best_match = max(
                        candidates,
                        key=lambda c: fuzz.ratio(clean_word.lower(), c)
                    )
                    
                    # Calculate confidence
                    confidence = fuzz.ratio(clean_word.lower(), best_match) / 100.0
                    
                    if confidence >= min_confidence:
                        # Preserve original capitalization pattern
                        corrected = self._preserve_case(clean_word, best_match)
                        
                        corrections.append(Correction(
                            position=position,
                            original=clean_word,
                            corrected=corrected,
                            method=CorrectionMethod.SPELL_CHECK,
                            confidence=confidence,
                            context=""
                        ))
                        
                        # Replace in word (preserve punctuation)
                        corrected_word = word.replace(clean_word, corrected)
                        result_words.append(corrected_word)
                    else:
                        result_words.append(word)
                else:
                    result_words.append(word)
            else:
                result_words.append(word)
            
            position += len(word) + 1
        
        return ' '.join(result_words), corrections
    
    @staticmethod
    def _preserve_case(original: str, corrected: str) -> str:
        """Preserve capitalization pattern from original."""
        if original.isupper():
            return corrected.upper()
        elif original[0].isupper():
            return corrected.capitalize()
        else:
            return corrected.lower()
```

### Main Corrector Orchestrator

```python
# casestudypilot/transcript/corrector.py
from casestudypilot.models.correction import CorrectionResult, CorrectionStats


class TranscriptCorrector:
    """Orchestrate all correction layers."""
    
    def __init__(self):
        self.glossary_corrector = GlossaryCorrector()
        self.pattern_corrector = PatternCorrector()
        self.context_analyzer = ContextAnalyzer()
        self.spell_corrector = SpellCorrector()
    
    async def correct(self, text: str) -> CorrectionResult:
        """Apply all correction layers."""
        import time
        start_time = time.time()
        
        original_text = text
        all_corrections = []
        
        # Layer 1: Glossary corrections (highest confidence)
        text, glossary_corrections = self.glossary_corrector.correct(text)
        all_corrections.extend(glossary_corrections)
        
        # Layer 2: Pattern corrections
        text, pattern_corrections = self.pattern_corrector.correct(text)
        all_corrections.extend(pattern_corrections)
        
        # Layer 3: Spell corrections (with context preservation)
        words_to_correct = []
        for i, word in enumerate(text.split()):
            position = len(' '.join(text.split()[:i]))
            if not self.context_analyzer.should_preserve(text, position, word):
                words_to_correct.append((i, word))
        
        # Only spell-check words not in preserved contexts
        text, spell_corrections = self.spell_corrector.correct(text, min_confidence=0.50)
        all_corrections.extend(spell_corrections)
        
        # Calculate statistics
        original_words = len(original_text.split())
        corrected_words = len(all_corrections)
        
        high_conf = sum(1 for c in all_corrections if c.confidence >= 0.80)
        medium_conf = sum(1 for c in all_corrections if 0.50 <= c.confidence < 0.80)
        low_conf = sum(1 for c in all_corrections if c.confidence < 0.50)
        
        stats = CorrectionStats(
            total_words=original_words,
            corrected_words=corrected_words,
            high_confidence=high_conf,
            medium_confidence=medium_conf,
            low_confidence=low_conf
        )
        
        # Calculate overall confidence
        if corrected_words > 0:
            overall_confidence = sum(c.confidence for c in all_corrections) / corrected_words
        else:
            overall_confidence = 1.0  # No corrections needed = high confidence
        
        processing_time = (time.time() - start_time) * 1000  # ms
        
        return CorrectionResult(
            original=original_text,
            corrected=text,
            corrections=all_corrections,
            overall_confidence=overall_confidence,
            stats=stats,
            processing_time_ms=processing_time
        )
```

---

## 3. Company Verifier

**Responsibility:** Verify speaker's company is a CNCF end-user member using the Landscape.

### Interface

```python
# casestudypilot/landscape/client.py
from casestudypilot.models.company import VerificationResult


class LandscapeClient:
    """CNCF Landscape integration."""
    
    async def verify_company(self, company_name: str) -> VerificationResult:
        """
        Verify if company is CNCF end-user member.
        
        Args:
            company_name: Company name to verify
            
        Returns:
            VerificationResult with match confidence
        """
        ...
```

### Implementation

```python
# casestudypilot/landscape/matcher.py
from rapidfuzz import fuzz, process
from casestudypilot.models.company import CompanyInfo, VerificationResult, MembershipTier


class CompanyMatcher:
    """Fuzzy match company names against Landscape."""
    
    def __init__(self, end_user_companies: list[CompanyInfo]):
        self.companies = end_user_companies
        self.name_map = {
            self._normalize(company.name): company
            for company in end_user_companies
        }
        
        # Build alias map
        self.alias_map = {}
        for company in end_user_companies:
            for alias in company.aliases:
                self.alias_map[self._normalize(alias)] = company
    
    def match(self, query: str) -> VerificationResult:
        """
        Match company name with fuzzy matching.
        
        Matching strategy:
        1. Exact match (normalized)
        2. Alias match
        3. Fuzzy match (rapidfuzz)
        """
        normalized_query = self._normalize(query)
        
        # 1. Exact match
        if normalized_query in self.name_map:
            return VerificationResult(
                query_name=query,
                is_end_user_member=True,
                matched_company=self.name_map[normalized_query],
                confidence_score=1.0,
                match_method="exact"
            )
        
        # 2. Alias match
        if normalized_query in self.alias_map:
            return VerificationResult(
                query_name=query,
                is_end_user_member=True,
                matched_company=self.alias_map[normalized_query],
                confidence_score=0.98,
                match_method="alias"
            )
        
        # 3. Fuzzy match
        company_names = list(self.name_map.keys())
        matches = process.extract(
            normalized_query,
            company_names,
            scorer=fuzz.ratio,
            limit=5
        )
        
        if not matches:
            return VerificationResult(
                query_name=query,
                is_end_user_member=False,
                matched_company=None,
                confidence_score=0.0,
                match_method="none"
            )
        
        # Best match
        best_match_name, score, _ = matches[0]
        confidence = score / 100.0
        
        # Decision thresholds
        if confidence >= 0.95:
            is_member = True
        elif confidence >= 0.80:
            # Medium confidence - flag for review but proceed
            is_member = True
        else:
            is_member = False
        
        matched_company = self.name_map[best_match_name] if is_member else None
        
        return VerificationResult(
            query_name=query,
            is_end_user_member=is_member,
            matched_company=matched_company,
            confidence_score=confidence,
            match_method="fuzzy"
        )
    
    @staticmethod
    def _normalize(name: str) -> str:
        """Normalize company name for matching."""
        # Lowercase
        name = name.lower()
        
        # Remove punctuation
        name = re.sub(r'[^\w\s]', '', name)
        
        # Remove common suffixes
        suffixes = ["inc", "ltd", "llc", "corp", "corporation", "limited", "co"]
        for suffix in suffixes:
            name = re.sub(r'\b' + suffix + r'\b', '', name)
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        return name.strip()
```

---

## 4. NLP Engine (spaCy)

**Responsibility:** Extract semantic structure from transcripts using spaCy for entity recognition, section classification, and metric extraction.

### Interface

```python
# casestudypilot/nlp/engine.py
from casestudypilot.models.analysis import NLPAnalysis, ExtractedEntity, Section


class NLPEngine:
    """spaCy-powered NLP analysis."""
    
    async def analyze(self, text: str) -> NLPAnalysis:
        """
        Perform comprehensive NLP analysis on transcript.
        
        Pipeline:
        1. Load spaCy model (en_core_web_lg)
        2. Extract entities (companies, people, projects)
        3. Classify sentences into sections
        4. Extract quantitative metrics
        5. Build knowledge graph
        
        Args:
            text: Corrected transcript text
            
        Returns:
            NLPAnalysis with entities, sections, metrics
        """
        ...
```

### Implementation Components

#### 1. spaCy Pipeline Setup

```python
# casestudypilot/nlp/pipeline.py
import spacy
from spacy.language import Language
from spacy.tokens import Doc


class SpaCyPipeline:
    """Initialize and manage spaCy pipeline."""
    
    def __init__(self, model_name: str = "en_core_web_lg"):
        """
        Load spaCy model with custom components.
        
        Model: en_core_web_lg (780MB, high accuracy)
        - Vectors: 685k keys, 300 dimensions
        - NER: 18 entity types
        - Dependency parsing
        - POS tagging
        """
        self.nlp = spacy.load(model_name)
        
        # Add custom CNCF components
        self._add_cncf_entity_ruler()
        self._add_section_classifier()
        self._add_metric_extractor()
    
    def _add_cncf_entity_ruler(self):
        """Add CNCF-specific entity patterns."""
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        
        patterns = [
            # CNCF Projects
            {"label": "PROJECT", "pattern": "Kubernetes"},
            {"label": "PROJECT", "pattern": "Prometheus"},
            {"label": "PROJECT", "pattern": "Argo CD"},
            {"label": "PROJECT", "pattern": "Helm"},
            {"label": "PROJECT", "pattern": "Istio"},
            {"label": "PROJECT", "pattern": "Envoy"},
            {"label": "PROJECT", "pattern": "Linkerd"},
            {"label": "PROJECT", "pattern": "Cilium"},
            {"label": "PROJECT", "pattern": "Flux"},
            {"label": "PROJECT", "pattern": "etcd"},
            {"label": "PROJECT", "pattern": "containerd"},
            
            # Technologies
            {"label": "TECHNOLOGY", "pattern": "GitOps"},
            {"label": "TECHNOLOGY", "pattern": "microservices"},
            {"label": "TECHNOLOGY", "pattern": "containers"},
            {"label": "TECHNOLOGY", "pattern": "service mesh"},
            
            # Metrics patterns
            {"label": "METRIC", "pattern": [{"LIKE_NUM": True}, {"LOWER": "percent"}]},
            {"label": "METRIC", "pattern": [{"LIKE_NUM": True}, {"LOWER": "%"}]},
            {"label": "METRIC", "pattern": [{"LIKE_NUM": True}, {"LOWER": "x"}]},  # "10x faster"
        ]
        
        ruler.add_patterns(patterns)
    
    def _add_section_classifier(self):
        """Add custom section classification component."""
        @Language.component("section_classifier")
        def section_classifier_component(doc: Doc) -> Doc:
            """Classify sentences into case study sections."""
            # Add custom attributes
            Doc.set_extension("sections", default=[], force=True)
            return doc
        
        self.nlp.add_pipe("section_classifier", last=True)
    
    def _add_metric_extractor(self):
        """Add metric extraction component."""
        @Language.component("metric_extractor")
        def metric_extractor_component(doc: Doc) -> Doc:
            """Extract quantitative metrics."""
            Doc.set_extension("metrics", default=[], force=True)
            return doc
        
        self.nlp.add_pipe("metric_extractor", last=True)
    
    def process(self, text: str) -> Doc:
        """Process text through pipeline."""
        return self.nlp(text)
```

#### 2. Entity Recognizer

```python
# casestudypilot/nlp/entity_recognizer.py
from typing import List
from spacy.tokens import Doc

from casestudypilot.models.analysis import ExtractedEntity, EntityType


class EntityRecognizer:
    """Extract and classify entities from transcript."""
    
    # CNCF project list (graduated + incubating)
    CNCF_PROJECTS = {
        "kubernetes", "prometheus", "envoy", "helm", "containerd",
        "argo", "argo cd", "flux", "flagger", "fluentd",
        "istio", "linkerd", "cilium", "etcd", "vitess",
        "harbor", "jaeger", "thanos", "cortex", "opentelemetry"
    }
    
    def extract(self, doc: Doc) -> List[ExtractedEntity]:
        """
        Extract entities from spaCy Doc.
        
        Entity types:
        - COMPANY: Organizations (ORG tag)
        - PERSON: Speaker names
        - PROJECT: CNCF projects
        - TECHNOLOGY: Cloud-native tech (GitOps, microservices)
        - METRIC: Quantitative measurements
        """
        entities = []
        
        for ent in doc.ents:
            # Classify entity type
            if ent.label_ == "ORG":
                entity_type = EntityType.COMPANY
            elif ent.label_ == "PERSON":
                entity_type = EntityType.PERSON
            elif ent.label_ == "PROJECT":
                entity_type = EntityType.PROJECT
            elif ent.label_ == "TECHNOLOGY":
                entity_type = EntityType.TECHNOLOGY
            elif ent.label_ == "METRIC":
                entity_type = EntityType.METRIC
            else:
                continue  # Skip other entity types
            
            # Additional validation for projects
            if entity_type == EntityType.PROJECT:
                if ent.text.lower() not in self.CNCF_PROJECTS:
                    continue  # Not a known CNCF project
            
            entities.append(ExtractedEntity(
                text=ent.text,
                type=entity_type,
                start_char=ent.start_char,
                end_char=ent.end_char,
                confidence=self._calculate_confidence(ent)
            ))
        
        # Deduplicate by (text, type)
        seen = set()
        unique_entities = []
        for entity in entities:
            key = (entity.text.lower(), entity.type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    @staticmethod
    def _calculate_confidence(ent) -> float:
        """
        Calculate entity confidence score.
        
        Factors:
        - Entity label confidence (if available)
        - Entity length (longer = more confident)
        - Entity capitalization pattern
        """
        # spaCy 3.x provides probabilities in ent._.kb_id
        base_confidence = 0.85  # Default for spaCy NER
        
        # Boost for proper nouns (all words capitalized)
        words = ent.text.split()
        if all(w[0].isupper() for w in words if len(w) > 0):
            base_confidence += 0.10
        
        # Boost for multi-word entities (more specific)
        if len(words) > 1:
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
```

#### 3. Section Classifier

```python
# casestudypilot/nlp/section_classifier.py
import re
from typing import List, Tuple
from spacy.tokens import Doc

from casestudypilot.models.analysis import Section, SectionType


class SectionClassifier:
    """
    Classify transcript sentences into case study sections.
    
    Case study structure:
    1. Background (company context, initial state)
    2. Challenge (problems faced)
    3. Solution (CNCF tech adopted, implementation)
    4. Impact (results, metrics, improvements)
    """
    
    # Keyword patterns for each section
    BACKGROUND_KEYWORDS = [
        "company", "organization", "business", "started", "initially",
        "founded", "team", "infrastructure", "legacy", "traditional"
    ]
    
    CHALLENGE_KEYWORDS = [
        "problem", "challenge", "issue", "difficulty", "struggle",
        "bottleneck", "limitation", "inefficient", "manual", "slow",
        "couldn't", "unable", "hard to", "difficult to", "pain point"
    ]
    
    SOLUTION_KEYWORDS = [
        "adopted", "implemented", "deployed", "migrated", "chose",
        "decided", "selected", "using", "kubernetes", "argo", "helm",
        "gitops", "automated", "built", "created", "solution", "approach"
    ]
    
    IMPACT_KEYWORDS = [
        "reduced", "increased", "improved", "faster", "better",
        "achieved", "result", "impact", "benefit", "now we", "today",
        "success", "enabled", "percent", "%", "times", "x faster"
    ]
    
    def classify(self, doc: Doc) -> List[Section]:
        """
        Classify sentences into sections.
        
        Algorithm:
        1. Split into sentences
        2. Score each sentence for each section type
        3. Assign to highest-scoring section
        4. Group consecutive sentences of same type
        """
        sentences = list(doc.sents)
        sections = []
        
        current_section_type = None
        current_section_text = []
        current_section_start = 0
        
        for i, sent in enumerate(sentences):
            # Score sentence for each section type
            scores = self._score_sentence(sent.text)
            
            # Get section with highest score
            section_type = max(scores, key=scores.get)
            
            # If same as current, accumulate
            if section_type == current_section_type:
                current_section_text.append(sent.text)
            else:
                # New section - save previous if exists
                if current_section_type is not None:
                    sections.append(Section(
                        type=current_section_type,
                        content=" ".join(current_section_text),
                        start_char=current_section_start,
                        end_char=sent.start_char,
                        confidence=self._calculate_section_confidence(current_section_text, current_section_type)
                    ))
                
                # Start new section
                current_section_type = section_type
                current_section_text = [sent.text]
                current_section_start = sent.start_char
        
        # Add final section
        if current_section_type is not None:
            sections.append(Section(
                type=current_section_type,
                content=" ".join(current_section_text),
                start_char=current_section_start,
                end_char=doc[-1].idx + len(doc[-1].text),
                confidence=self._calculate_section_confidence(current_section_text, current_section_type)
            ))
        
        return sections
    
    def _score_sentence(self, text: str) -> dict[SectionType, float]:
        """Score sentence for each section type."""
        text_lower = text.lower()
        
        scores = {
            SectionType.BACKGROUND: self._count_keywords(text_lower, self.BACKGROUND_KEYWORDS),
            SectionType.CHALLENGE: self._count_keywords(text_lower, self.CHALLENGE_KEYWORDS),
            SectionType.SOLUTION: self._count_keywords(text_lower, self.SOLUTION_KEYWORDS),
            SectionType.IMPACT: self._count_keywords(text_lower, self.IMPACT_KEYWORDS),
        }
        
        # Boost for quantitative metrics in Impact
        if re.search(r'\d+\s*(?:percent|%|x|times)', text_lower):
            scores[SectionType.IMPACT] += 2.0
        
        # Boost for CNCF project names in Solution
        cncf_projects = ["kubernetes", "argo", "helm", "prometheus", "istio"]
        if any(proj in text_lower for proj in cncf_projects):
            scores[SectionType.SOLUTION] += 1.5
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        else:
            # Default to BACKGROUND if no keywords matched
            scores[SectionType.BACKGROUND] = 1.0
        
        return scores
    
    @staticmethod
    def _count_keywords(text: str, keywords: List[str]) -> float:
        """Count keyword matches with word boundary detection."""
        count = 0.0
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = len(re.findall(pattern, text))
            count += matches
        return count
    
    def _calculate_section_confidence(self, sentences: List[str], section_type: SectionType) -> float:
        """Calculate overall confidence for section classification."""
        # More sentences = higher confidence
        base_confidence = min(0.60 + (len(sentences) * 0.05), 0.95)
        return base_confidence
```

#### 4. Metric Extractor

```python
# casestudypilot/nlp/metric_extractor.py
import re
from typing import List
from spacy.tokens import Doc

from casestudypilot.models.analysis import ExtractedMetric, MetricType


class MetricExtractor:
    """Extract quantitative metrics from transcript."""
    
    # Metric patterns (regex)
    PATTERNS = [
        # Percentage improvements
        (r'(\d+(?:\.\d+)?)\s*(?:percent|%)\s+(?:reduction|decrease|improvement|increase|faster|better)',
         MetricType.PERCENTAGE),
        
        # Multiplication improvements (10x, 5x)
        (r'(\d+)x\s+(?:faster|better|more|improvement)',
         MetricType.MULTIPLIER),
        
        # Time reductions
        (r'from\s+(\d+)\s+(hours?|minutes?|days?|weeks?)\s+to\s+(\d+)\s+(hours?|minutes?|days?|weeks?)',
         MetricType.TIME_REDUCTION),
        
        # Cost savings
        (r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s+(?:saved|reduction|savings?)',
         MetricType.COST_SAVINGS),
        
        # Resource reduction
        (r'reduced\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*(?:percent|%)',
         MetricType.REDUCTION),
    ]
    
    def extract(self, doc: Doc) -> List[ExtractedMetric]:
        """Extract metrics from document."""
        metrics = []
        text = doc.text
        
        for pattern, metric_type in self.PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Extract metric value
                value = match.group(1)
                
                # Get surrounding context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                metrics.append(ExtractedMetric(
                    type=metric_type,
                    value=value,
                    unit=self._extract_unit(match.group(0)),
                    context=context,
                    position=match.start(),
                    confidence=self._calculate_metric_confidence(match.group(0))
                ))
        
        return metrics
    
    @staticmethod
    def _extract_unit(text: str) -> str:
        """Extract unit from metric text."""
        if 'percent' in text.lower() or '%' in text:
            return 'percent'
        elif 'x' in text.lower():
            return 'multiplier'
        elif any(unit in text.lower() for unit in ['hour', 'minute', 'day', 'week']):
            return 'time'
        elif '$' in text:
            return 'currency'
        else:
            return 'count'
    
    @staticmethod
    def _calculate_metric_confidence(text: str) -> float:
        """Calculate confidence in extracted metric."""
        confidence = 0.70  # Base confidence
        
        # Boost for explicit improvement keywords
        improvement_words = ['improved', 'reduced', 'increased', 'faster', 'better']
        if any(word in text.lower() for word in improvement_words):
            confidence += 0.15
        
        # Boost for specific numbers (not rounded)
        if re.search(r'\d+\.\d+', text):
            confidence += 0.10
        
        return min(confidence, 0.95)
```

#### 5. Main NLP Engine Orchestrator

```python
# casestudypilot/nlp/engine.py
from casestudypilot.models.analysis import NLPAnalysis


class NLPEngine:
    """Orchestrate all NLP components."""
    
    def __init__(self):
        self.pipeline = SpaCyPipeline()
        self.entity_recognizer = EntityRecognizer()
        self.section_classifier = SectionClassifier()
        self.metric_extractor = MetricExtractor()
    
    async def analyze(self, text: str) -> NLPAnalysis:
        """Run full NLP analysis."""
        import time
        start_time = time.time()
        
        # Process with spaCy
        doc = self.pipeline.process(text)
        
        # Extract components
        entities = self.entity_recognizer.extract(doc)
        sections = self.section_classifier.classify(doc)
        metrics = self.metric_extractor.extract(doc)
        
        # Build project list
        projects = [
            entity.text
            for entity in entities
            if entity.type == EntityType.PROJECT
        ]
        
        # Build company list
        companies = [
            entity.text
            for entity in entities
            if entity.type == EntityType.COMPANY
        ]
        
        processing_time = (time.time() - start_time) * 1000  # ms
        
        return NLPAnalysis(
            entities=entities,
            sections=sections,
            metrics=metrics,
            projects=projects,
            companies=companies,
            processing_time_ms=processing_time
        )
```

---

## 5. AI Content Generator

**Responsibility:** Generate publication-ready case study content using OpenAI GPT-4 API.

### Interface

```python
# casestudypilot/ai/generator.py
from casestudypilot.models.case_study import GeneratedCaseStudy


class AIContentGenerator:
    """OpenAI GPT-4 powered content generation."""
    
    async def generate(
        self,
        nlp_analysis: NLPAnalysis,
        video_metadata: VideoMetadata,
        corrected_transcript: str
    ) -> GeneratedCaseStudy:
        """
        Generate case study content.
        
        Process:
        1. Build section-specific prompts
        2. Call OpenAI API for each section
        3. Validate generated content
        4. Assemble final case study
        
        Args:
            nlp_analysis: NLP analysis results
            video_metadata: Video metadata
            corrected_transcript: Corrected transcript text
            
        Returns:
            GeneratedCaseStudy with all sections
        """
        ...
```

### Implementation Components

#### 1. OpenAI Client Wrapper

```python
# casestudypilot/ai/client.py
from openai import AsyncOpenAI
from typing import Optional


class OpenAIClient:
    """Async OpenAI API client."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1500
    ) -> str:
        """
        Get completion from OpenAI.
        
        Args:
            prompt: User prompt
            system_prompt: System context
            temperature: Randomness (0.0-1.0)
            max_tokens: Max response length
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise AIGenerationError(f"OpenAI API error: {str(e)}")
```

#### 2. Prompt Builder

```python
# casestudypilot/ai/prompt_builder.py
from typing import List


class PromptBuilder:
    """Build context-aware prompts for case study generation."""
    
    SYSTEM_PROMPT = """You are a technical writer specializing in CNCF case studies.
Your task is to transform conference talk transcripts into professional case studies
following CNCF's editorial guidelines.

Key principles:
- Focus on business outcomes and measurable impact
- Use clear, concise language
- Highlight CNCF project usage
- Include specific metrics when available
- Write in third person
- Maintain professional tone"""
    
    def build_background_prompt(
        self,
        company: str,
        speakers: List[str],
        transcript: str,
        entities: List[ExtractedEntity]
    ) -> str:
        """Build prompt for Background section."""
        context_entities = [
            e.text for e in entities
            if e.type in [EntityType.COMPANY, EntityType.TECHNOLOGY]
        ]
        
        return f"""Based on this conference talk transcript, write a Background section
for a CNCF case study about {company}.

Company: {company}
Speakers: {', '.join(speakers)}
Key Technologies: {', '.join(context_entities[:10])}

Transcript excerpt:
{transcript[:2000]}

The Background section should:
1. Introduce the company (industry, size, mission)
2. Describe their initial infrastructure/tech stack
3. Set context for their cloud-native journey

Write 2-3 paragraphs (150-200 words). Be specific and factual."""
    
    def build_challenge_prompt(
        self,
        company: str,
        challenge_section: Section,
        full_transcript: str
    ) -> str:
        """Build prompt for Challenge section."""
        return f"""Based on this conference talk transcript, write a Challenge section
for a CNCF case study about {company}.

Challenge context from transcript:
{challenge_section.content}

Full transcript reference:
{full_transcript[:3000]}

The Challenge section should:
1. Describe specific technical/business problems
2. Explain why existing solutions weren't working
3. Highlight pain points and bottlenecks
4. Quantify impact where possible

Write 2-3 paragraphs (150-200 words). Focus on concrete problems."""
    
    def build_solution_prompt(
        self,
        company: str,
        projects: List[str],
        solution_section: Section,
        full_transcript: str
    ) -> str:
        """Build prompt for Solution section."""
        return f"""Based on this conference talk transcript, write a Solution section
for a CNCF case study about {company}.

CNCF Projects Used: {', '.join(projects)}

Solution context from transcript:
{solution_section.content}

Full transcript reference:
{full_transcript[:3000]}

The Solution section should:
1. Describe what CNCF technologies they adopted
2. Explain the implementation approach
3. Highlight architectural decisions
4. Mention integration with existing systems

Write 3-4 paragraphs (200-300 words). Be technical but accessible."""
    
    def build_impact_prompt(
        self,
        company: str,
        metrics: List[ExtractedMetric],
        impact_section: Section,
        full_transcript: str
    ) -> str:
        """Build prompt for Impact/Results section."""
        metrics_text = "\n".join([
            f"- {m.value} {m.unit}: {m.context[:100]}"
            for m in metrics
        ])
        
        return f"""Based on this conference talk transcript, write an Impact section
for a CNCF case study about {company}.

Extracted Metrics:
{metrics_text}

Impact context from transcript:
{impact_section.content}

Full transcript reference:
{full_transcript[:3000]}

The Impact section should:
1. Present quantitative improvements (use the metrics above)
2. Describe qualitative benefits
3. Highlight business outcomes
4. Explain ongoing benefits

Write 2-3 paragraphs (150-200 words). Lead with metrics."""
```

#### 3. Section Summarizer

```python
# casestudypilot/ai/summarizer.py


class SectionSummarizer:
    """Generate case study sections using AI."""
    
    def __init__(self, openai_client: OpenAIClient, prompt_builder: PromptBuilder):
        self.client = openai_client
        self.prompt_builder = prompt_builder
    
    async def summarize_background(
        self,
        company: str,
        speakers: List[str],
        transcript: str,
        entities: List[ExtractedEntity]
    ) -> str:
        """Generate Background section."""
        prompt = self.prompt_builder.build_background_prompt(
            company, speakers, transcript, entities
        )
        
        return await self.client.complete(
            prompt=prompt,
            system_prompt=self.prompt_builder.SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=300
        )
    
    async def summarize_challenge(
        self,
        company: str,
        challenge_section: Section,
        full_transcript: str
    ) -> str:
        """Generate Challenge section."""
        prompt = self.prompt_builder.build_challenge_prompt(
            company, challenge_section, full_transcript
        )
        
        return await self.client.complete(
            prompt=prompt,
            system_prompt=self.prompt_builder.SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=300
        )
    
    async def summarize_solution(
        self,
        company: str,
        projects: List[str],
        solution_section: Section,
        full_transcript: str
    ) -> str:
        """Generate Solution section."""
        prompt = self.prompt_builder.build_solution_prompt(
            company, projects, solution_section, full_transcript
        )
        
        return await self.client.complete(
            prompt=prompt,
            system_prompt=self.prompt_builder.SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=500
        )
    
    async def summarize_impact(
        self,
        company: str,
        metrics: List[ExtractedMetric],
        impact_section: Section,
        full_transcript: str
    ) -> str:
        """Generate Impact section."""
        prompt = self.prompt_builder.build_impact_prompt(
            company, metrics, impact_section, full_transcript
        )
        
        return await self.client.complete(
            prompt=prompt,
            system_prompt=self.prompt_builder.SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=300
        )
```

#### 4. Content Validator

```python
# casestudypilot/ai/validator.py
import re
from typing import List, Tuple


class ContentValidator:
    """Validate generated case study content."""
    
    MIN_WORD_COUNT_BACKGROUND = 100
    MIN_WORD_COUNT_CHALLENGE = 100
    MIN_WORD_COUNT_SOLUTION = 150
    MIN_WORD_COUNT_IMPACT = 100
    
    def validate_section(
        self,
        section_type: SectionType,
        content: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate section content.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check word count
        word_count = len(content.split())
        min_words = self._get_min_word_count(section_type)
        
        if word_count < min_words:
            issues.append(f"Word count too low: {word_count} < {min_words}")
        
        # Check for hallucinated metrics (numbers without context)
        if section_type == SectionType.IMPACT:
            if not self._has_valid_metrics(content):
                issues.append("No valid metrics found in Impact section")
        
        # Check for placeholder text
        placeholders = ["[insert", "[company", "[add", "TODO", "TBD"]
        if any(p.lower() in content.lower() for p in placeholders):
            issues.append("Contains placeholder text")
        
        # Check for proper formatting
        if len(content.split('\n\n')) < 2:
            issues.append("Should have multiple paragraphs")
        
        # Check for third person (no "we", "our", "us")
        first_person = re.findall(r'\b(we|our|us|I|my)\b', content, re.IGNORECASE)
        if first_person:
            issues.append(f"Contains first person pronouns: {', '.join(set(first_person))}")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    @staticmethod
    def _get_min_word_count(section_type: SectionType) -> int:
        """Get minimum word count for section type."""
        mapping = {
            SectionType.BACKGROUND: 100,
            SectionType.CHALLENGE: 100,
            SectionType.SOLUTION: 150,
            SectionType.IMPACT: 100
        }
        return mapping.get(section_type, 100)
    
    @staticmethod
    def _has_valid_metrics(content: str) -> bool:
        """Check if content has valid quantitative metrics."""
        # Look for percentage or multiplier patterns
        metric_pattern = r'\d+(?:\.\d+)?\s*(?:percent|%|x|times)'
        matches = re.findall(metric_pattern, content, re.IGNORECASE)
        return len(matches) >= 1  # At least one metric
```

#### 5. Main Generator Orchestrator

```python
# casestudypilot/ai/generator.py


class AIContentGenerator:
    """Orchestrate AI content generation."""
    
    def __init__(self, api_key: str):
        self.client = OpenAIClient(api_key)
        self.prompt_builder = PromptBuilder()
        self.summarizer = SectionSummarizer(self.client, self.prompt_builder)
        self.validator = ContentValidator()
    
    async def generate(
        self,
        nlp_analysis: NLPAnalysis,
        video_metadata: VideoMetadata,
        corrected_transcript: str
    ) -> GeneratedCaseStudy:
        """Generate complete case study."""
        import asyncio
        
        # Find sections by type
        sections_by_type = {s.type: s for s in nlp_analysis.sections}
        
        # Generate all sections in parallel
        background_task = self.summarizer.summarize_background(
            company=video_metadata.company,
            speakers=video_metadata.speakers,
            transcript=corrected_transcript,
            entities=nlp_analysis.entities
        )
        
        challenge_task = self.summarizer.summarize_challenge(
            company=video_metadata.company,
            challenge_section=sections_by_type.get(SectionType.CHALLENGE),
            full_transcript=corrected_transcript
        )
        
        solution_task = self.summarizer.summarize_solution(
            company=video_metadata.company,
            projects=nlp_analysis.projects,
            solution_section=sections_by_type.get(SectionType.SOLUTION),
            full_transcript=corrected_transcript
        )
        
        impact_task = self.summarizer.summarize_impact(
            company=video_metadata.company,
            metrics=nlp_analysis.metrics,
            impact_section=sections_by_type.get(SectionType.IMPACT),
            full_transcript=corrected_transcript
        )
        
        # Await all sections
        background, challenge, solution, impact = await asyncio.gather(
            background_task,
            challenge_task,
            solution_task,
            impact_task
        )
        
        # Validate each section
        validations = {
            "background": self.validator.validate_section(SectionType.BACKGROUND, background),
            "challenge": self.validator.validate_section(SectionType.CHALLENGE, challenge),
            "solution": self.validator.validate_section(SectionType.SOLUTION, solution),
            "impact": self.validator.validate_section(SectionType.IMPACT, impact)
        }
        
        return GeneratedCaseStudy(
            background=background,
            challenge=challenge,
            solution=solution,
            impact=impact,
            validations=validations
        )
```

---

## 6. Case Study Assembler

**Responsibility:** Assemble final case study markdown document following CNCF templates.

### Interface

```python
# casestudypilot/assembler/assembler.py
from casestudypilot.models.case_study import FinalCaseStudy


class CaseStudyAssembler:
    """Assemble final case study document."""
    
    async def assemble(
        self,
        generated_content: GeneratedCaseStudy,
        video_metadata: VideoMetadata,
        nlp_analysis: NLPAnalysis,
        verification_result: VerificationResult
    ) -> FinalCaseStudy:
        """
        Assemble complete case study.
        
        Process:
        1. Load CNCF template
        2. Populate metadata (frontmatter)
        3. Insert generated sections
        4. Add project tags
        5. Calculate quality score
        6. Render final markdown
        
        Returns:
            FinalCaseStudy with markdown content and metadata
        """
        ...
```

### Implementation Components

#### 1. Template Renderer

```python
# casestudypilot/assembler/template_renderer.py
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path


class TemplateRenderer:
    """Render case study using Jinja2 templates."""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render_case_study(
        self,
        company: str,
        projects: List[str],
        background: str,
        challenge: str,
        solution: str,
        impact: str,
        metadata: dict
    ) -> str:
        """
        Render case study from template.
        
        Template variables:
        - company: Company name
        - projects: List of CNCF projects
        - background: Background section content
        - challenge: Challenge section content
        - solution: Solution section content
        - impact: Impact section content
        - date: Publication date
        - speakers: List of speaker names
        - video_url: YouTube URL
        """
        template = self.env.get_template("case_study.md.j2")
        
        return template.render(
            company=company,
            projects=projects,
            background=background,
            challenge=challenge,
            solution=solution,
            impact=impact,
            **metadata
        )
```

**Template file:**

```jinja2
{# casestudypilot/templates/case_study.md.j2 #}
---
title: {{ company }} Case Study
linkTitle: {{ company }}
case_study_styles: true
cid: caseStudies
css: /css/case-studies.css
featured: false
weight: {{ weight }}
quote: >
  {{ quote }}
---

## About {{ company }}

{{ background }}

## Challenge

{{ challenge }}

## Solution

{{ solution }}

## Impact

{{ impact }}

## Projects Used

{% for project in projects %}
- [{{ project }}](https://{{ project|lower }}.io)
{% endfor %}

---

**Video:** [Watch the talk]({{ video_url }})
**Speakers:** {{ speakers|join(', ') }}
**Date:** {{ date }}
```

#### 2. Project Recognizer

```python
# casestudypilot/assembler/project_recognizer.py
from typing import List, Dict


class ProjectRecognizer:
    """Recognize and standardize CNCF project names."""
    
    # CNCF project metadata
    PROJECTS = {
        "kubernetes": {
            "name": "Kubernetes",
            "maturity": "graduated",
            "url": "https://kubernetes.io"
        },
        "prometheus": {
            "name": "Prometheus",
            "maturity": "graduated",
            "url": "https://prometheus.io"
        },
        "argo": {
            "name": "Argo",
            "maturity": "graduated",
            "url": "https://argoproj.github.io"
        },
        "argo cd": {
            "name": "Argo CD",
            "maturity": "graduated",
            "url": "https://argo-cd.readthedocs.io"
        },
        "helm": {
            "name": "Helm",
            "maturity": "graduated",
            "url": "https://helm.sh"
        },
        # ... more projects
    }
    
    def recognize(self, text: str) -> List[Dict[str, str]]:
        """
        Recognize CNCF projects mentioned in text.
        
        Returns:
            List of project metadata dicts
        """
        found_projects = []
        text_lower = text.lower()
        
        for key, metadata in self.PROJECTS.items():
            if key in text_lower:
                if metadata not in found_projects:
                    found_projects.append(metadata)
        
        # Sort by maturity (graduated first)
        found_projects.sort(key=lambda p: (
            p["maturity"] != "graduated",
            p["name"]
        ))
        
        return found_projects
```

#### 3. Style Matcher

```python
# casestudypilot/assembler/style_matcher.py
import re


class StyleMatcher:
    """Match CNCF case study style guidelines."""
    
    def analyze_tone(self, text: str) -> dict:
        """
        Analyze if text matches CNCF tone guidelines.
        
        Guidelines:
        - Third person (no "we", "our")
        - Professional but accessible
        - Focus on outcomes, not features
        - Active voice preferred
        """
        issues = []
        
        # Check for first person
        first_person_matches = re.findall(
            r'\b(we|our|us|I|my)\b',
            text,
            re.IGNORECASE
        )
        if first_person_matches:
            issues.append(f"First person usage: {len(first_person_matches)} instances")
        
        # Check for passive voice (rough heuristic)
        passive_indicators = re.findall(
            r'\b(?:was|were|is|are|been)\s+\w+ed\b',
            text
        )
        passive_ratio = len(passive_indicators) / len(text.split())
        if passive_ratio > 0.15:
            issues.append(f"High passive voice usage: {passive_ratio:.1%}")
        
        # Check for marketing speak
        marketing_terms = ["revolutionary", "game-changing", "best-in-class", "world-class"]
        marketing_matches = [t for t in marketing_terms if t in text.lower()]
        if marketing_matches:
            issues.append(f"Marketing language: {', '.join(marketing_matches)}")
        
        return {
            "is_style_compliant": len(issues) == 0,
            "issues": issues
        }
```

#### 4. Quality Validator

```python
# casestudypilot/assembler/quality_validator.py


class QualityValidator:
    """Validate case study quality."""
    
    def calculate_quality_score(
        self,
        generated_content: GeneratedCaseStudy,
        nlp_analysis: NLPAnalysis,
        style_analysis: dict
    ) -> float:
        """
        Calculate overall quality score (0.0 - 1.0).
        
        Factors:
        - Content validation (30%)
        - Metric presence (25%)
        - CNCF project coverage (20%)
        - Style compliance (15%)
        - Length appropriateness (10%)
        """
        scores = {}
        
        # Content validation (30%)
        validation_scores = [
            1.0 if generated_content.validations[section][0] else 0.0
            for section in ["background", "challenge", "solution", "impact"]
        ]
        scores["content_validation"] = sum(validation_scores) / len(validation_scores) * 0.30
        
        # Metric presence (25%)
        metric_count = len(nlp_analysis.metrics)
        metric_score = min(metric_count / 3.0, 1.0)  # Target: 3+ metrics
        scores["metrics"] = metric_score * 0.25
        
        # CNCF project coverage (20%)
        project_count = len(nlp_analysis.projects)
        project_score = min(project_count / 2.0, 1.0)  # Target: 2+ projects
        scores["projects"] = project_score * 0.20
        
        # Style compliance (15%)
        style_score = 1.0 if style_analysis["is_style_compliant"] else 0.60
        scores["style"] = style_score * 0.15
        
        # Length appropriateness (10%)
        total_words = sum([
            len(generated_content.background.split()),
            len(generated_content.challenge.split()),
            len(generated_content.solution.split()),
            len(generated_content.impact.split())
        ])
        # Target: 600-1000 words
        if 600 <= total_words <= 1000:
            length_score = 1.0
        elif 500 <= total_words < 600 or 1000 < total_words <= 1200:
            length_score = 0.80
        else:
            length_score = 0.60
        scores["length"] = length_score * 0.10
        
        overall_score = sum(scores.values())
        
        return overall_score
```

#### 5. Main Assembler Orchestrator

```python
# casestudypilot/assembler/assembler.py
from datetime import datetime


class CaseStudyAssembler:
    """Orchestrate case study assembly."""
    
    def __init__(self, template_dir: Path):
        self.renderer = TemplateRenderer(template_dir)
        self.project_recognizer = ProjectRecognizer()
        self.style_matcher = StyleMatcher()
        self.quality_validator = QualityValidator()
    
    async def assemble(
        self,
        generated_content: GeneratedCaseStudy,
        video_metadata: VideoMetadata,
        nlp_analysis: NLPAnalysis,
        verification_result: VerificationResult
    ) -> FinalCaseStudy:
        """Assemble complete case study."""
        
        # Recognize projects
        all_text = " ".join([
            generated_content.background,
            generated_content.solution
        ])
        projects = self.project_recognizer.recognize(all_text)
        
        # Analyze style
        full_content = " ".join([
            generated_content.background,
            generated_content.challenge,
            generated_content.solution,
            generated_content.impact
        ])
        style_analysis = self.style_matcher.analyze_tone(full_content)
        
        # Calculate quality score
        quality_score = self.quality_validator.calculate_quality_score(
            generated_content,
            nlp_analysis,
            style_analysis
        )
        
        # Prepare metadata
        metadata = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "speakers": video_metadata.speakers,
            "video_url": video_metadata.url,
            "weight": 50,  # Default weight
            "quote": self._extract_quote(generated_content.impact)
        }
        
        # Render final markdown
        markdown_content = self.renderer.render_case_study(
            company=video_metadata.company,
            projects=[p["name"] for p in projects],
            background=generated_content.background,
            challenge=generated_content.challenge,
            solution=generated_content.solution,
            impact=generated_content.impact,
            metadata=metadata
        )
        
        # Generate filename
        company_slug = video_metadata.company.lower().replace(" ", "-")
        filename = f"{company_slug}-case-study.md"
        
        return FinalCaseStudy(
            markdown_content=markdown_content,
            filename=filename,
            company=video_metadata.company,
            projects=[p["name"] for p in projects],
            quality_score=quality_score,
            metadata=metadata,
            style_analysis=style_analysis
        )
    
    @staticmethod
    def _extract_quote(impact_text: str) -> str:
        """Extract a compelling quote from Impact section."""
        # Take first sentence with a metric
        sentences = impact_text.split('.')
        for sentence in sentences:
            if re.search(r'\d+\s*(?:percent|%|x|times)', sentence):
                return sentence.strip() + '.'
        
        # Fallback: first sentence
        return sentences[0].strip() + '.' if sentences else ""
```

---

## 7. GitHub Integration

**Responsibility:** Parse GitHub issues, create branches, commit files, and create pull requests.

### Interface

```python
# casestudypilot/github/integration.py
from casestudypilot.models.github import PullRequestResult


class GitHubIntegration:
    """GitHub operations for case study workflow."""
    
    async def process_issue(self, issue_number: int) -> PullRequestResult:
        """
        Process GitHub issue end-to-end.
        
        Workflow:
        1. Parse issue to extract YouTube URL
        2. Run full pipeline
        3. Create branch
        4. Commit case study file
        5. Create pull request
        6. Add labels and reviewers
        
        Args:
            issue_number: GitHub issue number
            
        Returns:
            PullRequestResult with URL and metadata
        """
        ...
```

### Implementation Components

#### 1. Issue Parser

```python
# casestudypilot/github/issue_parser.py
import re
from typing import Optional

from github import Github
from github.Issue import Issue


class IssueParser:
    """Parse GitHub issues for video URLs."""
    
    YOUTUBE_URL_PATTERN = re.compile(
        r'(?:https?://)?(?:www\.)?'
        r'(?:youtube\.com/watch\?v=|youtu\.be/)'
        r'([a-zA-Z0-9_-]{11})'
    )
    
    def __init__(self, github_token: str, repo_name: str):
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)
    
    def parse_issue(self, issue_number: int) -> tuple[Issue, str]:
        """
        Parse issue and extract YouTube URL.
        
        Returns:
            (Issue object, video_id)
            
        Raises:
            ValueError: If no YouTube URL found
        """
        issue = self.repo.get_issue(issue_number)
        
        # Search issue body for YouTube URL
        match = self.YOUTUBE_URL_PATTERN.search(issue.body)
        
        if not match:
            # Try issue title as fallback
            match = self.YOUTUBE_URL_PATTERN.search(issue.title)
        
        if not match:
            raise ValueError(f"No YouTube URL found in issue #{issue_number}")
        
        video_id = match.group(1)
        
        return issue, video_id
```

#### 2. Git Operations

```python
# casestudypilot/github/git_operations.py
from pathlib import Path
import git


class GitOperations:
    """Git operations using GitPython."""
    
    def __init__(self, repo_path: Path):
        self.repo = git.Repo(repo_path)
    
    def create_branch(self, branch_name: str) -> str:
        """
        Create new branch from main.
        
        Returns:
            Branch name
        """
        # Ensure we're on main and up-to-date
        self.repo.git.checkout("main")
        self.repo.remotes.origin.pull()
        
        # Create new branch
        new_branch = self.repo.create_head(branch_name)
        new_branch.checkout()
        
        return branch_name
    
    def commit_file(
        self,
        file_path: Path,
        content: str,
        commit_message: str
    ) -> str:
        """
        Write file and commit.
        
        Returns:
            Commit SHA
        """
        # Write file
        file_path.write_text(content, encoding="utf-8")
        
        # Stage file
        self.repo.index.add([str(file_path)])
        
        # Commit
        commit = self.repo.index.commit(commit_message)
        
        return commit.hexsha
    
    def push_branch(self, branch_name: str):
        """Push branch to origin."""
        origin = self.repo.remote("origin")
        origin.push(branch_name)
```

#### 3. PR Creator

```python
# casestudypilot/github/pr_creator.py
from github import Github
from typing import List, Optional


class PRCreator:
    """Create pull requests with metadata."""
    
    def __init__(self, github_token: str, repo_name: str):
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)
    
    def create_pr(
        self,
        branch_name: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        reviewers: Optional[List[str]] = None
    ) -> str:
        """
        Create pull request.
        
        Returns:
            PR URL
        """
        # Create PR
        pr = self.repo.create_pull(
            title=title,
            body=body,
            head=branch_name,
            base="main"
        )
        
        # Add labels
        if labels:
            pr.add_to_labels(*labels)
        
        # Request reviewers
        if reviewers:
            pr.create_review_request(reviewers=reviewers)
        
        return pr.html_url
    
    def generate_pr_body(
        self,
        case_study: FinalCaseStudy,
        video_metadata: VideoMetadata,
        issue_number: int,
        quality_score: float
    ) -> str:
        """Generate PR description."""
        return f"""## Case Study: {case_study.company}

**Auto-generated from issue #{issue_number}**

### Video Information
- **Title:** {video_metadata.title}
- **Speakers:** {', '.join(video_metadata.speakers)}
- **URL:** {video_metadata.url}

### Generated Content
- **Company:** {case_study.company}
- **CNCF Projects:** {', '.join(case_study.projects)}
- **Quality Score:** {quality_score:.2f} / 1.0

### Files Changed
- `{case_study.filename}`

### Review Checklist
- [ ] Verify company information is accurate
- [ ] Check CNCF project usage is correct
- [ ] Validate metrics and claims
- [ ] Review tone and style
- [ ] Confirm quotes are accurate

### Metrics Extracted
- **Total:** {len(case_study.metadata.get('metrics', []))} quantitative metrics

---

Closes #{issue_number}
"""
```

#### 4. Main GitHub Integration Orchestrator

```python
# casestudypilot/github/integration.py
from pathlib import Path


class GitHubIntegration:
    """Orchestrate GitHub workflow."""
    
    def __init__(
        self,
        github_token: str,
        repo_name: str,
        repo_path: Path,
        case_study_dir: Path
    ):
        self.issue_parser = IssueParser(github_token, repo_name)
        self.git_ops = GitOperations(repo_path)
        self.pr_creator = PRCreator(github_token, repo_name)
        self.case_study_dir = case_study_dir
    
    async def process_issue(self, issue_number: int) -> PullRequestResult:
        """Process issue end-to-end."""
        # 1. Parse issue
        issue, video_id = self.issue_parser.parse_issue(issue_number)
        
        # 2. Run full pipeline (orchestrated elsewhere)
        # This is a placeholder - actual implementation would call
        # the full pipeline: YouTube → Correction → NLP → AI → Assembly
        # For now, assume we receive these as parameters
        
        # Example call to pipeline (pseudo-code):
        # case_study, video_metadata, quality_score = await pipeline.run(video_id)
        
        # 3. Create branch
        branch_name = f"case-study/{video_id}"
        self.git_ops.create_branch(branch_name)
        
        # 4. Commit file
        file_path = self.case_study_dir / case_study.filename
        commit_message = f"Add case study: {case_study.company}\n\nGenerated from issue #{issue_number}\nVideo: {video_metadata.url}"
        
        commit_sha = self.git_ops.commit_file(
            file_path,
            case_study.markdown_content,
            commit_message
        )
        
        # 5. Push branch
        self.git_ops.push_branch(branch_name)
        
        # 6. Create PR
        pr_title = f"Case Study: {case_study.company}"
        pr_body = self.pr_creator.generate_pr_body(
            case_study,
            video_metadata,
            issue_number,
            quality_score
        )
        
        pr_url = self.pr_creator.create_pr(
            branch_name=branch_name,
            title=pr_title,
            body=pr_body,
            labels=["case-study", "automated"],
            reviewers=["content-team"]  # Configure as needed
        )
        
        # 7. Comment on issue
        issue.create_comment(
            f"✅ Case study generated!\n\n"
            f"Pull request: {pr_url}\n"
            f"Quality score: {quality_score:.2f}/1.0\n\n"
            f"Please review the generated content for accuracy."
        )
        
        return PullRequestResult(
            pr_url=pr_url,
            branch_name=branch_name,
            commit_sha=commit_sha,
            quality_score=quality_score
        )
```

---

## Summary

This milestone defines the detailed specifications for all 7 core components of the CNCF Case Study Automation System:

1. ✅ **YouTube API Client** - Video metadata and transcript extraction
2. ✅ **Transcript Corrector** - Multi-layer correction pipeline (glossary, patterns, context, spell check)
3. ✅ **Company Verifier** - Fuzzy matching against CNCF Landscape
4. ✅ **NLP Engine** - spaCy-powered entity recognition, section classification, metric extraction
5. ✅ **AI Content Generator** - OpenAI GPT-4 for section summarization with validation
6. ✅ **Case Study Assembler** - Template rendering, style matching, quality scoring
7. ✅ **GitHub Integration** - Issue parsing, git operations, PR creation

**Next:** [Milestone 3: Implementation Roadmap & Testing](./2026-02-09-python-design-m3-implementation.md)

---

**Key Design Principles Applied:**

- **Async/await** throughout for I/O operations
- **Pydantic models** for all data structures (from Milestone 1)
- **Type hints** on all functions (Python 3.11+ strict mode)
- **Error handling** with custom exceptions
- **Confidence scoring** for all AI/ML operations
- **Validation** at every pipeline stage
- **Modular design** with clear interfaces
- **Production-ready** with proper logging, metrics, timeouts
