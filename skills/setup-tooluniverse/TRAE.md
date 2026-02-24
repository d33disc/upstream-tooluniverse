# Trae IDE Setup

## Step 1: Find Your Global Config Path

Trae's **global** MCP config is the only config the AI agent can access. Ask the user to confirm the path on their system:

**Open Trae → Settings → MCP (or "..." menu → Open MCP config)** to find the exact file path.

Expected locations by OS:
- **Windows**: `%APPDATA%\Trae\User\mcp.json` (e.g. `C:\Users\yourname\AppData\Roaming\Trae\User\mcp.json`)
- **macOS**: `~/Library/Application Support/Trae/User/mcp.json`
- **Linux**: `~/.config/Trae/User/mcp.json`

> ⏸️ Ask the user: "Can you open Trae Settings → MCP and tell me the config file path it shows?" Confirm the path before proceeding.

---

## ⚠️ Do Not Use Project-Level Config

`.trae/mcp.json` is an **experimental/beta feature** in Trae. The AI agent **cannot access** project-level MCP servers — only the global config is visible to the agent.

**If you see "Enable Project MCP" in the Trae UI — ignore it.** This beta feature does not expose tools to the agent and will cause confusion. Always use the global config path above.

---

## Step 2: Write the Config

The config format is the standard `"mcpServers"` object (same as Cursor and Claude Desktop):

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

### Option A — Python one-liner (try this first)

Replace `CONFIG_PATH` with the confirmed path from Step 1:

```bash
python3 -c "
import json, os
p = r'CONFIG_PATH'
os.makedirs(os.path.dirname(p), exist_ok=True)
cfg = json.load(open(p)) if os.path.exists(p) else {}
cfg.setdefault('mcpServers', {})['tooluniverse'] = {
    'command': 'uvx', 'args': ['--refresh', 'tooluniverse'],
    'env': {'PYTHONIOENCODING': 'utf-8'}
}
json.dump(cfg, open(p, 'w'), indent=2)
print('Done:', p)
"
```

### Option B — Manual paste (if Trae blocks the write)

Trae may restrict programmatic modifications to its config file. If Option A fails or the file isn't updated:

1. Open the global config file directly in a text editor (the path confirmed in Step 1)
2. If the file is empty or doesn't exist, paste the full JSON above
3. If the file already has content, merge by adding the `"tooluniverse"` block inside the existing `"mcpServers"` object
4. Save the file
5. Restart Trae

> ⏸️ Ask: "Did the config get written, or did you need to paste manually?" Wait before continuing.

---

## Step 3: Restart Trae

Fully quit Trae (not just close the window), then reopen it.

⏱️ **First launch takes 60–90 seconds** while Trae downloads and installs ToolUniverse in the background.

---

## Step 4: Verify

After restart, check that `tooluniverse` appears as a connected server:

- Open Trae **Settings → MCP** (or the "..." menu in the AI panel)
- `tooluniverse` should be listed with a green/connected status

**Live test** — ask the agent to run:
```
list_tools
```
or
```
execute_tool("PubMed_search_articles", {"query": "CRISPR", "max_results": 1})
```

If tools are returned, setup is working. If not, check that:
1. The config file is at the correct global path (not `.trae/mcp.json`)
2. `uvx tooluniverse --help` runs successfully in the terminal
3. Trae was fully restarted (not just the window closed)

> ⏸️ Ask: "Do you see `tooluniverse` in the MCP panel? Did the test call return results?" Confirm before proceeding to skills installation.
