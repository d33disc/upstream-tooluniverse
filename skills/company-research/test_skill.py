#!/usr/bin/env python3
"""Test script for company-research skill."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from python_implementation import company_research


def test_moderna() -> None:
    """Test with Moderna -- large public biotech, rich data."""
    output = company_research("Moderna", output_file="/tmp/test_moderna.md")
    assert os.path.exists(output), f"Output file {output} not created"
    with open(output) as f:
        content = f.read()
    assert "Company Brief:" in content
    assert "## What They're Doing NOW" in content
    assert "## Pipeline & Science" in content
    assert "## Foundation" in content
    assert "## Sources" in content
    assert len(content) > 1000, f"Report too short: {len(content)} chars"
    print(f"PASS: Moderna ({len(content)} chars)")


def test_recursion() -> None:
    """Test with Recursion Pharmaceuticals -- smaller public biotech."""
    output = company_research(
        "Recursion Pharmaceuticals", output_file="/tmp/test_recursion.md"
    )
    assert os.path.exists(output), f"Output file {output} not created"
    with open(output) as f:
        content = f.read()
    assert "Company Brief:" in content
    assert "## What They're Doing NOW" in content
    assert "## Pipeline & Science" in content
    assert len(content) > 500, f"Report too short: {len(content)} chars"
    print(f"PASS: Recursion Pharmaceuticals ({len(content)} chars)")


def test_private_company() -> None:
    """Test with a private company -- should handle missing SEC data gracefully."""
    output = company_research("Anthropic", output_file="/tmp/test_anthropic.md")
    assert os.path.exists(output), f"Output file {output} not created"
    with open(output) as f:
        content = f.read()
    assert "Company Brief:" in content
    # Should not crash even without SEC data
    assert len(content) > 300, f"Report too short: {len(content)} chars"
    print(f"PASS: Anthropic/private ({len(content)} chars)")


def test_error_handling() -> None:
    """Test with nonsense input -- should not crash."""
    output = company_research(
        "XYZNONEXISTENT99999", output_file="/tmp/test_nonexistent.md"
    )
    assert os.path.exists(output), f"Output file {output} not created"
    with open(output) as f:
        content = f.read()
    assert "Company Brief:" in content
    print(f"PASS: Error handling ({len(content)} chars)")


def main() -> int:
    tests = [
        ("Moderna (large public)", test_moderna),
        ("Recursion (smaller public)", test_recursion),
        ("Private company", test_private_company),
        ("Error handling", test_error_handling),
    ]

    results: dict[str, str] = {}
    for label, fn in tests:
        try:
            fn()
            results[label] = "PASS"
        except Exception as e:
            print(f"FAIL: {label}: {e}")
            results[label] = f"FAIL: {e!s:.100}"

    print("\n--- Summary ---")
    passed = sum(1 for v in results.values() if v == "PASS")
    for label, result in results.items():
        print(f"  {'PASS' if result == 'PASS' else 'FAIL'}: {label}")
    print(f"\n{passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
