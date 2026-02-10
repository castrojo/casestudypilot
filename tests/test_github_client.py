"""Tests for GitHub client functionality."""

import pytest
import httpx
from unittest.mock import Mock, patch

from casestudypilot.tools.github_client import (
    fetch_github_profile,
    get_profile_completeness,
    GITHUB_API_BASE,
)


class TestFetchGitHubProfile:
    """Tests for fetch_github_profile function."""

    @patch("casestudypilot.tools.github_client.httpx.Client")
    def test_fetch_github_profile_success(self, mock_client_class):
        """Test successful profile fetch with complete data."""
        # Mock user data
        user_data = {
            "login": "octocat",
            "name": "The Octocat",
            "bio": "GitHub mascot and software developer",
            "location": "San Francisco, CA",
            "email": "octocat@github.com",
            "blog": "https://github.blog",
            "twitter_username": "github",
            "company": "@github",
            "hireable": True,
            "public_repos": 42,
            "public_gists": 10,
            "followers": 1000,
            "following": 50,
            "created_at": "2011-01-25T18:44:36Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "avatar_url": "https://avatars.githubusercontent.com/u/583231",
            "html_url": "https://github.com/octocat",
        }

        # Mock organizations data
        orgs_data = [
            {"login": "github"},
            {"login": "cncf"},
        ]

        # Setup mock responses
        mock_client = Mock()
        mock_user_response = Mock()
        mock_user_response.json.return_value = user_data
        mock_orgs_response = Mock()
        mock_orgs_response.json.return_value = orgs_data

        mock_client.get.side_effect = [mock_user_response, mock_orgs_response]
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        # Execute
        profile = fetch_github_profile("octocat")

        # Verify
        assert profile["username"] == "octocat"
        assert profile["name"] == "The Octocat"
        assert profile["bio"] == "GitHub mascot and software developer"
        assert profile["location"] == "San Francisco, CA"
        assert profile["email"] == "octocat@github.com"
        assert profile["website"] == "https://github.blog"
        assert profile["twitter_username"] == "github"
        assert profile["company"] == "@github"
        assert profile["hireable"] is True
        assert profile["public_repos"] == 42
        assert profile["followers"] == 1000
        assert profile["organizations"] == ["github", "cncf"]
        assert profile["avatar_url"] == "https://avatars.githubusercontent.com/u/583231"

        # Verify API calls
        assert mock_client.get.call_count == 2
        mock_client.get.assert_any_call(f"{GITHUB_API_BASE}/users/octocat")
        mock_client.get.assert_any_call(f"{GITHUB_API_BASE}/users/octocat/orgs")

    @patch("casestudypilot.tools.github_client.httpx.Client")
    def test_fetch_github_profile_blog_without_protocol(self, mock_client_class):
        """Test that blog URLs without protocol are handled correctly."""
        user_data = {
            "login": "testuser",
            "name": "Test User",
            "blog": "example.com",  # No https://
            "public_repos": 0,
            "public_gists": 0,
            "followers": 0,
            "following": 0,
        }

        mock_client = Mock()
        mock_user_response = Mock()
        mock_user_response.json.return_value = user_data
        mock_orgs_response = Mock()
        mock_orgs_response.json.return_value = []

        mock_client.get.side_effect = [mock_user_response, mock_orgs_response]
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        profile = fetch_github_profile("testuser")

        # Website should have protocol added
        assert profile["website"] == "https://example.com"

    @patch("casestudypilot.tools.github_client.httpx.Client")
    def test_fetch_github_profile_no_blog(self, mock_client_class):
        """Test profile with no blog/website field."""
        user_data = {
            "login": "testuser",
            "name": "Test User",
            "blog": "",  # Empty blog
            "public_repos": 0,
            "public_gists": 0,
            "followers": 0,
            "following": 0,
        }

        mock_client = Mock()
        mock_user_response = Mock()
        mock_user_response.json.return_value = user_data
        mock_orgs_response = Mock()
        mock_orgs_response.json.return_value = []

        mock_client.get.side_effect = [mock_user_response, mock_orgs_response]
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        profile = fetch_github_profile("testuser")

        # Website should be None when blog is empty
        assert profile["website"] is None

    @patch("casestudypilot.tools.github_client.httpx.Client")
    def test_fetch_github_profile_user_not_found(self, mock_client_class):
        """Test 404 error when user does not exist."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        error = httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        mock_client.get.side_effect = error
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        with pytest.raises(ValueError, match="GitHub user 'nonexistent' not found"):
            fetch_github_profile("nonexistent")

    @patch("casestudypilot.tools.github_client.httpx.Client")
    def test_fetch_github_profile_rate_limit_exceeded(self, mock_client_class):
        """Test 403 error when rate limit is exceeded."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 403
        error = httpx.HTTPStatusError("Forbidden", request=Mock(), response=mock_response)
        mock_client.get.side_effect = error
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        with pytest.raises(ValueError, match="GitHub API rate limit exceeded"):
            fetch_github_profile("testuser")

    @patch("casestudypilot.tools.github_client.httpx.Client")
    def test_fetch_github_profile_other_http_error(self, mock_client_class):
        """Test other HTTP errors (500, etc)."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        error = httpx.HTTPStatusError("Server Error", request=Mock(), response=mock_response)
        mock_client.get.side_effect = error
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        with pytest.raises(httpx.HTTPStatusError):
            fetch_github_profile("testuser")

    @patch("casestudypilot.tools.github_client.httpx.Client")
    def test_fetch_github_profile_network_error(self, mock_client_class):
        """Test network error during request."""
        mock_client = Mock()
        error = httpx.RequestError("Connection failed")
        mock_client.get.side_effect = error
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        with pytest.raises(httpx.RequestError):
            fetch_github_profile("testuser")

    @patch("casestudypilot.tools.github_client.httpx.Client")
    def test_fetch_github_profile_no_organizations(self, mock_client_class):
        """Test profile with no organizations."""
        user_data = {
            "login": "testuser",
            "name": "Test User",
            "public_repos": 0,
            "public_gists": 0,
            "followers": 0,
            "following": 0,
        }

        mock_client = Mock()
        mock_user_response = Mock()
        mock_user_response.json.return_value = user_data
        mock_orgs_response = Mock()
        mock_orgs_response.json.return_value = []  # No orgs

        mock_client.get.side_effect = [mock_user_response, mock_orgs_response]
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client

        profile = fetch_github_profile("testuser")

        assert profile["organizations"] == []


class TestGetProfileCompleteness:
    """Tests for get_profile_completeness function."""

    def test_complete_profile_all_fields(self):
        """Test profile with all fields present."""
        profile = {
            "username": "octocat",
            "name": "The Octocat",
            "bio": "GitHub mascot and software developer",
            "location": "San Francisco, CA",
            "website": "https://github.blog",
            "company": "@github",
            "organizations": ["github", "cncf"],
        }

        result = get_profile_completeness(profile)

        assert result["score"] == 1.0
        assert result["required_present"] == 3
        assert result["required_total"] == 3
        assert result["optional_present"] == 4
        assert result["optional_total"] == 4
        assert result["missing_required"] == []
        assert result["missing_optional"] == []
        assert result["is_complete"] is True

    def test_minimal_profile_required_only(self):
        """Test profile with only required fields."""
        profile = {
            "username": "testuser",
            "name": "Test User",
            "bio": "A software developer",
            # No optional fields
        }

        result = get_profile_completeness(profile)

        # Required: 3/3 = 1.0 * 0.7 = 0.7
        # Optional: 0/4 = 0.0 * 0.3 = 0.0
        # Total: 0.7
        assert result["score"] == 0.7
        assert result["required_present"] == 3
        assert result["optional_present"] == 0
        assert result["missing_required"] == []
        assert result["missing_optional"] == ["location", "website", "company", "organizations"]
        assert result["is_complete"] is True

    def test_profile_missing_required_fields(self):
        """Test profile missing required fields."""
        profile = {
            "username": "testuser",
            # Missing name and bio
            "location": "San Francisco",
            "website": "https://example.com",
        }

        result = get_profile_completeness(profile)

        # Required: 1/3 = 0.33 * 0.7 = 0.233
        # Optional: 2/4 = 0.5 * 0.3 = 0.15
        # Total: 0.383
        assert result["score"] == pytest.approx(0.383, rel=0.01)
        assert result["required_present"] == 1
        assert result["missing_required"] == ["name", "bio"]
        assert result["is_complete"] is False

    def test_profile_empty_values_not_counted(self):
        """Test that empty strings and None values are not counted as present."""
        profile = {
            "username": "testuser",
            "name": "",  # Empty
            "bio": None,  # None
            "location": "San Francisco",
            "website": "",  # Empty
            "company": None,  # None
            "organizations": [],  # Empty list
        }

        result = get_profile_completeness(profile)

        # Required: username=1, name=0, bio=0 -> 1/3
        # Optional: location=1, website=0, company=0, organizations=0 -> 1/4
        assert result["required_present"] == 1
        assert result["optional_present"] == 1
        assert result["missing_required"] == ["name", "bio"]
        assert "website" in result["missing_optional"]
        assert "company" in result["missing_optional"]
        assert "organizations" in result["missing_optional"]
        assert result["is_complete"] is False

    def test_profile_with_some_optional_fields(self):
        """Test profile with some optional fields."""
        profile = {
            "username": "testuser",
            "name": "Test User",
            "bio": "A developer interested in cloud native technologies",
            "location": "Remote",
            "company": "CNCF",
            # Missing website and organizations
        }

        result = get_profile_completeness(profile)

        # Required: 3/3 = 1.0 * 0.7 = 0.7
        # Optional: 2/4 = 0.5 * 0.3 = 0.15
        # Total: 0.85
        assert result["score"] == 0.85
        assert result["required_present"] == 3
        assert result["optional_present"] == 2
        assert result["missing_optional"] == ["website", "organizations"]
        assert result["is_complete"] is True

    def test_profile_completeness_score_calculation(self):
        """Test score calculation formula."""
        # Test various combinations
        test_cases = [
            # (required_present, optional_present, expected_score)
            (3, 4, 1.0),  # All fields
            (3, 0, 0.7),  # Required only
            (0, 4, 0.3),  # Optional only (should not happen in practice)
            (2, 2, 0.616),  # 2/3 * 0.7 + 2/4 * 0.3 = 0.466 + 0.15 = 0.616
            (1, 3, 0.458),  # 1/3 * 0.7 + 3/4 * 0.3 = 0.233 + 0.225 = 0.458
        ]

        for req, opt, expected in test_cases:
            profile = {}
            if req >= 1:
                profile["username"] = "test"
            if req >= 2:
                profile["name"] = "Test"
            if req >= 3:
                profile["bio"] = "Bio"
            if opt >= 1:
                profile["location"] = "Location"
            if opt >= 2:
                profile["website"] = "https://example.com"
            if opt >= 3:
                profile["company"] = "Company"
            if opt >= 4:
                profile["organizations"] = ["org"]

            result = get_profile_completeness(profile)
            assert result["score"] == pytest.approx(expected, rel=0.01), f"Failed for req={req}, opt={opt}"
