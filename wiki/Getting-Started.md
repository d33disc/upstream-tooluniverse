# Getting Started

## Install

```bash
uvx --from tooluniverse tooluniverse-smcp-stdio --compact-mode
```

## Claude Code MCP Config

Add to `~/.claude/settings.json` under `mcpServers`:

```json
{
  "tooluniverse": {
    "command": "uvx",
    "args": ["--from", "tooluniverse", "tooluniverse-smcp-stdio", "--compact-mode"],
    "env": {
      "TOOLUNIVERSE_CACHE_ENABLED": "true",
      "TOOLUNIVERSE_LAZY_LOADING": "true",
      "TOOLUNIVERSE_COERCE_TYPES": "true",
      "TOOLUNIVERSE_STDIO_MODE": "1"
    }
  }
}
```

## Claude Desktop MCP Config

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "uvx",
      "args": ["--from", "tooluniverse", "tooluniverse-smcp-stdio", "--compact-mode"],
      "env": {
        "TOOLUNIVERSE_CACHE_ENABLED": "true",
        "TOOLUNIVERSE_LAZY_LOADING": "true",
        "TOOLUNIVERSE_COERCE_TYPES": "true",
        "TOOLUNIVERSE_STDIO_MODE": "1"
      }
    }
  }
}
```

## Verify

Run a quick smoke test after setup:

```bash
tu test
```

## Further Reading

- [Architecture](Architecture.md) -- how the system works
- [Contributing](Contributing.md) -- how to add tools, skills, or config
- [mims-harvard/ToolUniverse](https://github.com/mims-harvard/ToolUniverse) -- upstream repository
