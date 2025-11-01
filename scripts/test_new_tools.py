#!/usr/bin/env python3
"""
Test newly integrated tools using test_examples from their configs.

This script:
1. Loads tool configs using ToolUniverse
2. Extracts test_examples from each config
3. Runs each tool with its test examples
4. Validates return results against return_schema
5. Reports success/failure
"""
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tooluniverse import ToolUniverse

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("⚠️  jsonschema not available. Schema validation will be skipped.")


def load_config_from_file(config_path: str) -> list:
    """Load tool config JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)


def validate_against_schema(data: Any, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate data against JSON schema.
    
    Args:
        data: Data to validate
        schema: JSON schema to validate against
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not JSONSCHEMA_AVAILABLE:
        return True, None  # Skip validation if jsonschema not available
        
    if not schema:
        return True, None  # No schema to validate against
        
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        error_path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        error_msg = f"Schema validation failed at '{error_path}': {e.message}"
        if e.context:
            error_msg += f"\n  Context: {', '.join(str(c.message) for c in e.context[:3])}"
        return False, error_msg
    except Exception as e:
        return False, f"Schema validation error: {str(e)}"


def extract_result_data(result: Dict[str, Any]) -> Any:
    """
    Extract the actual data from ToolUniverse result format.
    
    ToolUniverse may return results in different formats:
    - {"success": True, "data": {...}}
    - {"success": True, ...}  (direct data)
    - The result itself if it's not a dict
    """
    if not isinstance(result, dict):
        return result
        
    if result.get("success") is False:
        return None  # Error case, no data to validate
        
    # Try to extract data field
    if "data" in result:
        return result["data"]
    
    # If no "data" field, return the whole result (minus success/error fields)
    return {k: v for k, v in result.items() if k not in ["success", "error", "error_details"]}


def test_tool_with_examples(
    tu: ToolUniverse, 
    tool_name: str, 
    examples: list, 
    return_schema: Optional[Dict[str, Any]] = None
):
    """Test a tool with its test examples and validate against return_schema."""
    results = []
    for idx, example in enumerate(examples):
        try:
            result = tu.run_one_function(
                {"name": tool_name, "arguments": example}
            )
            success = isinstance(result, dict) and result.get("success", False)
            
            schema_valid = True
            schema_error = None
            
            if success and return_schema:
                # Extract actual data from result
                result_data = extract_result_data(result)
                if result_data is not None:
                    # If schema expects top-level structure with status/url but we have just data,
                    # wrap it appropriately or validate the inner data.data structure
                    schema_to_validate = return_schema
                    data_to_validate = result_data
                    
                    # Check if schema expects status/url at root but we only have data
                    schema_root_props = return_schema.get("properties", {})
                    if "status" in schema_root_props and "data" in schema_root_props:
                        # Schema expects full structure, but we only have extracted data
                        # If result_data is the inner data object, wrap it
                        if isinstance(result_data, dict) and "data" in result_data:
                            # result_data is already {"data": [...]} - validate inner structure
                            inner_data_schema = schema_root_props.get("data", {})
                            if inner_data_schema:
                                schema_to_validate = inner_data_schema
                        else:
                            # Wrap in expected structure (make status/url optional in validation)
                            pass  # Try validating as-is first
                    
                    schema_valid, schema_error = validate_against_schema(data_to_validate, schema_to_validate)
                else:
                    schema_valid = False
                    schema_error = "No data returned to validate"
            
            results.append(
                {
                    "example_idx": idx,
                    "example": example,
                    "success": success,
                    "schema_valid": schema_valid,
                    "error": None if success else result.get("error", "Unknown error"),
                    "schema_error": schema_error,
                }
            )
        except Exception as e:
            results.append(
                {
                    "example_idx": idx,
                    "example": example,
                    "success": False,
                    "schema_valid": False,
                    "error": str(e),
                    "schema_error": None,
                }
            )
    return results


def main():
    # Tool config files for newly integrated tools
    tool_configs = {
        "GBIF": "src/tooluniverse/data/gbif_tools.json",
        "OBIS": "src/tooluniverse/data/obis_tools.json",
        "WikiPathways": "src/tooluniverse/data/wikipathways_tools.json",
        "RNAcentral": "src/tooluniverse/data/rnacentral_tools.json",
        "ENCODE": "src/tooluniverse/data/encode_tools.json",
        "GTEx": "src/tooluniverse/data/gtex_tools.json",
        "MGnify": "src/tooluniverse/data/mgnify_tools.json",
        "GDC": "src/tooluniverse/data/gdc_tools.json",
    }

    repo_root = Path(__file__).parent.parent
    tu = ToolUniverse()
    tu.load_tools()

    all_results = {}
    total_tests = 0
    total_passed = 0
    total_schema_tests = 0
    total_schema_passed = 0

    for tool_group, config_path in tool_configs.items():
        full_path = repo_root / config_path
        if not full_path.exists():
            print(f"⚠️  Config not found: {config_path}")
            continue

        config = load_config_from_file(full_path)
        group_results = []

        for tool_def in config:
            tool_name = tool_def.get("name")
            test_examples = tool_def.get("test_examples", [])
            return_schema = tool_def.get("return_schema")

            if not tool_name:
                continue

            if not test_examples:
                print(f"⚠️  {tool_name}: No test_examples found")
                continue

            schema_info = " (with schema validation)" if return_schema else " (no return_schema)"
            print(f"\n🧪 Testing {tool_name} ({len(test_examples)} examples){schema_info}...")
            results = test_tool_with_examples(tu, tool_name, test_examples, return_schema)

            for r in results:
                total_tests += 1
                execution_pass = r["success"]
                schema_pass = r.get("schema_valid", True)
                
                # Track schema validation separately
                if return_schema and execution_pass:
                    total_schema_tests += 1
                    if schema_pass:
                        total_schema_passed += 1
                
                if execution_pass and schema_pass:
                    total_passed += 1
                    status_icon = "✅"
                    status_msg = "PASS"
                else:
                    status_icon = "❌"
                    status_parts = []
                    if not execution_pass:
                        status_parts.append(f"Execution: {r['error']}")
                    if not schema_pass and return_schema:
                        status_parts.append(f"Schema: {r.get('schema_error', 'Invalid')}")
                    status_msg = " | ".join(status_parts) if status_parts else "FAIL"
                
                print(f"  {status_icon} Example {r['example_idx']+1}: {status_msg}")
                
                # Show schema validation details if failed
                if execution_pass and not schema_pass and r.get("schema_error"):
                    print(f"      └─ Schema error: {r['schema_error']}")

            group_results.append(
                {"tool_name": tool_name, "results": results}
            )

        all_results[tool_group] = group_results

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_tests - total_passed}")
    if total_tests > 0:
        print(f"  Success rate: {100 * total_passed / total_tests:.1f}%")
    
    if total_schema_tests > 0:
        print(f"\n📋 Schema Validation:")
        print(f"  Schema tests: {total_schema_tests}")
        print(f"  Schema passed: {total_schema_passed}")
        print(f"  Schema failed: {total_schema_tests - total_schema_passed}")
        if total_schema_tests > 0:
            print(f"  Schema validation rate: {100 * total_schema_passed / total_schema_tests:.1f}%")

    # Exit with error if any tests failed
    if total_passed < total_tests:
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

