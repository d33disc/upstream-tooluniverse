# ToolUniverse Skill Routing Test Report

**Date**: 2026-02-14
**Skill Tested**: `/tooluniverse` (Router + General Strategies)
**Test Purpose**: Evaluate routing logic, general strategy application, and identify gaps/issues

---

## Executive Summary

The `/tooluniverse` skill was tested across 5 scenarios designed to evaluate its routing capabilities and fallback strategies. The skill **consistently failed to route to specialized skills** and instead displayed the general strategy documentation to the user. This represents a **critical failure** in the skill's core functionality as a router.

### Key Findings

- **Routing Accuracy**: 0/5 scenarios correctly routed to specialized skills
- **Clarification Behavior**: 0/5 scenarios asked for clarification when appropriate
- **General Strategy Application**: Not evaluated (skill never reached this stage)
- **Primary Issue**: Skill only displays documentation instead of executing routing logic

---

## Test Scenario Results

### Scenario 1: Clear Specialized Skill Match

**Question**: "I need a comprehensive research report on breast cancer including genetics, treatments, and clinical trials"

**Expected Behavior**: Should route to `/tooluniverse-disease-research`

**Actual Behavior**:
- Skill loaded successfully
- Instead of routing, the skill **displayed the entire SKILL.md documentation** to the user
- No routing decision was made
- No invocation of `/tooluniverse-disease-research` occurred

**Analysis**:
- Keywords clearly matched: "comprehensive research report", "disease" (breast cancer), "genetics", "treatments", "clinical trials"
- According to SKILL.md routing table (line 33): "research **disease**" should route to `/tooluniverse-disease-research`
- This is an **unambiguous case** that should have triggered immediate routing

**Result**: ❌ **FAILED** - Did not route to specialized skill

---

### Scenario 2: Tool Discovery (General Strategy)

**Question**: "How can I find all ToolUniverse tools related to metabolomics and mass spectrometry?"

**Expected Behavior**: Should use general Strategy 1 (Tool Discovery) - no specialized skill exists for this

**Actual Behavior**:
- Skill loaded successfully
- Displayed the entire SKILL.md documentation to the user
- No tool discovery queries were executed
- No guidance was provided beyond showing the documentation

**Analysis**:
- This is a valid use case for general strategies (no specialized skill for "tool discovery")
- Should have proceeded to execute Strategy 1: Exhaustive Tool Discovery
- Should have used `Tool_Finder_Keyword`, `Tool_Finder_LLM`, or `Tool_Finder` to search for metabolomics and mass spectrometry tools
- Instead, the skill treated this as a documentation request

**Result**: ❌ **FAILED** - Did not execute general strategies

---

### Scenario 3: Ambiguous Request

**Question**: "Tell me about aspirin"

**Expected Behavior**: Should ask user to clarify intent (drug profile? safety? repurposing? chemical compound retrieval?)

**Actual Behavior**:
- Skill loaded successfully
- Displayed the entire SKILL.md documentation to the user
- No clarifying question was asked
- No routing or strategy execution occurred

**Analysis**:
- "Tell me about aspirin" is ambiguous and matches multiple use cases:
  - Drug profile → `/tooluniverse-drug-research`
  - Safety profile → `/tooluniverse-pharmacovigilance`
  - Chemical compound retrieval → `/tooluniverse-chemical-compound-retrieval`
  - Drug repurposing → `/tooluniverse-drug-repurposing`
- According to SKILL.md Step 0 (line 153-181), unclear scope should trigger clarification
- The skill should have asked: "Would you like a comprehensive drug profile, safety analysis, chemical compound data, or repurposing opportunities for aspirin?"

**Result**: ❌ **FAILED** - Did not ask for clarification

---

### Scenario 4: Multi-Database Query Strategy

**Question**: "I want to find protein interaction data for TP53 from multiple databases and compare their coverage"

**Expected Behavior**:
- **Option A** (preferred): Route to `/tooluniverse-protein-interactions` (specialized skill exists)
- **Option B** (acceptable): Use general Strategy 3 (Query Multiple Databases)

**Actual Behavior**:
- Skill loaded successfully
- Displayed the entire SKILL.md documentation to the user
- No routing occurred
- No database queries were executed

**Analysis**:
- Keywords clearly match: "protein interaction", "multiple databases", "compare coverage"
- According to SKILL.md routing table (line 71): "**protein interactions**" should route to `/tooluniverse-protein-interactions`
- This specialized skill exists specifically for "Multi-database PPI aggregation, network analysis, quality scoring"
- Should have been an immediate route to the specialized skill

**Result**: ❌ **FAILED** - Did not route to specialized skill

---

### Scenario 5: Completely Novel Task

**Question**: "I want to build a custom workflow that combines gene expression data with protein structure predictions and GWAS data to find novel drug targets"

**Expected Behavior**: Should use general strategies (no single specialized skill covers this complex workflow)

**Actual Behavior**:
- Skill loaded successfully
- Displayed the entire SKILL.md documentation to the user
- No general strategies were applied
- No tool discovery or workflow guidance provided

**Analysis**:
- This is a legitimate use case for general strategies - no single specialized skill covers this
- Could potentially route to multiple skills in sequence:
  - `/tooluniverse-expression-data-retrieval` for gene expression
  - `/tooluniverse-protein-structure-retrieval` for structure predictions
  - `/tooluniverse-gwas-drug-discovery` for GWAS to drug target mapping
- Or should use general strategies to:
  1. Discover tools for each data type (Strategy 1)
  2. Build multi-hop workflow (Strategy 2)
  3. Query multiple databases (Strategy 3)
  4. Generate comprehensive integration report (Strategy 6)
- Instead, the skill only showed documentation

**Result**: ❌ **FAILED** - Did not apply general strategies or suggest workflow

---

## Critical Issues Identified

### 1. Routing Logic Not Executing

**Issue**: The skill displays documentation instead of executing routing logic

**Evidence**: All 5 test scenarios resulted in documentation display, not routing or execution

**Root Cause**: The skill appears to be implemented as a **documentation viewer** rather than an **executable router**

**Impact**: HIGH - The core value proposition of the skill (intelligent routing) is non-functional

**Required Fix**:
- Skill needs to **parse** the routing table, not just display it
- Skill needs to **match keywords** against the routing table programmatically
- Skill needs to **invoke specialized skills** using the Skill tool
- Skill needs to **execute general strategies** when no routing match is found

---

### 2. No Clarification Logic

**Issue**: The skill never asks clarifying questions, even for ambiguous requests

**Evidence**: Scenario 3 ("Tell me about aspirin") received no clarification prompt

**Root Cause**: No implementation of the "Step 0: Clarify the Request" logic

**Impact**: MEDIUM - Users with ambiguous questions get documentation instead of helpful guidance

**Required Fix**:
- Implement logic to detect ambiguous patterns (multiple possible routes)
- Ask user a single concise question covering all ambiguities
- Route based on user's clarification response

---

### 3. No General Strategy Execution

**Issue**: When no specialized skill matches, the skill should execute general strategies but doesn't

**Evidence**: Scenarios 2 and 5 required general strategies but received only documentation

**Root Cause**: No implementation of Strategy 1-10 execution logic

**Impact**: HIGH - Users who need general guidance get documentation instead of actionable help

**Required Fix**:
- Implement tool discovery queries (Strategy 1)
- Implement multi-hop workflow guidance (Strategy 2)
- Implement multi-database query patterns (Strategy 3)
- Implement report generation templates (Strategy 6)

---

### 4. Routing Table Gaps

**Issue**: Some routing keywords may not cover all user query patterns

**Evidence**: While testing revealed implementation issues, some edge cases may exist

**Gaps Identified**:

| User Query Pattern | Missing Keywords | Should Route To |
|-------------------|------------------|-----------------|
| "I need biomarker data for cancer" | "biomarker", "diagnostic marker" | `/tooluniverse-disease-research` OR new skill |
| "Show me all drugs approved for diabetes" | "approved drugs", "medication list" | `/tooluniverse-drug-research` with filter |
| "What are the resistance mechanisms for EGFR inhibitors?" | "resistance mechanisms", "drug resistance" | No clear match - needs new skill or general strategy |
| "Compare expression profiles across tissues" | "compare expression", "tissue comparison" | `/tooluniverse-expression-data-retrieval` |
| "Find all orthologs of human TP53" | "orthologs", "homologs", "evolutionary conservation" | No clear match - needs new skill |

**Impact**: MEDIUM - Once routing is implemented, some queries may not match correctly

**Required Fix**: Expand routing table with additional keywords and patterns

---

### 5. Routing Table Ambiguities

**Issue**: Some queries could legitimately match multiple skills

**Examples**:

| Query | Possible Matches | Current Routing Logic |
|-------|-----------------|----------------------|
| "Find drugs for Alzheimer's" | disease-research, drug-research, drug-repurposing | No tie-breaking logic specified |
| "Analyze BRCA1 mutations in cancer" | target-research, variant-interpretation, precision-oncology | No tie-breaking logic specified |
| "Safety profile of metformin" | drug-research, pharmacovigilance | No tie-breaking logic specified |

**Impact**: MEDIUM - Ambiguous routing could lead to suboptimal skill selection

**Required Fix**: Add tie-breaking rules to SKILL.md:
- Prefer more specific skill over general skill
- If equal specificity, ask user to choose
- Document precedence rules in routing table

---

## Missing Specialized Skills

Through testing, several gaps in specialized skill coverage were identified:

### 1. Biomarker Discovery Skill

**Need**: Users searching for diagnostic, prognostic, or predictive biomarkers

**Current Gap**: No skill specifically handles:
- Biomarker identification for diseases
- Validation of biomarker candidates
- Clinical utility assessment
- Biomarker panel optimization

**Workaround**: Use `/tooluniverse-disease-research` but it's not optimized for biomarker discovery

---

### 2. Comparative Analysis Skill

**Need**: Users wanting to compare multiple entities side-by-side

**Current Gap**: No skill for:
- Comparing drugs (efficacy, safety, properties)
- Comparing targets (expression, druggability)
- Comparing diseases (symptoms, genetics, treatments)
- Comparing pathways (overlap, regulation)

**Workaround**: Use general strategies to query each entity separately, then manually compare

---

### 3. Ortholog/Homolog Analysis Skill

**Need**: Users researching evolutionary conservation and cross-species data

**Current Gap**: No skill for:
- Finding orthologs across species
- Comparing ortholog function/expression
- Evolutionary conservation analysis
- Cross-species translation of findings

**Workaround**: Use general strategies with OMA, Ensembl Compara tools

---

### 4. Drug Resistance Mechanisms Skill

**Need**: Users investigating resistance to therapeutics

**Current Gap**: No skill for:
- Identifying resistance mutations
- Predicting resistance mechanisms
- Finding drugs to overcome resistance
- Resistance prevalence analysis

**Workaround**: Partial coverage in `/tooluniverse-precision-oncology` but not comprehensive

---

### 5. Multi-Omics Integration Skill

**Need**: Users building integrated views across data types

**Current Gap**: Limited coverage for:
- Genomics + transcriptomics + proteomics integration
- Multi-modal data correlation
- Systems-level analysis across data types
- Custom workflow building for complex analyses

**Workaround**: `/tooluniverse-systems-biology` partially covers this but may need expansion

---

## Routing Table Quality Assessment

### Well-Defined Routes (✅ Clear and Comprehensive)

| Category | Quality | Notes |
|----------|---------|-------|
| **Data Retrieval** | Excellent | Clear keywords, unambiguous routing |
| **Clinical Decision Support** | Excellent | Well-differentiated skill boundaries |
| **Genomics & Variant Analysis** | Excellent | Comprehensive coverage with 6 specialized skills |
| **Discovery & Design** | Good | Clear routes but some overlap with research skills |

### Poorly-Defined Routes (⚠️ Ambiguous or Incomplete)

| Category | Issues | Recommendations |
|----------|--------|-----------------|
| **Research & Profiling** | Overlap between disease-research, drug-research, target-research, literature-deep-research | Add tie-breaking rules and cross-references |
| **Systems & Network Analysis** | Boundary between protein-interactions and systems-biology unclear | Clarify when to use each; add decision flowchart |
| **Infrastructure** | Only 2 skills; may need more for tool development, debugging | Consider adding tooluniverse-troubleshooting skill |

---

## Documentation Quality Assessment

### Strengths

1. **Comprehensive coverage**: All 10 strategies are well-documented with examples
2. **Clear structure**: Routing table → General strategies → Examples is logical
3. **Actionable guidance**: Specific tool names, workflows, and best practices provided
4. **Evidence grading system**: T1-T4 tiers help users assess claim strength
5. **Completeness checks**: Universal questions help ensure thoroughness

### Weaknesses

1. **Too long**: 799 lines makes it hard to navigate during skill execution
2. **No executable examples**: All examples are descriptive, not code-based
3. **Missing error handling**: What if routing fails? What if specialized skill is unavailable?
4. **No feedback loop**: No mechanism to learn from routing mistakes
5. **Assumes skill implementation**: Documentation reads like a manual, not executable instructions for an AI agent

---

## Recommendations for Improvement

### Priority 1: Critical (Must Fix for Skill to Work)

#### 1.1 Implement Routing Logic

**Current State**: Skill only displays documentation

**Required Implementation**:
```python
# Pseudo-code for routing logic
def route_to_skill(user_query: str) -> str:
    """Parse user query and route to appropriate specialized skill."""

    # Extract keywords from query
    keywords = extract_keywords(user_query)

    # Match against routing table
    matches = match_routing_table(keywords)

    if len(matches) == 0:
        return "USE_GENERAL_STRATEGIES"
    elif len(matches) == 1:
        return invoke_skill(matches[0])
    else:
        return ask_clarification(matches)
```

**Acceptance Criteria**:
- Test Scenario 1 correctly routes to `/tooluniverse-disease-research`
- Test Scenario 4 correctly routes to `/tooluniverse-protein-interactions`

---

#### 1.2 Implement Clarification Logic

**Current State**: No clarification questions asked

**Required Implementation**:
```python
# Pseudo-code for clarification
def ask_clarification(possible_skills: list) -> str:
    """Ask user to clarify intent when multiple skills match."""

    question = "Your question could be answered by:\n"
    for skill in possible_skills:
        question += f"- {skill.name}: {skill.description}\n"
    question += "\nWhich approach would you prefer?"

    return question
```

**Acceptance Criteria**:
- Test Scenario 3 asks for clarification between drug-research, pharmacovigilance, chemical-compound-retrieval

---

#### 1.3 Implement General Strategy Execution

**Current State**: Strategies are documented but not executed

**Required Implementation**:

For **Strategy 1: Tool Discovery**:
```python
def execute_tool_discovery(keywords: list) -> dict:
    """Execute tool discovery for given keywords."""

    results = {}
    for keyword in keywords:
        results[keyword] = {
            'tool_finder_keyword': Tool_Finder_Keyword(query=keyword),
            'tool_finder_llm': Tool_Finder_LLM(query=keyword),
            'tool_finder_embedding': Tool_Finder(query=keyword)
        }

    return aggregate_and_deduplicate(results)
```

**Acceptance Criteria**:
- Test Scenario 2 executes tool discovery queries
- Results are aggregated and presented to user

---

### Priority 2: Important (Improves User Experience)

#### 2.1 Add Routing Table Expansion

Add these keywords to routing table:

```markdown
#### Additional Routing Patterns

| User Question Keywords | Route To | Why |
|------------------------|----------|-----|
| "biomarker", "diagnostic marker", "prognostic marker" | `/tooluniverse-disease-research` | Biomarker discovery is disease research |
| "compare drugs", "drug comparison" | `/tooluniverse-drug-research` + custom comparison | Multi-entity comparison |
| "orthologs", "homologs", "cross-species" | General Strategy 1 + OMA/Ensembl tools | No specialized skill yet |
| "resistance", "drug resistance", "resistance mechanism" | `/tooluniverse-precision-oncology` | Resistance is precision oncology subdomain |
| "approved drugs for [disease]", "medications for [disease]" | `/tooluniverse-disease-research` | Disease-centric query |
```

---

#### 2.2 Add Tie-Breaking Rules

Add this section to SKILL.md after routing table:

```markdown
### Tie-Breaking Rules

When multiple skills match, use these rules:

1. **Specificity Rule**: Prefer more specific skill over general skill
   - Example: "cancer treatment" → `/tooluniverse-precision-oncology` (specific) over `/tooluniverse-disease-research` (general)

2. **Data Type Rule**: Prefer retrieval skills for data-focused queries
   - Example: "get compound structure" → `/tooluniverse-chemical-compound-retrieval` over `/tooluniverse-drug-research`

3. **Workflow Rule**: Prefer end-to-end skills for complex multi-step queries
   - Example: "diagnose rare disease" → `/tooluniverse-rare-disease-diagnosis` over `/tooluniverse-variant-interpretation`

4. **User Intent Rule**: If rules 1-3 don't resolve, ask user to clarify
```

---

#### 2.3 Add Error Handling

Add this section to SKILL.md:

```markdown
### Error Handling

**If specialized skill is unavailable:**
1. Inform user of the issue
2. Fall back to general strategies
3. Document what was attempted

**If routing confidence is low:**
1. Present top 2-3 options to user
2. Let user choose
3. Remember choice for similar future queries

**If general strategies fail:**
1. Document what was tried
2. Suggest manual tool exploration
3. Offer to search ToolUniverse documentation
```

---

### Priority 3: Nice to Have (Future Enhancements)

#### 3.1 Create Missing Specialized Skills

Based on gap analysis, create:
1. `/tooluniverse-biomarker-discovery`
2. `/tooluniverse-comparative-analysis`
3. `/tooluniverse-ortholog-analysis`
4. `/tooluniverse-resistance-mechanisms`

---

#### 3.2 Add Learning Mechanism

Implement feedback loop:
- Track which routes users find most helpful
- Learn from corrections (user says "no, I meant X")
- Improve keyword matching over time

---

#### 3.3 Shorten Documentation

Create two versions:
1. **Compact routing guide** (200 lines) - used during skill execution
2. **Full strategy documentation** (799 lines) - used as reference

---

## Testing Plan for Updated Skill

After implementing fixes, re-run these tests:

### Test Suite A: Routing Accuracy

| Test | Query | Expected Route | Pass Criteria |
|------|-------|----------------|---------------|
| A1 | "Research Alzheimer's disease" | `/tooluniverse-disease-research` | Correct skill invoked |
| A2 | "Get aspirin structure" | `/tooluniverse-chemical-compound-retrieval` | Correct skill invoked |
| A3 | "Find protein interactions for EGFR" | `/tooluniverse-protein-interactions` | Correct skill invoked |
| A4 | "Interpret BRCA1 variant" | `/tooluniverse-variant-interpretation` | Correct skill invoked |
| A5 | "Design protein therapeutic" | `/tooluniverse-protein-therapeutic-design` | Correct skill invoked |

### Test Suite B: Clarification Logic

| Test | Query | Expected Behavior | Pass Criteria |
|------|-------|-------------------|---------------|
| B1 | "Tell me about metformin" | Ask: drug profile, safety, repurposing, or compound? | Clarification question asked |
| B2 | "Research TP53" | Ask: target profile, literature review, or variant analysis? | Clarification question asked |
| B3 | "Find all cancer drugs" | Ask: for specific cancer, all cancers, or drug discovery? | Clarification question asked |

### Test Suite C: General Strategy Execution

| Test | Query | Expected Strategy | Pass Criteria |
|------|-------|-------------------|---------------|
| C1 | "How to search for proteomics tools?" | Strategy 1: Tool Discovery | Tool discovery queries executed |
| C2 | "Build workflow for multi-omics analysis" | Strategy 2: Multi-hop chains | Workflow guidance provided |
| C3 | "Compare data from UniProt and Proteins API" | Strategy 3: Multiple databases | Multi-database query executed |

### Test Suite D: Edge Cases

| Test | Query | Expected Behavior | Pass Criteria |
|------|-------|-------------------|---------------|
| D1 | "asdfghjkl" (nonsense) | Ask for clarification or indicate unclear | Graceful handling |
| D2 | "" (empty query) | Ask user what they need | Prompt for input |
| D3 | Very long complex query (200+ words) | Extract key intent and route | Correct routing despite length |
| D4 | Query in Spanish | Translate to English, route, respond in Spanish | Correct language handling |

---

## Conclusion

The `/tooluniverse` skill has **excellent documentation** but **no functional implementation**. The skill architecture and strategy framework are sound, but the skill currently only displays documentation instead of executing routing logic or general strategies.

### Summary Scores

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Documentation Quality** | 9/10 | Comprehensive, clear, actionable |
| **Routing Table Coverage** | 8/10 | Good coverage, some gaps identified |
| **Implementation** | 0/10 | No routing or strategy execution |
| **User Experience** | 2/10 | Users receive documentation, not help |
| **Overall** | 3/10 | Cannot fulfill purpose until implemented |

### Next Steps

1. **Immediate**: Implement routing logic (Priority 1.1)
2. **Short-term**: Implement clarification and general strategies (Priority 1.2, 1.3)
3. **Medium-term**: Expand routing table and add error handling (Priority 2)
4. **Long-term**: Create missing specialized skills (Priority 3)

### Success Criteria

The skill will be considered functional when:
- ✅ 80%+ of clear queries route to correct specialized skill
- ✅ 100% of ambiguous queries ask for clarification
- ✅ 100% of general strategy queries execute appropriate strategies
- ✅ All 5 test scenarios pass with correct behavior

---

## Appendix: Test Execution Logs

### Scenario 1 Log
```
User: "I need a comprehensive research report on breast cancer including genetics, treatments, and clinical trials"
Skill: /tooluniverse
Action: Displayed SKILL.md documentation (799 lines)
Expected: Invoke /tooluniverse-disease-research
Result: FAIL
```

### Scenario 2 Log
```
User: "How can I find all ToolUniverse tools related to metabolomics and mass spectrometry?"
Skill: /tooluniverse
Action: Displayed SKILL.md documentation (799 lines)
Expected: Execute Strategy 1 (Tool Discovery)
Result: FAIL
```

### Scenario 3 Log
```
User: "Tell me about aspirin"
Skill: /tooluniverse
Action: Displayed SKILL.md documentation (799 lines)
Expected: Ask clarification (drug profile, safety, compound, repurposing?)
Result: FAIL
```

### Scenario 4 Log
```
User: "I want to find protein interaction data for TP53 from multiple databases and compare their coverage"
Skill: /tooluniverse
Action: Displayed SKILL.md documentation (799 lines)
Expected: Invoke /tooluniverse-protein-interactions
Result: FAIL
```

### Scenario 5 Log
```
User: "I want to build a custom workflow that combines gene expression data with protein structure predictions and GWAS data to find novel drug targets"
Skill: /tooluniverse
Action: Displayed SKILL.md documentation (799 lines)
Expected: Execute general strategies (multi-hop workflow, tool discovery)
Result: FAIL
```

---

**Report End**
