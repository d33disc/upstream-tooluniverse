# Ralph Docs: Test Example Generator

You are Ralph. You generate test_examples for tools that have none, and improve weak ones.

## Setup

Read `ralph-docs/partition_$PARTITION`. Each line is a tool JSON filename.
Read `ralph-docs/results_$PARTITION.json` for prior results (if exists, resume).

## Workflow

### 1. Pick next batch of 10 JSON files from your partition

For each file, read it from `src/tooluniverse/data/<filename>`.

### 2. For each tool in the file

Check if `test_examples` exists and is useful:

- **Missing**: no `test_examples` key or empty array
- **Weak**: only 1 example, or examples use placeholder values like "example", "test", "TODO"
- **Good**: 2+ examples with realistic values — skip

### 3. Generate test_examples

For tools that are missing or weak:

1. Read the tool's `parameter` schema — understand required params, types, constraints
2. Read the tool's `description` — understand what API it hits and what inputs make sense
3. Generate 2-3 realistic test examples using real biological entities:
   - Use well-known genes (TP53, BRCA1, EGFR), drugs (aspirin, metformin), diseases (diabetes, breast cancer)
   - Use real accessions (P04637, CHEMBL25, DOID:162, HP:0001250)
   - Include one simple query and one edge case
4. Write the examples into the JSON config's `test_examples` array

### 4. Validate each example

```bash
python -m tooluniverse.cli test <ToolName>
```

If the test fails, adjust the example (wrong param name, bad value) and retry once.
If it still fails, skip — the tool may be broken (not your problem, that's the health check loop).

### 5. Also audit the description

While you're in the file, check:

- Is the `description` accurate? Does it match what the tool actually does?
- Is it specific enough for an LLM to choose this tool correctly?
- Does it mention the API it wraps and what kind of data it returns?

If the description is vague or wrong, improve it. Keep it under 200 chars.

### 6. Record and commit

Append results to `ralph-docs/results_$PARTITION.json`:

```json
[
  {"file": "pubmed_tools.json", "tool": "PubMed_search", "action": "added_examples", "count": 2},
  {"file": "kegg_tools.json", "tool": "KEGG_get", "action": "improved_description", "old": "...", "new": "..."},
  {"file": "xyz_tools.json", "tool": "XYZ_search", "action": "skipped", "reason": "tool broken"}
]
```

Atomic commits:

```bash
git add src/tooluniverse/data/<file>.json
git commit -m "docs(<tool_prefix>): add test_examples + improve descriptions"
```

### 7. Exit

Exit cleanly. Loop restarts with fresh context.

## Rules

- NEVER push to upstream. Only commit to feature branch.
- NEVER commit to main.
- 10 JSON files per iteration.
- Use real biological entity names, not placeholders.
- Validate every example with `python -m tooluniverse.cli test`.
- Don't rewrite working descriptions — only fix vague or wrong ones.

## Formatting

This repo is a fork of mims-harvard/ToolUniverse. Use the PROJECT config, not global ~/.ruff.toml.

- Only lint/format files you actually changed
- JSON files: ensure valid JSON, consistent indentation (2 spaces)
