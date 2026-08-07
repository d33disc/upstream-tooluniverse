"""Unit tests for tool-config hashing in the incremental build optimizer.

Guards machine-independence of ``calculate_tool_hash``: the loader injects
``source_file`` (an absolute path to the defining JSON config) into every
tool config, and absolute paths differ per checkout and per machine. If
such fields leak into the hash, every fresh clone or CI runner sees all
~2,658 tools as "changed", rewrites ``.tool_metadata.json`` wholesale, and
defeats both the incremental build cache and the stub drift gate -- even
though the rendered stub code is byte-identical.
"""

import pytest

from tooluniverse.build_optimizer import calculate_tool_hash

_BASE_CONFIG = {
    "name": "Example_tool",
    "type": "ExampleTool",
    "category": "example",
    "description": "An example tool.",
    "parameter": {
        "type": "object",
        "properties": {"q": {"type": "string", "description": "query"}},
    },
}


@pytest.mark.unit
class TestCalculateToolHash:
    def test_source_file_does_not_affect_hash(self):
        """Identical configs from different checkout paths must hash equal."""
        mac = dict(_BASE_CONFIG, source_file="/Users/dev/repo/src/data/x.json")
        ci = dict(
            _BASE_CONFIG,
            source_file="/home/runner/work/repo/repo/src/data/x.json",
        )
        assert calculate_tool_hash(mac) == calculate_tool_hash(ci)

    def test_source_file_absence_matches_presence(self):
        """A config with no source_file hashes the same as one with it."""
        with_field = dict(_BASE_CONFIG, source_file="/anywhere/x.json")
        assert calculate_tool_hash(_BASE_CONFIG) == calculate_tool_hash(with_field)

    def test_semantic_change_still_changes_hash(self):
        """Real config changes (the thing the cache exists for) must register."""
        changed = dict(_BASE_CONFIG, description="A different description.")
        assert calculate_tool_hash(_BASE_CONFIG) != calculate_tool_hash(changed)

    def test_hash_stable_across_key_order(self):
        """Key insertion order must not affect the hash."""
        reordered = dict(reversed(list(_BASE_CONFIG.items())))
        assert calculate_tool_hash(_BASE_CONFIG) == calculate_tool_hash(reordered)
