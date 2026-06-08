# Schema-Teeth Remediation Queue (audit #2)

Source: [[project_sdk_correctness_blind_spots]]. Crown enabler shipped (PR #51:
missing jsonschema now fails loud). Pattern proven + shipped on openalex (PR #54).

## The proven pattern (apply per tool; oracle = LIVE API, never the schema)
1. Run the tool live with its `test_examples[0]` args; capture `result["data"]`.
2. Derive `required` = keys present in EVERY real sample (>=2 samples; over-tighten = false reds).
3. If root `type` is `["object","null"]` -> `"object"` (a success is never null);
   if `array` w/o `items` -> add `items`; if `object` w/o `required`/`properties` -> add both.
4. DUAL-VERIFY: live payload(s) PASS; `{}`, `null`, `{"error":...}` REJECTED.
5. If the API is down / key missing / output is genuinely free-form -> DEFER, do not guess.

## DETERMINISTIC — need teeth (100 tools, by file; verify determinism first)
Some "DET" files are infra/meta (compose/finder/embedding/smolagent/output_summarization/
tool_composition) and may legitimately stay loose — confirm before tightening.

```
13  nvidia_nim_tools.json          5  crossref_tools.json       1  cadd_tools.json
 9  proteins_api_tools.json        5  intact_tools.json         1  core_tools.json
 6  faers_analytics_tools.json     4  finder_tools.json*        1  appris_tools.json
 6  emdb_tools.json                4  cellxgene_census_tools    1  uspto_downloader_tools
 6  monarch_v3_tools.json          3  enrichr_ext_tools.json    1  expression_atlas_tools
 5  embedding_tools.json*          3  mutalyzer_tools.json      1  pubtator_tools.json
 5  compose_tools.json*            3  file_download_tools.json  1  hpa_tools.json
 5  crossref_tools.json            2  url_fetch_tools.json      1  biothings_tools.json
                                   2  cellosaurus_tools.json    + ~8 singletons
```
(* = verify determinism; may be intentionally loose)

## GENERATIVE — leave loose (41 tools): all *Agent tools (drug_discovery_agents.json),
special_tools Finish/CallAgent, etc. Prose output; tightening manufactures false reds.

## Execution: ideal fleet work (high-N, mechanical, live-oracle-verifiable) per
[[reference_fleet_token_economics]]. Each tool: live-run -> derive -> dual-verify -> commit.
Full machine-readable list: regenerate via the scan in [[project_sdk_correctness_blind_spots]].
