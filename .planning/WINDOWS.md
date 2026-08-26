---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-08-06T20:17:09.949Z
---

# Broken Windows Ledger

> Cross-phase defect register. `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 02 | deviation | scripts/probe_custom_tools.py |  | 3 of 120 preservation.json symlinks (plugin/skills/*-workspace) verdict 'retargeted' not 'preserved' in re-merge stage; PRES-02 reverted to Pending; see 02-05-SUMMARY.md Issues Encountered | open |  | 2026-08-06T20:17:09.949Z |  |

````json
[
  {
    "id": 1,
    "kind": "deviation",
    "phase": "02",
    "file": "scripts/probe_custom_tools.py",
    "line": null,
    "description": "3 of 120 preservation.json symlinks (plugin/skills/*-workspace) verdict 'retargeted' not 'preserved' in re-merge stage; PRES-02 reverted to Pending; see 02-05-SUMMARY.md Issues Encountered",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-06T20:17:09.949Z",
    "resolved_at": null
  }
]
````
