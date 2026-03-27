# Upstream Sync Conventions

This repo is a fork of `mims-harvard/ToolUniverse`. Minimize diff noise to keep merges clean.

## Formatting

- **Do NOT run `ruff format .`** on this repo. Upstream does not use ruff format.
- Run `ruff check --fix .` for real lint issues only.
- When editing upstream files, preserve the original formatting style.
- Only format files you create from scratch in this fork.

## Branches

- Never commit directly to main.
- Fork-specific features go on `feat/` branches.
- Fixes that could be PR'd upstream go on `fix/` branches.
- Never push to upstream (`mims-harvard`). Origin is our boundary.
