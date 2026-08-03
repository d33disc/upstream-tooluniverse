# Documentation validation guide

Run the smallest checks that cover the edited pages, then build the complete
documentation when navigation, shared references, or generated content changes.

## 1. Review scope

```bash
git status --short
git diff --name-status
git diff --check
```

Generated locale catalogs and `.doctree` files should not appear in an ordinary
documentation patch.

## 2. Check stale inventory language

Public docs use durable rounded counts. This command should not find retired
inventories in maintained English sources:

```bash
rg -n '(~2,300|136 orchestration|134 skills|129 SKILL|66 specialized|54 skills|68 pre-built|9 subcommands|Actual count.*1962)' \
  --glob '!VALIDATION_GUIDE.md' \
  AGENTS.md README.md plugin/README.md docs/index.rst docs/dev_docs docs/guide docs/reference
```

When an exact count is needed, query the source instead of updating prose:

```bash
tu status
find -L skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l
```

## 3. Validate generated pages

After changing a skill or the showcase generator:

```bash
python docs/generate_skills_showcase.py
source_count=$(find -L skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')
page_count=$(rg -c '^      :link: https://github.com/mims-harvard/ToolUniverse/tree/main/skills/' docs/guide/skills_showcase.rst)
test "$source_count" = "$page_count"
```

After changing tool JSON, run the tool-document generators named in
`DOCUMENTATION_STANDARDS.md` and review their diffs rather than editing generated
pages directly.

## 4. Smoke-test examples

The legacy example checker scans Python blocks in top-level `docs/*.rst` files:

```bash
python docs/validate_examples.py
```

This is only a narrow smoke test; it does not scan nested guides or prove that
remote examples return live data. The Sphinx build below is the required
repository-wide structural check. Network examples require targeted integration
tests.

Check documented tool names against the live registry when a page names
specific tools:

```bash
tu info UniProt_get_entry_by_accession
```

## 5. Build Sphinx with warnings as errors

Install the project documentation group in an isolated `uv` environment, then
build outside the source tree:

```bash
uv sync --extra docs
uv run sphinx-build -W --keep-going -b html docs /tmp/codex-tooluniverse-docs
```

For a faster structural pass while iterating:

```bash
uv run sphinx-build -W --keep-going -b dummy docs /tmp/codex-tooluniverse-docs-dummy
```

Fix warnings in maintained source pages. Regenerate rather than hand-editing
generated API, tool, locale, or doctree content.

## 6. Validate machine-readable metadata

When `server.json` changes:

```bash
jq empty server.json
```

When command or environment-variable documentation changes, compare it with the
live CLI and source reads:

```bash
tu --help
tu health --help
rg -n 'os\.(getenv|environ\.get)\(' src/tooluniverse
```

## 7. Final review

```bash
git diff --check
git diff --stat
git diff -- docs README.md AGENTS.md plugin/README.md server.json
```

Confirm that examples use registered names, internal links resolve, generated
pages match their sources, and no unrelated file was reformatted.
