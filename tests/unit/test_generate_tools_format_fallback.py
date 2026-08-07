"""Unit tests for the stub generator's formatting fallback chain.

Guards a silent-failure mode: ``_format_files`` prefers ``pre-commit`` when it
is on PATH, but a pyenv *shim* can exist on PATH while the underlying tool is
not installed in the active pyenv version. The shim then exits nonzero
("pyenv: pre-commit: command not found"), and because the subprocess runs with
``check=False``, the old code swallowed the failure and returned before ever
reaching the ruff fallback -- leaving every generated stub unformatted and the
working tree permanently dirty against the committed, formatted stubs.
"""

from unittest import mock

import pytest

from tooluniverse.generate_tools import _format_files


def _which_factory(available):
    """Return a shutil.which stand-in that resolves only names in ``available``."""

    def _which(name):
        return f"/fake/bin/{name}" if name in available else None

    return _which


def _completed(returncode):
    return mock.Mock(returncode=returncode)


@pytest.mark.unit
class TestFormatFilesFallback:
    def test_precommit_success_skips_ruff(self):
        """When pre-commit runs cleanly, ruff must not be invoked."""
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd[0])
            return _completed(0)

        with (
            mock.patch(
                "tooluniverse.generate_tools.shutil.which",
                _which_factory({"pre-commit", "ruff"}),
            ),
            mock.patch(
                "tooluniverse.generate_tools.subprocess.run", side_effect=fake_run
            ),
        ):
            _format_files(["a.py"])

        assert calls == ["/fake/bin/pre-commit"]

    def test_precommit_broken_shim_falls_back_to_ruff(self):
        """A pre-commit that exists but exits nonzero must fall through to ruff.

        This is the pyenv-shim failure mode: shutil.which finds the shim, the
        shim exits 127, and formatting must still happen via ruff.
        """
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            if cmd[0].endswith("pre-commit"):
                return _completed(127)
            return _completed(0)

        with (
            mock.patch(
                "tooluniverse.generate_tools.shutil.which",
                _which_factory({"pre-commit", "ruff"}),
            ),
            mock.patch(
                "tooluniverse.generate_tools.subprocess.run", side_effect=fake_run
            ),
        ):
            _format_files(["a.py"])

        ruff_calls = [c for c in calls if c[0].endswith("ruff")]
        assert len(ruff_calls) == 2, (
            f"expected ruff format + ruff check after pre-commit failure, "
            f"got calls: {calls}"
        )
        assert ruff_calls[0][:2] == ["/fake/bin/ruff", "format"]
        assert ruff_calls[1][:2] == ["/fake/bin/ruff", "check"]

    def test_no_precommit_uses_ruff(self):
        """Without pre-commit on PATH, the ruff fallback runs (format + check)."""
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return _completed(0)

        with (
            mock.patch(
                "tooluniverse.generate_tools.shutil.which",
                _which_factory({"ruff"}),
            ),
            mock.patch(
                "tooluniverse.generate_tools.subprocess.run", side_effect=fake_run
            ),
        ):
            _format_files(["a.py"])

        assert [c[:2] for c in calls] == [
            ["/fake/bin/ruff", "format"],
            ["/fake/bin/ruff", "check"],
        ]

    def test_skip_env_var_short_circuits(self, monkeypatch):
        """TOOLUNIVERSE_SKIP_FORMAT=1 disables formatting entirely."""
        monkeypatch.setenv("TOOLUNIVERSE_SKIP_FORMAT", "1")
        with mock.patch(
            "tooluniverse.generate_tools.subprocess.run"
        ) as fake_run:
            _format_files(["a.py"])
        fake_run.assert_not_called()
