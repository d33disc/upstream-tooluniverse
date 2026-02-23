# Troubleshooting ToolUniverse Setup

When something fails, always provide the **exact copy-paste fix command** — don't just say "check the logs."

## Issue 1: Python Version Incompatibility

**Symptom**: Error containing `requires-python = ">=3.10"` or `Python 3.9 is not supported`

**Fix**:
```bash
brew install python@3.12        # macOS
# or: sudo apt install python3.12  # Ubuntu/Debian
python3.12 -m pip install tooluniverse
```

## Issue 2: uvx or uv Not Found

**Symptom**: `uvx: command not found` or `uv: command not found`

**Fix**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc 2>/dev/null || source ~/.bashrc 2>/dev/null
uvx --version   # verify it worked
```

## Issue 3: Context Window Overflow

**Symptom**: MCP server loads but the client becomes very slow, or gives "context too large" errors

**Note**: Compact mode is already the default — the `tooluniverse` entry point enables it automatically. If still hitting context limits:
```json
"args": ["--refresh", "tooluniverse", "--tool-categories", "uniprot,chembl,pubmed"]
```
Restart the app after editing.

## Issue 4: Import Errors for Specific Tools

**Symptom**: Tool fails with `ModuleNotFoundError: No module named 'rdkit'` (or similar)

**Fix**:
```bash
pip install tooluniverse[all]
# Or the specific extra needed:
# pip install tooluniverse[visualization]   # rdkit, py3Dmol
# pip install tooluniverse[singlecell]       # cellxgene
# pip install tooluniverse[ml,embedding]     # sentence-transformers, admet-ai
```

## Issue 5: MCP Server Won't Start

**Symptom**: No tooluniverse server in client's server list, "Failed to spawn process", "ENOENT", "command not found"

**#1 most common cause — GUI apps (Claude Desktop, Windsurf) don't inherit shell PATH.**

**Option A — Homebrew (macOS, recommended, permanent):**
```bash
brew install uv
# Then restart the app — can now use "uvx" everywhere, no absolute path needed
```

**Option B — Symlink (macOS/Linux, permanent):**
```bash
sudo ln -sf "$(which uvx)" /usr/local/bin/uvx   # Intel Mac / Linux
# OR for Apple Silicon Mac:
sudo ln -sf "$(which uvx)" /opt/homebrew/bin/uvx
```

**Option C — Absolute path (all platforms, quick fix):**
```bash
which uvx   # macOS/Linux → e.g. /opt/homebrew/bin/uvx or /Users/you/.local/bin/uvx
where uvx   # Windows
```
Use that full path as `"command"` in your config instead of `"uvx"`.

**Full diagnostic chain — run these in order:**
```bash
# 1. Can uvx find and run it?
uvx tooluniverse --help

# 2. Does it start without errors? (Ctrl+C to stop)
uvx tooluniverse

# 3. Is the config file valid JSON?
python3 -m json.tool ~/.cursor/mcp.json   # replace path for your client

# 4. View the client's MCP logs
tail -50 ~/Library/Logs/Claude/mcp*.log 2>/dev/null        # Claude Desktop (macOS)
tail -50 ~/Library/Application\ Support/Cursor/logs/*.log  # Cursor (macOS)
```

Fix based on where the chain breaks. Other common causes: trailing commas in JSON, wrong config file path.

## Issue 6: API Key Errors (401/403)

**Symptom**: Tool returns `"unauthorized"`, `"forbidden"`, or `"invalid API key"`

**Diagnostic**:
```bash
echo $NCBI_API_KEY    # replace with the failing key name
```

**Common fixes**:
- Keys must be in the `"env"` block in your MCP config file (not a `.env` file the app doesn't load):
  ```json
  "env": { "PYTHONIOENCODING": "utf-8", "NCBI_API_KEY": "your_key_here" }
  ```
- Wrong key name: variable must match exactly (e.g., `ONCOKB_API_TOKEN` not `ONCOKB_API_KEY`)
- Restart required after editing the config file
- Free tier pending: DisGeNET and OMIM may take 24–48h for account approval

## Issue 7: Upgrading ToolUniverse

**Symptom**: User wants a newer version, or tools are missing / behavior is outdated

The recommended config uses `"--refresh"` which auto-updates on every launch. If the user's config doesn't have it:
```json
"args": ["--refresh", "tooluniverse"]
```

To upgrade immediately:
```bash
uv cache clean tooluniverse   # clears uvx cache, then restart the MCP client
```

To pin a specific version:
```json
"args": ["tooluniverse==1.0.19"]
```

For pip users:
```bash
pip install --upgrade tooluniverse
```

## Still Stuck?

Run `uvx tooluniverse --help` and share the output. Then open a GitHub issue at https://github.com/mims-harvard/ToolUniverse/issues or email [Shanghua Gao](mailto:shanghuagao@gmail.com).
