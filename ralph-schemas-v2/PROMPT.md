# Ralph Schema Loop v2: Remaining 36 return_schemas

You are Ralph. Run tools, capture real output, write correct return_schemas.

These are the hard cases — tools that failed, timed out, or lacked examples in v1.

## Commands

```bash
source .venv/bin/activate
python -m tooluniverse.cli run <Tool> '<json_args>'
python -m tooluniverse.cli info <Tool>
```

## Workflow

1. Read your partition file at `ralph-schemas-v2/partition_<ID>.json`
2. Read `ralph-schemas-v2/progress_<ID>.txt` to see what's done
3. For each unprocessed tool:
   a. Run `info` to check current state and parameter schema
   b. If the tool has a test example in the partition file, use it
   c. If the example field is empty, construct a minimal valid call from the parameter schema
   d. Run the tool. If it times out (>30s), try with smaller/simpler args
   e. If the tool returns data, write a return_schema matching the ACTUAL output
   f. If the tool returns an image/binary (e.g. PubChem 2D image), use `{"type": "string", "format": "base64", "description": "..."}`
   g. If the tool consistently errors after 2 attempts, log as SKIP with the error
   h. Edit the source JSON file and add the return_schema
   i. Validate JSON: `python -c "import json; json.load(open('src/tooluniverse/data/<file>.json'))"`
   j. Log result to progress file
4. Process ALL tools in your partition. Commit when done. Exit.

## Schema Format

JSON Schema draft-07. Describe top 2 levels minimum:

```json
{
  "type": "object",
  "properties": {
    "key": {"type": "string", "description": "what this field contains"}
  }
}
```

For arrays: `{"type": "array", "items": {"type": "object", "properties": {...}}}`
For simple returns: `{"type": "string"}` or `{"type": "number"}`
For binary/images: `{"type": "string", "format": "base64"}`

## Special Cases

- **OmniPath tools**: These return TSV-like tabular data. Run the tool and inspect the actual JSON structure returned by the CLI wrapper.
- **Tools without examples**: Check `info` output for parameter schema, construct minimal valid args.
- **OncoKB**: May require API key. If auth fails, SKIP with note.
- **GEO/ENCODE**: May return large results. Use small queries (limit=1 or similar).

## Progress Format

```
[DONE] ToolName — schema written (N fields)
[SKIP] ToolName — reason (auth required/service down/no data)
```

## Rules

- NEVER commit broken JSON. Validate after every edit.
- NEVER guess schemas. Run the tool. Write what you see.
- Process ALL tools in your partition before exiting.
- Use `--config pyproject.toml` for any ruff commands.
