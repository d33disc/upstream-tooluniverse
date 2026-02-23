---
name: setup-tooluniverse
description: Install and configure ToolUniverse with MCP integration for any AI coding client (Cursor, Claude Desktop, Windsurf, VS Code, Codex, Gemini CLI, Trae, Cline, Antigravity, OpenCode, etc.). Covers uv/uvx setup, MCP configuration, API key walkthrough, skill installation, and upgrading. Use when setting up ToolUniverse, configuring MCP servers, troubleshooting installation issues, upgrading versions, or when user mentions installing ToolUniverse or setting up scientific tools.
---

# Setup ToolUniverse

Guide the user step-by-step through setting up ToolUniverse with MCP (Model Context Protocol) integration.

## Agent Behavior

**Be friendly, conversational, and interactive.** This is a setup wizard, not a reference manual.

- **Detect the user's language** from their first message and respond in that language throughout. Keep commands, code blocks, URLs, and env variable names in English.
- Go **one step at a time**. Don't dump all steps at once.
- **Ask before proceeding** to the next step. Confirm the previous step worked.
- Use the **AskQuestion tool** for structured choices when available (client selection, research areas, etc.).
- **Explain briefly** what each step does and why, in plain language.
- When something goes wrong, be reassuring and help troubleshoot before moving on.
- **Celebrate small wins** — when uv installs successfully, when the MCP server appears, when the first tool call works.

## Internal Notes (do not show to user)

⚠️ **ToolUniverse has 1200+ tools** which will cause context window overflow if all exposed directly. The default `tooluniverse` command enables compact mode automatically, exposing only 5 core tools (list_tools, grep_tools, get_tool_info, execute_tool, find_tools) while keeping all 1200+ accessible via execute_tool.

**This skill's own URL** (for bootstrapping):
`https://raw.githubusercontent.com/mims-harvard/ToolUniverse/main/skills/setup-tooluniverse/SKILL.md`

## Step 0: Auto-Detect & Quick Start

Welcome the user, then immediately run these detection commands **before asking any questions**:

```bash
echo "=== Detecting OS ===" && \
  ([ "$(uname)" = "Darwin" ] && echo "OS: macOS") || \
  ([ "$(uname)" = "Linux" ] && echo "OS: Linux") || \
  echo "OS: Unknown"

echo "=== Detecting your AI client ===" && \
  ([ -f ~/.cursor/mcp.json ] && echo "✅ Cursor detected") || true && \
  ([ -f ~/Library/Application\ Support/Claude/claude_desktop_config.json ] && echo "✅ Claude Desktop detected (macOS)") || true && \
  ([ -f ~/.config/Claude/claude_desktop_config.json ] && echo "✅ Claude Desktop detected (Linux)") || true && \
  ([ -f ~/.claude.json ] && echo "✅ Claude Code detected") || true && \
  ([ -f ~/.codeium/windsurf/mcp_config.json ] && echo "✅ Windsurf detected") || true && \
  ([ -f ~/.gemini/settings.json ] && echo "✅ Gemini CLI detected") || true && \
  ([ -f ~/.codex/config.toml ] && echo "✅ Codex CLI detected") || true && \
  ([ -f ~/.qwen/settings.json ] && echo "✅ Qwen Code detected") || true && \
  ([ -f opencode.json ] && echo "✅ OpenCode detected") || true && \
  echo "=== Detection complete ==="
```

**On Windows**, detection won't run in bash — ask the user to check manually: Claude Desktop `%APPDATA%\Claude\claude_desktop_config.json`, Cursor `%USERPROFILE%\.cursor\mcp.json`.

**Remember the detected OS** — it changes config paths, uv install commands, and log locations in later steps.

Based on results:
- **One client detected**: "I can see you're using [Client]. I'll set up ToolUniverse for that." Skip Question 1.
- **Multiple detected**: Ask which one to configure.
- **None detected**: Ask Question 1.

**Question 1 (only if not auto-detected):** Which app are you using?
Cursor · Claude Desktop · VS Code / Copilot · Windsurf · Claude Code · Gemini CLI · Qwen Code · Codex (OpenAI) · Cline · Trae · Antigravity · OpenCode · Other

---

**Bootstrap check for terminal-based clients (OpenCode, Gemini CLI, Codex CLI, Claude Code):**

If the user found this guide from README/docs rather than from a skill already running inside their client, give them this one-liner to paste into their client instead:

```
Please read https://raw.githubusercontent.com/mims-harvard/ToolUniverse/main/skills/setup-tooluniverse/SKILL.md and follow it to help me set up ToolUniverse.
```

After they paste that, your job here is done.

---

**Quick Start mode** (offer before Question 2):

Ask: "Would you like a **quick start** (running in ~2 minutes, no questions) or a **full setup** (I walk you through API keys and options)?"

- **Quick start**: Pick the fastest single path — `brew install uv` (or curl installer), write the config with the python3 one-liner, restart the app, confirm hammer icon. Skip API keys entirely (user adds them later).
- **Full setup**: Continue with all steps including API keys.

**Question 2:** How will you use ToolUniverse?
- **MCP server** (use scientific tools through chat) — default for most users
- **Python coding** (write scripts that `import tooluniverse`) — also needs pip install

## Step 1: Make sure uv is installed

Check first — **skip install entirely if uv is already present**:

```bash
which uv && uv --version || echo "NOT_INSTALLED"
```

- **Found**: "✅ uv is already installed — skipping." Go to Step 2.
- **NOT_INSTALLED**: Explain uv is a fast package manager that makes MCP setup simple, then install.

**macOS — check for Homebrew first (preferred for Claude Desktop):**
```bash
which brew && echo "Homebrew found" || echo "No Homebrew"
```

- **Homebrew found:**
  ```bash
  brew install uv
  ```
  Verify with Homebrew path directly (GUI apps use this, not the shell's `which uvx`):
  ```bash
  /opt/homebrew/bin/uvx --version   # Apple Silicon
  /usr/local/bin/uvx --version      # Intel Mac
  ```

- **No Homebrew:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  source "$HOME/.local/bin/env" 2>/dev/null || source ~/.zshrc 2>/dev/null || source ~/.bashrc 2>/dev/null
  ```

**Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh && source "$HOME/.local/bin/env" 2>/dev/null || source ~/.bashrc`

**Windows (PowerShell):** `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` then reopen PowerShell.

Verify: `uvx --version`

## Step 2: Add ToolUniverse to your MCP config

**Validate uvx tooluniverse works before touching any config:**

```bash
uvx tooluniverse --help
```

- **Prints usage text** → proceed.
- **Error** → fix the uv install (see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) Issue 2) before writing the config.

**Check if config file already exists:**
```bash
cat <CONFIG_PATH> 2>/dev/null || echo "CONFIG_NOT_FOUND"
```

- **CONFIG_NOT_FOUND**: Create with config below.
- **Exists, no `tooluniverse` entry**: Merge the `tooluniverse` block into the existing `mcpServers`.
- **Already has `tooluniverse`**: "ToolUniverse is already configured — I'll skip rewriting to avoid overwriting any API keys." Only overwrite if user asks.

---

⚠️ **Claude Desktop only** — GUI apps don't inherit shell PATH. Read [MCP_CONFIG.md](MCP_CONFIG.md) for the full PATH fix (Homebrew, symlink, or absolute path options) before writing this config.

---

**Ask:** "Would you like ToolUniverse to auto-update whenever your app starts? (~1–2s startup overhead, recommended: yes)"

- **Yes** → use `["--refresh", "tooluniverse"]` in args
- **No** → use `["tooluniverse"]`; upgrade manually with `uv cache clean tooluniverse`

**Standard config (works for Cursor, Claude Desktop, Windsurf, Claude Code, Gemini CLI, Qwen Code, Trae, Cline):**
```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "uvx",
      "args": ["--refresh", "tooluniverse"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

**One-liner to write or merge the config safely:**
```bash
python3 -c "
import json, os
p = os.path.expanduser('CONFIG_PATH')
os.makedirs(os.path.dirname(p), exist_ok=True)
cfg = json.load(open(p)) if os.path.exists(p) else {}
cfg.setdefault('mcpServers', {})['tooluniverse'] = {
    'command': 'uvx', 'args': ['--refresh', 'tooluniverse'],
    'env': {'PYTHONIOENCODING': 'utf-8'}
}
json.dump(cfg, open(p, 'w'), indent=2)
print('Done — tooluniverse added to', p)
"
```

Replace `CONFIG_PATH` with the path for the user's client:

| Client | Config File |
|--------|-------------|
| **Cursor** | `~/.cursor/mcp.json` |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) · `%APPDATA%\Claude\...` (Win) · `~/.config/Claude/...` (Linux) |
| **Claude Code** | `~/.claude.json` or `.mcp.json` |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` |
| **VS Code (Copilot)** | `.vscode/mcp.json` — uses `"servers"` key, needs `"type": "stdio"` — see [MCP_CONFIG.md](MCP_CONFIG.md) |
| **Codex (OpenAI)** | TOML format: `codex mcp add tooluniverse -- uvx tooluniverse` — see [MCP_CONFIG.md](MCP_CONFIG.md) |
| **OpenCode** | `opencode.json` — uses `"mcp"` key — see [MCP_CONFIG.md](MCP_CONFIG.md) |
| **Gemini CLI** | `~/.gemini/settings.json` |
| **Qwen Code** | `~/.qwen/settings.json` |
| **Trae** | `.trae/mcp.json` |
| **Cline** | `cline_mcp_settings.json` (in VS Code extension globalStorage) |
| **Antigravity** | `mcp_config.json` |

For VS Code, Codex, and OpenCode special formats, read [MCP_CONFIG.md](MCP_CONFIG.md).

## Step 3 (coding use only): Install Python package

Skip if user only needs MCP. For scripting use:
```bash
pip install tooluniverse
```
Verify:
```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
print(f"ToolUniverse version: {tu.__version__}")
```

## Step 4: Set up API Keys

Many tools work without keys, but some unlock powerful features. First, **ask the user about their research interests** to recommend only what's relevant. Use AskQuestion if available:
- Literature search & publications
- Drug discovery & pharmacology
- Protein structure & interactions
- Genomics & disease associations
- Rare diseases & clinical
- AI-powered analysis (needs LLM key)
- Not sure yet / skip for now

Then walk through **2–4 recommended keys** one at a time: explain what each unlocks, give the registration link, wait for them to sign up, help add the key to the `env` block in their config.

For the full list of keys, registration steps, and which tools each enables, read [API_KEYS_REFERENCE.md](API_KEYS_REFERENCE.md).

**Quick reference — Tier 1 (most users):**

| Key | Service | What It Unlocks | Registration |
|-----|---------|----------------|-------------|
| `NCBI_API_KEY` | NCBI/PubMed | PubMed rate limit 3→10 req/s | https://account.ncbi.nlm.nih.gov/settings/ |
| `NVIDIA_API_KEY` | NVIDIA NIM | 16 tools: AlphaFold2, docking, genomics | https://build.nvidia.com |
| `BIOGRID_API_KEY` | BioGRID | Protein-protein interactions | https://webservice.thebiogrid.org/ |
| `DISGENET_API_KEY` | DisGeNET | Gene-disease associations | https://disgenet.com/academic-apply |
| `GEMINI_API_KEY` | Google Gemini | Agentic features (free tier) | https://aistudio.google.com/apikey |

Add keys to the `env` block in your MCP config:
```json
"env": {
  "PYTHONIOENCODING": "utf-8",
  "NCBI_API_KEY": "your_key_here",
  "NVIDIA_API_KEY": "your_key_here"
}
```

## Step 5: Test & Status Check

**Pre-flight check before restarting:**
```bash
timeout 10 uvx tooluniverse --help
```
- Prints usage → proceed to restart.
- Fails → fix first (see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) Issue 5). Don't restart yet.

Ask user to **fully quit and reopen their app** (⌘Q on Mac — closing the window is not enough).

⏱️ **First launch takes 60–90 seconds** while the app downloads and installs ToolUniverse. Watch logs:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log          # Claude Desktop (macOS)
tail -f ~/.config/Claude/logs/mcp*.log          # Claude Desktop (Linux)
```
Look for `"tooluniverse" connected` or tool schema output.

**What to look for in the app UI:**
- **Claude Desktop / Cursor / Windsurf**: 🔨 hammer icon at the bottom of the chat input.
- **Claude Code / Gemini CLI / Codex CLI**: Run `/mcp` or `mcp list`.

**Show this status summary** and fill in each line:
```
Setup Status
─────────────────────────────────────
✅/❌  uv installed         (uvx --version)
✅/❌  ToolUniverse starts  (uvx tooluniverse --help)
✅/❌  MCP config created   (config file found)
✅/❌  Server visible       (🔨 hammer / Settings → Developer → MCP Servers)
✅/❌  Test tool call works
⬜     API keys (optional — add anytime)
─────────────────────────────────────
```

**Live test call:**
```
list_tools
```
or
```
execute_tool("PubMed_search_articles", {"query": "CRISPR", "max_results": 1})
```

If all ✅, celebrate! 🎉 If any ❌, jump to the matching issue in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Step 6: Install ToolUniverse Skills

Explain to the user: **Skills turn ToolUniverse from a toolbox into an expert research assistant.** Each skill is a pre-built workflow that knows exactly which of the 1200+ tools to call, in what order, to produce a complete research report — for drug profiling, literature reviews, cancer variant interpretation, and 60+ more domains. See the full catalog in [SKILLS_CATALOG.md](SKILLS_CATALOG.md).

**Option A — User runs in terminal (quickest):**
```bash
npx skills add mims-harvard/ToolUniverse
```
This auto-detects the client and installs into the correct directory. Ask the user to confirm it completed successfully.

**Option B — Agent installs directly** (use this if you have shell/terminal access, or if npx fails):
```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/mims-harvard/ToolUniverse.git /tmp/tu-skills
cd /tmp/tu-skills && git sparse-checkout set skills
```
Then copy to the client's skills directory:

| Client | Skills Directory |
|--------|----------------|
| Cursor | `.cursor/skills/` |
| Windsurf | `.windsurf/skills/` |
| Claude Code | `.claude/skills/` |
| Gemini CLI | `.gemini/skills/` |
| Qwen Code | `.qwen/skills/` |
| Codex (OpenAI) | `.agents/skills/` |
| OpenCode | `.opencode/skills/` |
| Trae | `.trae/skills/` |
| Cline / VS Code | `.skills/` |

```bash
# Example for Cursor (run from the project root):
mkdir -p .cursor/skills && cp -r /tmp/tu-skills/skills/* .cursor/skills/
rm -rf /tmp/tu-skills
```

**Suggest a skill to try** based on their research interests from Step 4:
- "Try: **'Research the drug metformin'**" — triggers the drug-research skill
- "Try: **'What does the literature say about CRISPR in cancer?'**" — triggers literature-deep-research

## Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| uv not found | `uvx: command not found` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` then re-source shell |
| GUI app can't find uvx | "Failed to spawn process" / "ENOENT" | `brew install uv` on macOS, or use absolute path in config |
| Server won't appear | No hammer icon after restart | Run diagnostic chain in [TROUBLESHOOTING.md](TROUBLESHOOTING.md) Issue 5 |
| API key rejected | 401/403 errors | Move key to `env` block in MCP config; restart app |
| Context overflow | Client very slow | Already in compact mode; narrow categories if needed |

Full diagnostics in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## What's Next?

Suggest the user try one of these:
- **"Research the drug metformin"** — full drug profile via drug-research skill
- **"What are the known targets of imatinib?"** — target-research
- **"What does the literature say about CRISPR in sickle cell disease?"** — literature-deep-research
- **"Find protein structures for human EGFR"** — protein-structure-retrieval

Point them to the `tooluniverse` general skill for tips on getting the most out of 1200+ tools.

## Quick Reference

- **Instant bootstrap**: `Please read https://raw.githubusercontent.com/mims-harvard/ToolUniverse/main/skills/setup-tooluniverse/SKILL.md and follow it to help me set up ToolUniverse.`
- **Auto-update config**: `["--refresh", "tooluniverse"]`
- **Manual upgrade**: `uv cache clean tooluniverse` then restart
- **Detailed API keys**: [API_KEYS_REFERENCE.md](API_KEYS_REFERENCE.md)
- **All client config formats**: [MCP_CONFIG.md](MCP_CONFIG.md)
- **Skills catalog**: [SKILLS_CATALOG.md](SKILLS_CATALOG.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Help**: https://github.com/mims-harvard/ToolUniverse/issues
