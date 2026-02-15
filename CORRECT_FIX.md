# Correct Fix: Merge Instead of Replace

## The Real Problem

When `load_tools(include_tools=["TOOL_A"])` is called:

```python
# Before:
all_tools = [TOOL_1, TOOL_2, TOOL_3]  # Previously loaded tools

# Load and filter:
load_tools(include_tools=["TOOL_A"])
# → Loads all categories, appends to all_tools
# → all_tools = [TOOL_1, TOOL_2, TOOL_3, ...1232 newly loaded tools...]
# → Filters to include_tools
# → all_tools = [TOOL_A]  ← LOSES TOOL_1, TOOL_2, TOOL_3! ❌
```

**The bug**: Filtering discards ALL tools not in `include_tools`, including previously loaded ones!

---

## The Correct Fix: Merge Mode

When `include_tools` is specified, **preserve existing tools** + add new ones:

```python
# Before:
all_tools = [TOOL_1, TOOL_2, TOOL_3]

# Load and merge:
load_tools(include_tools=["TOOL_A"])
# → Loads all categories, appends to all_tools
# → Filter new tools to include_tools
# → all_tools = [TOOL_1, TOOL_2, TOOL_3, TOOL_A]  ← Keeps old + adds new ✅
```

---

## Implementation

### Step 1: Track Existing Tools Before Loading

In `load_tools()` method, before line 906:

```python
def load_tools(self, tool_type=None, exclude_tools=None, exclude_categories=None,
               include_tools=None, ...):
    # ... existing code ...

    # NEW: Remember which tools were already loaded (before this call)
    existing_tool_names = {t.get("name") for t in self.all_tools} if include_tools else set()

    # Filter and deduplicate tools
    self._filter_and_deduplicate_tools(
        exclude_tools_set,
        include_tools_set,
        include_tool_types_set,
        exclude_tool_types_set,
        existing_tool_names=existing_tool_names,  # ← Pass to filter function
    )
```

### Step 2: Update Filter Function to Merge

In `_filter_and_deduplicate_tools()` method:

```python
def _filter_and_deduplicate_tools(
    self,
    exclude_tools_set,
    include_tools_set,
    include_tool_types_set=None,
    exclude_tool_types_set=None,
    existing_tool_names=None,  # ← NEW PARAMETER
):
    """
    Filter tools based on inclusion/exclusion criteria and remove duplicates.

    Args:
        existing_tool_names (set): Names of tools that were already loaded
                                   before this call. These will be preserved.
    """
    tool_name_list = []
    dedup_all_tools = []

    # ... existing filtering logic (lines 966-1048) ...

    for each in self.all_tools:
        tool_name = each.get("name", "")

        # NEW: Preserve existing tools even if not in include_tools_set
        if existing_tool_names and tool_name in existing_tool_names:
            # Keep previously loaded tools (don't re-filter them)
            if tool_name not in tool_name_list:
                tool_name_list.append(tool_name)
                dedup_all_tools.append(each)
            continue

        # Apply filters to newly loaded tools only
        if include_tools_set:
            if tool_name not in include_tools_set:
                continue  # Skip new tools not in include set

        # ... rest of existing filtering logic ...

    # Update the tool list
    self.all_tools = dedup_all_tools
    self.refresh_tool_name_desc()
```

---

## Behavior After Fix

### Scenario 1: Selective Loading (Your Use Case)

```python
tu = ToolUniverse()  # Empty registry

# Load only STRING tools
tu.load_tools(include_tools=["STRING_map_identifiers", "STRING_get_network"])
# Registry: [STRING_map_identifiers, STRING_get_network]
# Tool finder sees: 2 tools ✅

# Later, load more tools
tu.tools.UniProt_get_entry(...)  # Triggers on-demand load
# Registry: [STRING_map_identifiers, STRING_get_network, UniProt_get_entry]
# Tool finder sees: 3 tools ✅

# No reload on second STRING call
tu.tools.STRING_map_identifiers(...)  # Fast, no reload ✅
```

### Scenario 2: Load All (If User Wants)

```python
tu = ToolUniverse()
tu.load_tools()  # No include_tools → loads everything
# Registry: [all 1232 tools]
# Tool finder sees: all 1232 tools
```

### Scenario 3: Progressive Loading

```python
tu = ToolUniverse()

result1 = tu.tools.TOOL_A()  # Loads once, registry = [TOOL_A]
result2 = tu.tools.TOOL_B()  # Loads once, registry = [TOOL_A, TOOL_B] ✅
result3 = tu.tools.TOOL_A()  # Fast, no reload ✅
```

---

## Benefits

✅ **Preserves selective loading**: Tool finder only sees loaded tools
✅ **No repeated reloads**: Tools cached after first load
✅ **Accumulative**: Registry grows as you use more tools
✅ **Backward compatible**: Full loads still work the same
✅ **Clean**: No error message spam after first load

---

## Additional Fix: Suppress Error Messages

Change missing optional tool files from ERROR to DEBUG:

```python
# In load_tools(), around line 893-896:
except Exception as e:
    # Optional files should not show as errors
    if "No such file or directory" in str(e):
        self.logger.debug(f"Optional category '{each}' not found: {e}")
    else:
        self.logger.error(f"Error loading tools from category '{each}': {e}")
```

---

## Summary

The fix makes `include_tools` work in **merge mode**:
- **Before**: Replace entire registry with filtered subset (bug)
- **After**: Keep existing tools + add newly loaded tools (correct)

This preserves your selective loading use case while fixing the reload bug.

Ready to implement?
