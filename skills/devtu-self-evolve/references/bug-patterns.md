# Bug Patterns Reference

Detailed code-level fix patterns discovered through role-play debug rounds.

## Table of Contents
- [Regex Overmatch: Mutation vs Fusion](#regex-overmatch)
- [Silent Parameter Alias](#silent-parameter-alias)
- [Always-Fires Conditional](#always-fires-conditional)
- [Silent Normalization](#silent-normalization)
- [Notation / Case Sensitivity](#notation-case)
- [Truncation Not Top-Level](#truncation)
- [Gene Symbol Substring Match](#gene-symbol)
- [try/except Indentation](#try-except)
- [Multi-Word Search Hints](#multi-word-search)
- [Expression Units Inference](#expression-units)
- [Auto-Selected vs Explicit Study](#auto-selected-study)
- [CIViC Therapy + AND Logic](#civic-therapy-and)

---

## Regex Overmatch: Mutation vs Fusion {#regex-overmatch}

**Tools**: civic_search_evidence_items, civic_search_variants
**Bug IDs**: BUG-56A-001

A regex that normalizes `GENE1-GENE2` fusion notation can accidentally match `GENE-MutationCode` (e.g., `EGFR-T790M`, `BRAF-V600E`, `KRAS-G12C`) because mutation codes start with an uppercase letter.

**Fix**: Use a lambda that checks if the second part matches HGVS protein-change format before applying the substitution:
```python
def _maybe_fuse(m):
    second = m.group(2)
    # Protein-change: single letter + digits + letter/asterisk (e.g. T790M, V600E, G12C)
    if re.match(r"^[A-Z]\d+[A-Z*]?$", second):
        return m.group(0)  # leave unchanged
    return m.group(1) + "::" + second

normalized = re.sub(r"\b([A-Z][A-Z0-9]*)-([A-Z][A-Z0-9]+)\b", _maybe_fuse, mol_profile)
```

When the input matches the mutation pattern and returns 0 results, add a hint:
```python
elif re.search(r"\b[A-Z][A-Z0-9]*-[A-Z]\d+[A-Z*]?\b", mol_profile):
    space_form = mol_profile.replace("-", " ", 1)
    mp_warn += f" If '{mol_profile}' is a point mutation, try molecular_profile='{space_form}'..."
```

---

## Silent Parameter Alias

**Tools**: SYNERGxDB_search_combos
**Bug IDs**: BUG-55A-011

Users pass `cancer_type` but tool only accepts `sample`, `tissue_name`, `tissue`. Parameter silently dropped → all-tissue results returned with `status: "success"`.

**Fix**:
```python
sample = (
    arguments.get("sample")
    or arguments.get("tissue_name")
    or arguments.get("tissue")
    or arguments.get("cancer_type")  # ADD aliases here
)
```

---

## Always-Fires Conditional

**Tools**: GtoPdb_get_interactions
**Bug IDs**: BUG-55A-002, BUG-55A-003, BUG-55B-001

`item.get("approved")` on interaction records returns `None` always (field only exists on `/ligands` objects). So `has_approved` was always `False` → conditional note always fired. Also used wrong category language ("kinase/enzyme") for GPCR targets.

**Fix**: Remove the conditional check; always emit the note as factual guidance. Use neutral language; embed the queried gene symbol:
```python
if isinstance(data, list) and len(data) > 0:
    _chembl_target = gene_symbol or result.get("queried_target", {}).get("name", "the target")
    result["coverage_note"] = (
        "GtoPdb interactions list pharmacological research compounds — approved "
        "drugs for this target may not be represented. For approved drugs and "
        "clinical compounds, use ChEMBL_get_drug_mechanisms or "
        f"ChEMBL_search_compounds with target_name='{_chembl_target}'."
    )
```

---

## Silent Normalization

**Tools**: civic_search_evidence_items, civic_search_variants
**Bug IDs**: BUG-55A-008, BUG-55B-005

CIViC normalizes therapy (lowercase → Title Case) and molecular_profile (BCR-ABL1 → BCR::ABL1) without disclosing the transformation. Users debugging empty results can't see what was tried.

**Fix**: Track pre-normalization values, add a `normalization_note` field to the result:
```python
_therapy_normalized_from = None
_mp_normalized_from = None

# When normalizing therapy:
_therapy_normalized_from = therapy
arguments["therapy"] = therapy.title()

# After result is built:
_norm_parts = []
if _therapy_normalized_from:
    _norm_parts.append(f"therapy '{_therapy_normalized_from}' → '{arguments.get('therapy')}' (CIViC uses Title Case)")
if _mp_normalized_from:
    _norm_parts.append(f"molecular_profile '{_mp_normalized_from}' → '{arguments.get('molecular_profile')}' ...")
if _norm_parts:
    result["normalization_note"] = "Input auto-normalized: " + "; ".join(_norm_parts) + "."
```

---

## Notation / Case Sensitivity {#notation-case}

**Tools**: civic_search_evidence_items
**Bug IDs**: BUG-55B-005 (fusion), BUG-53B-002 (therapy case)

CIViC uses `::` for gene fusions (`BCR::ABL1 Fusion`, `EML4::ALK Fusion`). Users write hyphenated forms (`BCR-ABL1`) → 0 results.
CIViC therapy names are Title Case (`"Sotorasib"` not `"sotorasib"`).

**Fix (fusion normalization)**:
```python
import re as _re
mol_profile = arguments.get("molecular_profile")
if mol_profile and isinstance(mol_profile, str):
    normalized_mp = _re.sub(
        r"\b([A-Z][A-Z0-9]*)-([A-Z][A-Z0-9]+)\b",
        r"\1::\2",
        mol_profile,
    )
    if normalized_mp != mol_profile:
        _mp_normalized_from = mol_profile
        arguments = dict(arguments)
        arguments["molecular_profile"] = normalized_mp
```

**Fix (therapy case)**:
```python
if therapy == therapy.lower() or therapy == therapy.upper():
    _therapy_normalized_from = therapy
    arguments["therapy"] = therapy.title()
```

---

## Truncation Not Top-Level {#truncation}

**Tools**: CancerPrognosis_get_gene_expression
**Bug IDs**: BUG-55A-006

Truncation info (e.g., 500 of 1100 samples returned) buried inside `data.note` string. Researchers reading top-level fields miss it.

**Fix**: Add top-level flags:
```python
response = {"status": "success", "data": result_data}
if len(values) > max_samples:
    response["truncated"] = True
    response["truncation_note"] = (
        f"Returning {len(values[:max_samples])} of {len(values)} samples. "
        f"Pass max_samples={len(values)} (up to 2000) to retrieve the full dataset."
    )
return response
```

---

## Gene Symbol Substring Match {#gene-symbol}

**Tools**: GtoPdb_get_interactions
**Bug IDs**: BUG-54B-001

`?name=AR` returns all targets containing "AR" (13+ targets). `?geneSymbol=AR` is the unambiguous HGNC lookup.

**Fix**: Try `?geneSymbol=` first; fall back to `?name=` if nothing returned:
```python
gs_url = f"{base_url}/targets?{urlencode({'geneSymbol': gene_symbol})}"
gs_resp = request_with_retry(...)
if gs_resp.status_code == 200:
    gs_targets = gs_resp.json()
    if gs_targets:
        target_id = gs_targets[0]["targetId"]

# Fall back to ?name= only if geneSymbol returned nothing
if target_id is None:
    lookup_url = f"{base_url}/targets?{urlencode({'name': gene_symbol})}"
    ...
```

---

## try/except Indentation {#try-except}

Every `try:` MUST have an `except` at the **exact same indentation level**. A common error is placing code after `try:` at the same level as the `try:` keyword — Python sees the try block as having no except.

```python
# CORRECT
try:              # 16 spaces
    resp = ...    # 20 spaces (inside try)
    if resp.ok:   # 20 spaces (still inside try)
        ...
except Exception: # 16 spaces — matches try
    pass

# WRONG — SyntaxError
try:              # 16 spaces
    resp = ...    # 20 spaces
if resp.ok:       # 16 spaces — OUTSIDE try, before except!
    ...
except Exception: # 16 spaces — Python: "try without except"
    pass
```

---

## Multi-Word Search Hints {#multi-word-search}

**Tools**: GtoPdb_search_targets, GtoPdb_search_ligands
**Bug IDs**: BUG-54B-002

`name="androgen receptor"` returns empty — GtoPdb text search doesn't reliably match multi-word phrases.

**Fix**: When count=0 and query has a space, add a hint suggesting first word only:
```python
if result["count"] == 0 and name_q and " " in str(name_q):
    first_word = str(name_q).split()[0]
    result["multi_word_hint"] = (
        f"GtoPdb text search may not match multi-word phrases like '{name_q}'. "
        f"Try a single keyword: name='{first_word}'."
    )
```

---

## Expression Units Inference {#expression-units}

**Tools**: CancerPrognosis_get_gene_expression
**Bug IDs**: BUG-54A-002

`_get_expression_units(profile_id)` infers units from the profile ID string. Some studies use misleading suffixes (e.g., `aml_ohsu_2022` uses `_rna_seq_v2_mrna` but stores log2 RPKM).

**Fix**: Return `(profile_id, profile_name)` from `_get_mrna_profile()` and prefer the actual API description over inference:
```python
def _get_expression_units(self, profile_id, profile_name=None):
    if profile_name:
        return profile_name  # Prefer actual API name
    # ... fallback inference from profile_id
```

---

## Auto-Selected vs Explicit Study {#auto-selected-study}

**Tools**: CancerPrognosis_get_gene_expression
**Bug IDs**: BUG-54A-004

`study_note` always said "Auto-selected study_id=..." even when user explicitly passed a full study ID like `brca_tcga`.

**Fix**: Detect explicit specification and use a different message:
```python
study_was_explicit = (
    cancer == study_id_arg
    and study_id_arg
    and "_" in str(study_id_arg)
    and str(study_id_arg).upper() not in TCGA_STUDY_MAP
    and str(study_id_arg).upper() not in _CANCER_NAME_ALIASES
)
"study_note": (
    f"Using explicitly specified study_id='{study_id}'."
    if study_was_explicit
    else f"Auto-selected study_id='{study_id}'. Use CancerPrognosis_search_studies "
         "to find alternative cohorts for this cancer type."
),
```

---

## CIViC Therapy + AND Logic {#civic-therapy-and}

**Tools**: civic_search_evidence_items, civic_search_variants
**Bug IDs**: BUG-54A-001, BUG-54A-005

1. When both `query` and `variant_name` are provided, one silently wins. Fix: apply AND logic.
2. When `molecular_profile + therapy` returns 0, silently fails. Fix: auto-probe without therapy to surface available therapy names.

**Fix (AND logic)**:
```python
raw_query = arguments.get("query")
raw_variant_name = arguments.get("variant_name") or arguments.get("variant")
_both = raw_query and raw_variant_name and raw_query != raw_variant_name
if _both:
    query_term = raw_query
    _secondary_term = raw_variant_name
else:
    query_term = raw_query or raw_variant_name
    _secondary_term = None

# Later, apply AND filter:
if _secondary_term:
    filtered = [v for v in filtered if _secondary_term.lower() in v.get("name","").lower()]
    result["filter_note"] = f"Applied AND logic for query+variant_name."
```

**Fix (therapy auto-probe)**:
```python
if mol_profile and therapy and not disease and len(evidence_nodes) == 0:
    probe_args = {k: v for k, v in arguments.items() if k != "therapy"}
    probe_nodes = civic_query(probe_args)
    available_therapies = sorted({
        t.get("name") for node in probe_nodes
        for t in node.get("therapies", []) if t.get("name")
    })
    result["therapy_warning"] = (
        f"No evidence for '{mol_profile}' + therapy='{therapy}'. "
        f"Available therapies: {available_therapies[:10]}"
    )
```
