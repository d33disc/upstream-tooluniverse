#!/usr/bin/env python3
"""Audit the six-link tool registration chain, one name at a time.

Phase 3 (``docs/gsd-codebase-map``) plan 03-01: prove the whole chain on a
single credential-free tracer tool before Wave 2 scales the same functions
across the full catalog (~2,900 names). The six links are: (1) a canonical
JSON definition in ``src/tooluniverse/data/*.json``, (2) an implementing
Python class, (3) live category wiring in ``src/tooluniverse/default_config.py``,
(4) a lazy-registry type entry, (5) a generated ``tools/<Name>.py`` module
plus a ``tools/__init__.py`` import, and (6) a reference somewhere under
``tests/``.

Every link-check and classification function here is pure and importable
without the ``tooluniverse`` package itself -- ``tests/unit/test_audit_registration_chain.py``
exercises them directly. Only ``probe_discovery`` (the CAT-02 discovery
surface, called from ``main``) needs a real ``ToolUniverse`` instance, and
that import is deferred to the point of use.

Git/evidence helpers are reused from ``scripts/capture_sync_baseline.py`` and
the AST definition-extractor from ``scripts/audit_upstream_merge.py``, both
via ``importlib.util`` -- ``scripts/`` has no ``__init__.py``, so a plain
import fails; ``tests/unit/test_sync_baseline_git.py`` uses the same idiom.

This entry point is commonly invoked with the caller's own ambient
``python3`` (see ``03-01-PLAN.md``'s verify command), which may not have
``tooluniverse`` installed at all -- only this repository's own ``.venv``
is guaranteed to. ``main`` re-execs itself once, up front, under
``.venv/bin/python`` when the running interpreter cannot import the
package, mirroring the interpreter-matching idiom in
``scripts/probe_custom_tools.py`` (``_module_matches_interpreter``).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

# ---------------------------------------------------------------------------
# Reused helpers -- loaded via importlib, never reimplemented. Same idiom as
# tests/unit/test_sync_baseline_git.py and scripts/probe_custom_tools.py.
# ---------------------------------------------------------------------------

_CAPTURE_SPEC = importlib.util.spec_from_file_location(
    "capture_sync_baseline",
    Path(__file__).resolve().parent / "capture_sync_baseline.py",
)
_CAPTURE_MODULE = importlib.util.module_from_spec(_CAPTURE_SPEC)
assert _CAPTURE_SPEC and _CAPTURE_SPEC.loader
_CAPTURE_SPEC.loader.exec_module(_CAPTURE_MODULE)

_canonical_json = _CAPTURE_MODULE._canonical_json
_contains_secret = _CAPTURE_MODULE._contains_secret
publish_evidence = _CAPTURE_MODULE.publish_evidence
verify_checksums = _CAPTURE_MODULE.verify_checksums
EvidencePublicationError = _CAPTURE_MODULE.EvidencePublicationError

_AUDIT_MERGE_SPEC = importlib.util.spec_from_file_location(
    "audit_upstream_merge",
    Path(__file__).resolve().parent / "audit_upstream_merge.py",
)
_AUDIT_MERGE_MODULE = importlib.util.module_from_spec(_AUDIT_MERGE_SPEC)
assert _AUDIT_MERGE_SPEC and _AUDIT_MERGE_SPEC.loader
_AUDIT_MERGE_SPEC.loader.exec_module(_AUDIT_MERGE_MODULE)

extract_definition_names = _AUDIT_MERGE_MODULE.extract_definition_names

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[1]
PR161_MERGE_OID = "16af425c053c306a658c96e254b4c4114338dd11"
EXCLUDED_DEFINITION_FILE = "api_keys_catalog.json"

# Phase 2's landed merge (f81448f2) -- Tier 1's hand-resolved-file source.
# Distinct from PR161_MERGE_OID above: that one is SYNC-03's ancestor check
# for the single-tool tracer; this one is Wave 2's Tier 1 scope derivation.
MERGED_OID = "f81448f2047a6f35bd552956a0d9990019a39eb1"
UNION_JSON_DEFAULT_REL = (
    ".planning/phases/02-upstream-main-integration/evidence/"
    "a4d3d95a096a14ce4d147faa20334d24f8db9f9a/union.json"
)

# Base classes resolved outside the lazy registry -- mirrors
# tests/unit/test_registry_integrity.py's ``special`` allowance set exactly.
_SPECIAL_TYPES = frozenset(
    {"BaseRESTTool", "VisualizationTool", "ClaudeCodeSkill", "SpecialTool"}
)

_REEXEC_SENTINEL = "_AUDIT_REGISTRATION_CHAIN_REEXECED"


# ---------------------------------------------------------------------------
# Small shared utilities
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    """Current UTC time, ISO-8601, millisecond precision."""
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _module_matches_interpreter(python_bin: Path) -> bool:
    """Same check ``scripts/probe_custom_tools.py`` uses to compare interpreters."""
    try:
        return Path(python_bin).resolve() == Path(sys.executable).resolve()
    except OSError:
        return False


# ---------------------------------------------------------------------------
# SYNC-03: PR #161 ancestry, re-derived live every run.
# ---------------------------------------------------------------------------


def derive_pr161_ancestry(repo_root: Path | str) -> dict[str, Any]:
    """Re-derive PR #161's ancestry against the live HEAD -- never copy it."""
    repo_root = Path(repo_root)
    head_oid = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", PR161_MERGE_OID, "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    is_ancestor = result.returncode == 0
    return {
        "head_oid": head_oid,
        "pr161_merge_oid": PR161_MERGE_OID,
        "is_ancestor": is_ancestor,
        # Alias mirroring Phase 1's git.json field name -- this plan's own
        # verify command asserts on ``pr161_ancestor`` specifically.
        "pr161_ancestor": is_ancestor,
        "exit_code": result.returncode,
        "derived_at": _now_iso(),
    }


# ---------------------------------------------------------------------------
# D-06: fingerprint the hazardous pre-existing dirty working tree.
# ---------------------------------------------------------------------------


def _parse_porcelain_paths(porcelain_output: str) -> list[str]:
    """Extract the path from each ``git status --porcelain`` line.

    Handles the plain ``XY path`` form and the ``XY old -> new`` rename form
    (keeping the new path); strips a git-quoted path's surrounding quotes.
    """
    paths: list[str] = []
    for line in porcelain_output.splitlines():
        if not line:
            continue
        rest = line[3:]
        if " -> " in rest and line[:1] in ("R", "C"):
            rest = rest.split(" -> ", 1)[1]
        if len(rest) >= 2 and rest[0] == '"' and rest[-1] == '"':
            rest = rest[1:-1]
        paths.append(rest)
    return paths


def _max_mtime(directory: Path) -> tuple[float, str]:
    """Greatest ``st_mtime`` over every file under *directory*, plus its ISO form.

    Derived purely from the filesystem so it is stable across runs at an
    unchanged tree. Never uses ``datetime.now()`` -- that would defeat the
    determinism this field exists to prove.
    """
    epoch = 0.0
    if directory.is_dir():
        for path in directory.rglob("*"):
            if path.is_file():
                mtime = path.stat().st_mtime
                if mtime > epoch:
                    epoch = mtime
    iso = (
        datetime.fromtimestamp(epoch, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
    return epoch, iso


def fingerprint_worktree(repo_root: Path | str) -> dict[str, Any]:
    """Read-only snapshot of the dirty working tree -- never stages or reverts."""
    repo_root = Path(repo_root)
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    paths = sorted(_parse_porcelain_paths(result.stdout))
    digest = hashlib.sha256("\n".join(paths).encode("utf-8")).hexdigest()

    by_prefix: dict[str, int] = {}
    for path in paths:
        parent = str(PurePosixPath(path).parent)
        prefix = "" if parent in ("", ".") else f"{parent}/"
        by_prefix[prefix] = by_prefix.get(prefix, 0) + 1

    epoch, iso = _max_mtime(repo_root / "src" / "tooluniverse" / "tools")

    return {
        "paths": paths,
        "count": len(paths),
        "digest": digest,
        "by_prefix": dict(sorted(by_prefix.items())),
        "max_mtime_src_tools": {"epoch": epoch, "iso": iso},
        "captured_at": _now_iso(),
    }


# ---------------------------------------------------------------------------
# CAT-01: the six registration links, as pure, individually testable functions.
# ---------------------------------------------------------------------------


def load_definitions(
    data_dir: Path | str, recursive: bool
) -> dict[str, list[dict[str, Any]]]:
    """Map tool name -> sorted list of defining JSON entries.

    Each entry carries the resolved absolute ``path``, the JSON ``type``,
    and the sorted ``required_api_keys``. ``recursive`` selects ``*.json``
    (this plan; matches ``test_registry_integrity.py``) versus ``**/*.json``
    (Wave 2, to see ``data/broken_apis/`` too).
    """
    data_dir = Path(data_dir)
    pattern = "**/*.json" if recursive else "*.json"
    result: dict[str, list[dict[str, Any]]] = {}
    for json_path in sorted(data_dir.glob(pattern)):
        if json_path.name == EXCLUDED_DEFINITION_FILE or not json_path.is_file():
            continue
        try:
            raw = json.loads(json_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        if isinstance(raw, dict):
            items: list[Any] = [raw]
        elif isinstance(raw, list):
            items = raw
        else:
            continue
        resolved = json_path.resolve()
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if not isinstance(name, str) or not name:
                continue
            entry = {
                "path": resolved,
                "type": item.get("type"),
                "required_api_keys": sorted(item.get("required_api_keys", []) or []),
            }
            result.setdefault(name, []).append(entry)
    for entries in result.values():
        entries.sort(key=lambda e: str(e["path"]))
    return result


_DICT_START_RE = re.compile(r"^default_tool_files\s*=\s*\{", re.MULTILINE)
_CATEGORY_ENTRY_RE = re.compile(
    r'(?P<hash>#[ \t]*)?["\'](?P<key>[A-Za-z0-9_]+)["\']\s*:\s*os\.path\.join\(\s*'
    r"(?P<args>[^)]*?)\s*\)",
    re.DOTALL,
)
_ARCHIVED_MARKER_RE = re.compile(r"#\s*Archived at:", re.IGNORECASE)


def load_live_categories(
    default_config_path: Path | str,
) -> tuple[dict[str, Path], dict[str, Path]]:
    """Parse ``default_tool_files`` into (live, archived) category -> path maps.

    Accepts both the single-line ``os.path.join(...)`` form and the
    multi-line form spanning three physical lines (the ``uniprot_proteomes``
    and ``open_meteo_airquality`` shape) -- a single-line regex silently
    misses those. A commented-out entry with an "Archived at:" marker within
    five lines above it is archived (intentionally excluded); a commented-out
    entry with no marker is neither live nor archived.
    """
    path = Path(default_config_path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    start_match = _DICT_START_RE.search(text)
    if start_match is None:
        return {}, {}
    start_line = text.count("\n", 0, start_match.start())
    end_line = next(
        (i for i in range(start_line + 1, len(lines)) if lines[i].rstrip() == "}"),
        len(lines) - 1,
    )
    body_lines = lines[start_line : end_line + 1]
    body = "\n".join(body_lines)
    base_dir = path.resolve().parent

    live: dict[str, Path] = {}
    archived: dict[str, Path] = {}
    for match in _CATEGORY_ENTRY_RE.finditer(body):
        key = match.group("key")
        segments = [
            segment.strip().strip("'\"")
            for segment in match.group("args").split(",")[1:]
        ]
        segments = [segment for segment in segments if segment]
        if not segments:
            continue
        resolved = base_dir.joinpath(*segments)

        if match.group("hash"):
            line_no = body.count("\n", 0, match.start())
            window = body_lines[max(0, line_no - 5) : line_no]
            if any(_ARCHIVED_MARKER_RE.search(w) for w in window):
                archived[key] = resolved
            # else: commented without a marker -- neither live nor archived.
        else:
            live[key] = resolved

    return live, archived


def check_link_definition(name: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Link 1: a canonical JSON definition exists for *name*."""
    if not entries:
        return {
            "link": "definition",
            "ok": False,
            "evidence": f"no data/*.json entry defines name {name!r}",
        }
    evidence = "; ".join(str(entry["path"]) for entry in entries)
    return {"link": "definition", "ok": True, "evidence": evidence}


def check_link_implementation(
    name: str,
    tool_type: str | None,
    repo_root: Path | str,
    extract_names_fn: Any = extract_definition_names,
) -> dict[str, Any]:
    """Link 2: the JSON ``type`` resolves to a genuinely defined Python class.

    Primary evidence is AST verification: the lazy registry's module mapping
    names a candidate ``src/tooluniverse/<module>.py``, and *extract_names_fn*
    confirms the class is actually defined there. Falls back to plain
    registry membership (``STATIC_LAZY_REGISTRY`` / ``_tool_registry`` keys),
    exactly as ``test_registry_integrity.py`` checks, when AST verification
    is not possible. Both registry imports are lazy and guarded so this
    function never requires ``tooluniverse`` to be importable to run.
    """
    link = "implementation"
    if not tool_type:
        return {
            "link": link,
            "ok": False,
            "evidence": "no type recorded on the definition",
        }
    if tool_type in _SPECIAL_TYPES:
        return {
            "link": link,
            "ok": True,
            "evidence": f"special-cased base type {tool_type}",
        }

    registry: dict[str, str] = {}
    tool_registry_names: set[str] = set()
    try:
        from tooluniverse._lazy_registry_static import STATIC_LAZY_REGISTRY

        registry = STATIC_LAZY_REGISTRY
    except Exception:
        pass
    try:
        from tooluniverse.tool_registry import _tool_registry

        tool_registry_names = set(_tool_registry.keys())
    except Exception:
        pass

    module_name = registry.get(tool_type)
    if module_name:
        module_path = Path(repo_root) / "src" / "tooluniverse" / f"{module_name}.py"
        if module_path.is_file():
            try:
                source = module_path.read_text(encoding="utf-8")
            except OSError:
                source = ""
            if source and tool_type in extract_names_fn(source):
                return {
                    "link": link,
                    "ok": True,
                    "evidence": (
                        f"class {tool_type} defined in "
                        f"src/tooluniverse/{module_name}.py"
                    ),
                }

    if tool_type in registry or tool_type in tool_registry_names:
        return {
            "link": link,
            "ok": True,
            "evidence": f"type {tool_type} registered (registry membership)",
        }

    return {
        "link": link,
        "ok": False,
        "evidence": f"no defining class found for type {tool_type}",
    }


def check_link_category(
    entries: list[dict[str, Any]],
    live: dict[str, Path],
    archived: dict[str, Path],
) -> dict[str, Any]:
    """Link 3: the defining file's category is live in ``default_config.py``."""
    link = "category"
    defining_paths = {entry["path"] for entry in entries}
    for key, category_path in live.items():
        if category_path in defining_paths:
            return {
                "link": link,
                "ok": True,
                "evidence": f"category '{key}' is live in default_config.py",
                "archived": False,
            }
    for key, category_path in archived.items():
        if category_path in defining_paths:
            return {
                "link": link,
                "ok": False,
                "evidence": f"category '{key}' is archived in default_config.py",
                "archived": True,
            }
    return {
        "link": link,
        "ok": False,
        "evidence": "no matching category entry (live or archived) found",
        "archived": False,
    }


def check_link_lazy_metadata(tool_type: str | None) -> dict[str, Any]:
    """Link 4: the type has a lazy-registry (type -> module) entry."""
    link = "lazy_metadata"
    if not tool_type:
        return {
            "link": link,
            "ok": False,
            "evidence": "no type recorded on the definition",
        }
    if tool_type in _SPECIAL_TYPES:
        return {
            "link": link,
            "ok": True,
            "evidence": (
                f"special-cased base type {tool_type} (no lazy-registry entry expected)"
            ),
        }
    try:
        from tooluniverse._lazy_registry_static import STATIC_LAZY_REGISTRY
    except Exception as exc:
        return {
            "link": link,
            "ok": False,
            "evidence": f"could not import STATIC_LAZY_REGISTRY: {exc}",
        }
    module_name = STATIC_LAZY_REGISTRY.get(tool_type)
    if module_name:
        return {
            "link": link,
            "ok": True,
            "evidence": f"STATIC_LAZY_REGISTRY['{tool_type}'] = '{module_name}'",
        }
    return {
        "link": link,
        "ok": False,
        "evidence": f"type {tool_type} has no STATIC_LAZY_REGISTRY entry",
    }


def _git_show(repo_root: Path, ref: str, path: str) -> str | None:
    """``git show ref:path``, or ``None`` if the path does not exist at *ref*."""
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def check_link_generated_module(name: str, repo_root: Path | str) -> dict[str, Any]:
    """Link 5: a generated module plus its ``tools/__init__.py`` import, at HEAD.

    Reads both from ``git show HEAD:<path>`` rather than the working tree --
    ``src/tooluniverse/tools/`` is dirty with another session's regeneration
    output and must never be trusted or touched (D-06).
    """
    link = "generated_module"
    repo_root = Path(repo_root)
    module_rel = f"src/tooluniverse/tools/{name}.py"
    module_src = _git_show(repo_root, "HEAD", module_rel)
    if module_src is None:
        return {
            "link": link,
            "ok": False,
            "evidence": f"{module_rel} not found at HEAD",
        }

    init_src = _git_show(repo_root, "HEAD", "src/tooluniverse/tools/__init__.py")
    if init_src is None:
        return {
            "link": link,
            "ok": False,
            "evidence": "tools/__init__.py not found at HEAD",
        }

    import_re = re.compile(
        rf"^from \.{re.escape(name)} import {re.escape(name)}\s*$", re.MULTILINE
    )
    match = import_re.search(init_src)
    if not match:
        return {
            "link": link,
            "ok": False,
            "evidence": (
                f"{module_rel} exists at HEAD but no matching import line in "
                "tools/__init__.py"
            ),
        }
    return {
        "link": link,
        "ok": True,
        "evidence": f"{module_rel} at HEAD; tools/__init__.py: {match.group(0).strip()}",
    }


def check_link_tests(name: str, repo_root: Path | str) -> dict[str, Any]:
    """Link 6: *name* is referenced somewhere under ``tests/``."""
    link = "tests"
    tests_dir = Path(repo_root) / "tests"
    if tests_dir.is_dir():
        for path in sorted(tests_dir.rglob("*.py")):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if name not in text:
                continue
            rel = path.relative_to(Path(repo_root)).as_posix()
            for lineno, line in enumerate(text.splitlines(), start=1):
                if name in line:
                    return {
                        "link": link,
                        "ok": True,
                        "evidence": f"{rel}:{lineno}: {line.strip()}",
                    }
    return {
        "link": link,
        "ok": False,
        "evidence": f"no reference to {name} found under tests/",
    }


# ---------------------------------------------------------------------------
# Two-stage verdict, shaped after audit_upstream_merge.py's classify_finding.
# ---------------------------------------------------------------------------


def classify_chain(links: list[dict[str, Any]], gated: list[str]) -> str:
    """Primary link-boolean pass, then an archived/gated recheck.

    Precedence: ``archived`` (the category link says so, regardless of any
    other link) beats ``intact``/``gated``/``broken`` -- an intentionally
    excluded tool is not a chain break. Otherwise: all links ok -> ``intact``;
    not all ok but *gated* (unmet ``required_api_keys``) -> ``gated``, never
    ``broken`` -- a credential gap must never be reported as catalog damage.
    Otherwise -> ``broken``.

    An empty *links* list is rejected as ``broken`` rather than falling
    through to Python's vacuous ``all([]) is True`` -- the same empty-as-
    success trap this repository has a recorded history of, applied to the
    chain verdict rather than a tool response.
    """
    if not links:
        return "broken"
    category_link = next(
        (link for link in links if link.get("link") == "category"), None
    )
    if category_link is not None and category_link.get("archived"):
        return "archived"
    if all(link.get("ok") for link in links):
        return "intact"
    if gated:
        return "gated"
    return "broken"


def audit_names(names: Iterable[str], repo_root: Path | str) -> list[dict[str, Any]]:
    """Map the six link checks over *names*, sorted by tool name then source path."""
    repo_root = Path(repo_root)
    data_dir = repo_root / "src" / "tooluniverse" / "data"
    config_path = repo_root / "src" / "tooluniverse" / "default_config.py"

    definitions = load_definitions(data_dir, recursive=False)
    live, archived = load_live_categories(config_path)

    records: list[dict[str, Any]] = []
    for name in sorted(set(names)):
        entries = definitions.get(name, [])
        tool_type = entries[0]["type"] if entries else None
        required_keys = sorted({key for e in entries for key in e["required_api_keys"]})
        missing_keys = sorted(key for key in required_keys if not os.getenv(key))

        links = [
            check_link_definition(name, entries),
            check_link_implementation(name, tool_type, repo_root),
            check_link_category(entries, live, archived),
            check_link_lazy_metadata(tool_type),
            check_link_generated_module(name, repo_root),
            check_link_tests(name, repo_root),
        ]
        verdict = classify_chain(links, missing_keys)

        source_paths = sorted(
            entry["path"].relative_to(repo_root).as_posix()
            if repo_root in entry["path"].parents
            else str(entry["path"])
            for entry in entries
        )
        records.append(
            {
                "name": name,
                "type": tool_type,
                "source_paths": source_paths,
                "required_keys": required_keys,
                "missing_keys": missing_keys,
                "links": links,
                "verdict": verdict,
            }
        )
    return records


# ---------------------------------------------------------------------------
# 03-02 Wave 2: two-tier full-catalog audit on one joinable verdict field.
#
# Tier 1 scopes to every tool Phase 2's merge actually touched (the hand-
# resolved set plus the both-sides data/*.json set); Tier 2 runs mechanically
# over the whole catalog. Both call audit_names/classify_chain unchanged, so
# they share one verdict schema and join on tool name without re-derivation.
# ---------------------------------------------------------------------------

EXCLUSION_RULE = (
    "names containing ':' are non-Python-module catalog entries (e.g. the "
    "'skill:'-prefixed skill-catalog entries) -- they have no generated "
    "module or implementing class to audit, so both tiers exclude them from "
    "the six-link check rather than silently mis-scoring them as broken. "
    "Counted here, not dropped without a trace."
)


def tier1_scope(repo_root: Path | str, union_json_path: Path | str) -> dict[str, Any]:
    """Derive Tier 1's scope from Phase 2's own recorded artifacts.

    Two independent sources, unioned -- never a list typed into this plan:

    - ``hand_resolved_files``: every path ``git diff-tree --cc <MERGED_OID>
      --name-only`` reports for Phase 2's landed merge, excluding that
      command's own leading commit-OID header line.
    - ``union_files``: the ``files[].path`` array Phase 2's own
      ``union.json`` recorded for the both-sides ``data/*.json`` set (213 at
      planning time).

    Every ``src/tooluniverse/data/**/*.json`` path in either source
    contributes its defined tool names to ``names`` via a *recursive*
    ``load_definitions`` lookup -- confirmed necessary, not merely
    defensive: one measured union.json path
    (``data/packages/machine_learning_tools.json``) is nested one level
    under ``data/``, which a non-recursive glob would silently miss.

    Raises ``RuntimeError`` if either source resolves to zero paths -- a
    silently empty Tier 1 would look green while proving nothing.
    """
    repo_root = Path(repo_root)

    diff_tree = subprocess.run(
        ["git", "diff-tree", "--cc", MERGED_OID, "--name-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [line for line in diff_tree.stdout.splitlines() if line]
    if not lines or lines[0] != MERGED_OID:
        raise RuntimeError(
            "tier1_scope: expected `git diff-tree --cc "
            f"{MERGED_OID} --name-only` to start with its own commit OID; "
            f"got {lines[:1]!r}"
        )
    hand_resolved_files = sorted(lines[1:])
    if not hand_resolved_files:
        raise RuntimeError(
            f"tier1_scope: git diff-tree --cc {MERGED_OID} yielded zero "
            "hand-resolved paths -- Tier 1 would be silently empty"
        )

    union_data = json.loads(Path(union_json_path).read_text(encoding="utf-8"))
    union_files = sorted(
        entry["path"]
        for entry in union_data.get("files", [])
        if isinstance(entry, dict) and entry.get("path")
    )
    if not union_files:
        raise RuntimeError(
            f"tier1_scope: {union_json_path} yielded zero both-sides paths "
            "-- Tier 1 would be silently empty"
        )

    scope_paths = sorted(set(hand_resolved_files) | set(union_files))
    scope_json_paths = {
        (repo_root / p).resolve()
        for p in scope_paths
        if p.startswith("src/tooluniverse/data/") and p.endswith(".json")
    }

    data_dir = repo_root / "src" / "tooluniverse" / "data"
    definitions = load_definitions(data_dir, recursive=True)
    names = sorted(
        name
        for name, entries in definitions.items()
        if any(entry["path"] in scope_json_paths for entry in entries)
    )

    return {
        "hand_resolved_files": hand_resolved_files,
        "union_files": union_files,
        "paths": scope_paths,
        "names": names,
    }


def run_full_audit(repo_root: Path | str, tier: str) -> dict[str, Any]:
    """Run the unchanged six-link audit over one tier's resolved name set.

    ``tier1`` scopes to ``tier1_scope``'s resolved names; ``tier2`` scopes to
    every name ``load_definitions(recursive=True)`` finds catalog-wide. Both
    exclude colon-containing (non-Python-module) names before calling
    ``audit_names``, so every emitted record carries the same six-link
    ``verdict`` schema and the two tiers join on tool name with no
    downstream re-derivation.
    """
    repo_root = Path(repo_root)
    data_dir = repo_root / "src" / "tooluniverse" / "data"

    if tier == "tier1":
        scope = tier1_scope(repo_root, repo_root / UNION_JSON_DEFAULT_REL)
        names = [n for n in scope["names"] if ":" not in n]
        records = audit_names(names, repo_root)
        return {"scope": scope, "records": records}
    if tier == "tier2":
        all_names = load_definitions(data_dir, recursive=True).keys()
        names = [n for n in all_names if ":" not in n]
        records = audit_names(names, repo_root)
        return {"records": records}
    raise ValueError(f"run_full_audit: unknown tier {tier!r}")


def _colon_excluded_count(repo_root: Path) -> int:
    """Catalog-wide count of colon-containing (non-Python-module) names."""
    data_dir = repo_root / "src" / "tooluniverse" / "data"
    return sum(1 for name in load_definitions(data_dir, recursive=True) if ":" in name)


def _verdict_summary(registration_chain: dict[str, Any]) -> dict[str, dict[str, int]]:
    """Per-tier verdict-count rollup: ``intact``/``gated``/``archived``/``broken``."""
    summary: dict[str, dict[str, int]] = {}
    for tier_name in ("tier1", "tier2"):
        tier = registration_chain.get(tier_name)
        if tier is None:
            continue
        counts = {"intact": 0, "gated": 0, "archived": 0, "broken": 0}
        for record in tier["records"]:
            counts[record["verdict"]] += 1
        summary[tier_name] = counts
    return summary


def _collect_secrets(records: Iterable[dict[str, Any]]) -> tuple[str, ...]:
    """Env-var values for any ``required_api_keys`` set across *records*.

    Generalizes the single-tool tracer's own secret collection (``main``'s
    ``set_keys``/``secrets`` pair) to the full catalog, so
    ``publish_evidence``'s credential canary can reject a leaked value
    across every record this run touched, not just one tool's.
    """
    set_keys: set[str] = set()
    for record in records:
        required = record.get("required_keys") or []
        missing = set(record.get("missing_keys") or [])
        set_keys.update(key for key in required if key not in missing)
    return tuple(
        value for value in (os.environ.get(key) for key in sorted(set_keys)) if value
    )


def _load_existing_chain_evidence(out_dir: Path) -> dict[str, Any]:
    """Read back already-published ``chain/`` evidence (JSON files, not
    ``SHA256SUMS``) so a flag-scoped invocation composes with earlier output
    in the same directory instead of clobbering it.

    ``publish_evidence`` requires an empty output directory (it stages then
    atomically renames), so composing across independent ``--tier1``/
    ``--tier2`` and ``--duplicates`` invocations into one ``chain/``
    directory means reading whatever is already published there first and
    re-including it in the next call's evidence dict.
    """
    existing: dict[str, Any] = {}
    if out_dir.is_dir():
        for path in sorted(out_dir.glob("*.json")):
            try:
                existing[path.stem] = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
    return existing


def _run_chain_mode(args: argparse.Namespace, repo_root: Path) -> int:
    """CLI handler for ``--tier1``/``--tier2``.

    Writes into the ``chain/`` evidence directory, composing with whatever
    an earlier invocation already published there (see
    ``_load_existing_chain_evidence``) rather than requiring both flags in
    one run.
    """
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()

    existing = _load_existing_chain_evidence(out_dir)
    new_evidence: dict[str, Any] = {}
    records_for_secrets: list[dict[str, Any]] = []

    if args.tier1 or args.tier2:
        head_oid = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        registration_chain: dict[str, Any] = {"head_oid": head_oid}
        if args.tier1:
            tier1_result = run_full_audit(repo_root, "tier1")
            registration_chain["tier1"] = tier1_result
            records_for_secrets.extend(tier1_result["records"])
        if args.tier2:
            tier2_result = run_full_audit(repo_root, "tier2")
            registration_chain["tier2"] = tier2_result
            records_for_secrets.extend(tier2_result["records"])
        registration_chain["summary"] = _verdict_summary(registration_chain)
        registration_chain["exclusions"] = {
            "count": _colon_excluded_count(repo_root),
            "rule": EXCLUSION_RULE,
        }
        new_evidence["registration_chain"] = registration_chain

    merged = {**existing, **new_evidence}
    if not merged:
        print(
            "error: chain mode requires at least one of --tier1/--tier2/--duplicates",
            file=sys.stderr,
        )
        return 2

    secrets = _collect_secrets(records_for_secrets)

    if out_dir.exists():
        if out_dir == repo_root or repo_root not in out_dir.parents:
            print(
                f"error: refusing to clear --out {out_dir} -- it is not a "
                f"strict subdirectory of the repository root {repo_root}",
                file=sys.stderr,
            )
            return 2
        shutil.rmtree(out_dir)

    published = publish_evidence(merged, out_dir, secrets=secrets)
    verify_checksums(published)

    summary = {"out": str(published), "wrote": sorted(new_evidence.keys())}
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            f"chain evidence -> {published} ({', '.join(sorted(new_evidence.keys()))})"
        )
    return 0


# ---------------------------------------------------------------------------
# CAT-02: discovery surface (grep_tools path + get_tool_info schema).
# ---------------------------------------------------------------------------


def assert_discovery_contract(discovery: dict[str, Any]) -> dict[str, Any]:
    """Pure verdict over an already-gathered discovery result.

    Mirrors ``scripts/probe_custom_tools.py``'s ``assert_probe_contract``
    split: this function only classifies facts ``probe_discovery`` already
    gathered (``grep_found``, ``schema_has_parameters``, ``gated``,
    ``missing_keys``) and never touches ``ToolUniverse`` itself, so it is
    provable by ``tests/unit/test_audit_registration_chain.py`` without
    importing the package. A gated tool always yields ``gated`` regardless
    of the other fields -- the environment cannot masquerade as catalog
    damage. Otherwise, an empty result (``grep_found`` and
    ``schema_has_parameters`` both false) with no gating signal is a
    failure, not a pass -- this repository has a recorded history of an
    empty result masquerading as success past a health gate.
    """
    missing_keys = list(discovery.get("missing_keys") or [])
    if discovery.get("gated"):
        return {
            "verdict": "gated",
            "reason": "required_api_keys unmet",
            "missing_keys": missing_keys,
        }
    if discovery.get("grep_found") and discovery.get("schema_has_parameters"):
        return {
            "verdict": "pass",
            "reason": (
                "grep_tools found the tool and get_tool_info returned a "
                "parameter schema"
            ),
            "missing_keys": [],
        }
    return {
        "verdict": "fail",
        "reason": (
            "empty discovery result (grep_tools/get_tool_info) with no gating signal"
        ),
        "missing_keys": [],
    }


def probe_discovery(tool_name: str, repo_root: Path | str) -> dict[str, Any]:
    """Instantiate ``ToolUniverse`` and probe the discovery surface for one tool.

    Gathers ``grep_found``/``schema_has_parameters``/``gated``/
    ``missing_keys`` from a live ``ToolUniverse`` instance, then defers the
    pass/gated/fail conclusion to ``assert_discovery_contract`` so that
    decision stays pure and independently testable.
    """
    repo_root = Path(repo_root)
    src_path = str(repo_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    from tooluniverse import ToolUniverse

    tu = ToolUniverse()
    try:
        tu.load_tools(include_tools=[tool_name])
        gated_map = getattr(tu, "_excluded_api_key_tools", {}) or {}
        if tool_name in gated_map:
            facts = {
                "tool": tool_name,
                "gated": True,
                "missing_keys": sorted(gated_map[tool_name]),
                "grep_found": False,
                "schema_has_parameters": False,
            }
        else:
            grep_found = bool(
                tu.find_tools_by_pattern(
                    tool_name, search_in="name", case_sensitive=True
                )
            )
            spec = tu.tool_specification(tool_name)
            schema_has_parameters = bool(
                isinstance(spec, dict) and ("parameter" in spec or "parameters" in spec)
            )
            facts = {
                "tool": tool_name,
                "gated": False,
                "missing_keys": [],
                "grep_found": grep_found,
                "schema_has_parameters": schema_has_parameters,
            }
    finally:
        tu.close()

    verdict_info = assert_discovery_contract(facts)
    return {**facts, **verdict_info}


# ---------------------------------------------------------------------------
# Interpreter selection: re-exec under .venv/bin/python when ambient python3
# cannot import tooluniverse. See module docstring.
# ---------------------------------------------------------------------------


def _ensure_capable_interpreter(repo_root: Path) -> None:
    if os.environ.get(_REEXEC_SENTINEL) == "1":
        return  # already re-exec'd once; never loop.
    if importlib.util.find_spec("tooluniverse") is not None:
        return
    venv_python = repo_root / ".venv" / "bin" / "python"
    if not venv_python.is_file() or _module_matches_interpreter(venv_python):
        return
    os.environ[_REEXEC_SENTINEL] = "1"
    os.execv(
        str(venv_python),
        [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]],
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", help="single tool name to audit (tracer mode)")
    parser.add_argument(
        "--tier1",
        action="store_true",
        help="audit every tool Phase 2's merge touched (chain mode)",
    )
    parser.add_argument(
        "--tier2",
        action="store_true",
        help="audit every tool in the catalog, mechanically (chain mode)",
    )
    parser.add_argument("--out", required=True, help="evidence output directory")
    parser.add_argument(
        "--repo", default=None, help="repository root (default: this script's own repo)"
    )
    parser.add_argument(
        "--json", action="store_true", help="print a JSON summary to stdout"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = Path(args.repo).resolve() if args.repo else REPO_ROOT_DEFAULT

    _ensure_capable_interpreter(repo_root)

    if args.tier1 or args.tier2 or getattr(args, "duplicates", False):
        return _run_chain_mode(args, repo_root)

    if not args.tool:
        print("error: --tool is required (single-tool tracer mode)", file=sys.stderr)
        return 2

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()

    # Clear this run's own prior output *before* fingerprinting the tree --
    # otherwise a second run's fingerprint would see the first run's
    # leftover evidence files as new dirty paths, breaking the byte-identical
    # rerun guarantee. Guarded so a mistaken --out (repo root or above) never
    # triggers a wide deletion.
    if out_dir.exists():
        if out_dir == repo_root or repo_root not in out_dir.parents:
            print(
                f"error: refusing to clear --out {out_dir} -- it is not a "
                f"strict subdirectory of the repository root {repo_root}",
                file=sys.stderr,
            )
            return 2
        shutil.rmtree(out_dir)

    # SYNC-03: re-derive PR #161 ancestry live, every run (D-01).
    git_result = derive_pr161_ancestry(repo_root)
    if not git_result["is_ancestor"]:
        print(
            "error: PR #161 (16af425c...) is no longer an ancestor of HEAD -- "
            "halting per D-02; this is a planning-time finding, not something "
            "to work around here.",
            file=sys.stderr,
        )
        return 1

    # D-06: fingerprint the hazardous dirty working tree before other work.
    fingerprint = fingerprint_worktree(repo_root)

    # CAT-01: six-link chain for the single tracer tool.
    records = audit_names([args.tool], repo_root)
    if not records:
        print(
            f"error: tool {args.tool!r} not found in src/tooluniverse/data/*.json",
            file=sys.stderr,
        )
        return 1
    record = records[0]

    # CAT-02: discovery surface.
    discovery = probe_discovery(args.tool, repo_root)

    chain_tracer = {
        "tool": record["name"],
        "type": record["type"],
        "source_paths": record["source_paths"],
        "links": record["links"],
        "verdict": record["verdict"],
        "missing_keys": record["missing_keys"],
        "discovery": discovery,
    }

    set_keys = [k for k in record["required_keys"] if k not in record["missing_keys"]]
    secrets = tuple(v for v in (os.environ.get(k) for k in set_keys) if v)

    evidence = {
        "git": git_result,
        "worktree_fingerprint": fingerprint,
        "chain_tracer": chain_tracer,
    }

    published = publish_evidence(evidence, out_dir, secrets=secrets)
    verify_checksums(published)

    summary = {"tool": args.tool, "verdict": record["verdict"], "out": str(published)}
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"{args.tool}: {record['verdict']} -> {published}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
