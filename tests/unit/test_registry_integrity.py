#!/usr/bin/env python3
"""
Registry integrity test — prevents ghost tool references.

Collects every tool name *defined* in data/*.json and every tool name
*referenced* in configs, skills, and rules, then asserts that every
reference points to a real tool.

Also verifies that every JSON config ``type`` field maps to a known
Python class in the lazy registry.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent.parent
SRC = REPO / "src" / "tooluniverse"
DATA_DIR = SRC / "data"
SKILLS_DIR = REPO / "skills"
RULES_DIR = REPO / "claude" / "rules"
REGISTRATION_CHAIN_BASELINE = Path(__file__).parent / "registration_chain_baseline.json"

sys.path.insert(0, str(REPO / "src"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_defined_tool_names() -> set[str]:
    """All tool names from ``name`` fields in data/*.json."""
    names: set[str] = set()
    for jf in DATA_DIR.glob("*.json"):
        if jf.name == "api_keys_catalog.json":
            continue
        try:
            data = json.loads(jf.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        items = (
            data if isinstance(data, list) else [data] if isinstance(data, dict) else []
        )
        for item in items:
            if isinstance(item, dict) and "name" in item:
                names.add(item["name"])
    return names


def _load_type_names() -> set[str]:
    """All ``type`` fields from data/*.json (Python class names)."""
    types: set[str] = set()
    for jf in DATA_DIR.glob("*.json"):
        if jf.name == "api_keys_catalog.json":
            continue
        try:
            data = json.loads(jf.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        items = (
            data if isinstance(data, list) else [data] if isinstance(data, dict) else []
        )
        for item in items:
            if isinstance(item, dict) and "type" in item:
                types.add(item["type"])
    return types


def _load_lazy_registry_class_names() -> set[str]:
    """All class names known to the static lazy registry."""
    from tooluniverse._lazy_registry_static import STATIC_LAZY_REGISTRY

    return set(STATIC_LAZY_REGISTRY.keys())


def _load_required_tools_refs() -> dict[str, list[str]]:
    """Collect tool names from ``required_tools`` arrays in data/*.json.

    Returns {source_file: [tool_name, ...]} for traceability.
    """
    refs: dict[str, list[str]] = {}
    for jf in DATA_DIR.glob("*.json"):
        try:
            data = json.loads(jf.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        items = (
            data if isinstance(data, list) else [data] if isinstance(data, dict) else []
        )
        for item in items:
            if not isinstance(item, dict):
                continue
            for name in item.get("required_tools", []):
                if isinstance(name, str):
                    refs.setdefault(str(jf.relative_to(REPO)), []).append(name)
    return refs


# Pattern: backtick-wrapped tool names like `PubMed_search_articles`
# Requires: CamelCase prefix, underscore, then lowercase action — excludes
# ALL_CAPS env vars (TOOLUNIVERSE_*) and ontology IDs (EFO_0000537).
_TOOL_NAME_RE = re.compile(r"`((?:[A-Z][a-z][a-zA-Z0-9]*_)+[a-z][a-z_A-Z0-9]*)`")

# Known false positives: strings that match the regex but aren't tool names
_FALSE_POSITIVES = {
    "ThreadPoolExecutor",
    "CodeAgent",
    "AzureOpenAIModel",
    "SentenceTransformer",
}


def _load_markdown_tool_refs(directory: Path) -> dict[str, list[str]]:
    """Scan .md files for tool-name-like references.

    Returns {source_file: [tool_name, ...]} for traceability.
    """
    refs: dict[str, list[str]] = {}
    if not directory.exists():
        return refs
    for md in directory.rglob("*.md"):
        text = md.read_text(errors="replace")
        for match in _TOOL_NAME_RE.finditer(text):
            name = match.group(1)
            if name not in _FALSE_POSITIVES:
                refs.setdefault(str(md.relative_to(REPO)), []).append(name)
    return refs


# ---------------------------------------------------------------------------
# Registration-chain drift (links 5 and 6): generated module + tools/__init__.py
# import, against a reviewed, checked-in baseline of pre-existing drift.
# ---------------------------------------------------------------------------


def _load_defined_tool_names_recursive() -> set[str]:
    """All tool names from ``name`` fields in ``data/**/*.json`` (recursive).

    Unlike ``_load_defined_tool_names``'s non-recursive top-level glob, this
    sees ``data/broken_apis/``, ``data/packages/``, ``data/remote_tools/``,
    and any other nested category subdirectory -- the same recursive
    universe ``scripts/audit_registration_chain.py``'s Tier 2 audits, which
    is what ``registration_chain_baseline.json`` was generated from. The
    drift tests below must walk that same universe, or a genuinely-still-
    drifting recursive-only name would misreport as a stale baseline entry.
    """
    names: set[str] = set()
    for jf in DATA_DIR.glob("**/*.json"):
        if jf.name == "api_keys_catalog.json":
            continue
        try:
            data = json.loads(jf.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        items = (
            data if isinstance(data, list) else [data] if isinstance(data, dict) else []
        )
        for item in items:
            if isinstance(item, dict) and "name" in item:
                names.add(item["name"])
    return names


def _load_committed_tools_module_names() -> set[str]:
    """Module-file stems under the *committed* ``src/tooluniverse/tools/``.

    Read via ``git ls-tree HEAD``, never the working tree: this checkout
    carries thousands of uncommitted generated modules from a concurrent
    session's regeneration, so reading the working tree would encode that
    stale state into the gate.
    """
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD", "src/tooluniverse/tools/"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    names: set[str] = set()
    for line in result.stdout.splitlines():
        if line.endswith(".py") and not line.endswith("__init__.py"):
            names.add(Path(line).stem)
    return names


def _load_committed_tools_init_imports() -> set[str]:
    """Import names in the *committed* ``src/tooluniverse/tools/__init__.py``.

    Read via ``git show HEAD:...``, never the working tree, for the same
    reason as ``_load_committed_tools_module_names`` above.
    """
    result = subprocess.run(
        ["git", "show", "HEAD:src/tooluniverse/tools/__init__.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    return set(re.findall(r"^from \.(\w+) import \1\s*$", result.stdout, re.MULTILINE))


def _load_registration_chain_baseline_names() -> set[str]:
    """The reviewed, checked-in set of names already known to be drifting."""
    data = json.loads(REGISTRATION_CHAIN_BASELINE.read_text())
    return set(data["names"])


def _load_currently_drifting_names() -> set[str]:
    """Names (recursive, non-colon) missing a committed module and/or a
    committed ``tools/__init__.py`` import -- mirrors
    ``scripts/audit_registration_chain.py``'s ``check_link_generated_module``
    over the same recursive universe the baseline was built from.
    """
    defined = _load_defined_tool_names_recursive()
    modules = _load_committed_tools_module_names()
    imports = _load_committed_tools_init_imports()
    return {
        name
        for name in defined
        if ":" not in name and not (name in modules and name in imports)
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRegistryIntegrity:
    """Every referenced tool name must exist in the JSON-defined tool set."""

    @pytest.fixture(scope="class")
    def defined_names(self) -> set[str]:
        return _load_defined_tool_names()

    def test_defined_names_is_nonempty(self, defined_names):
        assert len(defined_names) > 100, (
            f"Expected 100+ tools, got {len(defined_names)}"
        )

    def test_required_tools_refs_exist(self, defined_names):
        """Every name in a required_tools array must be a real tool."""
        refs = _load_required_tools_refs()
        missing: list[str] = []
        for source, names in refs.items():
            for name in names:
                if name not in defined_names:
                    missing.append(f"  {name}  (referenced in {source})")
        assert not missing, "Ghost tools in required_tools arrays:\n" + "\n".join(
            sorted(set(missing))
        )

    def test_rules_refs_exist(self, defined_names):
        """Every tool-name-like reference in claude/rules/*.md must be a real tool."""
        refs = _load_markdown_tool_refs(RULES_DIR)
        missing: list[str] = []
        for source, names in refs.items():
            for name in names:
                if name not in defined_names:
                    missing.append(f"  {name}  (referenced in {source})")
        assert not missing, "Ghost tools in claude/rules/:\n" + "\n".join(
            sorted(set(missing))
        )

    def test_json_type_fields_exist_in_lazy_registry(self):
        """Every ``type`` in data/*.json must map to a known Python class."""
        types = _load_type_names()
        registry = _load_lazy_registry_class_names()
        # Also include built-in types that aren't in lazy registry
        # (e.g. BaseRESTTool is a base class used directly in some configs)
        from tooluniverse.tool_registry import _tool_registry

        all_known = registry | set(_tool_registry.keys())
        missing = types - all_known
        # Filter out types that are resolved outside the lazy registry
        # (e.g. base classes used directly, or special plugin types).
        special = {
            "BaseRESTTool",
            "VisualizationTool",
            "ClaudeCodeSkill",
            "SpecialTool",
        }
        missing -= special
        assert not missing, (
            "JSON configs reference unknown Python classes:\n"
            + "\n".join(f"  {t}" for t in sorted(missing))
        )

    def test_generated_module_exists_for_defined_names(self):
        """Every JSON-defined name (excluding the reviewed baseline and
        colon-prefixed catalog entries) has a committed
        ``src/tooluniverse/tools/<Name>.py`` module."""
        baseline = _load_registration_chain_baseline_names()
        defined = _load_defined_tool_names_recursive()
        modules = _load_committed_tools_module_names()
        missing = [
            name
            for name in sorted(defined)
            if ":" not in name and name not in baseline and name not in modules
        ]
        assert not missing, (
            "JSON-defined names missing a committed tools/<Name>.py module "
            "(not covered by the reviewed baseline in "
            "tests/unit/registration_chain_baseline.json):\n"
            + "\n".join(f"  {n}" for n in missing)
        )

    def test_defined_names_imported_in_tools_init(self):
        """Every JSON-defined name (excluding the reviewed baseline and
        colon-prefixed catalog entries) has a matching import line in the
        committed ``tools/__init__.py``."""
        baseline = _load_registration_chain_baseline_names()
        defined = _load_defined_tool_names_recursive()
        imports = _load_committed_tools_init_imports()
        missing = [
            name
            for name in sorted(defined)
            if ":" not in name and name not in baseline and name not in imports
        ]
        assert not missing, (
            "JSON-defined names missing a committed tools/__init__.py import "
            "(not covered by the reviewed baseline in "
            "tests/unit/registration_chain_baseline.json):\n"
            + "\n".join(f"  {n}" for n in missing)
        )

    def test_no_new_registration_chain_drift(self):
        """Drift (missing module or import) beyond the reviewed baseline
        fails loudly rather than silently passing."""
        baseline = _load_registration_chain_baseline_names()
        drifting = _load_currently_drifting_names()
        new_drift = sorted(drifting - baseline)
        assert not new_drift, (
            "New registration-chain drift beyond the reviewed baseline in "
            "tests/unit/registration_chain_baseline.json -- either a "
            "definition was added without regenerating its module, or a "
            "module was removed without removing its definition:\n"
            + "\n".join(f"  {n}" for n in new_drift)
        )

    def test_baseline_has_no_stale_entries(self):
        """A baseline entry that no longer drifts must be pruned, so the
        baseline can only shrink deliberately and never becomes a permanent
        dumping ground."""
        baseline = _load_registration_chain_baseline_names()
        drifting = _load_currently_drifting_names()
        stale = sorted(baseline - drifting)
        assert not stale, (
            "Stale entries in tests/unit/registration_chain_baseline.json -- "
            "these names no longer drift (they now have both a committed "
            "module and a committed tools/__init__.py import) and must be "
            "pruned from the baseline file:\n" + "\n".join(f"  {n}" for n in stale)
        )
