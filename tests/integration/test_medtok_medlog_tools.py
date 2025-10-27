import importlib.util
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from fastapi import FastAPI, HTTPException

from tooluniverse.execute_function import ToolUniverse


class _ServerHandle:
    """Utility wrapper for running uvicorn servers in tests."""

    def __init__(self, app: FastAPI, host: str, port: int):
        config = uvicorn.Config(
            app, host=host, port=port, log_level="error", lifespan="off"
        )
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    def start(self) -> None:
        self.thread.start()
        while not self.server.started:
            time.sleep(0.05)

    def stop(self) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)


def _import_medtok_app(module_path: Path):
    spec = importlib.util.spec_from_file_location("medtok_service_app", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def medtok_server():
    repo_root = Path(__file__).resolve().parents[3]
    medtok_root = repo_root / "MedTok-FHIR-Starter"
    service_dir = medtok_root / "services" / "medtok_service"
    sys.path.insert(0, str(service_dir))

    base_config_path = medtok_root / "config" / "medtok_config.json"
    config_data = json.loads(base_config_path.read_text(encoding="utf-8"))
    config_data["code_metadata_path"] = str(
        medtok_root / "samples" / "code_metadata.csv"
    )
    config_data["graph_edges_path"] = str(
        medtok_root / "samples" / "code_graph_edges.csv"
    )
    tmp_config = tempfile.NamedTemporaryFile(
        "w", suffix="_medtok_config.json", delete=False
    )
    json.dump(config_data, tmp_config)
    tmp_config.flush()
    tmp_config.close()
    os.environ["MEDTOK_CONFIG"] = tmp_config.name

    module = _import_medtok_app(service_dir / "app.py")
    module.MAPPING_CSV = str(medtok_root / "samples" / "code_mapping.csv")
    app = module.app

    host = "127.0.0.1"
    port = 8910
    server = _ServerHandle(app, host, port)
    server.start()

    base_url = f"http://{host}:{port}"
    os.environ["MEDTOK_BASE_URL"] = base_url

    yield base_url

    server.stop()
    os.environ.pop("MEDTOK_BASE_URL", None)
    os.environ.pop("MEDTOK_CONFIG", None)
    try:
        os.remove(tmp_config.name)
    except FileNotFoundError:
        pass
    sys.path.remove(str(service_dir))


def _build_medlog_collector(store):
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


def _build_medlog_fhir(store):
    app = FastAPI()

    def _bundle_for_records(records):
        entries = []
        for rec in records:
            entries.append(
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": rec["header"]["event_id"],
                        "status": "final",
                    }
                }
            )
        return {"resourceType": "Bundle", "type": "collection", "entry": entries}

    @app.get("/bundle/{event_id}")
    def bundle(event_id: str):
        record = store.get(event_id)
        if record is None:
            raise HTTPException(404, "event not found")
        return _bundle_for_records([record])

    @app.get("/bundle/run/{run_id}")
    def bundle_run(run_id: str):
        records = [
            record
            for record in store.values()
            if record["header"].get("run_id") == run_id
        ]
        if not records:
            raise HTTPException(404, "run not found")
        return _bundle_for_records(records)

    return app


@pytest.fixture(scope="session")
def medlog_servers():
    store = {}
    host = "127.0.0.1"
    collector_port = 8911
    fhir_port = 8912

    collector_app = _build_medlog_collector(store)
    fhir_app = _build_medlog_fhir(store)

    collector = _ServerHandle(collector_app, host, collector_port)
    fhir = _ServerHandle(fhir_app, host, fhir_port)
    collector.start()
    fhir.start()

    os.environ["MEDLOG_COLLECTOR_BASE_URL"] = f"http://{host}:{collector_port}"
    os.environ["MEDLOG_FHIR_BASE_URL"] = f"http://{host}:{fhir_port}"

    yield store

    collector.stop()
    fhir.stop()
    os.environ.pop("MEDLOG_COLLECTOR_BASE_URL", None)
    os.environ.pop("MEDLOG_FHIR_BASE_URL", None)


def test_medtok_rest_tools(medtok_server):
    tu = ToolUniverse(hooks_enabled=False)
    tu.load_tools(tool_type=["medtok"])

    tokenize = tu.tools.MedTok_tokenize(
        codes=["A00", "E11"], system="ICD-10", include_metadata=True
    )
    token_ids = tokenize.get("token_ids", [])
    assert isinstance(token_ids, list)
    assert len(token_ids) in (0, 2)

    embed = tu.tools.MedTok_embed(codes=["A00"], system="ICD-10")
    embeddings = embed.get("embeddings", [])
    if embeddings:
        assert isinstance(embeddings[0], list)
        assert embed.get("dim") == len(embeddings[0])

    neighbors = tu.tools.MedTok_nearest_neighbors(code="A00", k=3)
    neighbor_list = neighbors.get("neighbors", [])
    assert len(neighbor_list) <= 3

    mapped = tu.tools.MedTok_map_text_to_code(text="type 2 diabetes", system="ICD-10")
    assert "code" in mapped

    search = tu.tools.MedTok_search_text(text="hypertension", k=4)
    assert len(search.get("matches", [])) <= 4

    code_info = tu.tools.MedTok_code_info(code="E11", system="ICD-10")
    assert isinstance(code_info, dict)


def test_medlog_tools_workflow(medlog_servers):
    tu = ToolUniverse(hooks_enabled=False)
    tu.load_tools(tool_type=["medlog"])

    header = {
        "event_id": "evt-1",
        "run_id": "run-123",
        "timestamp": "2025-01-01T00:00:00Z",
    }
    model_instance = {"model": "demo", "version": "1.0"}
    user_identity = {"name": "Dr. Example"}

    init_resp = tu.tools.MedLog_init_event(
        header=header, model_instance=model_instance, user_identity=user_identity
    )
    assert init_resp["status"] == "ok"

    fragment = {"outputs": {"summary": "Patient stable"}}
    append_resp = tu.tools.MedLog_append_fragment(event_id="evt-1", fragment=fragment)
    assert append_resp["status"] == "ok"

    prov_resp = tu.tools.MedLog_get_provenance(event_id="evt-1")
    assert prov_resp["event_id"] == "evt-1"

    query_resp = tu.tools.MedLog_query_events(run_id="run-123")
    assert query_resp["count"] == 1
    assert query_resp["results"][0]["event_id"] == "evt-1"

    export_resp = tu.tools.MedLog_export_parquet()
    assert export_resp["status"] == "ok"

    bundle_resp = tu.tools.MedLog_fhir_bundle(event_id="evt-1")
    assert bundle_resp["resourceType"] == "Bundle"

    run_bundle_resp = tu.tools.MedLog_fhir_run_bundle(run_id="run-123")
    assert len(run_bundle_resp["entry"]) == 1
