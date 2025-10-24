# generic_harvest_tool.py
from __future__ import annotations

import os
import re
import json
import time
import pkgutil
import importlib
import inspect
import traceback
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from .base_tool import BaseTool
from .tool_registry import register_tool

# -----------------------------------------------------------------------------
# Debug helpers
# -----------------------------------------------------------------------------

DEBUG = os.environ.get("TOOLUNIVERSE_DEBUG", "1").strip() not in {"", "0", "false", "False"}
DBG_PREFIX = "[HARVEST]"

def _dbg(*args: Any) -> None:
    if DEBUG:
        try:
            print(DBG_PREFIX, *args, flush=True)
        except Exception:
            pass

def _pp(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    except Exception:
        return repr(obj)


# -----------------------------------------------------------------------------
# URL helpers
# -----------------------------------------------------------------------------

def _looks_like_url(s: str) -> bool:
    try:
        p = urlparse(s)
        ok = bool(p.scheme in ("http", "https") and p.netloc)
        _dbg("looks_like_url?", s, "=>", ok)
        return ok
    except Exception as e:
        _dbg("looks_like_url EXC:", e)
        return False


def _normalize_url(u: str) -> str:
    try:
        p = urlparse(u)
        scheme = (p.scheme.lower() if p.scheme else "https")
        netloc = p.netloc.lower()
        path = p.path or "/"
        query = p.query or ""
        out = f"{scheme}://{netloc}{path}"
        if query:
            out += f"?{query}"
        _dbg("normalize_url:", u, "=>", out)
        return out
    except Exception as e:
        _dbg("normalize_url EXC:", e, "for:", u)
        return (u or "").strip()


def _dedupe_candidates(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    _dbg("dedupe_candidates: incoming", len(items))
    seen = set()
    out: List[Dict[str, Any]] = []
    for it in items:
        url = _normalize_url(it.get("url", ""))
        if not _looks_like_url(url):
            _dbg("dedupe_candidates: skip invalid url:", url, "item:", it)
            continue
        key = (urlparse(url).netloc, urlparse(url).path or "/")
        if key in seen:
            _dbg("dedupe_candidates: dup:", url)
            continue
        seen.add(key)
        it["url"] = url
        out.append(it)
    _dbg("dedupe_candidates: outgoing", len(out))
    return out


def _score_candidate(name: str, description: str, query: str, source_boost: float) -> float:
    q = (query or "").lower().strip()
    text = f"{name or ''} {description or ''}".lower()
    score = 0.0
    for token in set(re.split(r"\W+", q)):
        if token and token in text:
            score += 1.0
    if q and q in text:
        score += 2.0
    final = score + source_boost
    _dbg("score_candidate:", {"name": name, "sboost": source_boost, "score": final})
    return final


def _rank_and_limit(cands: List[Dict[str, Any]], query: str, limit: int) -> List[Dict[str, Any]]:
    _dbg("rank_and_limit: incoming", len(cands), "limit", limit)
    src_weight = {
        "publicapis.org": 0.40,
        "apis.guru": 0.35,
        "data.gov": 0.35,
        "awesome": 0.25,
        "query": 0.10,
        "manual": 0.05,
    }
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for c in cands:
        name = c.get("name") or ""
        desc = c.get("description") or ""
        sboost = src_weight.get(c.get("source", ""), 0.0)
        score = _score_candidate(name, desc, query, sboost)
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    limited = [c for _, c in scored[: max(1, min(limit, 50))]]
    _dbg("rank_and_limit: outgoing", len(limited))
    return limited


# -----------------------------------------------------------------------------
# Harvest folder integration
# -----------------------------------------------------------------------------

def _load_harvester_modules() -> List[Any]:
    """
    Import all modules under tooluniverse.harvest that expose harvest(query, limit).
    Adds detailed debugging: which modules found, which skipped, exceptions, etc.
    """
    modules = []
    try:
        from . import harvest as harvest_pkg  # type: ignore
        _dbg("harvest_pkg:", getattr(harvest_pkg, "__name__", harvest_pkg))
    except Exception as e:
        _dbg("import harvest package FAILED:", e)
        return modules

    paths = getattr(harvest_pkg, "__path__", [])
    _dbg("iter_modules over path(s):", list(paths))
    for m in pkgutil.iter_modules(paths):  # type: ignore[arg-type]
        mod_name = f"{harvest_pkg.__name__}.{m.name}"
        try:
            t0 = time.time()
            mod = importlib.import_module(mod_name)
            dt = (time.time() - t0) * 1000
            has_harvest = hasattr(mod, "harvest") and callable(getattr(mod, "harvest"))
            _dbg("loaded module:", mod_name, "ms:", round(dt, 1), "has_harvest:", has_harvest)
            if has_harvest:
                modules.append(mod)
        except Exception as e:
            _dbg("import module FAILED:", mod_name, "err:", e)
            _dbg(traceback.format_exc())
            continue
    _dbg("total harvester modules:", len(modules))
    return modules


def _run_all_harvesters(query: str, limit: int) -> List[Dict[str, Any]]:
    _dbg("run_all_harvesters: query=", query, "limit=", limit)
    results: List[Dict[str, Any]] = []
    modules = _load_harvester_modules()
    for mod in modules:
        try:
            t0 = time.time()
            out = mod.harvest(query=query, limit=limit)  # type: ignore[attr-defined]
            dt = round((time.time() - t0) * 1000, 1)
            _dbg("harvest() returned from", getattr(mod, "__name__", mod), "in", dt, "ms")
            if isinstance(out, list):
                added = 0
                for c in out:
                    if not isinstance(c, dict):
                        _dbg("harvester output non-dict, skip:", type(c))
                        continue
                    c.setdefault("name", "Candidate")
                    c.setdefault("url", "")
                    c.setdefault("source", getattr(mod, "__name__", "harvest"))
                    c.setdefault("description", "")
                    results.append(c)
                    added += 1
                _dbg("harvester added", added, "candidates")
            else:
                _dbg("harvester returned non-list; skip. type:", type(out))
        except Exception as e:
            _dbg("harvest call FAILED for", getattr(mod, "__name__", mod), "err:", e)
            _dbg(traceback.format_exc())
            continue
    _dbg("run_all_harvesters: total raw candidates:", len(results))
    return results


# -----------------------------------------------------------------------------
# MCP Tool
# -----------------------------------------------------------------------------

@register_tool(
    "GenericHarvestTool",
    config={
        "name": "GenericHarvestTool",
        "type": "GenericHarvestTool",
        "description": "Live-harvest candidate API endpoints by invoking all modules in tooluniverse.harvest.",
        "tool_type": "special_tools",
        "enabled": True,
        "visible": True,
    },
)
class GenericHarvestTool(BaseTool):
    """
    Live-harvesting helper that delegates to every harvester in tooluniverse/harvest/.
    - If `urls` provided: validate/dedupe and return as candidates.
    - Else `query`: call all harvesters, merge/dedupe, rank, and return.
    Output: {"candidates":[{"name","url","source","description", ...}]}
    """

    name = "GenericHarvestTool"
    description = "Live-harvest candidate API endpoints by invoking all modules in tooluniverse.harvest."
    tool_type = "special_tools"

    arguments_jsonschema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free-text hint, passed to all harvesters under tooluniverse.harvest.",
            },
            "urls": {
                "type": "array",
                "items": {"type": "string", "format": "uri"},
                "description": "Explicit candidate URLs to validate and return (skips live harvesting).",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "default": 5,
                "description": "Max number of candidates to return.",
            },
        },
        "additionalProperties": False,
    }
    # camelCase alias for adapters that expect it
    inputSchema: Dict[str, Any] = arguments_jsonschema

    def __init__(self, tool_config: Optional[dict] = None):
        _dbg("GenericHarvestTool.__init__ start", "tool_config:", _pp(tool_config))
        if tool_config is None:
            tool_config = {
                "name": self.name,
                "description": self.description,
                "key": "generic_harvest_tool",
                "tool_type": self.tool_type,
                "enabled": True,
                "visible": True,
            }
        super().__init__(tool_config=tool_config)

        # mirror metadata on the instance
        self.name = tool_config.get("name", self.name)
        self.description = tool_config.get("description", self.description)
        self.key = tool_config.get("key", "generic_harvest_tool")
        self.tool_type = tool_config.get("tool_type", self.tool_type)
        self.enabled = tool_config.get("enabled", True)
        self.visible = tool_config.get("visible", True)

        # expose schemas on the instance (copy to avoid accidental mutation)
        self.arguments_jsonschema = dict(self.arguments_jsonschema)
        self.inputSchema = self.arguments_jsonschema
        _dbg("GenericHarvestTool.__init__ done", "key:", self.key)

    def to_mcp_tool(self, *_: Any, **__: Any):
        """
        Return a callable carrying schema & metadata (works even if your shim is bypassed).
        NOTE: We expose a single-argument callable (arguments: Dict[str, Any]) since
        FastMCP v2 calls TypeAdapter.validate_python(arguments) by default.
        """
        _dbg("to_mcp_tool: building callable wrapper")

        def _callable(arguments: Dict[str, Any]):
            """
            Fast path for FastMCP v2: accept one 'arguments' dict.
            The server passes exactly this object to TypeAdapter.validate_python(...),
            so Pydantic won't try to treat keys like 'query'/'limit' as unexpected kwargs.
            """
            _dbg("MCP CALL START - raw arguments:", _pp(arguments))
            try:
                if not isinstance(arguments, dict):
                    _dbg("arguments is not a dict; coercing to empty dict.")
                    arguments = {}
                q = (arguments.get("query") or "").strip()
                u = arguments.get("urls") or []
                lim = int(arguments.get("limit") or 5)
                _dbg("normalized args =>", {"query": q, "urls_len": len(u) if isinstance(u, list) else "n/a", "limit": lim})
                result = self.run({"query": q, "urls": u, "limit": lim})
                _dbg("MCP CALL END - result:", _pp(result))
                return result
            except Exception as e:
                _dbg("MCP CALL EXC:", e)
                _dbg(traceback.format_exc())
                # surface a structured error back to MCP
                return {"candidates": [], "error": str(e)}

        # Attach metadata & schemas directly to callable (fixes "function has no inputSchema")
        setattr(_callable, "name", self.name)
        setattr(_callable, "description", self.description)
        setattr(_callable, "key", self.key)
        setattr(_callable, "tool_type", self.tool_type)
        setattr(_callable, "enabled", self.enabled)
        setattr(_callable, "visible", self.visible)
        setattr(_callable, "arguments_jsonschema", self.arguments_jsonschema)
        setattr(_callable, "inputSchema", self.inputSchema)

        _dbg("to_mcp_tool: attached metadata and schema")
        _dbg("to_mcp_tool: signature =>", str(inspect.signature(_callable)))
        return _callable

    # -------------------------------------------------------------------------
    # Core Logic
    # -------------------------------------------------------------------------

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        _dbg("run() begin with:", _pp(arguments))
        args = arguments or {}
        urls: List[str] = args.get("urls") or []
        query: str = args.get("query") or ""
        limit: int = int(args.get("limit") or 5)
        limit = max(1, min(limit, 50))
        _dbg("run() parsed:", {"query": query, "urls_len": len(urls) if isinstance(urls, list) else "n/a", "limit": limit})

        # explicit URLs path
        if urls:
            _dbg("run(): explicit URLs path")
            candidates: List[Dict[str, Any]] = []
            for u in urls:
                if not _looks_like_url(u):
                    _dbg("run(): skip non-url:", u)
                    continue
                cand = {
                    "name": "Candidate",
                    "url": _normalize_url(u),
                    "source": "manual",
                    "description": "",
                }
                _dbg("run(): add explicit candidate:", _pp(cand))
                candidates.append(cand)
            candidates = _dedupe_candidates(candidates)
            out = {"candidates": candidates[:limit]}
            _dbg("run(): returning explicit URLs result:", _pp(out))
            return out

        # query → run all harvesters
        q = query.strip()
        if q:
            _dbg("run(): query path")
            aggregated = _run_all_harvesters(q, limit)
            _dbg("run(): aggregated count:", len(aggregated))
            aggregated = _dedupe_candidates(aggregated)
            _dbg("run(): after dedupe:", len(aggregated))
            ranked = _rank_and_limit(aggregated, q, limit)
            out = {"candidates": ranked}
            _dbg("run(): returning ranked result:", _pp(out))
            return out

        # no inputs
        _dbg("run(): no inputs; returning empty candidates")
        return {"candidates": []}

    # -------------------------------------------------------------------------
    # Registration helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def register(server) -> None:
        """
        Class-level registration for loaders that call Class.register(server).
        We register a callable carrying schemas and metadata.
        Also: emit debug of the registered function signature and what FastMCP stores.
        """
        _dbg("class-level register() start")
        tool = GenericHarvestTool()
        fn = tool.to_mcp_tool()
        _dbg("class-level register: will add under name", tool.name, "sig:", inspect.signature(fn))
        server.add_tool(tool.name, fn)

        # Try to introspect what FastMCP actually stored
        try:
            tm = getattr(server, "tool_manager", None)
            if tm and hasattr(tm, "tools"):
                t = tm.tools.get(tool.name)
                if t and hasattr(t, "fn"):
                    _dbg("class-level register: stored fn:", t.fn)
                    _dbg("class-level register: stored sig:", inspect.signature(t.fn))
        except Exception as e:
            _dbg("class-level register: post-add introspect failed:", e)
        _dbg("class-level register() done")


# -----------------------------------------------------------------------------
# Module-level register
# -----------------------------------------------------------------------------

def register(server) -> None:
    """
    Some bootstraps expect a module-level register(server).
    Register a callable that *already carries* inputSchema so even if the
    FastMCP shim is bypassed, validation succeeds. Includes deep debug.
    """
    _dbg("module-level register() start")
    tool = GenericHarvestTool()
    fn = tool.to_mcp_tool()
    _dbg("module-level register: will add under name", tool.name, "sig:", inspect.signature(fn))
    try:
        server.add_tool(tool.name, fn)  # common pattern
    except TypeError as e:
        _dbg("module-level register: TypeError on (name, fn) path; falling back to object. err:", e)
        server.add_tool(tool)

    # Introspect what FastMCP actually stored
    try:
        tm = getattr(server, "tool_manager", None)
        if tm and hasattr(tm, "tools"):
            t = tm.tools.get(tool.name)
            if t and hasattr(t, "fn"):
                _dbg("module-level register: stored fn:", t.fn)
                _dbg("module-level register: stored sig:", inspect.signature(t.fn))
    except Exception as e:
        _dbg("module-level register: post-add introspect failed:", e)
    _dbg("module-level register() done")
