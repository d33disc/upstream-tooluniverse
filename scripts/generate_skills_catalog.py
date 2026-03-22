#!/usr/bin/env python3
"""Generate skills_catalog.json from Claude Code skill SKILL.md files.

Scans skills/*/SKILL.md for YAML frontmatter, extracts name + description,
and writes a JSON config compatible with ToolUniverse's tool_config_files.

Skills appear in find_tools/grep_tools search results but are NOT executable
via execute_tool. They carry a `skill:` prefix and an invocation note.

Usage:
    python scripts/generate_skills_catalog.py
    python scripts/generate_skills_catalog.py --skills-dir /path/to/skills
    python scripts/generate_skills_catalog.py --output /path/to/output.json
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_frontmatter(skill_md: Path) -> dict | None:
    """Extract name and description from YAML frontmatter in SKILL.md."""
    text = skill_md.read_text(encoding="utf-8")

    # Match YAML frontmatter between --- delimiters
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None

    frontmatter = match.group(1)

    # Extract name
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if not name_match:
        return None
    name = name_match.group(1).strip()

    # Extract description (may be multiline with > or |)
    desc_match = re.search(
        r"^description:\s*>?\s*\n?(.*?)(?=\n[a-z]|\Z)",
        frontmatter,
        re.MULTILINE | re.DOTALL,
    )
    if not desc_match:
        # Try single-line description
        desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)

    if not desc_match:
        return None

    description = desc_match.group(1).strip()
    # Clean up multiline descriptions
    description = re.sub(r"\s+", " ", description).strip()

    if not description:
        return None

    return {"name": name, "description": description}


def generate_catalog(skills_dir: Path) -> list[dict]:
    """Scan skills directory and generate tool catalog entries."""
    entries = []

    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        meta = extract_frontmatter(skill_md)
        if not meta:
            print(
                f"  SKIP {skill_md.parent.name}: no valid frontmatter", file=sys.stderr
            )
            continue

        skill_name = meta["name"]
        entry = {
            "type": "ClaudeCodeSkill",
            "name": f"skill:{skill_name}",
            "description": (
                f"{meta['description']} "
                f"[SKILL — not executable via execute_tool. "
                f"Invoke with: Skill(skill='{skill_name}')]"
            ),
            "category": "claude_code_skills",
            "parameter": {
                "type": "object",
                "properties": {},
                "required": [],
            },
            "invocation": f"Skill(skill='{skill_name}')",
        }
        entries.append(entry)
        print(f"  OK   {skill_name}", file=sys.stderr)

    return entries


def main():
    parser = argparse.ArgumentParser(
        description="Generate skills catalog for ToolUniverse"
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "skills",
        help="Path to skills directory (default: ./skills/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "src"
        / "tooluniverse"
        / "data"
        / "skills_catalog.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    if not args.skills_dir.is_dir():
        print(f"Skills directory not found: {args.skills_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning: {args.skills_dir}", file=sys.stderr)
    catalog = generate_catalog(args.skills_dir)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nWrote {len(catalog)} skill entries to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
