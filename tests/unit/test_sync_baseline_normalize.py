import json
import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location("capture_sync_baseline", Path(__file__).parents[2] / "scripts/capture_sync_baseline.py")
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader
_SPEC.loader.exec_module(_MODULE)

BaselineValidationError = _MODULE.BaselineValidationError
EvidencePublicationError = _MODULE.EvidencePublicationError
RetryExhaustedError = _MODULE.RetryExhaustedError
build_provider_manifest = _MODULE.build_provider_manifest
classify_retryable = _MODULE.classify_retryable
normalize_probe_result = _MODULE.normalize_probe_result
publish_evidence = _MODULE.publish_evidence
run_with_retry = _MODULE.run_with_retry
select_catalog_sample = _MODULE.select_catalog_sample
validate_probe_invariants = _MODULE.validate_probe_invariants


def test_normalize_replaces_only_allowlisted_paths_and_sorts_maps():
    raw = {"b": 2, "a": {"created": "old", "id": "keep"}, "items": ["second", "first"]}
    got = normalize_probe_result(raw, ["$.a.created"])
    assert got == {"a": {"created": "<volatile>", "id": "keep"}, "b": 2, "items": ["second", "first"]}


def test_unordered_arrays_sort_by_identity_but_ordered_arrays_do_not():
    raw = {"ordered": [{"id": "b"}, {"id": "a"}], "unordered": [{"id": "b"}, {"id": "a"}]}
    got = normalize_probe_result(raw, unordered_arrays={"$.unordered": "id"})
    assert [item["id"] for item in got["ordered"]] == ["b", "a"]
    assert [item["id"] for item in got["unordered"]] == ["a", "b"]


def test_degrees_of_unsaturation_invariants():
    raw = {"status": "success", "data": {"formula": "C6H6", "degrees_of_unsaturation": 4.0, "is_integer": True}}
    normalized = normalize_probe_result(raw)
    result = validate_probe_invariants(
        {"required_keys": ["status", "data"], "types": {"status": "string"}},
        raw,
        normalized,
        {"equals": {"$.data.degrees_of_unsaturation": 4.0, "$.data.is_integer": True}},
    )
    assert result["valid"] is True
    with pytest.raises(BaselineValidationError):
        validate_probe_invariants({}, raw, normalize_probe_result({"status": "success", "data": {"degrees_of_unsaturation": 3}}), {"equals": {"$.data.degrees_of_unsaturation": 4.0}})


def test_retry_policy_retries_transient_exactly_twice():
    calls, sleeps = [], []

    def run_once():
        calls.append(1)
        return {"status_code": 503} if len(calls) < 3 else {"status_code": 200}

    assert run_with_retry(run_once, sleeps.append) == {"status_code": 200}
    assert len(calls) == 3 and sleeps == [2.0, 2.0]
    assert classify_retryable({"status_code": 401}) is False


def test_retry_policy_surfaces_persistent_failure():
    calls, sleeps = [], []
    with pytest.raises(RetryExhaustedError):
        run_with_retry(lambda: calls.append(1) or {"status_code": 429}, sleeps.append)
    assert len(calls) == 3 and sleeps == [2.0, 2.0]


def test_provider_manifest_is_value_free_and_requires_configured_mapping():
    manifest = build_provider_manifest(
        [{"name": "OpenAI_tool", "description": "OpenAI provider"}],
        {"OPENAI_API_KEY": {"service": "OpenAI", "category": "LLM"}, "EMPTY_KEY": {"service": "Nope"}},
        {"OPENAI_API_KEY": "secret-value", "EMPTY_KEY": ""},
    )
    assert manifest["value_free"]
    assert next(item for item in manifest["providers"] if item["credential_name"] == "OPENAI_API_KEY")["configured"]
    assert "secret-value" not in json.dumps(manifest)


def test_catalog_sampling_is_repeatable():
    tools = [{"name": "b", "category": "chem"}, {"name": "a", "category": "chem"}, {"name": "x", "category": "bio"}]
    assert select_catalog_sample(tools, "a" * 40) == select_catalog_sample(tools, "a" * 40)


def test_publish_evidence_writes_canonical_checksums_and_rejects_secret(tmp_path):
    root = tmp_path / "bundle"
    result = publish_evidence({"baseline": {"stages": {"unit": "green"}}, "stages": {"unit": "green"}}, root, ["not-present"], ["unit"])
    sums = (result / "SHA256SUMS").read_text()
    assert "baseline.json" in sums and "SHA256SUMS" not in sums
    original = (result / "baseline.json").read_bytes()
    assert original == (result / "baseline.json").read_bytes()
    with pytest.raises(EvidencePublicationError):
        publish_evidence({"secret": {"token": "secret-value"}, "stages": {"unit": "green"}}, tmp_path / "secret", ["secret-value"], ["unit"])
