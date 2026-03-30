"""Run each tool missing a return_schema, infer schema from real output, write it back."""

import json
import subprocess
import sys
from pathlib import Path


def infer_schema(obj: object, depth: int = 0, max_depth: int = 3) -> dict:
    """Infer JSON Schema from a Python object."""
    if depth >= max_depth:
        return {}
    if obj is None:
        return {"type": "null"}
    if isinstance(obj, bool):
        return {"type": "boolean"}
    if isinstance(obj, int):
        return {"type": "integer"}
    if isinstance(obj, float):
        return {"type": "number"}
    if isinstance(obj, str):
        return {"type": "string"}
    if isinstance(obj, list):
        if not obj:
            return {"type": "array", "items": {}}
        # Infer from first item
        return {"type": "array", "items": infer_schema(obj[0], depth + 1, max_depth)}
    if isinstance(obj, dict):
        props = {}
        for k, v in obj.items():
            props[k] = infer_schema(v, depth + 1, max_depth)
        return {"type": "object", "properties": props}
    return {"type": "string"}


def run_tool(name: str, args: str) -> dict | None:
    """Run a tool via CLI and return parsed output."""
    try:
        r = subprocess.run(
            ["python", "-m", "tooluniverse.cli", "run", name, args],
            capture_output=True,
            text=True,
            timeout=45,
        )
        if r.returncode != 0:
            return None
        out = r.stdout.strip()
        if not out:
            return None
        return json.loads(out)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def main() -> None:
    # Load all tools
    Path("src/tooluniverse/data")
    all_partitions = list(Path("ralph-schemas-v2").glob("partition_*.json"))

    tools = []
    for p in sorted(all_partitions):
        tools.extend(json.loads(p.read_text()))

    print(f"Processing {len(tools)} tools...")

    # Fallback examples for tools without test_examples
    fallbacks = {
        "kegg_list_organisms": '{"keyword": "human"}',
        "PlantReactome_list_species": "{}",
        "Bgee_list_species": "{}",
        "OncoTree_list_tissues": "{}",
    }

    done = 0
    skip = 0
    errors: list[str] = []

    for tool in tools:
        name = tool["name"]
        src = Path(tool["source_file"])
        args = tool.get("example", "") or fallbacks.get(name, "")

        if not args:
            print(f"  SKIP {name} — no example and no fallback")
            skip += 1
            errors.append(f"{name}: no example")
            continue

        print(f"  Running {name}...", end=" ", flush=True)
        output = run_tool(name, args)

        if output is None:
            print("FAIL (error/timeout)")
            skip += 1
            errors.append(f"{name}: error or timeout")
            continue

        # Extract the actual data payload
        # Tools typically return {"status": "success", "data": {...}} or just the data
        data = output.get("data", output) if isinstance(output, dict) else output

        schema = infer_schema(data)
        if not schema or schema == {"type": "null"}:
            print("SKIP (empty output)")
            skip += 1
            errors.append(f"{name}: empty output")
            continue

        # Write schema back to source JSON
        if not src.exists():
            print(f"SKIP (source file not found: {src})")
            skip += 1
            continue

        tool_data = json.loads(src.read_text())
        updated = False
        for t in tool_data:
            if t.get("name") == name:
                t["return_schema"] = schema
                updated = True
                break

        if updated:
            src.write_text(json.dumps(tool_data, indent=2, ensure_ascii=False) + "\n")
            n_fields = len(schema.get("properties", {}))
            print(f"DONE ({n_fields} fields)")
            done += 1
        else:
            print(f"SKIP (tool not found in {src.name})")
            skip += 1

    print(f"\nResults: {done} written, {skip} skipped")
    if errors:
        print("Errors:")
        for e in errors:
            print(f"  {e}")


if __name__ == "__main__":
    main()
