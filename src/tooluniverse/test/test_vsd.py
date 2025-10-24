import os
from tooluniverse.tool_registry import get_tool_class

def test_discover_returns_candidates():
    t = get_tool_class("VerifiedSourceDiscoveryTool")({})
    out = t.run({"query": "Alzheimer's clinical trials last 6 months"})
    assert "candidates" in out and isinstance(out["candidates"], list)

def test_register_writes_files(tmp_path):
    os.environ["TOOLUNIVERSE_VSD_DIR"] = str(tmp_path)
    t = get_tool_class("VerifiedSourceRegisterTool")({})
    cand = {
        "domain": "clinicaltrials.gov",
        "endpoint": "https://clinicaltrials.gov/api/v2/studies",
        "license": "CC0",
        "score": 0.9
    }
    out = t.run({"candidate": cand, "tool_name": "clinicaltrials_list_alzheimers"})
    assert out.get("registered") is True
    assert os.path.exists(out["config_path"]) and os.path.exists(out["evidence"])
