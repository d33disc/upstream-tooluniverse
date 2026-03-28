"""Tool health cache — runtime-generated, never committed, never conflicts with upstream.

The health cache lives at ~/.tooluniverse/health.json (user-local, gitignored).
It records which tools pass/fail their test_examples and why.

Usage:
    from tooluniverse.tool_health import ToolHealthCache

    cache = ToolHealthCache()
    cache.check("PubMed_search_articles")  # -> {"status": "live", ...} or None
    cache.warn("PubMed_search_articles")   # -> None (live) or warning string (broken)
    cache.refresh(["PubMed_search_articles"])  # re-test specific tools
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_CACHE_PATH = Path.home() / ".tooluniverse" / "health.json"
STALE_DAYS = 7


class ToolHealthCache:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or DEFAULT_CACHE_PATH
        self._data: dict = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text())
            except (json.JSONDecodeError, OSError):
                self._data = {}
        self._loaded = True

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2))

    def check(self, tool_name: str) -> Optional[dict]:
        self._ensure_loaded()
        return self._data.get(tool_name)

    def is_live(self, tool_name: str) -> Optional[bool]:
        record = self.check(tool_name)
        if record is None:
            return None
        return record.get("status") == "live"

    def warn(self, tool_name: str) -> Optional[str]:
        record = self.check(tool_name)
        if record is None:
            return None
        if record.get("status") == "broken":
            detail = record.get("detail", "unknown reason")
            tested = record.get("tested", "unknown date")
            return (
                f"WARNING: {tool_name} failed health check ({detail}). "
                f"Last tested: {tested}. Results may be unreliable."
            )
        return None

    def is_stale(self, tool_name: str) -> bool:
        record = self.check(tool_name)
        if record is None:
            return True
        tested = record.get("tested_epoch", 0)
        return (time.time() - tested) > (STALE_DAYS * 86400)

    def test_tool(self, tool_name: str) -> dict:
        try:
            result = subprocess.run(
                ["python", "-m", "tooluniverse.cli", "test", tool_name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout + result.stderr
            if "passed" in output:
                return {
                    "status": "live",
                    "detail": "passed",
                    "tested": time.strftime("%Y-%m-%d"),
                    "tested_epoch": time.time(),
                }
            lines = output.strip().split("\n")
            err = [ln for ln in lines if "\u2717" in ln or "error" in ln.lower()]
            detail = err[0].strip()[:120] if err else "test failed"
            return {
                "status": "broken",
                "detail": detail,
                "tested": time.strftime("%Y-%m-%d"),
                "tested_epoch": time.time(),
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "broken",
                "detail": "timeout",
                "tested": time.strftime("%Y-%m-%d"),
                "tested_epoch": time.time(),
            }
        except Exception as e:
            return {
                "status": "broken",
                "detail": str(e)[:120],
                "tested": time.strftime("%Y-%m-%d"),
                "tested_epoch": time.time(),
            }

    def refresh(self, tool_names: list[str]) -> dict[str, dict]:
        self._ensure_loaded()
        results = {}
        for name in tool_names:
            record = self.test_tool(name)
            self._data[name] = record
            results[name] = record
        self._save()
        return results

    def summary(self) -> dict:
        self._ensure_loaded()
        live = sum(1 for r in self._data.values() if r.get("status") == "live")
        broken = sum(1 for r in self._data.values() if r.get("status") == "broken")
        return {"live": live, "broken": broken, "total": len(self._data)}

    def import_manifest(self, manifest_path: Path) -> None:
        manifest = json.loads(manifest_path.read_text())
        now = time.strftime("%Y-%m-%d")
        epoch = time.time()
        for cat_data in manifest.get("categories", {}).values():
            for tool in cat_data.get("tools", []):
                name = tool.get("name", "")
                if name:
                    self._data[name] = {
                        "status": tool.get("status", "unknown"),
                        "detail": tool.get("detail", ""),
                        "tested": now,
                        "tested_epoch": epoch,
                    }
        self._save()
        s = self.summary()
        logger.info(
            "Imported %d tools (%d live, %d broken)",
            s["total"],
            s["live"],
            s["broken"],
        )
