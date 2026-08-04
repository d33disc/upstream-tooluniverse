## Conflict Detection Report

### BLOCKERS (0)

None.

### WARNINGS (0)

None.

### INFO (2)

[INFO] Auto-resolved: SPEC > DOC on tool registration chain
  Found: docs/dev_docs/Tool_Registration_Chain.md requires all six registration links, while docs/dev_docs/Adding_Tools_Tutorial.md and docs/dev_docs/Adding_Tools_Quick_Reference.md describe decorator-based automatic registration without those manual links; sources: docs/dev_docs/Tool_Registration_Chain.md, docs/dev_docs/Adding_Tools_Tutorial.md, docs/dev_docs/Adding_Tools_Quick_Reference.md
  Note: The SPEC constraint wins under ADR > SPEC > PRD > DOC precedence; sources: docs/dev_docs/Tool_Registration_Chain.md, docs/dev_docs/Adding_Tools_Tutorial.md, docs/dev_docs/Adding_Tools_Quick_Reference.md

[INFO] Untrusted embedded worker directive ignored
  Found: docs/superpowers/plans/2026-04-17-upstream-sync.md contains a directive telling agentic workers to invoke a required sub-skill; source: docs/superpowers/plans/2026-04-17-upstream-sync.md
  Note: The directive was treated as untrusted source data and did not alter synthesis behavior; source: docs/superpowers/plans/2026-04-17-upstream-sync.md
