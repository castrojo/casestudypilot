"""GitHub client for fetching public profile data."""

import logging
from typing import Dict, Any, Optional, List
import httpx

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


def fetch_github_profile(username: str) -> Dict[str, Any]:
    """Fetch public GitHub profile data.

    Args:
        username: GitHub username

    Returns:
        Profile data dict with user information and organizations

    Raises:
        httpx.HTTPStatusError: If profile not found (404) or API error
        httpx.RequestError: If network error occurs
    """
    try:
        logger.info(f"Fetching GitHub profile for user: {username}")

        # Fetch user profile
        with httpx.Client(timeout=30.0) as client:
            # Get user info
            user_url = f"{GITHUB_API_BASE}/users/{username}"
            user_response = client.get(user_url)
            user_response.raise_for_status()
            user_data = user_response.json()

            # Get organizations
            orgs_url = f"{GITHUB_API_BASE}/users/{username}/orgs"
            orgs_response = client.get(orgs_url)
            orgs_response.raise_for_status()
            orgs_data = orgs_response.json()

        # Extract organization logins
        organizations = [org["login"] for org in orgs_data]

        # Build profile dict
        profile = {
            "username": user_data.get("login"),
            "name": user_data.get("name"),
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "email": user_data.get("email"),
            "blog": user_data.get("blog"),
            "twitter_username": user_data.get("twitter_username"),
            "company": user_data.get("company"),
            "hireable": user_data.get("hireable"),
            "public_repos": user_data.get("public_repos", 0),
            "public_gists": user_data.get("public_gists", 0),
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "created_at": user_data.get("created_at"),
            "updated_at": user_data.get("updated_at"),
            "organizations": organizations,
            "avatar_url": user_data.get("avatar_url"),
            "html_url": user_data.get("html_url"),
        }

        # Build website URL from blog field
        if profile.get("blog"):
            blog = profile["blog"]
            # Ensure it has a protocol
            if not blog.startswith("http://") and not blog.startswith("https://"):
                blog = f"https://{blog}"
            profile["website"] = blog
        else:
            profile["website"] = None

        logger.info(f"Successfully fetched profile for {username}")
        logger.info(f"  Name: {profile.get('name')}")
        logger.info(f"  Organizations: {len(organizations)}")
        logger.info(f"  Followers: {profile.get('followers')}")

        return profile

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.error(f"GitHub user not found: {username}")
            raise ValueError(f"GitHub user '{username}' not found")
        elif e.response.status_code == 403:
            logger.error("GitHub API rate limit exceeded")
            raise ValueError("GitHub API rate limit exceeded. Please try again later.")
        else:
            logger.error(f"GitHub API error: {e.response.status_code}")
            raise
    except httpx.RequestError as e:
        logger.error(f"Network error fetching GitHub profile: {e}")
        raise


def get_profile_completeness(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze profile completeness and return statistics.

    Args:
        profile: Profile data dict from fetch_github_profile

    Returns:
        Completeness analysis with score and missing fields
    """
    required_fields = ["username", "name", "bio"]
    optional_fields = ["location", "website", "company", "organizations"]

    present_required = sum(1 for f in required_fields if profile.get(f))
    present_optional = sum(1 for f in optional_fields if profile.get(f))

    missing_required = [f for f in required_fields if not profile.get(f)]
    missing_optional = [f for f in optional_fields if not profile.get(f)]

    # Calculate completeness score (required fields weighted more)
    required_score = present_required / len(required_fields) * 0.7
    optional_score = present_optional / len(optional_fields) * 0.3
    total_score = required_score + optional_score

    return {
        "score": total_score,
        "required_present": present_required,
        "required_total": len(required_fields),
        "optional_present": present_optional,
        "optional_total": len(optional_fields),
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "is_complete": len(missing_required) == 0,
    }
