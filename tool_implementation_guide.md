# Life Science Tool Implementation Plan

This document outlines the strategy for implementing new life science tools into `ToolUniverse`. It begins with a guideline for adding tools based on the project's best practices and then details the implementation plan for each specific data source.

## 1. Guidelines for Adding Tools to ToolUniverse

Based on `docs/expand_tooluniverse/contributing/local_tools.rst` and the current codebase structure:

### A. File Structure & Location
*   **Source Code**: Create a new Python file `src/tooluniverse/xxx_tool.py`.
*   **Configuration**: Create a corresponding JSON config file `src/tooluniverse/data/xxx_tools.json`.
*   **Tests**: Create a unit test file `tests/unit/test_xxx_tool.py`.
*   **⚠️ IMPORTANT**: **Do NOT** manually create files in `src/tooluniverse/tools/`. Files in this folder are automatically generated wrapper functions. They will be created automatically by ToolUniverse based on your JSON configuration.

### B. Implementation Pattern
1.  **Inheritance**: Your tool class must inherit from `BaseTool`.
2.  **Registration**: Use the `@register_tool` decorator with the class name.
    
    **Example `src/tooluniverse/my_new_tool.py`**:
    ```python
    from typing import Dict, Any
    from .base_tool import BaseTool
    from .tool_registry import register_tool

    @register_tool("MyNewTool")
    class MyNewTool(BaseTool):
        """
        My new tool description.
        """
        def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
            # Implementation logic here
            return {"result": "success"}
    ```

3.  **Configuration**:
    *   **Do NOT** embed large configs in the decorator based on current best practices for contributed tools. Use the external JSON file.
    *   The configuration file must define the tool's `name` (snake_case), `type` (matching the class name), `description`, `parameter` schema (JSON Schema), **`return_schema`** (output structure), and `test_examples`.

    **Example `src/tooluniverse/data/my_new_tools.json`**:
    ```json
    [
      {
        "name": "my_new_tool",
        "type": "MyNewTool",
        "description": "Convert text to uppercase",
        "parameter": {
          "type": "object",
          "properties": {
            "input": {
              "type": "string",
              "description": "Text to convert"
            }
          },
          "required": ["input"]
        },
        "return_schema": {
          "type": "object",
          "properties": {
            "result": {
              "type": "string",
              "description": "The converted text"
            }
          }
        },
        "test_examples": [
          {
            "input": "hello"
          }
        ]
      }
    ]
    ```

4.  **Auto-Discovery**:
    *   Modern `ToolUniverse` uses automated discovery. You generally **do not** need to modify `src/tooluniverse/__init__.py` if you place your file correctly in `src/tooluniverse/`.

### C. Development Checklist
1.  [ ] Create `src/tooluniverse/xxx_tool.py` with `@register_tool`.
2.  [ ] Create `src/tooluniverse/data/xxx_tools.json` including `returns` schema.
3.  [ ] Implement `run(arguments)` method.
4.  [ ] Implement `validate_parameters` (optional but recommended).
5.  [ ] Write unit tests in `tests/unit/`.
6.  [ ] Verify tool load with `tu.load_tools()`.

---

## 2. Tool Improvement and Maintenance Checklist

**Purpose**: This checklist guides LLMs through systematically improving and maintaining existing tools in ToolUniverse.

### Phase 1: Initial Assessment

#### Step 1.1: Identify Tool Files
- [ ] Locate tool class file: `src/tooluniverse/{category}_tool.py`
- [ ] Locate JSON config file: `src/tooluniverse/data/{category}_tools.json`
- [ ] List all tool function files: `src/tooluniverse/tools/{category}_*.py` (⚠️ Note: These are auto-generated wrappers)
- [ ] Check `default_config.py` for category registration
- [ ] Check `tools/__init__.py` for imports (⚠️ Note: Imports are auto-generated)

#### Step 1.2: Verify Basic Structure
- [ ] Tool class registration exists (`@register_tool`)
- [ ] Class name matches JSON config `"type"` field
- [ ] JSON file is valid
- [ ] Tool loads without errors
- [ ] Python syntax is valid

### Phase 2: Functionality Testing

#### Step 2.1: Test Tool Execution
- [ ] Load tools and test each tool with sample arguments
- [ ] Verify results contain data (not empty)
- [ ] Check response structure matches return_schema
- [ ] Test error handling with invalid inputs

#### Step 2.2: Test API Endpoints Directly
- [ ] Test REST/GraphQL endpoints respond correctly
- [ ] Verify status codes are 200 OK (not 404/502/503)
- [ ] Check response format matches tool expectations

### Phase 3: Description Improvement

#### Step 3.1: Review Tool Descriptions
- [ ] Check each tool's description field
- [ ] Description includes: purpose, input, output, use cases
- [ ] Description is clear to users unfamiliar with API
- [ ] Add examples if missing


#### Step 3.2: Review Parameter Descriptions
For each parameter:
- [ ] Has clear description with examples
- [ ] Has default value if optional
- [ ] Has constraints (min/max/enum) if applicable
- [ ] Type is correct


#### Step 3.3: Review Return Schema
- [ ] return_schema field exists
- [ ] Schema matches actual tool output
- [ ] All important fields documented
- [ ] Nested structures fully documented

### Phase 4: Error Handling Improvement

#### Step 4.1: Review Current Error Handling
- [ ] Test error messages with invalid inputs
- [ ] Test HTTP error handling (404, 502, 503)
- [ ] Verify try/except blocks exist
- [ ] Errors return dict with "error" key

#### Step 4.2: Improve Error Messages
- [ ] Error messages are specific (not generic)
- [ ] Errors suggest actionable solutions
- [ ] Errors include context (status_code, endpoint)
- [ ] Errors are user-friendly

#### Step 4.3: Add Retry Logic (if needed)
- [ ] Identify transient failures (ConnectionError, Timeout)
- [ ] Implement retry with exponential backoff
- [ ] Set max retries (typically 2-3)
- [ ] Handle final failure appropriately

### Phase 5: Finding Missing Tools

#### Step 5.1: Research API Capabilities
- [ ] **Read API Docs**: Check official documentation for all endpoints/operations
- [ ] **GraphQL Introspection**: Use schema introspection to find all queries
- [ ] **Test Endpoints**: Try different endpoint patterns
- [ ] **Check Related Packages**: Look at R/Bioconductor or Python packages
- [ ] **Web Search**: Search for "{API_NAME} API documentation"

#### Step 5.2: Create Gap Analysis Matrix
- [ ] List current tools from JSON config
- [ ] List all API capabilities
- [ ] Create comparison table (implemented vs available)
- [ ] Prioritize missing tools (HIGH/MEDIUM/LOW)
- [ ] Document findings

#### Step 5.3: Identify Subset Extraction Opportunities
- [ ] **Check Data Size**: If full response is large/complex
- [ ] **Identify Subsets**: Common fields users need (diseases, pathways, etc.)
- [ ] **Add Subset Tools**: Create tools that extract specific data types
- [ ] **Implement Method**: Create `_extract_subset()` helper if needed

### Phase 6: Fix Common Issues

#### Issue 6.1: Tool Class Name Mismatch
**Symptoms**: Tool doesn't load, registration errors

**Check**:
- [ ] Python class name matches `@register_tool("ClassName")`
- [ ] JSON config `"type"` field matches class name exactly
- [ ] No typos or case mismatches

**Fix**: Ensure Python class name matches JSON `"type"` field exactly

#### Issue 6.2: Response Format Mismatch
**Symptoms**: `'list' object has no attribute 'get'` or similar errors

**Check**:
- [ ] Test API response format directly
- [ ] Check if API returns list vs dict
- [ ] Verify tool expects correct format

**Fix**: Check API response format and convert if needed (list → dict or vice versa)

#### Issue 6.3: Endpoint URL Issues
**Symptoms**: 404 errors, "Not Found" responses

**Check**:
- [ ] Test endpoint directly
- [ ] Verify URL pattern in API documentation
- [ ] Check placeholder replacement logic
- [ ] Verify base URL is correct

**Fix**: Verify URL building logic and placeholder replacement

#### Issue 6.4: Missing Error Handling
**Symptoms**: Tool crashes on API errors, unhandled exceptions

**Check**:
- [ ] Test with invalid inputs
- [ ] Test with network failures
- [ ] Check for try/except blocks

**Fix**: Add try/except blocks with specific error handling for HTTP errors

### Phase 7: Final Verification

#### Step 7.1: Comprehensive Testing
- [ ] Test all tools with valid inputs
- [ ] Test error cases with invalid inputs
- [ ] Test edge cases (empty results, null values)
- [ ] Verify results contain meaningful data
- [ ] Check performance is reasonable

#### Step 7.2: Validation Checks
- [ ] JSON files are valid
- [ ] Python syntax is valid
- [ ] No linting errors
- [ ] All tools load without errors
- [ ] Tool functions imported in `tools/__init__.py` (⚠️ Auto-generated, verify they exist)
- [ ] Category registered in `default_config.py`

**Validation Commands**:
```bash
python3 -m json.tool src/tooluniverse/data/{category}_tools.json  # Validate JSON
python3 -m py_compile src/tooluniverse/{category}_tool.py  # Check syntax
```

#### Step 7.3: Documentation
- [ ] Tool descriptions are clear and complete
- [ ] Parameter descriptions include examples
- [ ] Return schemas match actual output
- [ ] Create example script in `examples/`
- [ ] Document findings and fixes

### Complete Tool Improvement Checklist Summary

**Quick Reference - Run through all phases**:

**Phase 1: Initial Assessment**
- [ ] Identify all tool files
- [ ] Verify basic structure (class names, JSON validity, loading)

**Phase 2: Functionality Testing**
- [ ] Test tool execution with sample inputs
- [ ] Test API endpoints directly
- [ ] Verify meaningful content returned

**Phase 3: Description Improvement**
- [ ] Review and improve tool descriptions
- [ ] Review and improve parameter descriptions
- [ ] Review and improve return schemas

**Phase 4: Error Handling**
- [ ] Review current error handling
- [ ] Improve error messages (specific, actionable)
- [ ] Add retry logic if needed

**Phase 5: Finding Missing Tools**
- [ ] Research API capabilities
- [ ] Create gap analysis matrix
- [ ] Identify subset extraction opportunities

**Phase 6: Fix Common Issues**
- [ ] Fix tool class name mismatches
- [ ] Fix response format mismatches
- [ ] Fix endpoint URL issues
- [ ] Add missing error handling

**Phase 7: Final Verification**
- [ ] Comprehensive testing
- [ ] Validation checks
- [ ] Documentation updates

---

## 3. Quick Reference: Common Commands

### Validation
```bash
python3 -m json.tool src/tooluniverse/data/{category}_tools.json  # Validate JSON
python3 -m py_compile src/tooluniverse/{category}_tool.py  # Check syntax
```

### Testing
```bash
python3 examples/{category}_tools_example.py  # Test tool execution
```

### Finding Tools
```bash
ls src/tooluniverse/tools/{category}_*.py  # List tool files
grep -c "\"name\":" src/tooluniverse/data/{category}_tools.json  # Count tools
grep "@register_tool" src/tooluniverse/{category}_tool.py  # Check registration
```

---