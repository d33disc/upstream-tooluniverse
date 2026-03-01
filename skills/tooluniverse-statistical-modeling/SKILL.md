---
name: tooluniverse-statistical-modeling
description: Perform statistical modeling and regression analysis on biomedical datasets. Supports linear regression, logistic regression (binary/ordinal/multinomial), mixed-effects models, Cox proportional hazards survival analysis, Kaplan-Meier estimation, and comprehensive model diagnostics. Extracts odds ratios, hazard ratios, confidence intervals, p-values, and effect sizes. Designed to solve BixBench statistical reasoning questions involving clinical/experimental data. Use when asked to fit regression models, compute odds ratios, perform survival analysis, run statistical tests, or interpret model coefficients from provided data.
---

# Statistical Modeling for Biomedical Data Analysis

Comprehensive statistical modeling skill for fitting regression models, survival models, and mixed-effects models to biomedical data. Produces publication-quality statistical summaries with odds ratios, hazard ratios, confidence intervals, and p-values.

## Supported Model Types

- **Linear Regression** - OLS for continuous outcomes with diagnostic tests
- **Logistic Regression** - Binary, ordinal, and multinomial models with odds ratios
- **Survival Analysis** - Cox proportional hazards and Kaplan-Meier curves
- **Mixed-Effects Models** - LMM/GLMM for hierarchical or repeated measures data
- **ANOVA** - One-way/two-way ANOVA, per-feature ANOVA for omics data
- **Statistical Tests** - t-tests, chi-square, Mann-Whitney, Kruskal-Wallis, and others

## When to Use This Skill

Apply when the user asks:
- "What is the odds ratio of X associated with Y?"
- "What is the hazard ratio for treatment?"
- "Fit a linear regression of Y on X1, X2, X3"
- "Perform ordinal logistic regression for severity outcome"
- "What is the Kaplan-Meier survival estimate at time T?"
- "What is the percentage reduction in odds ratio after adjusting for confounders?"
- "Run a mixed-effects model with random intercepts"
- "Test if gene/miRNA expression differs across cell types"

---

## Model Selection Decision Tree

```
START: What type of outcome variable?

CONTINUOUS (height, blood pressure, score)
  Independent observations -> Linear Regression (OLS)
  Repeated measures        -> Mixed-Effects Model (LMM)
  Count data               -> Poisson / Negative Binomial

BINARY (yes/no, disease/healthy)
  Independent observations -> Logistic Regression
  Repeated measures        -> Logistic Mixed-Effects (GLMM/GEE)
  Rare events              -> Firth logistic regression

ORDINAL (mild/moderate/severe, stages I/II/III/IV)
                           -> Ordinal Logistic Regression (Proportional Odds)

MULTINOMIAL (>2 unordered categories)
                           -> Multinomial Logistic Regression

TIME-TO-EVENT (survival time + censoring)
  With covariates          -> Cox Proportional Hazards
  Descriptive curves       -> Kaplan-Meier
  Group comparison         -> Log-rank test
```

---

## Workflow

### Phase 0: Data Validation

**Goal**: Load data, identify variable types, check for missing values.

**CRITICAL: Identify the Outcome Variable First**

Before any analysis, verify what you are actually predicting:

1. Read the full question — look for "predict [outcome]", "model [outcome]", or "dependent variable"
2. List all columns in the dataset
3. Match the question to a column; do not create outcome variables from predictors
4. Verify the outcome column exists before proceeding

**Common mistake (bix-51-q3 example)**:
- Wrong: Question mentions "obesity" → assumed outcome = BMI >= 30 (circular with BMI predictor)
- Correct: Reading the full question reveals actual outcome = treatment response (PR vs non-PR)

Steps:
- Load the data file (CSV, TSV, or Excel)
- Print shape: number of rows and columns
- Count missing values per column
- Classify each column: binary (2 unique values), categorical (object with few levels), continuous (numeric with wide range)
- Confirm the outcome column matches the question's target variable

---

### Phase 1: Model Fitting

**Goal**: Fit the appropriate model based on outcome type.

#### Linear Regression

Use when the outcome is continuous and observations are independent.

- Use an R-style formula: `outcome ~ predictor1 + predictor2 + age`
- Fit with OLS via `statsmodels.formula.api.ols`
- Key outputs: coefficient estimates, R-squared, AIC, model summary

#### Logistic Regression (Binary)

Use when the outcome is binary (0/1, yes/no).

- Formula: `disease ~ exposure + age + sex`
- Fit with `statsmodels.formula.api.logit`, pass `disp=0` to suppress iteration output
- Odds ratios = `exp(model.params)`
- Confidence intervals = `exp(model.conf_int())`
- Report OR, 95% CI, and p-value for each predictor

#### Ordinal Logistic Regression

Use when the outcome has ordered categories (e.g., mild/moderate/severe).

- Convert outcome to an ordered `pd.Categorical` with explicit category order
- Use integer codes as the dependent variable
- Fit with `statsmodels.miscmodels.ordinal_model.OrderedModel` with `distr='logit'`
- Use `method='bfgs'` for convergence; increase `maxiter` if needed
- Odds ratios = `exp(model.params[:n_predictors])` — exclude threshold parameters

#### Multinomial Logistic Regression

Use when the outcome has three or more unordered categories.

- Fit with `statsmodels.formula.api.mnlogit` or `statsmodels`'s `MNLogit`
- Results give log-odds relative to the reference category
- Exponentiate coefficients for relative risk ratios

#### Cox Proportional Hazards

Use when the outcome is time-to-event with possible censoring.

- Required columns: duration (time), event indicator (1=event, 0=censored), covariates
- Fit with `lifelines.CoxPHFitter`; call `.fit(df, duration_col=..., event_col=...)`
- Hazard ratio = `cph.hazard_ratios_['covariate']`
- Report concordance index as a measure of model discrimination

#### Kaplan-Meier Estimation

Use to describe survival curves without covariates.

- Fit with `lifelines.KaplanMeierFitter`; call `.fit(durations, event_observed=events)`
- Query survival probability at a specific time with `.predict(t)`
- Compare groups with the log-rank test (`lifelines.statistics.logrank_test`)

#### ANOVA

Use to compare means across three or more groups.

- Single-feature ANOVA: pass group arrays to `scipy.stats.f_oneway(*groups)`
- Returns F-statistic and p-value

**CRITICAL: Multi-feature ANOVA Decision Tree**

When data has multiple features (genes, miRNAs, metabolites), two approaches exist:

```
Question asks for "the F-statistic" comparing [feature] expression across groups?

Are there many features (genes, miRNAs, etc.)?
  YES -> Per-feature ANOVA (Method B) -- DEFAULT for gene expression data
  NO  -> Single-feature ANOVA (Method A)

Question asks about "all features" or a distribution?
  -> Per-feature ANOVA + report summary statistics (median, mean, range)
```

**Method A — Aggregate ANOVA**: Flatten all feature values across all samples per group into one array, then run one ANOVA. Returns a single very large F-statistic. Rarely the correct interpretation for genomics.

**Method B — Per-feature ANOVA** (recommended for genomics): For each gene/miRNA/metabolite, extract that feature's values per group and run a separate ANOVA. Returns one F-statistic per feature. Report median, mean, and range, or identify specific features matching a target range.

Real-world example (BixBench bix-36-q1):
- Question: "What is the F-statistic comparing miRNA expression across immune cell types?" (expected ~0.76-0.78)
- Method A (aggregate): returned 153.8 — WRONG
- Method B (per-miRNA): found two miRNAs with F in [0.76, 0.78] — CORRECT

**Default assumption for gene expression data**: Use per-feature ANOVA.

---

### Phase 2: Model Diagnostics

**Goal**: Check model assumptions and assess fit quality.

#### OLS Diagnostics

- Residual normality: Shapiro-Wilk test (`scipy.stats.shapiro`); p > 0.05 suggests normality
- Heteroscedasticity: Breusch-Pagan test (`statsmodels.stats.diagnostic.het_breuschpagan`); p > 0.05 suggests homoscedasticity
- Multicollinearity: Variance Inflation Factor (`statsmodels.stats.outliers_influence.variance_inflation_factor`); VIF > 10 indicates a problem
- Autocorrelation: Durbin-Watson statistic; values near 2 indicate no autocorrelation

#### Logistic Regression Diagnostics

- Check for complete separation (a predictor perfectly predicts the outcome): watch for very large coefficients and SEs
- Hosmer-Lemeshow goodness-of-fit test for calibration
- Report pseudo R-squared (McFadden's) and AIC

#### Cox Model Diagnostics

- Test the proportional hazards assumption using `cph.check_assumptions(df, p_value_threshold=0.05, show_plots=False)`
- If assumption is violated for a covariate, consider stratifying on that variable
- Report concordance index (C-statistic)

See `references/troubleshooting.md` for common diagnostic issues and remedies.

---

### Phase 3: Interpretation

**Goal**: Generate a clear, publication-quality summary.

#### Interpreting Odds Ratios

- OR > 1: increased odds (e.g., OR = 1.5 means 50% increase in odds)
- OR < 1: decreased odds (e.g., OR = 0.7 means 30% decrease in odds)
- OR = 1: no association
- Always report with 95% CI and p-value
- If CI excludes 1 and p < 0.05: statistically significant

Percentage reduction in odds between unadjusted and adjusted models:

```
pct_reduction = (OR_crude - OR_adjusted) / OR_crude * 100
```

#### Interpreting Hazard Ratios

- HR > 1: increased hazard (worse survival for that group)
- HR < 1: decreased hazard (better survival for that group)
- Report with 95% CI and p-value

#### Reporting Format

For each key predictor, report: `OR=X.XXXX, 95% CI [X.XXXX, X.XXXX], p=X.XXXXXX`

Round to the precision requested; default to 4 decimal places for effect sizes, 6 for p-values.

---

## Common BixBench Patterns

### Pattern 1: Odds Ratio from Ordinal Regression

Question: "What is the odds ratio of disease severity associated with exposure?"

1. Identify ordinal outcome (mild/moderate/severe)
2. Encode as ordered categorical variable
3. Fit ordinal logistic regression (proportional odds model)
4. Extract OR = exp(coefficient for exposure), excluding threshold parameters
5. Report with CI and p-value

### Pattern 2: Percentage Reduction in Odds

Question: "What is the percentage reduction in OR after adjusting for confounders?"

1. Fit unadjusted model with exposure only; extract OR_crude
2. Fit adjusted model with exposure + confounders; extract OR_adjusted
3. Compute: `(OR_crude - OR_adjusted) / OR_crude * 100`

### Pattern 3: Interaction Effects

Question: "What is the odds ratio for the interaction between A and B?"

1. Fit logistic model with `outcome ~ A * B + covariates` (the `*` includes main effects and interaction)
2. Interaction OR = exp(coefficient for `A:B`)
3. Report interaction OR, CI, p-value

### Pattern 4: Survival Analysis

Question: "What is the hazard ratio for treatment?"

1. Load survival data with time, event indicator, and covariates
2. Fit Cox proportional hazards model
3. Extract HR = exp(coefficient for treatment)
4. Check proportional hazards assumption
5. Report HR with CI and concordance index

### Pattern 5: Multi-feature ANOVA (Gene Expression)

Question: "What is the F-statistic comparing miRNA expression across cell types?"

1. Recognize that data contains multiple features (not a single outcome)
2. Use per-feature ANOVA — compute F-statistic for each feature independently
3. Summarize the distribution; if question specifies a target value or range, identify matching features
4. Do not use aggregate ANOVA; it inflates the F-statistic by orders of magnitude

---

## Known Gotchas

### 1. OrderedModel Coefficient Interpretation

In `statsmodels.miscmodels.ordinal_model.OrderedModel`, a positive coefficient means higher odds of being in a HIGHER (more severe) category. This matches R's `polr` with `method="logistic"`. Do not reverse the sign.

### 2. Threshold Parameters in OrderedModel

`model.params` includes threshold (cutpoint) parameters after the predictor coefficients. When computing odds ratios for predictors, slice only the first `n_predictors` entries: `model.params[:len(X.columns)]`. Do not exponentiate threshold parameters.

### 3. Reference Level Defaults

In statsmodels formula API, the reference level for categorical variables is the first level alphabetically. Use `C(var, Treatment(reference='level'))` to set an explicit reference.

### 4. Aggregate vs. Per-feature ANOVA

For gene expression datasets, aggregate ANOVA (flattening all features) returns F-statistics ~100-200x larger than per-feature ANOVA. The question almost always expects per-feature. Default to per-feature unless the question explicitly asks for a global test.

### 5. Outcome Variable Identification

Never derive the outcome from a predictor column (e.g., creating a "high BMI" flag when BMI is also a predictor). Always read the full question to find which column is the actual dependent variable. List all columns before modeling.

### 6. Missing Data Handling

The statsmodels formula API silently drops rows with any NA values in the formula variables. The matrix API (`sm.Logit(y, X)`) does not — it will raise an error or return NaN results. Always check missingness before fitting.

### 7. Convergence Failures

For ordinal models: use `method='bfgs'` and set `maxiter=200` or higher. For logistic regression: use `disp=0` to suppress output and `maxiter=100`. If a model fails to converge, scale continuous predictors or remove collinear variables.

### 8. Formula Syntax for Interactions

In R-style formulas, `A:B` adds only the interaction term; `A*B` adds main effects A, B, and the interaction A:B. Use `A*B` when you want to include main effects automatically.

### 9. Hazard Ratio Direction

HR > 1 means the group has a higher hazard (shorter survival). A treatment that improves survival will have HR < 1. Confirm which group is the reference before reporting.

### 10. Proportional Hazards Violation

If `cph.check_assumptions()` flags a variable, the Cox model HR for that variable may be unreliable. Consider stratifying on the violating variable (`strata=['var']` in `cph.fit()`), which removes its HR from output but adjusts for it.

---

## Statsmodels vs. Scikit-learn

| Use Case | Library | Reason |
|----------|---------|--------|
| Inference (p-values, CIs, ORs) | statsmodels | Full statistical output |
| Prediction (accuracy, AUC) | scikit-learn | Better prediction tools |
| Mixed-effects models | statsmodels | Only standard option |
| Regularization (LASSO, Ridge) | scikit-learn | Better optimization |
| Survival analysis | lifelines | Specialized library |

General rule: Use statsmodels for BixBench questions — they ask for p-values, ORs, and HRs.

---

## Abbreviated Tool Reference

While this skill is primarily computational, ToolUniverse tools can retrieve data before modeling.

| Use Case | Tool |
|----------|------|
| Clinical trial data | `clinical_trials_search` |
| Drug safety outcomes | `FAERS_calculate_disproportionality` |
| Gene-disease associations | `OpenTargets_target_disease_evidence` |
| PubMed literature | `PubMed_search_articles` |
| Biomarker data | `fda_pharmacogenomic_biomarkers` |

See `references/tools.md` for complete parameter tables and return formats.

---

## Completeness Checklist

Before finalizing any statistical analysis:

- [ ] Outcome variable identified: verified which column is the actual outcome
- [ ] Data validated: N, missing values, variable types confirmed
- [ ] Multi-feature data identified: if data has multiple features (genes, miRNAs), use per-feature ANOVA
- [ ] Model appropriate: outcome type matches model family
- [ ] Assumptions checked: relevant diagnostics performed
- [ ] Effect sizes reported: OR/HR/Cohen's d with 95% CI
- [ ] P-values reported: with correction if multiple testing applies
- [ ] Model fit assessed: R-squared, AIC/BIC, or concordance index
- [ ] Results interpreted: plain-language interpretation provided
- [ ] Precision correct: numbers rounded to requested decimal places
- [ ] Confounders addressed: adjusted analyses performed if applicable

---

## Key Principles

1. Data-first — inspect and validate data before any modeling
2. Model selection by outcome type — use the decision tree above
3. Assumption checking — verify linearity, proportional hazards, normality as appropriate
4. Complete reporting — always report effect sizes, CIs, p-values, and model fit statistics
5. Confounder awareness — adjust for confounders when specified or clinically relevant
6. Round correctly — match the precision requested (typically 2-4 decimal places)

---

## Package Requirements

```
statsmodels>=0.14.0
scikit-learn>=1.3.0
lifelines>=0.27.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
```

---

## File Structure

```
tooluniverse-statistical-modeling/
├── SKILL.md                    # This file
├── TOOLS_REFERENCE.md          # Legacy tool catalog (superseded by references/tools.md)
├── references/
│   ├── tools.md                # Full parameter tables for ToolUniverse tools
│   ├── logistic_regression.md  # Detailed logistic examples
│   ├── ordinal_logistic.md     # Ordinal logit guide
│   ├── cox_regression.md       # Survival analysis guide
│   ├── linear_models.md        # OLS and mixed-effects
│   ├── bixbench_patterns.md    # 15+ question patterns
│   └── troubleshooting.md      # Diagnostic issues and remedies
└── scripts/
    ├── format_statistical_output.py
    └── model_diagnostics.py
```

---

## References

- statsmodels: https://www.statsmodels.org/
- lifelines: https://lifelines.readthedocs.io/
- scikit-learn: https://scikit-learn.org/
- Ordinal models: `statsmodels.miscmodels.ordinal_model.OrderedModel`
