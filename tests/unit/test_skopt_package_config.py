"""Regression: get_skopt_info must use the PyPI distribution name, not the import name.

Real bug: the config set ``package_name: "skopt"``, but skopt's PyPI distribution
is ``scikit-optimize`` (``skopt`` is only the import name). PyPI returned 404 and
the tool errored with "No local information available for package 'skopt'". Ours to
fix — wrong metadata in our config. Fix: ``package_name: "scikit-optimize"`` plus
``local_info.import_name: "skopt"`` so usage examples still say ``import skopt``.

Deterministic (no network): asserts the config is correct. Frozen — the fix edits
the data file only, never this test.
"""

import json
from pathlib import Path

_CFG = (
    Path(__file__).resolve().parents[2]
    / "src/tooluniverse/data/packages/machine_learning_tools.json"
)


def _skopt_config():
    tools = json.loads(_CFG.read_text())
    for t in tools:
        if isinstance(t, dict) and t.get("name") == "get_skopt_info":
            return t
    raise AssertionError("get_skopt_info config not found")


def test_skopt_uses_pypi_distribution_name():
    cfg = _skopt_config()
    assert cfg["package_name"] == "scikit-optimize"  # not "skopt" (404 on PyPI)
    assert cfg["local_info"]["import_name"] == "skopt"  # import is still `skopt`
