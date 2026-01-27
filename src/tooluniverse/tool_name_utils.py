"""
Tool Name Utilities for ToolUniverse

This module provides utilities for automatically shortening tool names to fit
within length constraints (e.g., MCP's 64-character limit with server prefix).

The shortening algorithm intelligently truncates words while maintaining
readability and uniqueness.
"""

from typing import Dict, Set
import logging


logger = logging.getLogger(__name__)


def shorten_tool_name(name: str, max_length: int = 55) -> str:
    """
    Intelligently shorten tool name by truncating words.

    The algorithm splits the tool name by underscores and applies intelligent
    truncation rules to each word while preserving the category prefix and
    maintaining readability.

    Strategy:
    - Split by underscores
    - Keep category (first word) intact
    - Truncate long words to 3-4 chars
    - Keep short words intact (≤3 chars)

    Args:
        name: Original tool name to shorten
        max_length: Maximum allowed length (default: 55 for mcp__tu__
            prefix)

    Returns:
        Shortened tool name that fits within max_length

    Examples:
        >>> shorten_tool_name(
        ...     "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name"
        ... )
        "FDA_get_info_on_cond_for_doc_cons_by_drug_name"

        >>> shorten_tool_name(
        ...     "euhealthinfo_search_diabetes_mellitus_epidemiology_registry"
        ... )
        "euhealthinfo_sear_diab_mell_epid_regi"

        >>> shorten_tool_name("UniProt_get_function_by_accession")
        "UniProt_get_function_by_accession"  # Already short enough
    """
    if len(name) <= max_length:
        return name

    words = name.split("_")
    if not words:
        return name[:max_length]

    # Keep first word (category) intact
    shortened_words = [words[0]]

    # Apply intelligent truncation to remaining words
    for word in words[1:]:
        if len(word) <= 3:
            # Keep very short words intact (by, get, on, or, for, etc.)
            shortened_words.append(word)
        elif len(word) <= 6:
            # Medium words: keep first 4 chars
            shortened_words.append(word[:4])
        else:
            # Long words: keep first 3-4 chars
            # Use 4 chars for better readability if possible
            shortened_words.append(word[:4])

    result = "_".join(shortened_words)

    # If still too long, apply more aggressive truncation
    if len(result) > max_length:
        shortened_words = [words[0]]  # Keep category
        for word in words[1:]:
            if len(word) <= 3:
                shortened_words.append(word)
            else:
                # More aggressive: only 3 chars
                shortened_words.append(word[:3])
        result = "_".join(shortened_words)

    # Final fallback: hard truncate if still too long
    if len(result) > max_length:
        result = result[:max_length]

    return result


class ToolNameMapper:
    """
    Bidirectional mapping between original and shortened tool names.

    This class manages the mapping of tool names to their shortened versions,
    ensuring uniqueness and providing reverse lookup capability.

    Attributes:
        _original_to_short: Dict mapping original names to shortened names
        _short_to_original: Dict mapping shortened names to original names

    Examples:
        >>> mapper = ToolNameMapper()
        >>> short = mapper.get_shortened(
        ...     "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name"
        ... )
        >>> print(short)
        "FDA_get_info_on_cond_for_doc_cons_by_drug_name"
        >>> original = mapper.get_original(short)
        >>> print(original)
        "FDA_get_info_on_conditions_for_doctor_consultation_by_drug_name"
    """

    def __init__(self):
        """Initialize the mapper with empty dictionaries."""
        self._original_to_short: Dict[str, str] = {}
        self._short_to_original: Dict[str, str] = {}

    def get_shortened(self, original: str, max_length: int = 55) -> str:
        """
        Get or create shortened name for original tool name.

        If the name has been shortened before, returns the cached version.
        Otherwise, computes a new shortened name, handles collisions if
        needed, and caches the result.

        Args:
            original: Original tool name
            max_length: Maximum allowed length for shortened name

        Returns:
            Shortened tool name (cached or newly computed)
        """
        # Return cached version if available
        if original in self._original_to_short:
            return self._original_to_short[original]

        # Compute shortened name
        short = shorten_tool_name(original, max_length)

        # Handle collisions: if shortened name already used, append counter
        if (
            short in self._short_to_original
            and self._short_to_original[short] != original
        ):
            # Truncate to leave room for suffix
            base = short[: max_length - 3] if len(short) >= max_length - 3 else short
            counter = 2

            # Find an unused suffix
            while f"{base}_{counter}" in self._short_to_original:
                counter += 1

            short = f"{base}_{counter}"

        # Cache the mapping
        self._original_to_short[original] = short
        self._short_to_original[short] = original

        return short

    def get_original(self, shortened: str) -> str:
        """
        Resolve shortened name back to original tool name.

        Args:
            shortened: Shortened tool name (or original if not shortened)

        Returns:
            Original tool name, or the input if no mapping exists
        """
        return self._short_to_original.get(shortened, shortened)
