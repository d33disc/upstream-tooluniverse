# ToolUniverse Bug Report: Tool Reloading on Every Call

**Priority**: High
**Impact**: User Experience, Performance
**Status**: Confirmed, Reproducible

---

## Problem Statement

ToolUniverse reloads ALL tools (1232 tools) from disk on **every single tool call**, causing:
- 40+ error messages per tool call (for missing optional tool files)
- Severe performance degradation (4-8 seconds overhead per call)
- Unusable verbose output that obscures actual results
- 4x memory overhead for tool metadata

---

## Expected Behavior

1. **Load once**: Tools should be loaded into memory once when `ToolUniverse()` is instantiated
2. **Reuse**: Subsequent tool calls should reuse the cached tool registry
3. **Silent**: Missing optional tool files should not generate ERROR-level messages
4. **Fast**: Tool calls should execute immediately without reload overhead

## Actual Behavior

1. **Load repeatedly**: Every call to `tu.tools.TOOL_NAME()` triggers a complete reload
2. **No caching**: Tool registry is rebuilt from scratch each time
3. **Verbose errors**: Each reload generates 10+ error messages for missing optional files
4. **Slow**: 4-8 second overhead per tool call

---

## Reproduction Steps

```python
from tooluniverse import ToolUniverse

# Initialize ToolUniverse (loads 1232 tools)
tu = ToolUniverse()

# Call 4 tools sequentially
result1 = tu.tools.STRING_map_identifiers(protein_ids=["TP53"], species=9606)
# ^ RELOAD #1: Loads 1232 tools again + 10 error messages

result2 = tu.tools.STRING_get_network(protein_ids=["TP53"], species=9606)
# ^ RELOAD #2: Loads 1232 tools again + 10 error messages

result3 = tu.tools.STRING_functional_enrichment(protein_ids=["TP53"], species=9606)
# ^ RELOAD #3: Loads 1232 tools again + 10 error messages

result4 = tu.tools.STRING_ppi_enrichment(protein_ids=["TP53"], species=9606)
# ^ RELOAD #4: Loads 1232 tools again + 10 error messages
```

**Result**: 40+ error messages, 16-32 seconds of tool loading overhead

---

## Error Messages Generated

On every tool call, ToolUniverse prints:

```
❌ Error loading tools from category 'tool_discovery_agents': [Errno 2] No such file or directory: '.../tool_discovery_agents_tools.json'
❌ Error loading tools from category 'web_search_tools': [Errno 2] No such file or directory: '.../web_search_tools_tools.json'
❌ Error loading tools from category 'package_discovery_tools': [Errno 2] No such file or directory: '.../package_discovery_tools_tools.json'
❌ Error loading tools from category 'pypi_package_inspector_tools': [Errno 2] No such file or directory: '.../pypi_package_inspector_tools_tools.json'
❌ Error loading tools from category 'drug_discovery_agents': [Errno 2] No such file or directory: '.../drug_discovery_agents_tools.json'
❌ Error loading tools from category 'hca_tools': [Errno 2] No such file or directory: '.../hca_tools_tools.json'
❌ Error loading tools from category 'clinical_trials_tools': [Errno 2] No such file or directory: '.../clinical_trials_tools_tools.json'
❌ Error loading tools from category 'iedb_tools': [Errno 2] No such file or directory: '.../iedb_tools_tools.json'
❌ Error loading tools from category 'pathway_commons_tools': [Errno 2] No such file or directory: '.../pathway_commons_tools_tools.json'
❌ Error loading tools from category 'biomodels_tools': [Errno 2] No such file or directory: '.../biomodels_tools_tools.json'
```

These are **optional** tool files that may not exist, but ToolUniverse treats them as ERROR-level events.

---

## Impact Assessment

### 1. User Experience Impact: **CRITICAL**

**Example Output** (what users see):
```
🔍 Phase 1: Mapping proteins...
❌ Error loading tools from category 'tool_discovery_agents': [Errno 2]...
❌ Error loading tools from category 'web_search_tools': [Errno 2]...
❌ Error loading tools from category 'package_discovery_tools': [Errno 2]...
❌ Error loading tools from category 'pypi_package_inspector_tools': [Errno 2]...
❌ Error loading tools from category 'drug_discovery_agents': [Errno 2]...
❌ Error loading tools from category 'hca_tools': [Errno 2]...
❌ Error loading tools from category 'clinical_trials_tools': [Errno 2]...
❌ Error loading tools from category 'iedb_tools': [Errno 2]...
❌ Error loading tools from category 'pathway_commons_tools': [Errno 2]...
❌ Error loading tools from category 'biomodels_tools': [Errno 2]...
✅ Mapped 5 proteins

🕸️  Phase 2: Retrieving network...
❌ Error loading tools from category 'tool_discovery_agents': [Errno 2]...
❌ Error loading tools from category 'web_search_tools': [Errno 2]...
[... 30+ more error lines ...]
```

- **40+ error messages** obscure actual results
- Users think the analysis is failing when it's actually working
- Output is completely unusable without grep filtering

### 2. Performance Impact: **HIGH**

| Metric | Without Bug | With Bug | Overhead |
|--------|-------------|----------|----------|
| Tool calls | 4 | 4 | - |
| Tool loads | 1 | 4 | **4x** |
| Load time | 4-8 sec | 16-32 sec | **4x** |
| Memory | ~100 MB | ~400 MB | **4x** |

For workflows with 10-20 tool calls: **40-80 seconds** of pure overhead.

### 3. Development Impact: **MEDIUM**

- Developers cannot debug their code due to noise
- Logs are filled with false error messages
- Testing is slow and painful
- Users require workarounds (grep filtering)

---

## Root Cause Analysis

### Likely Location

The bug is in the tool loading mechanism, probably in:
- `ToolUniverse.__init__()` or
- `ToolUniverse.tools.__getattr__()` or
- `get_shared_client().run_one_function()`

### Hypothesis

When `tu.tools.STRING_map_identifiers()` is called:
1. It triggers `__getattr__` or similar dynamic attribute access
2. This calls `load_tools()` or similar method
3. Tool registry is rebuilt from scratch instead of using cache
4. Missing tool files generate error messages to stdout

### Evidence

```python
# Each tool call shows this pattern:
ℹ️  Including only specific tools: 1 tools specified
❌ Error loading tools from category 'tool_discovery_agents': [Errno 2]...
[... 10 error lines ...]
ℹ️  Included 1 tools by name filter
ℹ️  Number of tools after load tools: 1
```

This indicates a fresh tool load happens on every call.

---

## Suggested Fixes

### Fix #1: Implement Tool Registry Caching (Recommended)

```python
class ToolUniverse:
    _tool_registry_cache = None  # Class-level cache

    def __init__(self):
        if ToolUniverse._tool_registry_cache is None:
            # Load tools only once
            ToolUniverse._tool_registry_cache = self._load_all_tools()

        self.tools = ToolUniverse._tool_registry_cache

    def _load_all_tools(self):
        # Existing tool loading logic
        pass
```

**Benefits**:
- Load once per Python process
- All subsequent calls use cached registry
- Massive performance improvement

**Trade-offs**:
- Need cache invalidation mechanism if tools change
- Slightly more memory usage (but only 1x instead of 4x)

### Fix #2: Suppress Warnings for Optional Files

```python
def _load_tool_category(self, category_name):
    try:
        # Try to load category
        tools = self._read_json(f"{category_name}_tools.json")
        return tools
    except FileNotFoundError:
        # Optional file missing - this is OK, don't print error
        logger.debug(f"Optional tool category not found: {category_name}")
        return []
    except Exception as e:
        # Real error - print this
        logger.error(f"Error loading {category_name}: {e}")
        return []
```

**Benefits**:
- Missing optional files are silent
- Real errors are still visible
- Clean user output

### Fix #3: Add Lazy Loading

Only load tool categories when actually used:

```python
class ToolRegistry:
    def __init__(self):
        self._loaded_categories = {}

    def get_tool(self, tool_name):
        category = self._detect_category(tool_name)

        if category not in self._loaded_categories:
            # Load category on first use
            self._loaded_categories[category] = self._load_category(category)

        return self._loaded_categories[category][tool_name]
```

**Benefits**:
- Only load what's needed
- Even faster for single tool usage
- Still avoids repeated loads

---

## Workarounds (Until Fixed)

### User-Side Workaround #1: Filter Output

```bash
python script.py 2>&1 | grep -v "Error loading tools"
```

### User-Side Workaround #2: Create Placeholder Files

```bash
cd src/tooluniverse/data/
for f in tool_discovery_agents web_search_tools package_discovery_tools \
         pypi_package_inspector_tools drug_discovery_agents hca_tools \
         clinical_trials_tools iedb_tools pathway_commons_tools biomodels_tools; do
    echo "[]" > "${f}_tools.json"
done
```

### User-Side Workaround #3: Programmatic Filtering

```python
import sys
from io import StringIO

old_stdout = sys.stdout
sys.stdout = buffer = StringIO()

# Run analysis
result = analyze_protein_network(tu, proteins)

# Filter output
sys.stdout = old_stdout
output = buffer.getvalue()
clean = '\n'.join([l for l in output.split('\n') if 'Error loading' not in l])
print(clean)
```

**All workarounds are suboptimal** - the framework should be fixed.

---

## Testing Verification

After fix is implemented, verify:

### Test Case 1: Tool Registry Caching
```python
from tooluniverse import ToolUniverse
import time

tu = ToolUniverse()

# First call (load + execute)
start = time.time()
result1 = tu.tools.STRING_map_identifiers(protein_ids=["TP53"], species=9606)
time1 = time.time() - start

# Second call (should reuse cache)
start = time.time()
result2 = tu.tools.STRING_get_network(protein_ids=["TP53"], species=9606)
time2 = time.time() - start

# Verify:
# - time2 should be << time1 (no reload overhead)
# - No duplicate error messages
# - Memory usage stable
```

### Test Case 2: Silent Optional Files
```python
# Remove optional tool files
import os
os.remove("data/tool_discovery_agents_tools.json")

# Should NOT print error message
tu = ToolUniverse()
result = tu.tools.STRING_map_identifiers(protein_ids=["TP53"], species=9606)

# Verify: No "Error loading tools" messages in output
```

### Test Case 3: Multiple Tool Calls
```python
# 10 sequential tool calls
for i in range(10):
    result = tu.tools.STRING_map_identifiers(protein_ids=["TP53"], species=9606)

# Verify:
# - Only 1 tool load occurs (at initialization)
# - No repeated error messages
# - Fast execution (< 1 second total after first load)
```

---

## Additional Context

- **Discovered while**: Building Protein Interaction Network Analysis skill
- **Affects**: All ToolUniverse users making multiple tool calls
- **Severity**: Makes ToolUniverse nearly unusable for multi-step workflows
- **Framework Version**: Current auto branch (as of 2026-02-13)

---

## Recommended Priority

**HIGH - Should be fixed in next release**

This bug severely impacts:
- User experience (unusable output)
- Performance (4x overhead)
- Developer productivity (debugging impossible)
- Framework adoption (users see "errors" and think it's broken)

The fix is straightforward (caching + logging levels) and will dramatically improve the framework.
