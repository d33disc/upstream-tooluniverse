"""Tests for PackageTool — full coverage, anchored on a real regression.

Real bug (the reason this file exists): some valid PyPI packages (e.g. cftime)
return ``"project_urls": null``. ``info.get("project_urls", {})`` returns ``None``
(the key exists with a null value, so the default is NOT used), and
``None.get("Documentation")`` raised ``'NoneType' object has no attribute 'get'``.
PyPI returns valid data → ours to fix. Fix: ``(info.get("project_urls") or {})``.

Foreman-authored, frozen: a fix may edit package_tool.py only, never this test.
The suite also drives package_tool.py to 100% line coverage (non-negotiable gate).
"""

import json
from unittest.mock import MagicMock, patch

import requests

from tooluniverse.package_tool import PackageTool


def _tool(pkg="cftime", local_info=None):
    cfg = {"package_name": pkg, "pypi_timeout": 5}
    if local_info is not None:
        cfg["local_info"] = local_info
    return PackageTool(cfg)


def _pypi_resp(info, last_serial=12345):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"info": info, "last_serial": last_serial}
    return resp


# --- the regression: project_urls is an explicit JSON null -------------------
@patch("tooluniverse.package_tool.requests.get")
def test_pypi_null_project_urls_does_not_crash(mock_get):
    mock_get.return_value = _pypi_resp(
        {
            "name": "cftime",
            "summary": "Time-handling functionality from netcdf4-python",
            "version": "1.6.4",
            "project_urls": None,  # <-- the crash trigger
            "keywords": "",
        }
    )
    result = _tool().run({"source": "pypi", "include_examples": False})
    assert result["package_name"] == "cftime"
    assert result["documentation"] == ""
    assert result["repository"] == ""
    assert result["source"] == "pypi"


# --- pypi success + full local merge + default examples ----------------------
@patch("tooluniverse.package_tool.requests.get")
def test_pypi_success_with_local_merge_and_default_examples(mock_get):
    mock_get.return_value = _pypi_resp(
        {
            "name": "widget",
            "summary": "short",
            "version": "2.0",
            "project_urls": {"Source": "https://src"},  # no Repository/Documentation
            "keywords": "a,b",
            "classifiers": ["Programming Language :: Python :: 3"],
        }
    )
    local = {
        "category": "Sci",
        "import_name": "widget",
        "popularity": 99,
        "description": "a much longer local description that should override summary",
        "documentation": "https://local-docs",
        "installation": {
            "pip": "pip install widget",
            "conda": "conda install widget",
            "additional": {"brew": "brew install widget"},
        },
    }
    result = _tool("widget", local).run(
        {}
    )  # default source=auto, include_examples=True
    assert result["repository"] == "https://src"  # Source fallback used
    assert result["documentation"] == "https://local-docs"  # local doc fallback
    assert result["description"].startswith("a much longer")  # local override
    assert result["category"] == "Sci" and result["popularity"] == 99
    assert result["keywords"] == ["a", "b"]
    assert result["installation"]["additional"]["brew"] == "brew install widget"
    assert "import widget" in result["usage_example"]  # default usage example
    assert any("Install the package" in s for s in result["quick_start"])


# --- source=local with no local info -> error path ---------------------------
def test_local_source_without_local_info_returns_error():
    result = _tool("nope").run({"source": "local"})
    assert result["status"] == "error"
    assert "No local information" in result["error"]


# --- source=pypi, network error -> outer error handler -----------------------
@patch("tooluniverse.package_tool.requests.get")
def test_pypi_request_exception_returns_error(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("boom")
    result = _tool().run({"source": "pypi"})
    assert result["status"] == "error"
    assert "Failed to get package information" in result["error"]


# --- source=pypi, bad JSON -> parse error -> outer error handler -------------
@patch("tooluniverse.package_tool.requests.get")
def test_pypi_json_decode_error_returns_error(mock_get):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.side_effect = json.JSONDecodeError("bad", "doc", 0)
    mock_get.return_value = resp
    result = _tool().run({"source": "pypi"})
    assert result["status"] == "error"


# --- auto: pypi fails -> fallback to local, with local examples --------------
@patch("tooluniverse.package_tool.requests.get")
def test_auto_falls_back_to_local_with_local_examples(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("down")
    local = {
        "name": "pkg",
        "description": "desc",
        "usage_example": "import pkg  # local",
        "quick_start": ["step one"],
        "installation": {
            "pip": "pip install pkg",
            "conda": "conda install pkg",
            "additional": {"brew": "brew install pkg"},
        },
    }
    result = _tool("pkg", local).run({})  # auto -> pypi fails -> local
    assert result["source"] == "local"
    assert result["usage_example"] == "import pkg  # local"
    assert result["quick_start"] == ["step one"]
    # local path flattens 'additional' via _get_installation_instructions
    assert result["installation"]["brew"] == "brew install pkg"
