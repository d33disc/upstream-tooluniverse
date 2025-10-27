#!/usr/bin/env python
"""
Lightweight MedLog stub servers for local demos.

Run the collector:
    python scripts/medlog_stub_server.py --mode collector --host 127.0.0.1 --port 8911

Run the FHIR bridge:
    python scripts/medlog_stub_server.py --mode fhir --host 127.0.0.1 --port 8912
"""

from __future__ import annotations

import argparse
import os
import threading
import time
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException


STORE: Dict[str, Dict] = {}
STORE_LOCK = threading.Lock()


def build_collector_app() -> FastAPI:
    app = FastAPI(title="MedLog Collector (Stub)", version="0.1.0")

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
        with STORE_LOCK:
            STORE[event_id] = record
        return {"status": "ok", "event_id": event_id}

    @app.post("/medlog/events/{event_id}/append")
    def append(event_id: str, fragment: dict):
        with STORE_LOCK:
            record = STORE.get(event_id)
            if record is None:
                raise HTTPException(404, "event not found")
            record["fragments"].append(fragment)
        return {"status": "ok", "event_id": event_id}

    @app.get("/medlog/events/{event_id}/prov")
    def prov(event_id: str):
        with STORE_LOCK:
            record = STORE.get(event_id)
            if record is None:
                raise HTTPException(404, "event not found")
            header = record["header"]
        return {"event_id": event_id, "provenance": {"header": header}}

    @app.post("/query")
    def query(body: dict):
        run_id = body.get("run_id")
        event_id = body.get("event_id")
        limit = body.get("limit", 50)
        results = []
        with STORE_LOCK:
            for eid, record in STORE.items():
                header = record["header"]
                if event_id and event_id != eid:
                    continue
                if run_id and header.get("run_id") != run_id:
                    continue
                results.append({"event_id": eid, "header": header})
                if len(results) >= limit:
                    break
        return {"count": len(results), "results": results}

    @app.post("/export/parquet")
    def export():
        return {"status": "ok", "outdir": "/tmp/parquet"}

    return app


def build_fhir_app() -> FastAPI:
    app = FastAPI(title="MedLog FHIR Stub", version="0.1.0")

    def bundle(records):
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
        with STORE_LOCK:
            record = STORE.get(event_id)
        if record is None:
            raise HTTPException(404, "event not found")
        return bundle([record])

    @app.get("/bundle/run/{run_id}")
    def bundle_run(run_id: str):
        with STORE_LOCK:
            records = [
                record
                for record in STORE.values()
                if record["header"].get("run_id") == run_id
            ]
        if not records:
            raise HTTPException(404, "run not found")
        return bundle(records)

    return app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["collector", "fhir"], required=True)
    parser.add_argument("--host", default=os.getenv("MEDLOG_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MEDLOG_PORT", 0)) or 0)
    args = parser.parse_args()

    if args.port == 0:
        args.port = 8911 if args.mode == "collector" else 8912

    app = build_collector_app() if args.mode == "collector" else build_fhir_app()
    print(f"Starting MedLog {args.mode} stub on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
