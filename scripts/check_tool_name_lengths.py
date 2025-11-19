"""
Utility to validate ToolUniverse tool name lengths.

This script loads tools via ToolUniverse and checks that every tool name
is at most MAX_LEN characters (default: 64). It prints a concise report
and returns a non-zero exit code if any violations are found.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Tuple


def check_tool_name_lengths(max_len: int = 64) -> Tuple[List[str], List[str]]:
    """
    Load all tools via ToolUniverse and check their name lengths.

    Returns a tuple of (valid_names, invalid_names) where invalid_names are
    those exceeding max_len.
    """
    # Import locally to avoid import overhead when used as a library
    from tooluniverse import ToolUniverse

    tool_universe = ToolUniverse()
    # Load all built-in/configured tools
    tool_universe.load_tools()

    # Retrieve only names for efficient scanning
    tool_names = tool_universe.get_available_tools(name_only=True)

    valid: List[str] = []
    invalid: List[str] = []

    for name in tool_names:
        if len(name) <= max_len:
            valid.append(name)
        else:
            invalid.append(name)

    return valid, invalid


def _format_report(valid: List[str], invalid: List[str], max_len: int) -> str:
    lines: List[str] = []
    lines.append(f"Max allowed length: {max_len}")
    lines.append(f"Total tools scanned: {len(valid) + len(invalid)}")
    lines.append(f"Valid (≤{max_len}): {len(valid)}")
    lines.append(f"Invalid (>{max_len}): {len(invalid)}")
    if invalid:
        lines.append("")
        lines.append("Invalid tool names:")
        for name in sorted(invalid):
            lines.append(f"  - {name} ({len(name)} chars)")
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate ToolUniverse tool name lengths",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--max-len",
        type=int,
        default=64,
        help="Maximum allowed tool name length",
    )
    args = parser.parse_args(argv)

    valid, invalid = check_tool_name_lengths(max_len=args.max_len)
    report = _format_report(valid, invalid, args.max_len)
    print(report)

    # Non-zero exit when violations are present (useful in CI)
    return 1 if invalid else 0


if __name__ == "__main__":
    sys.exit(main())


