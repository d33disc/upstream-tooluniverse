# Tools Reference: Statistical Modeling Skill

This file contains full parameter tables for ToolUniverse API tools used to retrieve data before statistical modeling, and quick-reference tables for the Python packages used in modeling.

---

## ToolUniverse API Tools

Agents call these tools via:

```
mcp__tooluniverse__execute_tool(tool_name="...", arguments={...})
```

### Clinical Trial Data

#### `clinical_trials_search`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | One of `"search_studies"`, `"get_study"`, `"list_conditions"` |
| `condition` | string | No | Disease or condition (e.g., `"breast cancer"`) |
| `intervention` | string | No | Drug or intervention name |
| `status` | string | No | `"RECRUITING"`, `"COMPLETED"`, etc. |
| `limit` | integer | No | Max results (default 10) |
| `nct_id` | string | No | Required when `action="get_study"` |

Returns: `{total_count, studies: [{nct_id, title, status, conditions, interventions, ...}]}`

#### `get_clinical_trial_eligibility_criteria`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nct_ids` | array of strings | Yes | List of NCT IDs (e.g., `["NCT12345678"]`) |
| `eligibility_criteria` | string | No | `"all"` (default), `"inclusion"`, `"exclusion"` |

Returns: `[{NCT ID, eligibility_criteria: {inclusion, exclusion}}]`

---

### Drug Safety / Adverse Events (FAERS)

#### `FAERS_calculate_disproportionality`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drug_name` | string | Yes | Drug name as reported in FAERS |
| `adverse_event` | string | Yes | Adverse event MedDRA preferred term |

Returns: `{metrics: {PRR, ROR, IC, EBGM}, signal_detection: {is_signal, method}}`

Key metrics:
- `PRR` — Proportional Reporting Ratio (signal if > 2 and N >= 3)
- `ROR` — Reporting Odds Ratio with 95% CI
- `IC` — Information Component (Bayesian)

#### `FAERS_stratify_by_demographics`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drug_name` | string | Yes | Drug name |
| `adverse_event` | string | Yes | Adverse event term |
| `stratify_by` | string | Yes | `"sex"`, `"age_group"`, `"reporter_country"` |

Returns: Stratified count table with ROR per stratum.

#### `FAERS_count_patient_reaction`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `medicinalproduct` | string | Yes | Drug name as stored in FAERS |
| `limit` | integer | No | Max reactions to return (default 20) |

Returns: `[{term, count}]` sorted by count descending.

---

### Gene-Disease Evidence (Open Targets)

#### `OpenTargets_target_disease_evidence`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ensemblId` | string | Yes | Ensembl gene ID (e.g., `"ENSG00000141510"`) |
| `efoId` | string | Yes | EFO disease ID (e.g., `"EFO_0000305"`) |
| `datasourceIds` | array | No | Filter by data source (e.g., `["gwas_catalog"]`) |
| `size` | integer | No | Max evidence records (default 10) |

Returns: Evidence records with score, data source, and publication details.

#### `OpenTargets_get_associated_targets_by_disease_efoId`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `efoId` | string | Yes | EFO disease ID |
| `size` | integer | No | Number of targets to return (default 10) |
| `sortBy` | string | No | `"score"` (default) |

Returns: `{data: {disease: {associatedTargets: {rows: [{target, score}]}}}}`

---

### Literature

#### `PubMed_search_articles`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | PubMed search query (supports MeSH terms and field tags) |
| `max_results` | integer | No | Max articles to return (default 10) |
| `sort` | string | No | `"relevance"` (default) or `"date"` |

Returns: List of article dicts with `{pmid, title, abstract, authors, journal, year}`.

---

### Biomarkers

#### `fda_pharmacogenomic_biomarkers`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `drug_name` | string | No | Filter by drug name |
| `biomarker` | string | No | Gene or biomarker name (e.g., `"CYP2D6"`) |
| `therapeutic_area` | string | No | Therapeutic area filter |

Returns: List of FDA biomarker-drug labeling entries with `{drug, biomarker, effect, labeling_section}`.

---

## Python Package Quick Reference

### statsmodels — Model Fitting Functions

| Function | Purpose | Key Parameters |
|----------|---------|---------------|
| `smf.ols(formula, data)` | OLS linear regression | R-style formula, DataFrame |
| `smf.logit(formula, data)` | Binary logistic regression | formula, data; `.fit(disp=0)` |
| `smf.mnlogit(formula, data)` | Multinomial logistic | formula, data |
| `smf.mixedlm(formula, data, groups)` | Linear mixed-effects | formula, data, groups, re_formula |
| `smf.gee(formula, groups, data, family)` | GEE models | formula, groups, data, family |
| `sm.OLS(y, X)` | OLS matrix interface | y (array), X (with constant) |
| `sm.Logit(y, X)` | Logistic matrix interface | y (binary array), X (array) |
| `sm.MNLogit(y, X)` | Multinomial matrix interface | y (coded), X (array) |
| `OrderedModel(y, X, distr)` | Ordinal logistic | y (integer codes), X, distr='logit' |

### statsmodels — Diagnostics

| Function | Purpose | Returns |
|----------|---------|---------|
| `het_breuschpagan(resid, exog)` | Heteroscedasticity | (LM, p, F, Fp); p > 0.05 = homoscedastic |
| `durbin_watson(resid)` | Autocorrelation | DW statistic; ~2 = no autocorrelation |
| `variance_inflation_factor(X, i)` | Multicollinearity | VIF; > 10 = high collinearity |
| `scipy.stats.shapiro(resid)` | Normality of residuals | (W, p); p > 0.05 = normal |

### lifelines — Survival Analysis

| Class / Function | Purpose | Key Parameters |
|-----------------|---------|---------------|
| `CoxPHFitter()` | Cox PH model | `.fit(df, duration_col, event_col)` |
| `KaplanMeierFitter()` | KM estimation | `.fit(durations, event_observed)` |
| `logrank_test(T1, T2, E1, E2)` | Log-rank test | durations and events for 2 groups |
| `NelsonAalenFitter()` | Cumulative hazard | `.fit(durations, event_observed)` |

Cox model result attributes:
- `cph.hazard_ratios_` — dict of HRs per covariate
- `cph.concordance_index_` — C-statistic (discrimination)
- `cph.summary` — full results table with CIs and p-values
- `cph.check_assumptions(df)` — test proportional hazards assumption

### scipy.stats — Statistical Tests

| Function | Purpose | Returns |
|----------|---------|---------|
| `ttest_ind(a, b)` | Independent t-test | (t, p) |
| `ttest_rel(a, b)` | Paired t-test | (t, p) |
| `mannwhitneyu(a, b)` | Mann-Whitney U | (U, p) |
| `chi2_contingency(table)` | Chi-square test | (chi2, p, dof, expected) |
| `fisher_exact(table)` | Fisher's exact test | (OR, p) |
| `f_oneway(*groups)` | One-way ANOVA | (F, p) |
| `kruskal(*groups)` | Kruskal-Wallis | (H, p) |
| `wilcoxon(a, b)` | Wilcoxon signed-rank | (W, p) |
| `shapiro(data)` | Shapiro-Wilk normality | (W, p) |

### scikit-learn — Supplementary

| Class | Purpose | Key Methods |
|-------|---------|------------|
| `LogisticRegression(multi_class='multinomial')` | Multinomial logistic | `.fit(X, y)`, `.predict_proba(X)` |
| `StandardScaler()` | Feature scaling | `.fit_transform(X)` |
| `LabelEncoder()` | Label encoding | `.fit_transform(y)` |

---

## Common Pitfalls (Quick Reference)

1. **OrderedModel threshold params**: `model.params` includes cutpoint parameters after predictors. Slice `model.params[:n_predictors]` for OR computation.
2. **Reference levels**: First alphabetical level is default. Use `C(var, Treatment(reference='X'))` to override.
3. **Convergence**: OrderedModel needs `method='bfgs'`, `maxiter=200+`. Logistic: `maxiter=100`, `disp=0`.
4. **Missing data**: Formula API drops NA rows silently; matrix API does not.
5. **Aggregate vs. per-feature ANOVA**: Aggregate inflates F ~100-200x for gene expression — use per-feature by default.
6. **OR direction**: OR > 1 = increased odds, OR < 1 = decreased odds.
7. **HR direction**: HR > 1 = increased hazard (worse survival), HR < 1 = decreased hazard.
8. **Formula interaction syntax**: `A:B` = interaction only; `A*B` = A + B + A:B.
