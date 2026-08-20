"""Tests for the filtered directory copy used by the plugin skill syncs."""

import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
COPY_SCRIPT = REPO_ROOT / "scripts" / "copy_skill_tree.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("copy_skill_tree", COPY_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COPY_MODULE = _load_module()

# The exclude set every skill sync passes. Kept here so a change to the copy
# helper's pattern semantics has to keep satisfying the real call sites.
SKILL_EXCLUDES = [
    "test_*.py",
    "*_test.py",
    "evals/",
    "__pycache__/",
    "*.pyc",
    ".pytest_cache/",
    ".coverage",
    ".coverage.*",
    "coverage.xml",
    "htmlcov/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".DS_Store",
]


def _tree(root: Path) -> set:
    """Paths of every file under root, relative to root."""
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


def _write(path: Path, text: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.mark.unit
class TestCopySkillTree:
    def test_copies_nested_content(self, tmp_path):
        """Files at every depth land in the destination with content intact."""
        src = tmp_path / "src"
        _write(src / "SKILL.md", "front matter")
        _write(src / "references" / "deep" / "notes.md", "notes")

        COPY_MODULE.copy_tree(src, tmp_path / "dest", [])

        assert _tree(tmp_path / "dest") == {
            "SKILL.md",
            "references/deep/notes.md",
        }
        assert (tmp_path / "dest" / "SKILL.md").read_text() == "front matter"

    def test_skill_excludes_drop_dev_artifacts(self, tmp_path):
        """The real exclude set drops test files, evals/, and cache artifacts."""
        src = tmp_path / "src"
        _write(src / "SKILL.md")
        _write(src / "helper.py")
        _write(src / "test_tools.py")
        _write(src / "tools_test.py")
        _write(src / "evals" / "case.json")
        _write(src / "references" / "__pycache__" / "mod.cpython-311.pyc")
        _write(src / "references" / "guide.md")
        _write(src / ".DS_Store")
        _write(src / ".coverage")
        _write(src / ".coverage.1")
        _write(src / "coverage.xml")
        _write(src / "htmlcov" / "index.html")

        COPY_MODULE.copy_tree(src, tmp_path / "dest", SKILL_EXCLUDES)

        assert _tree(tmp_path / "dest") == {
            "SKILL.md",
            "helper.py",
            "references/guide.md",
        }

    def test_directory_only_pattern_spares_same_named_file(self, tmp_path):
        """A trailing-slash pattern excludes the directory, not a like-named file."""
        src = tmp_path / "src"
        _write(src / "evals" / "case.json")
        _write(src / "evals.md")

        COPY_MODULE.copy_tree(src, tmp_path / "dest", ["evals/"])

        assert _tree(tmp_path / "dest") == {"evals.md"}

    def test_excluded_directory_prunes_whole_subtree(self, tmp_path):
        """Nothing under an excluded directory is copied, however deep."""
        src = tmp_path / "src"
        _write(src / "evals" / "nested" / "deep" / "case.json")
        _write(src / "keep.md")

        COPY_MODULE.copy_tree(src, tmp_path / "dest", ["evals/"])

        assert _tree(tmp_path / "dest") == {"keep.md"}

    def test_symlink_is_preserved_not_followed(self, tmp_path):
        """Symlinks are recreated as links, matching `rsync -a` behaviour."""
        src = tmp_path / "src"
        _write(src / "real.md", "real")
        (src / "link.md").symlink_to("real.md")

        COPY_MODULE.copy_tree(src, tmp_path / "dest", [])

        link = tmp_path / "dest" / "link.md"
        assert link.is_symlink()
        assert link.readlink().as_posix() == "real.md"

    def test_copy_into_existing_destination_is_idempotent(self, tmp_path):
        """Re-copying over an existing destination overwrites without error."""
        src = tmp_path / "src"
        _write(src / "SKILL.md", "v1")
        dest = tmp_path / "dest"

        COPY_MODULE.copy_tree(src, dest, [])
        _write(src / "SKILL.md", "v2")
        COPY_MODULE.copy_tree(src, dest, [])

        assert (dest / "SKILL.md").read_text() == "v2"

    def test_repeated_main_calls_do_not_accumulate_excludes(self, tmp_path):
        """Excludes from one run must not leak into the next in the same process."""
        src = tmp_path / "src"
        _write(src / "SKILL.md")
        _write(src / "helper.py")

        assert (
            COPY_MODULE.main(
                [str(src), str(tmp_path / "first"), "--exclude", "helper.py"]
            )
            == 0
        )
        assert COPY_MODULE.main([str(src), str(tmp_path / "second")]) == 0

        assert _tree(tmp_path / "first") == {"SKILL.md"}
        assert _tree(tmp_path / "second") == {"SKILL.md", "helper.py"}

    def test_main_reports_missing_source(self, tmp_path, capsys):
        """A missing source directory is a non-zero exit, not a traceback."""
        rc = COPY_MODULE.main([str(tmp_path / "nope"), str(tmp_path / "dest")])

        assert rc == 1
        assert "not a directory" in capsys.readouterr().err


@pytest.mark.unit
class TestIsExcluded:
    @pytest.mark.parametrize(
        "name,is_dir,expected",
        [
            ("test_tools.py", False, True),
            ("tools_test.py", False, True),
            ("mod.pyc", False, True),
            (".coverage", False, True),
            (".coverage.3", False, True),
            ("__pycache__", True, True),
            ("__pycache__", False, False),  # dir-only pattern
            ("SKILL.md", False, False),
            ("references", True, False),
            ("TEST_TOOLS.PY", False, False),  # case-sensitive, like rsync
        ],
    )
    def test_pattern_matching(self, name, is_dir, expected):
        """Patterns match base names, case-sensitively, honouring dir-only slashes."""
        assert COPY_MODULE.is_excluded(name, is_dir, SKILL_EXCLUDES) is expected
