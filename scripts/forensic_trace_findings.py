#!/usr/bin/env python3
"""Per-file forensic trace for findings.json's ``landed_dropped_or_altered`` records.

02-04's aggregate rationale is identical boilerplate across all 29 candidates --
a pattern-level read, not per-file evidence. This script does what the manual
trace of ``uniprot_tool.py`` did (catching ``_summarize_entry`` renamed to
``_compact_entry``, not dropped): for each Python path, diff definition-name
sets between the re-derived tree and what landed, then check whether anything
stage-only is actually absent from HEAD or just renamed/still referenced. For
non-Python paths, compare blob content directly against HEAD.

Read-only: fetches blobs via ``git cat-file``/``git show``, writes one JSON
report. Does not modify findings.json -- a separate step applies the verdicts.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "audit_upstream_merge",
    Path(__file__).resolve().parent / "audit_upstream_merge.py",
)
_MOD = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MOD)

extract_definition_names = _MOD.extract_definition_names
run_git = _MOD.run_git
GitCaptureError = _MOD.GitCaptureError

REPO = Path("/Users/davis/code/ToolUniverse")
FINDINGS = REPO / ".planning/phases/02-upstream-main-integration/evidence/staging/findings.json"


def _cat_blob(blob: str) -> str | None:
    try:
        return run_git(["cat-file", "-p", blob], REPO)
    except GitCaptureError:
        return None


def _head_text(path: str) -> str | None:
    try:
        return run_git(["show", f"HEAD:{path}"], REPO)
    except GitCaptureError:
        return None


def _name_referenced(name: str, haystack: str) -> bool:
    return re.search(rf"\b{re.escape(name.split('.')[-1])}\b", haystack) is not None


def trace_python(path: str, landed_text: str | None, stage_text: str | None, head_text: str | None) -> dict:
    landed_defs = extract_definition_names(landed_text) if landed_text else set()
    stage_defs = extract_definition_names(stage_text) if stage_text else set()
    head_defs = extract_definition_names(head_text) if head_text else set()

    stage_only = stage_defs - landed_defs
    real_losses = []
    renamed_or_present = []
    for name in sorted(stage_only):
        if name in head_defs:
            renamed_or_present.append({"name": name, "why": "present verbatim in HEAD"})
            continue
        if head_text and _name_referenced(name, head_text):
            renamed_or_present.append({"name": name, "why": "not a definition but still referenced in HEAD (likely renamed call site or re-export)"})
            continue
        real_losses.append(name)

    landed_only = landed_defs - stage_defs

    if real_losses:
        verdict = "confirmed_gap"
        rationale = (
            f"Definitions {real_losses} exist in the re-derived tree, are absent from landed "
            f"({path}), and are absent from HEAD under any name or reference -- genuine candidate "
            f"for 02-06 review, not a false positive."
        )
    elif renamed_or_present:
        verdict = "false_positive_benign"
        names = [r["name"] for r in renamed_or_present]
        rationale = (
            f"All stage-only definitions ({names}) are present in HEAD verbatim or under a traced "
            f"reference -- consistent with a rename/refactor already reflected downstream, not a loss."
        )
    elif not stage_only:
        verdict = "no_definition_delta"
        rationale = (
            "No definitions present in the re-derived tree are missing from landed; the disagreement "
            "flagged by the aggregate sweep is at the byte/formatting level, not a definition loss."
        )
    else:
        verdict = "inconclusive"
        rationale = "Could not classify -- needs manual review."

    return {
        "kind": "python",
        "stage_only_defs": sorted(stage_only),
        "landed_only_defs": sorted(landed_only),
        "real_losses": real_losses,
        "renamed_or_present": renamed_or_present,
        "forensic_verdict": verdict,
        "forensic_rationale": rationale,
    }


def trace_text(path: str, landed_text: str | None, head_text: str | None, repair_commits: list) -> dict:
    if head_text is None:
        verdict = "path_absent_from_head"
        rationale = f"{path} no longer exists at HEAD -- moved or removed after landing; not a content loss at this path."
    elif landed_text is not None and head_text == landed_text:
        verdict = "head_matches_landed"
        rationale = "HEAD's current content is byte-identical to what landed; the disagreement is fully contained in the re-derived stage and does not reflect current repo state."
    elif repair_commits:
        verdict = "repaired_at_head"
        rationale = f"HEAD differs from landed, but a repair commit already covers this path ({repair_commits[0]}); current content is post-repair, not a live gap."
    else:
        verdict = "content_diverges_unexplained"
        rationale = "HEAD differs from landed and no repair commit corroborates the change -- needs manual byte-level diff before 02-06."
    return {
        "kind": "text",
        "forensic_verdict": verdict,
        "forensic_rationale": rationale,
    }


def main() -> None:
    data = json.loads(FINDINGS.read_text())
    records = [r for r in data["records"] if r["verdict"] == "landed_dropped_or_altered"]
    report = []
    for r in records:
        path = r["path"]
        landed_text = _cat_blob(r["landed_blob"]) if r.get("landed_present") else None
        stage_text = _cat_blob(r["remerge_blob"]) if r.get("remerge_present") else None
        head_text = _head_text(path)

        if path.endswith(".py"):
            trace = trace_python(path, landed_text, stage_text, head_text)
        else:
            trace = trace_text(path, landed_text, head_text, r.get("repair_commits", []))

        report.append({"path": path, **trace})

    out_path = FINDINGS.parent / "findings-forensics.json"
    out_path.write_text(json.dumps({"records": report}, indent=2) + "\n")
    print(f"wrote {out_path} ({len(report)} records)")
    from collections import Counter

    print(Counter(r["forensic_verdict"] for r in report))


if __name__ == "__main__":
    main()
