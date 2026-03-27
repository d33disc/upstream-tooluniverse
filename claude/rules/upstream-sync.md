# Upstream Sync Conventions

This repo is a fork of `mims-harvard/ToolUniverse`. Minimize diff noise to keep merges clean.

## Formatting

Upstream uses `ruff check --fix` + `ruff format` via pre-commit (v0.14.7) and CI.
Project config in `pyproject.toml` matches upstream exactly:

- Line length: 88
- Lint ignores: E203, E402, E501, F401, F541
- Format: ruff defaults (double quotes, 4-space indent, preserve trailing comma)
- Scope: `src/tooluniverse/` only

Run both after editing:

```bash
ruff check --fix src/tooluniverse/<file>.py
ruff format src/tooluniverse/<file>.py
```

Do NOT run with global config overrides (`~/.ruff.toml` uses line-length 100
and extra lint rules). Ruff resolves project `pyproject.toml` first, but
verify with `ruff check --config pyproject.toml` if in doubt.

## Branches

- Never commit directly to main.
- Fork-specific features go on `feat/` branches.
- Fixes that could be PR'd upstream go on `fix/` branches.
- Never push to upstream (`mims-harvard`). Origin is our boundary.
