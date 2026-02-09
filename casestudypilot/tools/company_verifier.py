"""Company verification against CNCF end-user member list."""

import httpx
from typing import Dict, List, Any
from rapidfuzz import fuzz


def fetch_landscape_data() -> Dict[str, Any]:
    """Fetch CNCF landscape data."""
    url = "https://landscape.cncf.io/api/data.json"
    try:
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch CNCF landscape data: {e}")


def extract_enduser_members(landscape_data: Dict) -> List[str]:
    """Extract end-user member companies from landscape data."""
    members = []

    try:
        categories = landscape_data.get("data", {}).get("categories", [])

        for category in categories:
            if category.get("name") == "CNCF Members":
                subcategories = category.get("subcategories", [])
                for subcategory in subcategories:
                    if subcategory.get("name") == "End User":
                        items = subcategory.get("items", [])
                        for item in items:
                            name = item.get("name", "")
                            if name:
                                members.append(name)

        return members
    except Exception as e:
        raise RuntimeError(f"Failed to parse landscape data: {e}")


def normalize_name(name: str) -> str:
    """Normalize company name for comparison."""
    # Remove common suffixes
    suffixes = [
        " Inc.",
        " Inc",
        " LLC",
        " Ltd.",
        " Ltd",
        " Corporation",
        " Corp.",
        " Corp",
    ]
    normalized = name
    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]

    return normalized.strip().lower()


def find_best_match(company_name: str, member_list: List[str]) -> Dict[str, Any]:
    """Find best matching company in member list using fuzzy matching."""
    normalized_query = normalize_name(company_name)

    best_match = None
    best_score = 0
    best_raw_name = None

    for member in member_list:
        normalized_member = normalize_name(member)

        # Try exact match first
        if normalized_query == normalized_member:
            return {
                "matched_name": member,
                "confidence": 1.0,
                "is_member": True,
                "match_method": "exact",
            }

        # Fuzzy match
        score = fuzz.token_sort_ratio(normalized_query, normalized_member) / 100.0
        if score > best_score:
            best_score = score
            best_match = normalized_member
            best_raw_name = member

    # Determine if match is good enough
    is_member = best_score >= 0.70

    return {
        "matched_name": best_raw_name if best_raw_name else company_name,
        "confidence": best_score,
        "is_member": is_member,
        "match_method": "fuzzy" if is_member else "none",
    }


def verify_company(company_name: str) -> Dict[str, Any]:
    """Verify if a company is a CNCF end-user member."""
    landscape_data = fetch_landscape_data()
    members = extract_enduser_members(landscape_data)
    result = find_best_match(company_name, members)
    result["query_name"] = company_name
    return result
