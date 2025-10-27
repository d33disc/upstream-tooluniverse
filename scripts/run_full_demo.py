#!/usr/bin/env python
"""
End-to-end ToolUniverse demo runner.

This script bootstraps the MedTok and MedLog reference services locally, points
ToolUniverse at them, and exercises a curated set of tools (MedTok, MedLog, and
several public data tools such as InterPro, KEGG, IUCN, JASPAR, MarineSpecies,
cBioPortal, Phenome Jax). It prints friendly status updates and reports any
failures at the end.

Usage:
    python scripts/run_full_demo.py

Optional flags:
    --skip-network-tools   Skip external API tools (InterPro, KEGG, etc.).
    --medtok-host HOST     Override MedTok host (default 127.0.0.1).
    --medtok-port PORT     Override MedTok port (default 8910).
    --medlog-host HOST     Override MedLog host (default 127.0.0.1).
    --collector-port PORT  Override MedLog collector port (default 8911).
    --fhir-port PORT       Override MedLog FHIR port (default 8912).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
import uvicorn
from fastapi import FastAPI, HTTPException

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from tooluniverse.execute_function import ToolUniverse

MEDTOK_ROOT = REPO_ROOT.parent / "MedTok-FHIR-Starter"
MEDLOG_ROOT = REPO_ROOT.parent / "medlog-reference"


class ServerHandle:
    """Run a FastAPI app in a background thread via uvicorn."""

    def __init__(self, app: FastAPI, host: str, port: int):
        config = uvicorn.Config(app, host=host, port=port, log_level="error", lifespan="off")
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    def start(self) -> None:
        self.thread.start()
        while not self.server.started:
            time.sleep(0.05)

    def stop(self) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)


def _import_module_typed(module_path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _service_is_up(base_url: str, path: str, ok_statuses: Optional[List[int]] = None) -> bool:
    try:
        resp = requests.get(f"{base_url}{path}", timeout=2)
        if ok_statuses is None:
            return resp.status_code < 500
        return resp.status_code in ok_statuses
    except requests.RequestException:
        return False


def start_medtok(host: str, port: int):
    """Start MedTok FastAPI service and return context info."""
    service_path = MEDTOK_ROOT / "services" / "medtok_service"
    if str(service_path) not in sys.path:
        sys.path.insert(0, str(service_path))

    base_url = os.environ.get("MEDTOK_BASE_URL") or f"http://{host}:{port}"
    if _service_is_up(base_url, "/health", ok_statuses=[200]):
        os.environ["MEDTOK_BASE_URL"] = base_url
        print(f"MedTok already running at {base_url}, reusing existing instance.")
        return {"server": None, "temp_config": None, "sys_path": str(service_path), "started": False}

    config_path = MEDTOK_ROOT / "config" / "medtok_config.json"
    config_data = json.loads(config_path.read_text(encoding="utf-8"))
    config_data["code_metadata_path"] = str(MEDTOK_ROOT / "samples" / "code_metadata.csv")
    config_data["graph_edges_path"] = str(MEDTOK_ROOT / "samples" / "code_graph_edges.csv")

    tmp_config = tempfile.NamedTemporaryFile("w", suffix="_medtok_config.json", delete=False)
    json.dump(config_data, tmp_config)
    tmp_config.flush()
    tmp_config.close()
    os.environ["MEDTOK_CONFIG"] = tmp_config.name

    module = _import_module_typed(service_path / "app.py")
    module.MAPPING_CSV = str(MEDTOK_ROOT / "samples" / "code_mapping.csv")
    app = module.app

    server = ServerHandle(app, host, port)
    server.start()
    os.environ["MEDTOK_BASE_URL"] = f"http://{host}:{port}"

    return {
        "server": server,
        "temp_config": tmp_config.name,
        "sys_path": str(service_path),
        "started": True,
    }


def _build_medlog_collector(store: Dict[str, Dict]):
    app = FastAPI()

    @app.post("/medlog/events/init")
    def init(payload: dict):
        header = payload.get("header") or {}
        event_id = header.get("event_id")
        if not event_id:
            raise HTTPException(400, "event_id required")
        record = {
            "header": header,
            "model_instance": payload.get("model_instance", {}),
            "user_identity": payload.get("user_identity", {}),
            "target_identity": payload.get("target_identity"),
            "inputs": payload.get("inputs"),
            "retention_tier": payload.get("retention_tier", "steady"),
            "fragments": [],
        }
        store[event_id] = record
        return {"status": "ok", "event_id": event_id}

    @app.post("/medlog/events/{event_id}/append")
    def append(event_id: str, fragment: dict):
        record = store.get(event_id)
        if record is None:
            raise HTTPException(404, "event not found")
        record["fragments"].append(fragment)
        return {"status": "ok", "event_id": event_id}

    @app.get("/medlog/events/{event_id}/prov")
    def prov(event_id: str):
        record = store.get(event_id)
        if record is None:
            raise HTTPException(404, "event not found")
        return {"event_id": event_id, "provenance": {"header": record["header"]}}

    @app.post("/query")
    def query(body: dict):
        run_id = body.get("run_id")
        event_id = body.get("event_id")
        limit = body.get("limit", 50)
        matches = []
        for eid, record in store.items():
            header = record["header"]
            if event_id and event_id != eid:
                continue
            if run_id and header.get("run_id") != run_id:
                continue
            matches.append({"event_id": eid, "header": header})
            if len(matches) >= limit:
                break
        return {"count": len(matches), "results": matches}

    @app.post("/export/parquet")
    def export():
        return {"status": "ok", "outdir": "/tmp/parquet"}

    return app


def _build_medlog_fhir(store: Dict[str, Dict]):
    app = FastAPI()

    def _bundle(records):
        return {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": record["header"]["event_id"],
                        "status": "final",
                    }
                }
                for record in records
            ],
        }

    @app.get("/bundle/{event_id}")
    def bundle_event(event_id: str):
        record = store.get(event_id)
        if record is None:
            raise HTTPException(404, "event not found")
        return _bundle([record])

    @app.get("/bundle/run/{run_id}")
    def bundle_run(run_id: str):
        records = [
            record
            for record in store.values()
            if record["header"].get("run_id") == run_id
        ]
        if not records:
            raise HTTPException(404, "run not found")
        return _bundle(records)

    return app


def start_medlog(host: str, collector_port: int, fhir_port: int):
    store: Dict[str, Dict] = {}
    collector_app = _build_medlog_collector(store)
    fhir_app = _build_medlog_fhir(store)

    collector_url = os.environ.get("MEDLOG_COLLECTOR_BASE_URL") or f"http://{host}:{collector_port}"
    fhir_url = os.environ.get("MEDLOG_FHIR_BASE_URL") or f"http://{host}:{fhir_port}"

    collector_server = None
    fhir_server = None

    if _service_is_up(collector_url, "/"):
        print(f"MedLog collector already running at {collector_url}, reusing.")
    else:
        collector_server = ServerHandle(collector_app, host, collector_port)
        collector_server.start()

    if _service_is_up(fhir_url, "/bundle/test"):
        print(f"MedLog FHIR service already running at {fhir_url}, reusing.")
    else:
        fhir_server = ServerHandle(fhir_app, host, fhir_port)
        fhir_server.start()

    os.environ["MEDLOG_COLLECTOR_BASE_URL"] = f"http://{host}:{collector_port}"
    os.environ["MEDLOG_FHIR_BASE_URL"] = f"http://{host}:{fhir_port}"

    return {"collector": collector_server, "fhir": fhir_server, "started": bool(collector_server or fhir_server)}


def stop_medtok(ctx: Dict[str, str]):
    if ctx.get("server"):
        ctx["server"].stop()
    if ctx.get("started"):
        os.environ.pop("MEDTOK_BASE_URL", None)
        os.environ.pop("MEDTOK_CONFIG", None)
        temp_config = ctx.get("temp_config")
        if temp_config:
            try:
                os.remove(temp_config)
            except OSError:
                pass
    sys_path = ctx.get("sys_path")
    if sys_path:
        try:
            sys.path.remove(sys_path)
        except ValueError:
            pass


def stop_medlog(ctx: Dict[str, ServerHandle]):
    if ctx.get("collector"):
        ctx["collector"].stop()
    if ctx.get("fhir"):
        ctx["fhir"].stop()
    if ctx.get("started"):
        os.environ.pop("MEDLOG_COLLECTOR_BASE_URL", None)
        os.environ.pop("MEDLOG_FHIR_BASE_URL", None)


def preview_json(payload: Any, limit: int = 240) -> str:
    """Return a compact preview of a payload for console logging."""
    try:
        text = json.dumps(payload, indent=2, ensure_ascii=False)
    except TypeError:
        text = str(payload)
    text = text.strip()
    if len(text) > limit:
        return text[:limit].rstrip() + "..."
    return text


def call_tool(tu: ToolUniverse, name: str, **kwargs):
    """Call a tool and handle ToolUniverse-specific errors."""
    print(f"---> Calling {name} with {kwargs}")
    try:
        response = getattr(tu.tools, name)(**kwargs)
        print(f"[OK] {name} succeeded")
        return True, response
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[FAIL] {name} failed: {exc}")
        return False, str(exc)


def run_medlog_demo(tu: ToolUniverse) -> List[Dict[str, str]]:
    results = []
    header = {
        "event_id": "evt-demo-1",
        "run_id": "run-demo-1",
        "timestamp": "2025-01-01T00:00:00Z",
    }
    model_instance = {"model": "demo", "version": "1.0"}
    user_identity = {"name": "Dr. Example"}
    steps = [
        (
            "MedLog_init_event",
            dict(header=header, model_instance=model_instance, user_identity=user_identity),
            "Open an event with metadata (who, when, which model).",
        ),
        (
            "MedLog_append_fragment",
            dict(event_id="evt-demo-1", fragment={"outputs": {"summary": "Patient stable"}}),
            "Attach a fragment that captures model outputs for the event.",
        ),
        ("MedLog_get_provenance", dict(event_id="evt-demo-1"), "Retrieve provenance header saved for the event."),
        ("MedLog_query_events", dict(run_id="run-demo-1"), "Query the store by run identifier."),
        ("MedLog_export_parquet", dict(), "Trigger sample export (stub returns static location)."),
        ("MedLog_fhir_bundle", dict(event_id="evt-demo-1"), "View the event as a single FHIR Observation bundle."),
        ("MedLog_fhir_run_bundle", dict(run_id="run-demo-1"), "Bundle all events in the run as FHIR Observations."),
    ]

    for name, kwargs, description in steps:
        print(f"   - {description}")
        success, payload = call_tool(tu, name, **kwargs)
        note = None
        if success:
            if name == "MedLog_init_event":
                note = f"Created event {payload.get('event_id')}"
            elif name == "MedLog_append_fragment":
                note = "Attached fragment with outputs summary"
            elif name == "MedLog_get_provenance":
                prov = payload.get("provenance", {})
                note = f"Provenance keys: {', '.join(prov.keys()) or 'none'}"
            elif name == "MedLog_query_events":
                note = f"Query returned {payload.get('count', 0)} rows"
            elif name == "MedLog_fhir_bundle":
                note = f"Bundle contains {len(payload.get('entry', []))} resources"
            elif name == "MedLog_fhir_run_bundle":
                note = f"Run bundle resources: {len(payload.get('entry', []))}"
        if success and note:
            print(f"     Result: {note}")
        results.append({"tool": name, "success": success, "response": payload, "note": note})
    return results


def run_medtok_demo(tu: ToolUniverse) -> List[Dict[str, str]]:
    tests = [
        (
            "MedTok_tokenize",
            dict(codes=["A00", "E11"], system="ICD-10", include_metadata=True),
            "Convert ICD-10 codes into internal token IDs plus metadata for downstream models.",
        ),
        ("MedTok_embed", dict(codes=["A00"], system="ICD-10"), "Generate vector embeddings for a medical code."),
        ("MedTok_nearest_neighbors", dict(code="A00", k=3), "Find nearby codes in embedding space."),
        ("MedTok_map_text_to_code", dict(text="type 2 diabetes", system="ICD-10"), "Map free text to the closest code."),
        ("MedTok_search_text", dict(text="hypertension", k=4), "Search the terminology for matching codes by text."),
        ("MedTok_code_info", dict(code="E11", system="ICD-10"), "Fetch descriptive details for a specific code."),
    ]
    results = []
    for name, kwargs, description in tests:
        print(f"   - {description}")
        success, payload = call_tool(tu, name, **kwargs)
        note = None
        if success:
            if name == "MedTok_tokenize":
                note = f"Received {len(payload.get('token_ids', []))} token IDs"
            elif name == "MedTok_embed":
                emb = payload.get("embeddings") or []
                if emb:
                    note = f"Embedding dimension {payload.get('dim')}, first vector length {len(emb[0])}"
            elif name == "MedTok_nearest_neighbors":
                note = f"Returned {len(payload.get('neighbors', []))} neighbors"
            elif name == "MedTok_map_text_to_code":
                note = f"Mapped text to code {payload.get('code')}"
            elif name == "MedTok_search_text":
                note = f"Top match code {payload.get('matches', [{}])[0].get('code') if payload.get('matches') else 'N/A'}"
            elif name == "MedTok_code_info":
                note = f"Code info description: {payload.get('description', 'N/A')}"
        if success and note:
            print(f"     Result: {note}")
        results.append({"tool": name, "success": success, "response": payload, "note": note})
    return results


NETWORK_TOOLS = [
    ("InterPro_search_entries", {"query": "BRCA1"}),
    ("KEGG_find_entries", {"query": "ATP synthase", "database": "pathway"}),
    ("IUCN_get_species_status", {"species": "Panthera leo"}),
    ("JASPAR_search_motifs", {"query": "SOX2"}),
    ("MarineSpecies_lookup", {"scientific_name": "Gadus morhua"}),
    ("cBioPortal_search_studies", {"keyword": "breast cancer"}),
    ("PhenomeJax_list_projects", {"keyword": "glucose"}),
]


def run_network_tools(tu: ToolUniverse) -> List[Dict[str, str]]:
    outcomes = []
    for name, kwargs in NETWORK_TOOLS:
        success, payload = call_tool(tu, name, **kwargs)
        note_parts: List[str] = []
        if success:
            if name == "InterPro_search_entries":
                data = payload if isinstance(payload, dict) else {}
                note_parts.append(f"Entries returned: {len(data.get('results', []))}")
            elif name == "KEGG_find_entries":
                if isinstance(payload, dict):
                    note_parts.append(f"Matched {len(payload.get('results', []))} entries")
                elif isinstance(payload, list):
                    note_parts.append(f"Matched {len(payload)} entries")
            elif name == "IUCN_get_species_status":
                result = payload.get("result") if isinstance(payload, dict) else {}
                if isinstance(result, list) and result:
                    result = result[0]
                elif result is None:
                    result = {}
                species = result.get("scientific_name")
                category = result.get("category")
                note_parts.append(f"{species} status {category}")
            elif name == "JASPAR_search_motifs":
                data = payload if isinstance(payload, dict) else {}
                note_parts.append(f"Found {len(data.get('results', []))} motifs")
            elif name == "MarineSpecies_lookup":
                data = payload if isinstance(payload, dict) else {}
                note_parts.append(f"Matches: {len(data.get('results', []))}")
            elif name == "cBioPortal_search_studies":
                data = payload if isinstance(payload, dict) else {}
                note_parts.append(f"Studies returned: {len(data.get('studies', []))}")
            elif name == "PhenomeJax_list_projects":
                data = payload if isinstance(payload, dict) else {}
                note_parts.append(f"Projects listed: {len(data.get('projects', []))}")

            preview = preview_json(payload)
            print(f"     {name} preview: {preview}")
            note_parts.append(f"Preview: {preview}")
        else:
            print(f"     {name} error payload: {preview_json(payload)}")
        note = " | ".join(note_parts) if note_parts else None
        outcomes.append({"tool": name, "success": success, "response": payload, "note": note})
    return outcomes


def _extract_host(candidate: Dict[str, Any]) -> str:
    host = candidate.get("host")
    if host:
        return str(host)
    for key in ("url", "endpoint", "base_url"):
        maybe = candidate.get(key)
        if not maybe:
            continue
        parsed = urlparse(str(maybe))
        if parsed.netloc:
            return parsed.netloc
    return "candidate"


def _slugify_host(value: str) -> str:
    slug = "".join(ch if ch.isalnum() else "_" for ch in value.lower())
    slug = slug.strip("_")
    return slug or "candidate"


def run_vsd_demo(tu: ToolUniverse) -> List[Dict[str, str]]:
    """
    Demonstrate the Harvest -> Register -> Run workflow using Verified Source Directory helpers.
    """
    search_query = "ensembl rest api"
    print(f"\nSearching harvest catalog for '{search_query}' candidates...")
    results: List[Dict[str, Any]] = []

    success_search, harvest_resp = call_tool(
        tu,
        "GenericHarvestTool",
        query=search_query,
        limit=5,
    )
    selected_candidate: Optional[Dict[str, Any]] = None
    note_search: Optional[str] = None
    if success_search:
        candidates = (harvest_resp or {}).get("candidates") or []
        note_search = f"Candidates returned: {len(candidates)}"
        if candidates:
            preferred_hosts = {"rest.ensembl.org", "api.open-meteo.com"}
            for candidate_option in candidates:
                host = _extract_host(candidate_option).lower()
                if host in preferred_hosts:
                    selected_candidate = candidate_option
                    break
            if not selected_candidate:
                selected_candidate = candidates[0]
            host = _extract_host(selected_candidate)
            print(f"   - Selected candidate: {selected_candidate.get('name')} ({selected_candidate.get('url')}) [host: {host}]")
            print(f"     Candidate preview: {preview_json(selected_candidate)}")
        else:
            print("   - Harvest returned no candidates.")
    else:
        print(f"   - Harvest search failed payload: {preview_json(harvest_resp)}")
        note_search = "Harvest search failed"
    results.append({"tool": "GenericHarvestTool", "success": success_search, "response": harvest_resp, "note": note_search})

    if not (success_search and selected_candidate):
        results.append(
            {
                "tool": "HarvestCandidateTesterTool",
                "success": False,
                "response": {"error": "No harvest candidate available"},
                "note": "Skipped testing",
            }
        )
        return results

    candidate = selected_candidate
    print("\nTesting harvest candidate via HarvestCandidateTesterTool...")
    success_probe, probe_resp = call_tool(
        tu,
        "HarvestCandidateTesterTool",
        candidate=candidate,
    )
    probe_note = None
    if success_probe:
        status = (probe_resp.get("test") or {}).get("status")
        probe_note = f"Probe status {status}"
        print(f"   - Probe preview: {preview_json(probe_resp)}")
    else:
        print(f"   - Probe failure payload: {preview_json(probe_resp)}")
    results.append({"tool": "HarvestCandidateTesterTool", "success": success_probe, "response": probe_resp, "note": probe_note})

    if not (success_probe and probe_resp.get("ok")):
        print("Skipping registration because candidate probe failed.")
        results.append(
            {
                "tool": "VerifiedSourceRegisterTool",
                "success": False,
                "response": {"error": "Probe failed"},
                "note": None,
            }
        )
        return results

    host_slug = _slugify_host(_extract_host(candidate))
    tool_name = f"HarvestDemo_{host_slug[:40]}"

    print("\nRegistering candidate with VerifiedSourceRegisterTool...")
    success_reg, register_resp = call_tool(
        tu,
        "VerifiedSourceRegisterTool",
        tool_name=tool_name,
        candidate=candidate,
    )
    note_reg = None
    if success_reg:
        config = (register_resp or {}).get("config") or {}
        base_url = (config.get("fields") or {}).get("base_url") or config.get("endpoint")
        note_reg = f"Registered tool pointing to {base_url}"
        print(f"   - Registered config preview: {preview_json(config)}")
    else:
        print(f"   - Registration failure payload: {preview_json(register_resp)}")
    results.append(
        {
            "tool": "VerifiedSourceRegisterTool",
            "success": success_reg,
            "response": register_resp,
            "note": note_reg,
        }
    )

    if not success_reg:
        return results

    print("\nCalling newly registered tool...")
    tu.load_tools(include_tools=[tool_name])
    success_run, run_resp = call_tool(tu, tool_name)
    note_run = None
    if success_run:
        preview = preview_json(run_resp)
        note_run = f"Preview: {preview}"
        print(f"   - Run result preview: {preview}")
    else:
        print(f"   - Run failure payload: {preview_json(run_resp)}")
    results.append({"tool": tool_name, "success": success_run, "response": run_resp, "note": note_run})

    print("\nCleaning up registered tool...")
    success_rm, rm_resp = call_tool(
        tu,
        "VerifiedSourceRemoveTool",
        tool_name=tool_name,
    )
    note_rm = "Removed from catalog" if success_rm else None
    if success_rm:
        print(f"   - Removal confirmation: {preview_json(rm_resp)}")
    else:
        print(f"   - Removal failure payload: {preview_json(rm_resp)}")
    results.append({"tool": "VerifiedSourceRemoveTool", "success": success_rm, "response": rm_resp, "note": note_rm})

    return results


def main():
    parser = argparse.ArgumentParser(description="Run ToolUniverse end-to-end demo.")
    parser.add_argument("--skip-network-tools", action="store_true", help="Skip tools that require external HTTP APIs.")
    parser.add_argument("--skip-vsd", action="store_true", help="Skip harvest/register/run VSD demonstration.")
    parser.add_argument("--medtok-host", default="127.0.0.1")
    parser.add_argument("--medtok-port", type=int, default=8910)
    parser.add_argument("--medlog-host", default="127.0.0.1")
    parser.add_argument("--collector-port", type=int, default=8911)
    parser.add_argument("--fhir-port", type=int, default=8912)
    args = parser.parse_args()

    medtok_ctx = None
    medlog_ctx = None
    all_results: List[Dict[str, str]] = []

    try:
        print("Starting MedTok service...")
        medtok_ctx = start_medtok(args.medtok_host, args.medtok_port)
        print(f"MedTok running at {os.environ['MEDTOK_BASE_URL']}")

        print("Starting MedLog services...")
        medlog_ctx = start_medlog(args.medlog_host, args.collector_port, args.fhir_port)
        print(
            f"MedLog collector at {os.environ['MEDLOG_COLLECTOR_BASE_URL']}, "
            f"FHIR bridge at {os.environ['MEDLOG_FHIR_BASE_URL']}"
        )

        tu = ToolUniverse(hooks_enabled=False)
        tu.load_tools(tool_type=["medtok", "medlog"])

        print("\nRunning MedTok demo calls...")
        all_results.extend(run_medtok_demo(tu))

        print("\nRunning MedLog demo calls...")
        all_results.extend(run_medlog_demo(tu))

        if not args.skip_network_tools:
            print("\nLoading network-enabled tools (InterPro, KEGG, IUCN, etc.)...")
            categories = [
                "interpro",
                "kegg",
                "iucn_red_list",
                "jaspar",
                "marine_species",
                "cbioportal",
                "phenome_jax",
            ]
            try:
                tu.load_tools(tool_type=categories)
            except Exception as exc:  # pylint: disable=broad-except
                print(f"[WARN] Failed to load network tool categories: {exc}")
            else:
                print("Running network tool calls...")
                all_results.extend(run_network_tools(tu))
        else:
            print("\nSkipping external network tools.")

        if not args.skip_vsd:
            print("\nHarvest -> Register -> Run walkthrough...")
            vsd_results = run_vsd_demo(tu)
            all_results.extend(vsd_results)
        else:
            print("\nSkipping VSD harvest/register/run demo.")

    finally:
        if medtok_ctx:
            print("\nStopping MedTok service...")
            stop_medtok(medtok_ctx)
        if medlog_ctx:
            print("Stopping MedLog services...")
            stop_medlog(medlog_ctx)

    print("\n================ Demo Summary ================")
    failures = [r for r in all_results if not r["success"]]
    for result in all_results:
        status = "PASS" if result["success"] else "FAIL"
        print(f"{status:4} | {result['tool']}")
        note = result.get("note")
        if note:
            print(f"      {note}")
        if not result["success"]:
            print(f"    -> {result['response']}")
    print("=============================================")

    if failures:
        print(f"{len(failures)} tool calls failed.")
        sys.exit(1)
    print("All tool calls succeeded.")


if __name__ == "__main__":
    main()
