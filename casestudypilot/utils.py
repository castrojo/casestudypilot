"""Utility functions for casestudypilot."""

import re


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug.

    Args:
        text: Input text to slugify

    Returns:
        Lowercase slug with hyphens as separators

    Examples:
        >>> slugify("Supercharge Your Canary Deployments with Step Plugins")
        'supercharge-your-canary-deployments-with-step-plugins'
        >>> slugify("Intuit: How We Do GitOps at Scale!")
        'intuit-how-we-do-gitops-at-scale'
    """
    # Convert to lowercase
    text = text.lower()

    # Remove speaker names pattern (anything after " - " typically contains speakers)
    text = text.split(" - ")[0]

    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r"[^\w\s-]", "", text)

    # Replace spaces and multiple hyphens with single hyphen
    text = re.sub(r"[-\s]+", "-", text)

    # Strip leading/trailing hyphens
    text = text.strip("-")

    return text
