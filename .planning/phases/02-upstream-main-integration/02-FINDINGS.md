# Phase 2 Findings: Re-merge Audit vs. the Landed Merge

Generated: 2026-08-06T20:57:33.680Z

Related: [[02-CONTEXT]] [[02-RESEARCH]] [[01-VERIFICATION]]

This is the human review surface for Phase 2's criterion 2 (fork behavior not silently dropped by the landed merge) and criterion 3 (every custom code, tool, plugin, registration, and symlink asset accounted for). A disagreement below is not automatically a defect -- upstream superseding a shared definition is the expected, correct outcome under D-08.

## The Four Trees In Play

| Tree | OID | Role |
| --- | --- | --- |
| landed merge | f81448f2047a6f35bd552956a0d9990019a39eb1 | f81448f2 -- what actually shipped |
| re-merge stage | a4d3d95a096a14ce4d147faa20334d24f8db9f9a | this audit's independent D-08 re-derivation, throwaway, never merged |
| pin | 21945440c9f2a15537ba878500a800d9e330eab0 | 21945440 -- 31 commits downstream of landed |
| upstream | 56adcfd9c299078d0c40fde642b0be006510ccf3 | 56adcfd9 -- the merged-in upstream revision |

## Criterion 2: Full-tree Disagreement Classification

Full-tree diff (`git diff --raw -z --find-renames` f81448f2..a4d3d95a) enumerated **3446** disagreeing paths -- not only the 22 git's own `diff-tree --cc` flags as hand-resolved.

| Verdict | Count | Meaning |
| --- | --- | --- |
| landed_correct | 211 | landed and re-derived agree (including canonical-JSON-reformat-only differences confirmed union_ok) |
| remerge_only_artifact | 3205 | this audit's own regenerated/materialized tooling output (tool-wrapper stubs, lazy registry, plugin/skills/* directory materialization) -- not a fork-content judgment |
| dependency_scope | 1 | pyproject.toml/uv.lock -- routed to Phase 5 / COMP-01 per D-07's OQ1 decision |
| self_healed_downstream | 0 | landed disagreed with the re-derivation, but the pin already matches it -- repaired downstream, D-06a, no corrective commit needed |
| landed_dropped_or_altered | 29 | survived the D-06a pin recheck -- corrective-commit CANDIDATES below, proposal-only |
| **unclassified** | **0** | must be 0 |

## Corrective-commit Candidates (proposal-only, gated on plan 02-06)

The following disagreed with the landed merge, are not this audit's own tooling noise, and do not self-heal against the pin. Each is a PROPOSAL for plan 02-06's decision checkpoint -- none has been applied here (D-06's findings-only posture).

| Path | Landed blob | Remerge blob | Pin blob | Pin matches landed | Repair commits | Forensic verdict |
| --- | --- | --- | --- | --- | --- | --- |
| .gitignore | fbc6d1dfa67d | 5e92d8cc40ce | fbc6d1dfa67d | True | none | head_matches_landed |
| skills/setup-tooluniverse/SKILL.md | b09d9156f796 | 89aae673b6c5 | 1ed22b5d96db | False | 4b2c1c38 fix: harden sync, discovery, cache lifecycle, and docs | repaired_at_head |
| skills/tooluniverse-gene-enrichment/SKILL.md | d4c243448c44 | 6d86b6ac8256 | d4c243448c44 | True | none | head_matches_landed |
| skills/tooluniverse/.env.template | ef86cc732486 | - | ef86cc732486 | True | none | head_matches_landed |
| skills/tooluniverse/CHECKLIST.md | 4c4810e12d8e | - | 4c4810e12d8e | True | none | head_matches_landed |
| skills/tooluniverse/references/general-strategies.md | 8b2bb3c6e412 | - | 8b2bb3c6e412 | True | none | head_matches_landed |
| src/tooluniverse/admetai_tool.py | 1215641cec4e | 76f705e6af44 | 1215641cec4e | True | none | no_definition_delta |
| src/tooluniverse/agentic_tool.py | 1074f3fb3022 | 763df3ffe063 | 1074f3fb3022 | True | none | no_definition_delta |
| src/tooluniverse/brenda_tool.py | 6dea7d34609d | 9980107b536c | 6dea7d34609d | True | none | no_definition_delta |
| src/tooluniverse/cli.py | 08edefcde43e | 072266aebfc0 | 08edefcde43e | True | none | no_definition_delta |
| src/tooluniverse/ctd_tool.py | 75ef5f629e79 | c8cbb06cd3ef | 75ef5f629e79 | True | none | false_positive_superseded |
| src/tooluniverse/data/broken_apis/oxo_tools.json | c13ebf0f34a0 | 12e294e4b6c1 | c13ebf0f34a0 | True | none | head_matches_landed |
| src/tooluniverse/data/oxo_tools.json | 12e294e4b6c1 | - | 12e294e4b6c1 | True | none | head_matches_landed |
| src/tooluniverse/default_config.py | b0cf9aa8a569 | 81ac09a5ba1a | b0cf9aa8a569 | True | none | no_definition_delta |
| src/tooluniverse/execute_function.py | 60a4f248fc47 | 1db93e395de6 | 64208625367c | False | 4b2c1c38 fix: harden sync, discovery, cache lifecycle, and docs | no_definition_delta |
| src/tooluniverse/foldseek_tool.py | 3fa5b1ce41dc | 057b0bd48ae3 | 3fa5b1ce41dc | True | none | no_definition_delta |
| src/tooluniverse/gwas_tool.py | 8420ae42b847 | 94c764e01892 | 8420ae42b847 | True | none | dead_code_drop_no_functional_impact |
| src/tooluniverse/llm_clients.py | 80a54630d26e | 3a65a5b9f473 | 80a54630d26e | True | none | false_positive_superseded |
| src/tooluniverse/rdkit_cheminfo_tool.py | 64c80038eb02 | 4320cf2e1f4d | 64c80038eb02 | True | none | no_definition_delta |
| src/tooluniverse/sabdab_tool.py | 4fd9672fa415 | 40a4708745fe | 4fd9672fa415 | True | none | no_definition_delta |
| src/tooluniverse/therasabdab_tool.py | 9493222f35c6 | 938d8303a553 | 9493222f35c6 | True | none | no_definition_delta |
| src/tooluniverse/tool_finder_embedding.py | c4ae7760f730 | c613558ec003 | c4ae7760f730 | True | none | no_definition_delta |
| src/tooluniverse/unified_guideline_tools.py | 49c4341649af | 8b4820f14930 | 49c4341649af | True | none | no_definition_delta |
| src/tooluniverse/uniprot_tool.py | 2840aea2fec3 | 0fc2353481b7 | 2840aea2fec3 | True | none | false_positive_renamed |
| src/tooluniverse/xml_tool.py | 4bbc261d1ea6 | 7a38d1e6aae3 | 4bbc261d1ea6 | True | none | no_definition_delta |
| tests/integration/test_compose_tool.py | 23b637c7217d | c5796c526a5f | 23b637c7217d | True | none | no_definition_delta |
| tests/integration/test_tool_integration.py | 11bc2bbbdd4a | ab0d3e20524a | 11bc2bbbdd4a | True | none | no_definition_delta |
| tests/tools/test_brenda_tool.py | 15d6d3876e1e | 23c1adb8cb09 | 15d6d3876e1e | True | none | no_definition_delta |
| tests/unit/test_agentic_tool_env_vars.py | 6d56726f0eda | 6b7a8a643171 | 6d56726f0eda | True | none | confirmed_gap_test_coverage_only |

**Reading the table:** `pin matches landed = True` means the pin's content agrees with what actually shipped, not with this audit's re-derivation -- that is evidence the LANDED merge is correct and the re-derivation stage has its own git-auto-merge artifact (the same class of bug as F-02-03-01/F-02-03-02 in remerge.json), not evidence of a real fork-content loss. Treat those rows as informational, not corrective-commit candidates.

**Forensic verdict** (per-file trace, see `findings-forensics.json` for the full definition-diff / reference trace, `scripts/forensic_trace_findings.py`): `no_definition_delta` / `head_matches_landed` / `repaired_at_head` mean HEAD already carries no gap. `false_positive_renamed` / `false_positive_superseded` mean the apparent drop is a rename or a deliberate downstream rewrite (SDK migration, endpoint replacement), manually confirmed against HEAD source. `dead_code_drop_no_functional_impact` means the dropped definition had zero callers anywhere in the repo, including the re-derived stage itself. Only `confirmed_gap*` rows are live, actionable candidates for 02-06.

## dependency_scope Items (routed to Phase 5 / COMP-01)

| Path | Landed blob | Remerge blob |
| --- | --- | --- |
| pyproject.toml | c59462385392 | 5390a3c4aedf |

## upstream_deleted Data Files (relocated_to accounting)

| Path | Names lost | Relocated to |
| --- | --- | --- |
| src/tooluniverse/data/pathway_commons_tools.json | pc_get_interactions, pc_search_pathways | pc_get_interactions -> src/tooluniverse/data/broken_apis/pathway_commons_tools.json; pc_search_pathways -> src/tooluniverse/data/broken_apis/pathway_commons_tools.json |
| src/tooluniverse/data/soilgrids_tools.json | SoilGrids_get_properties | SoilGrids_get_properties -> src/tooluniverse/data/broken_apis/soilgrids_tools.json |

## Criterion 3: Preservation Disposition (1,392 of 1,392)

preservation.json's `fork_oid` (21945440c9f2a15537ba878500a800d9e330eab0) is the PIN, not `e0755067` -- an upstream (56adcfd9c299078d0c40fde642b0be006510ccf3) <-> pinned-fork delta, while the re-merge stage (a4d3d95a096a14ce4d147faa20334d24f8db9f9a) is comparable to the landed merge (f81448f2047a6f35bd552956a0d9990019a39eb1), 31 commits earlier. Every disposition below was checked against all four trees; pin presence alone was never accepted as proof of preservation.

| Disposition | Count |
| --- | --- |
| survived | 1377 |
| superseded_by_upstream | 6 |
| lost | 9 |

### Breakdown by Phase 1 class (verbatim, not re-derived)

| Class | Count |
| --- | --- |
| custom_code | 512 |
| documentation | 425 |
| plugin_asset | 240 |
| other_review_required | 84 |
| planning | 64 |
| test | 45 |
| skill | 8 |
| generated_asset | 5 |
| workflow | 5 |
| tool_definition | 4 |

### CONTEXT.md Discrepancy

Claimed: CONTEXT.md D-03/A2: all 1,392 preservation.json entries carry class: other_review_required

Measured (this plan's own re-count against the same 1,392-entry file): only 84 of 1,392 carry `other_review_required`; see the class breakdown above for the real distribution. Recorded here as a discrepancy, not silently corrected in CONTEXT.md.

### Blocker Paths (Phase 1's inventory-completeness gate, secondary breakdown)

`blocking: True`, 87 blocker paths -- this is Phase 1's own inventory-completeness gate, not a per-path Phase 2 defect flag. Their Phase 2 dispositions, for completeness:

| Disposition | Count |
| --- | --- |
| lost | 1 |
| survived | 86 |

### Untracked (user-owned, out of scope)

- `.planning/config.json` (planning) -- out_of_scope_user_owned
- `ralph-specs/fleet/results/cas-checkdigit.json` (other_review_required) -- out_of_scope_user_owned
- `ralph-specs/fleet/results/ensembl-format.json` (other_review_required) -- out_of_scope_user_owned
- `ralph-specs/fleet/results/hgnc-format.json` (other_review_required) -- out_of_scope_user_owned
- `ralph-specs/fleet/results/inchikey-format.json` (other_review_required) -- out_of_scope_user_owned
- `ralph-specs/fleet/results/mondo-format.json` (other_review_required) -- out_of_scope_user_owned
- `ralph-specs/fleet/results/nct-format.json` (other_review_required) -- out_of_scope_user_owned

## Self Heal Recheck

D-06a's pin recheck ran against `21945440c9f2a15537ba878500a800d9e330eab0` for 29 disagreements not already swept into a noise bucket.

## Overall Assessment

Of the 29 landed_dropped_or_altered candidates: 27 have `pin matches landed = True`, meaning the live, currently-shipped code (the pin, 31 commits past landed) agrees with what actually landed at f81448f2, not with this audit's own re-derivation -- direct evidence the LANDED merge is correct and the disagreement originates in this audit's own D-08 re-derivation tooling (AST-splice / whole-file-canonical / entry-union producing different bytes than the original human merge resolution), not in a real fork-content loss. The remaining candidates (`skills/setup-tooluniverse/SKILL.md`, `src/tooluniverse/execute_function.py`) carry an explaining downstream repair commit (`4b2c1c38`) unrelated to fork preservation.

Criterion 3's independent preservation-inventory join narrows this further: only 9 of the 1,392 preservation.json paths land at disposition `lost` and 6 at `superseded_by_upstream` (D-08's expected, non-defect outcome for a shared definition) -- both counts are the SAME small set of paths already listed in the corrective-commit candidates table above, not additional risk.

**Bottom line, after per-file forensic tracing (not just pattern-level boilerplate -- see the Forensic verdict column and `findings-forensics.json`): of the 29 candidates, 28 are false positives with a specific traced explanation each (rename, deliberate downstream rewrite/SDK migration, dead code with zero callers, or HEAD already matching landed).** The remaining 1 survives as a genuine, narrow candidate for 02-06: `tests/unit/test_agentic_tool_env_vars.py` -- the OPENROUTER-primary-falls-back-to-CLAUDE_CLI code path is live and exercised at HEAD (agentic_tool.py supports both api_types and per-tool fallback_api_type), but the regression test covering 'missing OPENROUTER_API_KEY falls back to configured CLAUDE_CLI' was dropped during merge resolution and has no replacement. Real, narrow gap: missing test coverage for a live behavior, not a functional or data loss. Candidate for a follow-up test, not a corrective source-code commit.

## Corrective-commit decision

Decided: 2026-08-06T21:16:24.796Z

**Reviewer decision (Task 1, checkpoint:decision):** `approve-subset`, naming exactly one path.

- **Approved:** `tests/unit/test_agentic_tool_env_vars.py` -- restore `test_openrouter_primary_falls_back_to_claude_cli`, the missing regression test for the live OPENROUTER -> CLAUDE_CLI fallback path (forensic_verdict `confirmed_gap_test_coverage_only`, see above and `findings-forensics.json`).
- **Rejected (false positives, no commit):** all other 28 `landed_dropped_or_altered` candidates -- `.gitignore`, both `skills/*/SKILL.md` entries, `skills/tooluniverse/{.env.template,CHECKLIST.md,references/general-strategies.md}`, `src/tooluniverse/{admetai_tool,agentic_tool,brenda_tool,cli,ctd_tool,default_config,execute_function,foldseek_tool,gwas_tool,llm_clients,rdkit_cheminfo_tool,sabdab_tool,therasabdab_tool,tool_finder_embedding,unified_guideline_tools,uniprot_tool,xml_tool}.py`, `src/tooluniverse/data/{broken_apis/oxo_tools.json,oxo_tools.json}`, `tests/integration/{test_compose_tool.py,test_tool_integration.py}`, `tests/tools/test_brenda_tool.py`. Each carries its own traced `forensic_verdict` (no_definition_delta / head_matches_landed / repaired_at_head / false_positive_superseded / false_positive_renamed / dead_code_drop_no_functional_impact) in the candidates table above -- landed content already matches, or the apparent drop is a rename or a deliberate downstream rewrite, verified against HEAD source, not inferred.
- **Flagged assumptions (A1, A2, A3):** all three accepted as resolved, on the measured evidence already recorded in this document and in `preservation-reclass.json` / `union.json`. None overturned.
- **Branch to commit on:** `docs/gsd-codebase-map`, per D-06b.

`git status --porcelain -- src/ tests/ pyproject.toml uv.lock` was empty at the moment this decision was recorded.

