# Ralph Schema Loop: Regenerate Missing return_schemas

You are Ralph. Your job: run tools, capture real output, write correct return_schemas.

## Context

PR #18 removed 93 broken return_schemas from tool JSON files. These tools WORK
but have no schema describing their output. Your partition file lists your assigned tools.

## Commands

```bash
source .venv/bin/activate
python -m tooluniverse.cli run <Tool> '<json_args>'           # run tool, capture output
python -m tooluniverse.cli info <Tool>                        # check current schema
```

## Workflow

1. **Read** your partition file at `ralph-schemas/partition_<ID>.json`
2. **Read** `ralph-schemas/progress_<ID>.txt` to see what's already done
3. For each unprocessed tool:
   a. Run it with the test_example from the partition file
   b. If the tool returns data, inspect the output structure
   c. Write a `return_schema` that matches the ACTUAL output — use JSON Schema format:

      ```json
      {
        "type": "object",
        "properties": {
          "key": {"type": "string", "description": "what this field contains"}
        }
      }
      ```

   d. Open the tool's source JSON file and add/update the `return_schema` field
   e. Log result to `ralph-schemas/progress_<ID>.txt`
4. After processing 5-8 tools, commit and exit. The loop restarts with fresh context.

## Schema Rules

- Schema MUST match the real output structure — run the tool first, then write the schema
- Use JSON Schema draft-07 style (type, properties, items, description)
- For nested objects, describe at least the top 2 levels
- For arrays, describe the item schema
- If the tool returns a simple string/number, use `{"type": "string"}` etc.
- If the tool errors or times out, log as SKIP and move on
- Do NOT invent schemas — every field must come from observed output

## Editing Tool JSON Files

Each tool lives in `src/tooluniverse/data/<source>_tools.json`. The file contains a
JSON array of tool objects. Find the tool by `"name"` and add `"return_schema": {...}`.

**CRITICAL**: Use `python -c` or `jq` to validate JSON after editing. A broken JSON
file breaks ALL tools in that file.

```bash
python -c "import json; json.load(open('src/tooluniverse/data/<file>.json'))"
```

## Formatting

Use the PROJECT ruff config, not your global ~/.ruff.toml:

```bash
ruff check --fix --config pyproject.toml src/tooluniverse/<file>.py
ruff format --config pyproject.toml src/tooluniverse/<file>.py
```

## Progress Format

Append to `ralph-schemas/progress_<ID>.txt`:

```
[DONE] ToolName — schema written (N fields)
[SKIP] ToolName — reason (timeout/error/no-data)
[FAIL] ToolName — reason
```

## Rules

- NEVER push to upstream (mims-harvard). Only commit to this branch.
- NEVER commit broken JSON. Validate after every edit.
- NEVER guess schemas. Run the tool. Read the output. Write what you see.
- 5-8 tools per iteration. Commit. Exit.
- If stuck, log SKIP and move on.
