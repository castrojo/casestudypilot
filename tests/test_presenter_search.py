"""Tests for presenter search functionality."""

import pytest
from casestudypilot.tools.presenter_search import (
    normalize_name,
    strict_match,
    fuzzy_match_name,
)


def test_normalize_name():
    """Test name normalization."""
    assert normalize_name("Jeffrey Sica") == "jeffrey sica"
    assert normalize_name("  John Smith  ") == "john smith"
    assert normalize_name("KELSEY HIGHTOWER") == "kelsey hightower"


def test_strict_match_exact():
    """Test exact name match."""
    assert strict_match("Jeffrey Sica", "Jeffrey Sica on Kubernetes")
    assert strict_match("Jeffrey Sica", "kubernetes by jeffrey sica")
    assert strict_match("Kelsey Hightower", "Kelsey Hightower presents")


def test_strict_match_case_insensitive():
    """Test case-insensitive matching."""
    assert strict_match("Jeffrey Sica", "JEFFREY SICA presents")
    assert strict_match("Jeffrey Sica", "jeffrey sica: kubernetes")
    assert strict_match("Kelsey Hightower", "kelsey hightower on cloud native")


def test_strict_match_no_match():
    """Test strict matching rejects non-matches."""
    assert not strict_match("Jeffrey Sica", "Bob Smith presents")
    assert not strict_match("Kelsey Hightower", "John Doe on Kubernetes")


def test_fuzzy_match_similar_name():
    """Test fuzzy matching for similar names."""
    # Jeff vs Jeffrey (common variation)
    match, score = fuzzy_match_name("Jeffrey Sica", "Jeff Sica presents")
    assert match
    assert score > 0.85

    # With middle initial
    match, score = fuzzy_match_name("John Smith", "John A Smith presents")
    assert match
    assert score > 0.85


def test_fuzzy_match_partial():
    """Test fuzzy matching for partial matches."""
    # First name only might not match
    match, score = fuzzy_match_name("Jeffrey Sica", "Jeffrey on Kubernetes")
    # This should not match - only first name present
    assert not match or score < 0.85


def test_fuzzy_match_no_match():
    """Test fuzzy matching rejects dissimilar names."""
    match, score = fuzzy_match_name("Jeffrey Sica", "Bob Smith presents")
    assert not match
    assert score < 0.85

    match, score = fuzzy_match_name("Kelsey Hightower", "John Doe discusses")
    assert not match
    assert score < 0.85


def test_fuzzy_match_exact_returns_high_score():
    """Test that exact matches return confidence 1.0."""
    match, score = fuzzy_match_name("Jeffrey Sica", "Jeffrey Sica presents")
    assert match
    assert score == 1.0


def test_normalize_handles_unicode():
    """Test name normalization with unicode characters."""
    assert normalize_name("José García") == "josé garcía"
    assert normalize_name("François Müller") == "françois müller"


def test_strict_match_with_unicode():
    """Test strict matching with unicode names."""
    assert strict_match("José García", "José García on Cloud Native")
    assert strict_match("François Müller", "françois müller presents")


# Integration tests would require mocking yt-dlp
# Those are omitted here as they would need substantial mocking infrastructure
