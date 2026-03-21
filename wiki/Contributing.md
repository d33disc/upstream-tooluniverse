# Contributing

## Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-change`
3. Make changes, commit with clear messages
4. Open a PR against `main`

All PRs are auto-labeled by path (see `.github/labeler.yml`) and require
review from `@d33disc` (see `.github/CODEOWNERS`).

## Adding Tools

Tools live in `src/` and are registered in the tool registry. Each tool
needs:

- A unique name following the `Source_action_target` convention
  (e.g., `PubMed_search_articles`)
- A JSON schema defining required and optional parameters
- An implementation that calls the upstream API

## Adding Skills

Skills live in `skills/` as structured Markdown files. Each skill defines
a multi-step research workflow. To add one:

1. Create `skills/your-skill-name.md`
2. Follow the existing skill format (title, description, steps)
3. Reference tools by their exact names from the registry

## Adding Claude Config

Claude Code integration files live in `claude/`:

- `commands/` -- slash commands (Markdown templates)
- `rules/` -- context rules loaded into every session
- `scripts/` -- shell scripts for MCP startup and helpers

## Testing

```bash
tu test
```

## Linting

The repo runs daily automated lint via GitHub Actions:

- **Python**: `ruff check --fix` + `ruff format`
- **Markdown**: `mdformat` + `markdownlint --fix`
- **Types**: `mypy` (report only)

Run locally before pushing:

```bash
ruff check --fix . && ruff format .
markdownlint --fix "**/*.md"
```
