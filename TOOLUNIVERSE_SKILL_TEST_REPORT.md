# `/tooluniverse` Skill Testing Report

**Date**: 2026-02-14
**Tester**: Claude Code Agent
**Skill Version**: Revised (with routing logic in SKILL.md)
**Test Purpose**: Validate skill routing behavior vs. previous implementation

---

## Executive Summary

**CRITICAL FAILURE**: The revised `/tooluniverse` skill does NOT execute routing logic. All three test scenarios failed because the skill only displays documentation instead of performing the expected actions.

**Status**: ❌ **FAILED** (0/3 test scenarios passed)

**Root Cause**: The skill appears to be a **documentation-only skill**. It has no executable code (`skill.py` does not exist), only markdown files (`SKILL.md`, `REFERENCE.md`, `CHECKLIST.md`). Claude Code skills that are prompt-based require the LLM to read and interpret the instructions, but the current implementation is not executing the routing logic as documented.

---

## Test Results

### Test Scenario 1: Clear Specialized Skill Match ❌ FAIL

**User Question**: "I need a comprehensive research report on breast cancer including genetics, treatments, and clinical trials"

**Expected Behavior**:
- Parse keywords: "comprehensive research report", "breast cancer" (disease)
- Match routing table line 66: `"research", "disease", "comprehensive report on [disease]"`
- **INVOKE**: `Skill(skill="tooluniverse-disease-research", args="breast cancer")`

**Actual Behavior**:
- Skill invoked successfully: `Launching skill: tooluniverse`
- **But**: Returned entire SKILL.md documentation (37,434 characters)
- **Did NOT**: Route to `tooluniverse-disease-research` skill
- **Did NOT**: Call the Skill tool

**Verdict**: ❌ **FAILED** - No routing action taken

---

### Test Scenario 2: Ambiguous Request ❌ FAIL

**User Question**: "Tell me about aspirin"

**Expected Behavior**:
- Parse keywords: "tell me about", "aspirin" (drug)
- Detect ambiguity: Could match drug-research, pharmacovigilance, chemical-compound-retrieval, or drug-repurposing
- **ASK USER**: Use AskUserQuestion tool with options: "(A) Comprehensive drug profile, (B) Safety/adverse events, (C) Chemical structure data, or (D) Repurposing opportunities?"

**Actual Behavior**:
- Skill invoked successfully: `Launching skill: tooluniverse`
- **But**: Returned entire SKILL.md documentation
- **Did NOT**: Call AskUserQuestion tool
- **Did NOT**: Present clarification options

**Verdict**: ❌ **FAILED** - No clarification request made

---

### Test Scenario 3: Tool Discovery (General Strategy) ❌ FAIL

**User Question**: "How can I find all ToolUniverse tools related to metabolomics?"

**Expected Behavior**:
- Parse keywords: "how can I find", "tools", "metabolomics"
- No specialized skill match (meta-question about ToolUniverse)
- **EXECUTE Strategy 1**: Actually run Tool_Finder_Keyword or Tool_Finder_LLM queries
- Example: `Tool_Finder_Keyword(keyword="metabolomics")`

**Actual Behavior**:
- Skill invoked successfully: `Launching skill: tooluniverse`
- **But**: Returned entire SKILL.md documentation
- **Did NOT**: Execute any Tool_Finder queries
- **Did NOT**: Return actual tool results

**Verdict**: ❌ **FAILED** - No tool discovery execution

---

## Skill Implementation Analysis

### Directory Structure
```
/Users/shgao/logs/25.05.28tooluniverse/codes/ToolUniverse-auto/skills/tooluniverse/
├── CHECKLIST.md    (2,640 bytes)
├── REFERENCE.md    (13,551 bytes)
└── SKILL.md        (37,434 bytes)
```

**Missing**:
- ❌ No `skill.py` (executable implementation)
- ❌ No `__init__.py`
- ❌ No Python code files

### SKILL.md Content Review

The SKILL.md file contains excellent routing logic documentation:

**Lines 8-42**: Clear routing workflow
- STEP 1: Parse user's question
- STEP 2: Check routing table and invoke skill if match found
- STEP 3: Use general strategies if no match

**Lines 45-150**: Comprehensive routing table with 10 categories
- Data Retrieval (4 specialized skills)
- Research & Profiling (4 specialized skills)
- Clinical Decision Support (4 specialized skills)
- Discovery & Design (4 specialized skills)
- Genomics & Variant Analysis (5 specialized skills)
- Systems & Network Analysis (3 specialized skills)
- Screening & Functional Genomics (2 specialized skills)
- Clinical Trial & Study Design (2 specialized skills)
- Outbreak Response (1 specialized skill)
- Infrastructure & Development (2 specialized skills)

**Lines 151-227**: Excellent routing examples
- Example 1: Clear match → Invoke skill (breast cancer → disease-research)
- Example 2: Ambiguous → Ask user (aspirin → clarify)
- Example 3: No match → General strategies (tool discovery → execute queries)

**Lines 229+**: Comprehensive general strategies (10 strategies)

**Assessment**: Documentation quality is **EXCELLENT**, but it's not being executed.

---

## Problem Diagnosis

### Issue Type: Implementation vs. Documentation Gap

The revised skill has **perfect documentation** of desired behavior but **zero execution**.

### Hypothesis: Prompt-Based Skills Not Working

Claude Code skills appear to support two types:
1. **Code-based skills**: Have `skill.py` with executable Python code
2. **Prompt-based skills**: Have only `SKILL.md` with instructions for the LLM to follow

The `/tooluniverse` skill appears to be designed as a **prompt-based skill**, where the LLM should:
1. Read SKILL.md instructions
2. Parse user's question
3. Execute the routing logic by calling appropriate tools

**Current behavior suggests**: The skill invocation only **displays** the SKILL.md content instead of having the LLM **interpret and execute** it.

### Comparison with Previous Version

**Previous version behavior** (unknown - needs testing):
- May have had similar issues
- User requested "REVISED" version, implying previous version had problems

---

## What Works vs. What Doesn't

### ✅ What Works

1. **Skill invocation**: `Skill(skill="tooluniverse", args="...")` successfully launches
2. **Documentation quality**: SKILL.md has excellent, clear instructions
3. **Routing table coverage**: Comprehensive mapping of 27+ specialized skills
4. **Examples**: Well-written examples showing expected behavior
5. **General strategies**: Detailed fallback strategies when no skill matches

### ❌ What Doesn't Work

1. **Routing execution**: Does not invoke specialized skills
2. **Clarification logic**: Does not ask user questions when ambiguous
3. **Tool discovery**: Does not execute Tool_Finder queries
4. **Action-oriented behavior**: Shows documentation instead of taking actions
5. **Step-by-step execution**: Does not follow the documented workflow

---

## Specific Improvements vs. Previous Version

**Cannot assess** because we don't have test results from the previous version. However, based on the user's request for a "REVISED" skill, we can infer:

### Likely Previous Problems (Inferred)

1. **Unclear routing**: Previous version may have had ambiguous routing rules
2. **Missing specialized skills**: May not have had comprehensive skill mapping
3. **Poor disambiguation**: May not have had clear ambiguity handling
4. **Weak fallback**: May not have had general strategies

### Improvements in Current Documentation (Theoretical)

1. ✅ **Clear 3-step workflow** (Parse → Route → Execute)
2. ✅ **Comprehensive routing table** (27+ specialized skills)
3. ✅ **Explicit tie-breaking rules** (Specificity, Data Type, Ask User)
4. ✅ **Concrete examples** (4 examples with exact expected behavior)
5. ✅ **Fallback mode** (10 general strategies)

**But**: None of these improvements matter if the skill doesn't execute the logic.

---

## Recommended Actions

### Option A: Implement Code-Based Skill ✅ RECOMMENDED

Create `skill.py` with Python implementation:

```python
"""ToolUniverse Router Skill - Executable Implementation"""

import re
from typing import Dict, List, Optional

# Routing table mapping keywords to skills
ROUTING_TABLE = {
    "tooluniverse-disease-research": [
        "research", "profile", "tell me about", "disease", "syndrome",
        "disorder", "illness", "comprehensive report on"
    ],
    "tooluniverse-drug-research": [
        "research", "profile", "drug", "medication", "therapeutic agent",
        "medicine", "tell me about"
    ],
    # ... (all other specialized skills)
}

def parse_keywords(question: str) -> List[str]:
    """Extract keywords from user question."""
    # Implementation
    pass

def find_matching_skills(keywords: List[str]) -> List[str]:
    """Find specialized skills matching keywords."""
    # Implementation
    pass

def route_question(question: str):
    """Main routing logic."""
    # 1. Parse keywords
    keywords = parse_keywords(question)

    # 2. Find matching skills
    matches = find_matching_skills(keywords)

    # 3. Take action
    if len(matches) == 1:
        # Invoke the skill
        invoke_skill(matches[0], question)
    elif len(matches) > 1:
        # Ask user to clarify
        ask_user_clarification(matches)
    else:
        # Execute general strategies
        execute_general_strategies(question)
```

**Effort**: Medium (2-4 hours)
**Impact**: High (skill will actually work)

### Option B: Fix Prompt-Based Skill Execution

Investigate why Claude Code is not executing SKILL.md instructions:

1. Check if there's a specific format/structure required
2. Review other working prompt-based skills for patterns
3. Add explicit action triggers in SKILL.md

**Effort**: Low (1-2 hours if solution exists)
**Impact**: High (if fixable)
**Risk**: May not be possible if Claude Code doesn't support this pattern

### Option C: Hybrid Approach

Minimal `skill.py` that loads SKILL.md and instructs LLM:

```python
"""ToolUniverse Router - Hybrid Implementation"""

def main(user_question: str):
    skill_md = open("SKILL.md").read()

    prompt = f"""
    You are the ToolUniverse router. Follow the instructions in SKILL.md exactly.

    User question: {user_question}

    CRITICAL: You MUST take action (invoke skill, ask question, or execute queries).
    Do NOT just return documentation.

    Instructions:
    {skill_md}
    """

    # Pass to LLM for execution
    return execute_prompt(prompt)
```

**Effort**: Low (30 minutes)
**Impact**: Medium (may work if LLM interpretation is the issue)

---

## Test Scoring Summary

| Scenario | Expected Behavior | Actual Behavior | Pass/Fail |
|----------|-------------------|-----------------|-----------|
| 1. Clear Match | Invoke `tooluniverse-disease-research` | Showed documentation | ❌ FAIL |
| 2. Ambiguous | Ask user with AskUserQuestion | Showed documentation | ❌ FAIL |
| 3. Tool Discovery | Execute Tool_Finder queries | Showed documentation | ❌ FAIL |

**Overall Score**: **0/3 (0%)**

---

## Conclusion

The revised `/tooluniverse` skill has **excellent design** but **zero execution**. It's a beautifully documented skill that does nothing.

**Critical blocker**: The skill needs executable code (`skill.py`) to implement the routing logic documented in SKILL.md.

**Priority**: **HIGH** - This is a core routing skill that other workflows depend on.

**Next step**: Implement Option A (code-based skill) or investigate Option B (fix prompt-based execution).

---

## Appendix: Test Evidence

### Evidence 1: Skill Directory Contents
```bash
$ ls -la /Users/shgao/logs/25.05.28tooluniverse/codes/ToolUniverse-auto/skills/tooluniverse/
total 120
drwxr-xr-x@  5 shgao  staff    160 Feb 14 12:32 .
drwxr-xr-x@ 46 shgao  staff   1472 Feb 13 21:56 ..
-rw-r--r--@  1 shgao  staff   2640 Feb  8 15:24 CHECKLIST.md
-rw-r--r--@  1 shgao  staff  13551 Feb  8 15:24 REFERENCE.md
-rw-r--r--@  1 shgao  staff  37434 Feb 14 12:32 SKILL.md
```

**No Python files found**.

### Evidence 2: SKILL.md Routing Instructions (Lines 8-42)

```markdown
## YOUR TASK: Route User Questions to the Right Solution

When a user asks a question, **DO NOT just show this documentation**. Instead, follow these steps:

### STEP 1: Parse the User's Question
[... clear instructions ...]

### STEP 2: Check for Routing Match
**IMMEDIATELY** check the routing table below. If the user's keywords match a specialized skill:
- **USE THE Skill TOOL** to invoke that specialized skill right now
- Pass the user's question to the specialized skill
[... more instructions ...]
```

**Note**: Instructions explicitly say "DO NOT just show this documentation" - yet that's exactly what happened.

### Evidence 3: Test Execution Results

All three skill invocations returned the same output:
```
Launching skill: tooluniverse
[... entire SKILL.md content ...]
```

No tool calls were made, no skills were invoked, no questions were asked.

---

**End of Report**
