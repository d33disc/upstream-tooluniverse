#!/usr/bin/env python3
"""Minimal tools generator - one tool, one file."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List


def json_type_to_python(json_type: str) -> str:
    """Convert JSON type to Python type."""
    return {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list[Any]",
        "object": "dict[str, Any]",
    }.get(json_type, "Any")


def generate_tool_file(
    tool_name: str,
    tool_config: Dict[str, Any],
    output_dir: Path,
) -> Path:
    """Generate one file for one tool."""
    schema = tool_config.get("parameter", {}) or {}
    description = tool_config.get("description", f"Execute {tool_name}")
    # Wrap long descriptions
    if len(description) > 100:
        description = description[:97] + "..."
    properties = schema.get("properties", {}) or {}
    required = schema.get("required", []) or []

    # Build parameters - required first, then optional
    required_params = []
    optional_params = []
    kwargs = []
    doc_params = []
    mutable_defaults_code = []

    for name, prop in properties.items():
        py_type = json_type_to_python(prop.get("type", "string"))
        desc = prop.get("description", "")

        if name in required:
            required_params.append(f"{name}: {py_type}")
        else:
            default = prop.get("default")
            if default is not None:
                # Handle mutable defaults to avoid B006 linting error
                if isinstance(default, (list, dict)):
                    # Use None as default and handle in function body
                    optional_params.append(f"{name}: Optional[{py_type}] = None")
                    mutable_defaults_code.append(
                        ("    if {n} is None:\n" "        {n} = {d}").format(
                            n=name, d=repr(default)
                        )
                    )
                else:
                    optional_params.append(
                        f"{name}: Optional[{py_type}] = {repr(default)}"
                    )
            else:
                optional_params.append(f"{name}: Optional[{py_type}] = None")

        kwargs.append(f'"{name}": {name}')
        # Wrap long descriptions
        if len(desc) > 80:
            desc = desc[:77] + "..."
        doc_params.append(f"    {name} : {py_type}\n        {desc}")

    # Combine required and optional parameters
    params = required_params + optional_params

    params_str = ",\n    ".join(params) if params else ""
    kwargs_str = ",\n                ".join(kwargs) if kwargs else ""
    doc_params_str = "\n".join(doc_params) if doc_params else "    No parameters"
    mutable_defaults_str = (
        "\n".join(mutable_defaults_code) if mutable_defaults_code else ""
    )

    # Infer return type
    return_schema = tool_config.get("return_schema", {})
    if return_schema:
        return_type = json_type_to_python(return_schema.get("type", ""))
    else:
        return_type = "Any"

    content = f'''"""
{tool_name}

{description}
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def {tool_name}(
    {params_str}{"," if params_str else ""}
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> {return_type}:
    """
    {description}

    Parameters
    ----------
{doc_params_str}
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    {return_type}
    """
    # Handle mutable defaults to avoid B006 linting error
{mutable_defaults_str}
    return get_shared_client().run_one_function(
        {{
            "name": "{tool_name}",
            "arguments": {{
                {kwargs_str}
            }}
        }},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate
    )


__all__ = ["{tool_name}"]
'''

    output_path = output_dir / f"{tool_name}.py"
    output_path.write_text(content)
    return output_path


def generate_init(tool_names: list, output_dir: Path) -> Path:
    """Generate __init__.py with all imports."""
    imports = [f"from .{name} import {name}" for name in sorted(tool_names)]

    # Generate the content without f-string escape sequences
    all_names = ",\n    ".join(f'"{name}"' for name in sorted(tool_names))
    content = f'''"""
ToolUniverse Tools

Type-safe Python interface to {len(tool_names)} scientific tools.
Each tool is in its own module for minimal import overhead.

Usage:
    from tooluniverse.tools import ArXiv_search_papers
    result = ArXiv_search_papers(query="machine learning")
"""

# Import exceptions from main package
from tooluniverse.exceptions import *

# Import shared client utilities
from ._shared_client import get_shared_client, reset_shared_client

# Import all tools
{chr(10).join(imports)}

__all__ = [
    "get_shared_client",
    "reset_shared_client",
    {all_names}
]
'''

    init_path = output_dir / "__init__.py"
    init_path.write_text(content)
    return init_path


def _chunked(sequence: List[str], chunk_size: int) -> List[List[str]]:
    """Yield chunks of the sequence with up to chunk_size elements."""
    if chunk_size <= 0:
        return [sequence]
    return [sequence[i : i + chunk_size] for i in range(0, len(sequence), chunk_size)]


def _format_files(paths: List[str]) -> None:
    """Format files using pre-commit if available, else ruff/autoflake/black.

    Honors TOOLUNIVERSE_SKIP_FORMAT=1 to skip formatting entirely.
    """
    if not paths:
        return
    if os.getenv("TOOLUNIVERSE_SKIP_FORMAT") == "1":
        return

    pre_commit = shutil.which("pre-commit")
    if pre_commit:
        # Run pre-commit on specific files to match repo config filters
        for batch in _chunked(paths, 80):
            try:
                subprocess.run(
                    [pre_commit, "run", "--files", *batch],
                    check=False,
                )
            except Exception:
                # Best-effort; continue to fallback below
                pass
        return

    # Fallback to direct formatter CLIs in the same spirit/order as hooks
    ruff = shutil.which("ruff")
    if ruff:
        try:
            subprocess.run(
                [
                    ruff,
                    "--fix",
                    "--line-length=88",
                    "--ignore=E203",
                    *paths,
                ],
                check=False,
            )
        except Exception:
            pass

    autoflake = shutil.which("autoflake")
    if autoflake:
        try:
            subprocess.run(
                [
                    autoflake,
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    "--in-place",
                    *paths,
                ],
                check=False,
            )
        except Exception:
            pass

    black = shutil.which("black")
    if black:
        try:
            subprocess.run(
                [black, "--line-length=88", *paths],
                check=False,
            )
        except Exception:
            pass


def main(format_enabled: Optional[bool] = None) -> None:
    """Generate tools and format the generated files if enabled.

    If format_enabled is None, decide based on TOOLUNIVERSE_SKIP_FORMAT env var
    (skip when set to "1").
    """
    from tooluniverse import ToolUniverse
    from .build_optimizer import cleanup_orphaned_files, get_changed_tools

    print("🔧 Generating tools...")

    tu = ToolUniverse()
    tu.load_tools()

    output = Path("src/tooluniverse/tools")
    output.mkdir(parents=True, exist_ok=True)

    # Cleanup orphaned files
    current_tool_names = set(tu.all_tool_dict.keys())
    cleaned_count = cleanup_orphaned_files(output, current_tool_names)
    if cleaned_count > 0:
        print(f"🧹 Removed {cleaned_count} orphaned tool files")

    # Check for changes
    metadata_file = output / ".tool_metadata.json"
    new_tools, changed_tools, unchanged_tools = get_changed_tools(
        tu.all_tool_dict, metadata_file
    )

    # Only generate if there are changes
    if not new_tools and not changed_tools:
        print("✨ No changes detected, skipping generation")
        return

    print(f"🔄 Generating {len(new_tools + changed_tools)} changed tools...")
    generated_paths: List[str] = []

    # Generate only changed tools
    for i, (tool_name, tool_config) in enumerate(tu.all_tool_dict.items(), 1):
        if tool_name in new_tools or tool_name in changed_tools:
            path = generate_tool_file(tool_name, tool_config, output)
            generated_paths.append(str(path))
        if i % 50 == 0:
            print(f"  Processed {i} tools...")

    # Always regenerate __init__.py to include all tools
    init_path = generate_init(list(tu.all_tool_dict.keys()), output)
    generated_paths.append(str(init_path))

    # Determine formatting behavior
    if format_enabled is None:
        # Enabled unless explicitly opted-out via env
        format_enabled = os.getenv("TOOLUNIVERSE_SKIP_FORMAT") != "1"

    if format_enabled:
        _format_files(generated_paths)

    print(f"✅ Generated {len(generated_paths)} files in {output}")


if __name__ == "__main__":
    # Lightweight CLI to allow opting out of formatting when run directly
    import argparse

    parser = argparse.ArgumentParser(description="Generate ToolUniverse tools")
    parser.add_argument(
        "--no-format",
        action="store_true",
        help="Do not run formatters on generated files",
    )
    args = parser.parse_args()
    main(format_enabled=not args.no_format)
