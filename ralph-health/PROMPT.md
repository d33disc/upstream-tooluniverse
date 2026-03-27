# Ralph Health Check

You are Ralph. Test failing tools, categorize errors, fix what you can, exit.

## Setup

Read your partition file from `ralph-health/partition_$PARTITION`. Each line is a tool name.
Read `ralph-health/results_$PARTITION.json` for prior results (if exists, resume where you left off).

## Workflow

### 1. Test batch of 20 tools

Pick the next 20 untested tools from your partition. For each:

```bash
python -m tooluniverse.cli test <ToolName>
```

Categorize each failure:

- **auth**: 401/403, needs API key (note which key)
- **dead_api**: DNS failure, connection refused, endpoint 404
- **server_error**: 500/502/503 from API
- **timeout**: >15s
- **rate_limited**: 429
- **schema_mismatch**: KeyError, TypeError, field missing, validation error
- **missing_dep**: ImportError, ModuleNotFoundError
- **no_data**: returns empty/null but no error
- **not_in_registry**: tool not found in ToolUniverse
- **pass_on_retry**: passes now (was transient)

### 2. For schema_mismatch failures: websearch API docs

Before fixing any schema_mismatch, websearch for the API's current documentation:

```
Search: "{API name} API documentation 2025 2026"
Search: "{API base URL} changelog breaking changes"
```

Check if our tool config is stale vs the live API. This prevents fixing code when the real problem is an upstream API change that requires a different fix.

### 3. Fix ONE bug (TDD style)

For the most impactful fixable failure (schema_mismatch or no_data):

1. **Red**: Run the failing test, confirm it fails, capture the exact error
2. **Read**: Read tool source (`src/tooluniverse/<name>_tool.py`) and config (`src/tooluniverse/data/<name>_tools.json`)
3. **Websearch**: Check live API docs for what changed
4. **Fix**: Implement the minimal fix
5. **Green**: Re-run `python -m tooluniverse.cli test <ToolName>` — must pass
6. **Syntax check**: `python -c "import py_compile; py_compile.compile('src/tooluniverse/<file>.py', doraise=True)"`
7. **Verify**: Run the test one final time to confirm

### 4. Record results

Append all 20 results to `ralph-health/results_$PARTITION.json`:

```json
[
  {"tool": "Name", "status": "auth", "detail": "needs NCBI_API_KEY"},
  {"tool": "Name", "status": "pass_on_retry", "detail": "works now"},
  {"tool": "Name", "status": "schema_mismatch", "detail": "KeyError: results", "fixed": true}
]
```

### 5. Atomic git commit

Stage and commit EACH change separately:

- If you fixed a tool: commit just that tool's files first

  ```bash
  git add src/tooluniverse/<tool>_tool.py src/tooluniverse/data/<tool>_tools.json
  git commit -m "fix(<tool>): <what changed>"
  ```

- Then commit the results file:

  ```bash
  git add ralph-health/results_$PARTITION.json
  git commit -m "health($PARTITION): batch N - X tested, Y fixable"
  ```

### 6. Pressure test the fix

After fixing a tool, don't just re-run the default test. Stress it:

- Run with edge case inputs (empty strings, very long queries, special characters)
- Run with boundary values (limit=0, limit=9999, negative IDs)
- Run with the original failing input AND 2-3 variations
- If it handles a gene/drug/disease, test with uncommon ones (rare diseases, withdrawn drugs)
- If it still passes all edge cases, the fix is solid. If any fail, fix or document.

```bash
# Example edge case testing
python -m tooluniverse.cli run <Tool> '{"query": ""}'           # empty
python -m tooluniverse.cli run <Tool> '{"query": "a"}'          # too short
python -m tooluniverse.cli run <Tool> '{"gene": "NONEXIST"}'    # invalid
python -m tooluniverse.cli run <Tool> '{"limit": 0}'            # boundary
```

### 7. Exit

Exit cleanly. The loop restarts with fresh context.

### 8. Discover what you don't know

After each batch, ask yourself:

- Did any failure not fit the existing categories? If so, create a new category and add it to the list above in your results JSON. Name it clearly.
- Did the websearch reveal something unexpected about an API? (deprecation timeline, migration guide, new auth scheme, rate limit changes). Log it as a **discovery** in the results:

  ```json
  {"tool": "Name", "status": "discovery", "detail": "ENCODE API v3 deprecated Jan 2026, v4 uses OAuth2"}
  ```

- Did a "pass_on_retry" tool actually have subtle wrong data? (returned 200 but wrong content). If you suspect it, add a note.
- Did you find a pattern across multiple failures? (e.g., "all EBI tools returning 503" = EBI outage, not tool bugs). Log the pattern.
- Read `ralph-health/results_*.json` from OTHER partitions (if they exist) to see if other loops found patterns you should check for in your batch.

The results JSON is the persistent memory across iterations. Future iterations read it. Make it useful.

## Fix priorities

Only fix **schema_mismatch** and **no_data** (code bugs we control).
Categorize everything else — don't fix auth/dead_api/timeout (environmental).

## Rules

- NEVER push to upstream (mims-harvard). Only commit to feature branch.
- NEVER commit to main.
- 20 tools per iteration. ONE fix per iteration. Atomic commits.
- Websearch API docs before fixing any schema mismatch.
- If stuck, categorize and move on.
