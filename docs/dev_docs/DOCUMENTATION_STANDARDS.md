# Documentation standards

These rules keep ToolUniverse documentation accurate as the tool and skill
catalogs change.

## Sources of truth

- Runtime tools and categories: `tu status`, `tu list --mode categories`, and
  the JSON definitions under `src/tooluniverse/data/`.
- Tool schemas: the JSON definitions and `tu info <tool>`.
- Console entry points: `pyproject.toml` `[project.scripts]`.
- CLI commands and flags: `tu --help`, `tu <command> --help`, and
  `src/tooluniverse/cli.py`.
- Skills: directories containing `skills/*/SKILL.md`.
- Plugin commands: `plugin/commands/*.md`.
- Environment variables: their reads in `src/tooluniverse/`.

`TOOL_MANIFEST.json` is a dated health snapshot. It is useful for health status
but is not the authoritative count of loadable runtime tools.

## Avoid volatile claims

Use durable rounded public wording: **2,500+ tools** and **150+ skills**. Do not
copy exact catalog, category, or health counts into prose. When an exact value
matters, show the command that obtains it:

```bash
tu status
find -L skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l
```

Do not include source line numbers in narrative documentation. Link to a file,
class, or function name; line numbers become stale after unrelated edits.

## Generated content

Do not manually edit generated documentation:

- `docs/api/tooluniverse.*.rst` (except manually maintained landing pages);
- `docs/tools/*_tools.rst` and generated tool indexes;
- `docs/guide/skills_showcase.rst`;
- `docs/locale/` translations;
- tracked `.doctree` artifacts.

Edit the source and regenerate instead:

```bash
# Skills showcase from skills/*/SKILL.md
python docs/generate_skills_showcase.py

# Tool catalog from src/tooluniverse/data/*.json
python docs/generate_config_index.py
python docs/generate_tool_reference.py

# API reference from Python docstrings
sphinx-apidoc -f -o docs/api src/tooluniverse
```

Every generated text file must begin with a visible generated-file comment
naming its generator and source.

## Maintained documentation map

```text
README.md                         Project overview and install path
AGENTS.md                         Repository orientation for coding agents
plugin/README.md                  Claude Code plugin usage
docs/index.rst                    Documentation landing page
docs/guide/                       User guides and tutorials
docs/reference/                   CLI, environment, and data references
docs/expand_tooluniverse/         Extension guides
docs/help/                        Troubleshooting
docs/about/                       Project and contribution information
docs/dev_docs/                    Maintainer documentation
docs/tools/                       Generated tool catalog
docs/api/                         Generated API reference
```

Keep navigation in `docs/index.rst` and `docs/sitemap.rst`. Prefer one canonical
page per topic and link to it instead of duplicating tables or examples.

## Commands and examples

- Use installed console commands, not `python -m ...`, when a
  `[project.scripts]` entry exists.
- Use `uv` for environments and dependency installation.
- Use current, registered tool names and inspect their schemas before writing
  examples.
- Keep examples small and executable. Avoid fake return payloads that look like
  guaranteed API contracts.
- Use `<user_cache_dir>` when a cache path is platform-dependent, followed by a
  table or link explaining macOS, Linux, and Windows locations.

## MCP terminology

Compact mode exposes four core proxies (`list_tools`, `grep_tools`,
`get_tool_info`, and `execute_tool`) plus `find_tools` when semantic search is
enabled. Backend tools remain available through `execute_tool`.

Use these transport names consistently:

- stdio: `tooluniverse` or `tooluniverse-smcp-stdio`;
- streamable HTTP: `tooluniverse-mcp` or `tooluniverse-smcp-server`;
- configurable legacy server: `tooluniverse-smcp`.

## Review checklist

Before committing documentation:

1. Confirm commands and identifiers against source.
2. Regenerate affected generated pages.
3. Run the checks in `docs/dev_docs/VALIDATION_GUIDE.md`.
4. Inspect the rendered page when layout or navigation changed.
5. Keep locale and `.doctree` updates in their dedicated generation workflow.
