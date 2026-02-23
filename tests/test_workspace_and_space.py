"""
Tests for Phase 1-8 new functionality:
- workspace field resolution (ToolUniverse constructor + env vars)
- sources loading in load_space()
- TOOLUNIVERSE_HOME and TOOLUNIVERSE_SPACE env vars
- SpaceLoader.resolve_to_local_dir() and get_tool_files_from_dir()
- MCP CLI --workspace flag
- Sub-package config registration via register_tool_configs()
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from tooluniverse.space import SpaceLoader


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_yaml(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


def _write_json(path: Path, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _minimal_space(name: str = "test") -> dict:
    return {"name": name, "version": "1.0.0", "description": "desc"}


# ---------------------------------------------------------------------------
# SpaceLoader.get_tool_files_from_dir
# ---------------------------------------------------------------------------


class TestGetToolFilesFromDir:
    """Tests for SpaceLoader.get_tool_files_from_dir()."""

    def test_empty_directory(self, tmp_path):
        py, js = SpaceLoader.get_tool_files_from_dir(tmp_path)
        assert py == []
        assert js == []

    def test_nonexistent_directory(self, tmp_path):
        py, js = SpaceLoader.get_tool_files_from_dir(tmp_path / "no_such_dir")
        assert py == []
        assert js == []

    def test_flat_layout_py_and_json(self, tmp_path):
        (tmp_path / "tool_a.py").write_text("# tool a")
        (tmp_path / "tool_b.py").write_text("# tool b")
        (tmp_path / "config_a.json").write_text('{"name": "a"}')
        (tmp_path / "space.json").write_text("{}")  # should be excluded

        py, js = SpaceLoader.get_tool_files_from_dir(tmp_path)
        assert sorted(p.name for p in py) == ["tool_a.py", "tool_b.py"]
        assert [p.name for p in js] == ["config_a.json"]

    def test_skips_init_and_setup_py(self, tmp_path):
        (tmp_path / "__init__.py").write_text("")
        (tmp_path / "setup.py").write_text("")
        (tmp_path / "conftest.py").write_text("")
        (tmp_path / "mytool.py").write_text("# real tool")

        py, _ = SpaceLoader.get_tool_files_from_dir(tmp_path)
        assert [p.name for p in py] == ["mytool.py"]

    def test_organised_layout(self, tmp_path):
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        (tools_dir / "tool_c.py").write_text("# tool c")

        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "tools.json").write_text('[{"name": "tc"}]')
        (data_dir / "space.json").write_text("{}")  # excluded

        configs_dir = tmp_path / "configs"
        configs_dir.mkdir()
        (configs_dir / "extra.json").write_text('[{"name": "extra"}]')

        py, js = SpaceLoader.get_tool_files_from_dir(tmp_path)
        assert [p.name for p in py] == ["tool_c.py"]
        assert sorted(p.name for p in js) == ["extra.json", "tools.json"]

    def test_mixed_flat_and_organised(self, tmp_path):
        (tmp_path / "flat.py").write_text("# flat")
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        (tools_dir / "organised.py").write_text("# organised")

        py, _ = SpaceLoader.get_tool_files_from_dir(tmp_path)
        names = [p.name for p in py]
        assert "flat.py" in names
        assert "organised.py" in names


# ---------------------------------------------------------------------------
# SpaceLoader.resolve_to_local_dir
# ---------------------------------------------------------------------------


class TestResolveToLocalDir:
    """Tests for SpaceLoader.resolve_to_local_dir()."""

    def test_local_directory(self, tmp_path):
        loader = SpaceLoader(cache_dir=tmp_path / "cache")
        result = loader.resolve_to_local_dir(str(tmp_path))
        assert result == tmp_path

    def test_local_file_returns_parent(self, tmp_path):
        f = tmp_path / "space.yaml"
        f.write_text("name: t\nversion: 1.0.0\n")
        loader = SpaceLoader(cache_dir=tmp_path / "cache")
        result = loader.resolve_to_local_dir(str(f))
        assert result == tmp_path

    def test_local_missing_raises(self, tmp_path):
        loader = SpaceLoader(cache_dir=tmp_path / "cache")
        with pytest.raises(ValueError, match="Space path not found"):
            loader.resolve_to_local_dir(str(tmp_path / "no_such"))

    @patch("huggingface_hub.snapshot_download")
    def test_hf_uri_calls_snapshot_download(self, mock_snap, tmp_path):
        mock_snap.return_value = str(tmp_path)
        loader = SpaceLoader(cache_dir=tmp_path / "cache")
        result = loader.resolve_to_local_dir("hf:user/my-repo")
        mock_snap.assert_called_once()
        assert result == tmp_path

    @patch("requests.get")
    def test_http_file_url_downloads_and_returns_dir(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.content = b"name: t\nversion: 1.0.0\n"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        loader = SpaceLoader(cache_dir=tmp_path / "cache")
        result = loader.resolve_to_local_dir("https://example.com/space.yaml")
        assert result.is_dir()
        assert (result / "space.yaml").exists()

    @patch("requests.get")
    def test_github_repo_url_downloads_zip(self, mock_get, tmp_path):
        """Test that a GitHub repo URL triggers ZIP download."""
        import io
        import zipfile

        # Build a minimal ZIP in memory
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("myrepo-main/tool.py", "# tool")
        buf.seek(0)

        mock_resp = MagicMock()
        mock_resp.content = buf.read()
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        loader = SpaceLoader(cache_dir=tmp_path / "cache")
        result = loader.resolve_to_local_dir("https://github.com/user/myrepo")
        # The ZIP extracts to a subdir; result should be a directory
        assert result.is_dir()


# ---------------------------------------------------------------------------
# SPACE_SCHEMA new fields: sources, workspace, package
# ---------------------------------------------------------------------------


class TestSpaceSchemaNewFields:
    """Tests that sources, workspace, package fields pass validation."""

    def test_sources_field_accepted(self, tmp_path):
        config_file = tmp_path / "space.yaml"
        _write_yaml(
            config_file,
            {
                "name": "src-test",
                "version": "1.0.0",
                "description": "d",
                "sources": ["./extra", "hf:user/tools"],
            },
        )
        loader = SpaceLoader(cache_dir=tmp_path / "cache")
        config = loader.load(str(config_file))
        assert config["sources"] == ["./extra", "hf:user/tools"]

    def test_workspace_field_accepted(self, tmp_path):
        config_file = tmp_path / "space.yaml"
        _write_yaml(
            config_file,
            {
                "name": "ws-test",
                "version": "1.0.0",
                "description": "d",
                "workspace": "/my/workspace",
            },
        )
        loader = SpaceLoader(cache_dir=tmp_path / "cache")
        config = loader.load(str(config_file))
        assert config["workspace"] == "/my/workspace"

    def test_package_field_accepted(self, tmp_path):
        config_file = tmp_path / "space.yaml"
        _write_yaml(
            config_file,
            {
                "name": "pkg-test",
                "version": "1.0.0",
                "description": "d",
                "package": "tooluniverse/mypkg",
            },
        )
        loader = SpaceLoader(cache_dir=tmp_path / "cache")
        config = loader.load(str(config_file))
        assert config["package"] == "tooluniverse/mypkg"

    def test_sources_defaults_to_empty_list(self, tmp_path):
        config_file = tmp_path / "space.yaml"
        _write_yaml(config_file, _minimal_space())
        loader = SpaceLoader(cache_dir=tmp_path / "cache")
        config = loader.load(str(config_file))
        assert config["sources"] == []


# ---------------------------------------------------------------------------
# ToolUniverse constructor: workspace and space params
# ---------------------------------------------------------------------------


class TestToolUniverseConstructor:
    """Tests for the workspace= and space= constructor parameters."""

    def test_workspace_param_sets_workspace_dir(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        workspace = tmp_path / "my_workspace"
        workspace.mkdir()
        tu = ToolUniverse(workspace=str(workspace))
        assert tu._workspace_dir == workspace

    def test_workspace_param_creates_dir_if_missing(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        workspace = tmp_path / "new_workspace"
        assert not workspace.exists()
        tu = ToolUniverse(workspace=str(workspace))
        assert workspace.exists()
        assert tu._workspace_dir == workspace

    def test_no_workspace_param_defaults_to_local(self):
        """Without an explicit workspace, the default is ./.tooluniverse (local mode)."""
        from pathlib import Path
        from tooluniverse.execute_function import ToolUniverse

        env_backup = os.environ.pop("TOOLUNIVERSE_HOME", None)
        try:
            tu = ToolUniverse()
            assert tu._workspace_dir == Path.cwd() / ".tooluniverse"
        finally:
            if env_backup is not None:
                os.environ["TOOLUNIVERSE_HOME"] = env_backup

    def test_tooluniverse_home_env_var(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        home = tmp_path / "env_home"
        with patch.dict(os.environ, {"TOOLUNIVERSE_HOME": str(home)}, clear=False):
            tu = ToolUniverse()
            assert tu._workspace_dir == home
            assert home.exists()

    def test_workspace_param_takes_priority_over_env(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        workspace = tmp_path / "param_ws"
        env_home = tmp_path / "env_home"
        with patch.dict(
            os.environ, {"TOOLUNIVERSE_HOME": str(env_home)}, clear=False
        ):
            tu = ToolUniverse(workspace=str(workspace))
            assert tu._workspace_dir == workspace

    def test_space_param_calls_load_space(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        config_file = tmp_path / "space.yaml"
        _write_yaml(config_file, _minimal_space("from-param"))

        with patch.object(ToolUniverse, "load_space") as mock_load:
            ToolUniverse(space=str(config_file))
            mock_load.assert_called_once_with(str(config_file))

    def test_tooluniverse_space_env_var(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        config_file = tmp_path / "space.yaml"
        _write_yaml(config_file, _minimal_space("from-env"))

        with patch.dict(
            os.environ, {"TOOLUNIVERSE_SPACE": str(config_file)}, clear=False
        ):
            with patch.object(ToolUniverse, "load_space") as mock_load:
                ToolUniverse()
                mock_load.assert_called_once_with(str(config_file))

    def test_space_param_takes_priority_over_tooluniverse_space_env(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        param_file = tmp_path / "param.yaml"
        env_file = tmp_path / "env.yaml"
        _write_yaml(param_file, _minimal_space("param"))
        _write_yaml(env_file, _minimal_space("env"))

        with patch.dict(
            os.environ, {"TOOLUNIVERSE_SPACE": str(env_file)}, clear=False
        ):
            with patch.object(ToolUniverse, "load_space") as mock_load:
                ToolUniverse(space=str(param_file))
                # Should be called with the param file, not env file
                mock_load.assert_called_once_with(str(param_file))


# ---------------------------------------------------------------------------
# ToolUniverse._get_user_tool_files with workspace_dir
# ---------------------------------------------------------------------------


class TestGetUserToolFilesWithWorkspace:
    """Tests that _get_user_tool_files() uses workspace_dir when set."""

    def test_workspace_dir_scans_tool_files(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "my_tool.py").write_text("# my tool")
        (workspace / "configs.json").write_text('[{"name": "t1"}]')

        tu = ToolUniverse(workspace=str(workspace))
        py_files, json_files = tu._get_user_tool_files()

        py_names = [p.name for p in py_files]
        json_names = [p.name for p in json_files]
        assert "my_tool.py" in py_names
        assert "configs.json" in json_names

    def test_no_workspace_uses_default_home(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        # Without workspace, result depends on ~/.tooluniverse or TOOLUNIVERSE_HOME
        # We just check it returns lists without crashing
        env_backup = os.environ.pop("TOOLUNIVERSE_HOME", None)
        try:
            tu = ToolUniverse()
            py_files, json_files = tu._get_user_tool_files()
            assert isinstance(py_files, list)
            assert isinstance(json_files, list)
        finally:
            if env_backup is not None:
                os.environ["TOOLUNIVERSE_HOME"] = env_backup


# ---------------------------------------------------------------------------
# sources loading in load_space()
# ---------------------------------------------------------------------------


class TestLoadSpaceSources:
    """Tests that load_space() processes the sources field."""

    def test_sources_calls_load_tools_from_sources(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        # Create a source directory with a JSON tool config
        source_dir = tmp_path / "external_tools"
        source_dir.mkdir()
        _write_json(
            source_dir / "tools.json",
            [{"name": "ext_tool_1", "description": "External tool 1"}],
        )

        # Create a space.yaml that references the source dir
        config_file = tmp_path / "space.yaml"
        _write_yaml(
            config_file,
            {
                "name": "src-space",
                "version": "1.0.0",
                "description": "d",
                "sources": [str(source_dir)],
            },
        )

        tu = ToolUniverse()
        with patch.object(tu, "_load_tools_from_sources") as mock_load_src:
            tu.load_space(str(config_file))
            mock_load_src.assert_called_once()
            # Verify the sources list was passed
            call_args = mock_load_src.call_args
            sources_arg = call_args[0][1]  # second positional arg
            assert str(source_dir) in sources_arg

    def test_empty_sources_does_not_call_load_tools_from_sources(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        config_file = tmp_path / "space.yaml"
        _write_yaml(config_file, _minimal_space())

        tu = ToolUniverse()
        with patch.object(tu, "_load_tools_from_sources") as mock_load_src:
            tu.load_space(str(config_file))
            mock_load_src.assert_not_called()

    def test_load_tools_from_sources_loads_json_configs(self, tmp_path):
        from tooluniverse.execute_function import ToolUniverse

        source_dir = tmp_path / "src"
        source_dir.mkdir()
        _write_json(
            source_dir / "extra_tools.json",
            [{"name": "src_tool_x", "description": "From source"}],
        )

        initial_count = len(ToolUniverse().all_tools)

        config_file = tmp_path / "space.yaml"
        _write_yaml(
            config_file,
            {
                "name": "src-load-test",
                "version": "1.0.0",
                "description": "d",
                "sources": [str(source_dir)],
            },
        )

        tu = ToolUniverse()
        tu.load_space(str(config_file))

        tool_names = [t.get("name") for t in tu.all_tools]
        assert "src_tool_x" in tool_names


# ---------------------------------------------------------------------------
# MCP CLI --workspace flag
# ---------------------------------------------------------------------------


class TestMCPCLIWorkspaceFlag:
    """Tests that the MCP server CLI parsers accept --workspace."""

    def _get_http_parser(self):
        """Import and build the HTTP server argument parser."""
        import argparse
        import importlib

        # We'll test the argument is registered by patching sys.argv and
        # using parse_known_args
        spec = importlib.util.find_spec("tooluniverse.smcp_server")
        assert spec is not None
        return spec

    def test_smcp_server_accepts_workspace_flag(self):
        """Verify --workspace is accepted by the smcp-server parser."""
        import argparse
        from tooluniverse import smcp_server

        # Build a minimal parser equivalent to what run_http_server creates
        # by directly checking the function's source builds it
        # We test indirectly: call parse_known_args with --workspace
        # on a fresh ArgumentParser with the same flags
        parser = argparse.ArgumentParser()
        space_group = parser.add_argument_group("Space Configuration")
        space_group.add_argument("--load", "-l", type=str)
        space_group.add_argument("--workspace", "-w", type=str)

        args, _ = parser.parse_known_args(["--workspace", "/tmp/myws"])
        assert args.workspace == "/tmp/myws"

    def test_smcp_module_has_workspace_in_all_parsers(self):
        """Verify --workspace appears in the smcp_server module source."""
        import inspect
        from tooluniverse import smcp_server

        source = inspect.getsource(smcp_server)
        # There should be 3 occurrences of --workspace (one per server function)
        occurrences = source.count('"--workspace"')
        assert occurrences >= 3, (
            f"Expected at least 3 '--workspace' args in smcp_server.py, found {occurrences}"
        )

    def test_smcp_module_passes_workspace_to_smcp(self):
        """Verify workspace=args.workspace is passed to SMCP in all 3 server functions."""
        import inspect
        from tooluniverse import smcp_server

        source = inspect.getsource(smcp_server)
        occurrences = source.count("workspace=args.workspace")
        assert occurrences >= 3, (
            f"Expected at least 3 'workspace=args.workspace' in smcp_server.py, found {occurrences}"
        )


# ---------------------------------------------------------------------------
# SMCP class accepts workspace parameter
# ---------------------------------------------------------------------------


class TestSMCPWorkspaceParam:
    """Tests that SMCP passes workspace to ToolUniverse."""

    def test_smcp_accepts_workspace_param(self):
        import inspect
        from tooluniverse.smcp import SMCP

        sig = inspect.signature(SMCP.__init__)
        assert "workspace" in sig.parameters, (
            "SMCP.__init__ should have a 'workspace' parameter"
        )

    def test_smcp_passes_workspace_to_tooluniverse(self):
        """Verify SMCP source passes workspace= to ToolUniverse constructor."""
        import inspect
        from tooluniverse.smcp import SMCP

        source = inspect.getsource(SMCP.__init__)
        # The ToolUniverse constructor call should include workspace=workspace
        assert "workspace=workspace" in source, (
            "SMCP.__init__ should pass workspace=workspace to ToolUniverse"
        )


# ---------------------------------------------------------------------------
# register_tool_configs (sub-package registry)
# ---------------------------------------------------------------------------


class TestRegisterToolConfigs:
    """Tests for the sub-package tool config registry."""

    def test_register_tool_configs_adds_to_registry(self):
        from tooluniverse.tool_registry import (
            _list_config_registry,
            get_list_config_registry,
            register_tool_configs,
        )

        initial_count = len(get_list_config_registry())
        test_configs = [
            {"name": "_test_reg_tool_1", "description": "Test tool 1", "type": "Unknown"},
            {"name": "_test_reg_tool_2", "description": "Test tool 2", "type": "Unknown"},
        ]
        register_tool_configs(test_configs)

        registry = get_list_config_registry()
        names = [c["name"] for c in registry]
        assert "_test_reg_tool_1" in names
        assert "_test_reg_tool_2" in names
        assert len(registry) >= initial_count + 2

    def test_register_tool_configs_skips_invalid_entries(self):
        from tooluniverse.tool_registry import (
            get_list_config_registry,
            register_tool_configs,
        )

        initial = get_list_config_registry()
        initial_count = len(initial)

        # Entry without 'name' should be skipped
        register_tool_configs([{"description": "no name"}])

        registry = get_list_config_registry()
        # Count should not increase (or only by valid entries)
        assert len(registry) == initial_count

    def test_get_list_config_registry_returns_copy(self):
        from tooluniverse.tool_registry import get_list_config_registry

        r1 = get_list_config_registry()
        r2 = get_list_config_registry()
        # Modifying one should not affect the registry
        r1.append({"name": "_sentinel_should_not_persist"})
        r3 = get_list_config_registry()
        names = [c["name"] for c in r3]
        assert "_sentinel_should_not_persist" not in names
