#!/usr/bin/env python3
"""Copy a directory tree, skipping entries that match exclude patterns.

The plugin skill syncs need a filtered recursive copy. That used to be
``rsync -a --exclude=...``, but rsync is an undeclared external dependency: it
is absent from slim container images and minimal distros, where the sync died
with a bare ``rsync: command not found`` (exit 127) *after* it had already
removed the destination tree. This helper does the same filtered copy with the
standard library, so the syncs depend only on the Python that already has to be
present for the description-compaction step.

Pattern semantics match the rsync patterns the syncs actually use: each pattern
is a shell glob matched against an entry's *base name* at any depth, and a
trailing ``/`` restricts the pattern to directories. Matching a directory prunes
the whole subtree.
"""

from __future__ import annotations

import argparse
import fnmatch
import shutil
import sys
from pathlib import Path
from typing import Sequence


def is_excluded(name: str, is_dir: bool, patterns: Sequence[str]) -> bool:
    """Return True when ``name`` matches any pattern (dir-only if it ends in /)."""
    for pattern in patterns:
        if pattern.endswith("/"):
            if not is_dir:
                continue
            pattern = pattern[:-1]
        if fnmatch.fnmatchcase(name, pattern):
            return True
    return False


def copy_tree(src: Path, dest: Path, patterns: Sequence[str]) -> int:
    """Copy ``src``'s contents into ``dest``. Returns the number of files copied."""
    dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    for entry in sorted(src.iterdir(), key=lambda p: p.name):
        # Check symlinks before is_dir() so a symlink to a directory is treated
        # as a link (rsync -a preserves it) rather than recursed into.
        if entry.is_symlink():
            if is_excluded(entry.name, entry.is_dir(), patterns):
                continue
            target = dest / entry.name
            if target.is_symlink() or target.exists():
                target.unlink()
            target.symlink_to(entry.readlink())
            copied += 1
        elif entry.is_dir():
            if is_excluded(entry.name, True, patterns):
                continue
            copied += copy_tree(entry, dest / entry.name, patterns)
        elif entry.is_file():
            if is_excluded(entry.name, False, patterns):
                continue
            shutil.copy2(entry, dest / entry.name)
            copied += 1
    return copied


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", type=Path, help="source directory")
    parser.add_argument("dest", type=Path, help="destination directory (created)")
    parser.add_argument(
        "--exclude",
        action="append",
        # Not `default=[]`: argparse appends into the default list object itself,
        # so a shared default leaks patterns between calls in one process.
        default=None,
        metavar="PATTERN",
        help="glob matched against base names; trailing / means directories only",
    )
    args = parser.parse_args(argv)

    if not args.src.is_dir():
        sys.stderr.write(f"copy_skill_tree: not a directory: {args.src}\n")
        return 1

    copy_tree(args.src, args.dest, args.exclude or [])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
