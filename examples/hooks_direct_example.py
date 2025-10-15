#!/usr/bin/env python3
"""
Simplified MCP stdio mode hooks test
Directly test tool calling functionality
"""
import subprocess
import sys
import signal
import time


def test_tool_call_directly(hooks_enabled=False, timeout=90):
    """Directly test tool calling"""
    print(f"\n{'='*60}")
    print(f"Test mode: {'hooks enabled' if hooks_enabled else 'hooks disabled'}")
    print(f"Timeout setting: {timeout} seconds")
    print(f"{'='*60}")

    # Build command
    cmd = [
        sys.executable,
        "-c",
        f"""
import sys
import time
sys.path.insert(0, 'src')
from tooluniverse.execute_function import ToolUniverse

# Create ToolUniverse instance
tooluniverse = ToolUniverse()

# Configure hooks
if {hooks_enabled}:
    print("Enabling hooks...")
    tooluniverse.toggle_hooks(True)
else:
    print("Disabling hooks...")
    tooluniverse.toggle_hooks(False)

# Load tools
print("Loading tools...")
tooluniverse.load_tools()

# Test tool call
function_call = {{
    "name": "OpenTargets_get_target_gene_ontology_by_ensemblID",
    "arguments": {{"ensemblId": "ENSG00000012048"}}
}}

print("Starting tool call...")
start_time = time.time()
result = tooluniverse.run_one_function(function_call)
end_time = time.time()

response_time = end_time - start_time
result_str = str(result)
result_length = len(result_str)

print(f"Tool call completed")
print(f"Response time: {{response_time:.2f}} seconds")
print(f"Response length: {{result_length}} characters")
print(f"Response type: {{type(result)}}")

# Check if it's a summary
if "summary" in result_str.lower() or "摘要" in result_str:
    print("✅ Summary content detected")
else:
    print("📄 Original content (not summarized)")

# Output first 200 characters of result
print(f"Result preview: {{result_str[:200]}}...")
""",
    ]

    print(f"Starting command: {' '.join(cmd[:3])} ...")

    # Start process
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,
    )

    try:
        # Wait for execution to complete
        stdout, stderr = process.communicate(timeout=timeout)

        print("Standard output:")
        print(stdout)

        if stderr:
            print("Standard error:")
            print(stderr)

        # Parse results
        lines = stdout.split("\n")
        response_time = None
        result_length = None
        is_summary = False

        for line in lines:
            if "Response time:" in line:
                try:
                    response_time = float(line.split(":")[1].strip().split()[0])
                except (ValueError, IndexError):
                    pass
            elif "Response length:" in line:
                try:
                    result_length = int(line.split(":")[1].strip().split()[0])
                except (ValueError, IndexError):
                    pass
            elif "Summary content detected" in line:
                is_summary = True

        return {
            "hooks_enabled": hooks_enabled,
            "response_time": response_time,
            "result_length": result_length,
            "is_summary": is_summary,
            "success": process.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
        }

    except subprocess.TimeoutExpired:
        print("❌ Test timeout")
        process.kill()
        return {
            "hooks_enabled": hooks_enabled,
            "response_time": None,
            "result_length": None,
            "is_summary": False,
            "success": False,
            "error": "timeout",
        }
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return {
            "hooks_enabled": hooks_enabled,
            "response_time": None,
            "result_length": None,
            "is_summary": False,
            "success": False,
            "error": str(e),
        }


def main():
    """Main function"""
    print("MCP stdio mode hooks direct test")
    print("Test tool: OpenTargets_get_target_gene_ontology_by_ensemblID")
    print("Test parameters: ensemblId=ENSG00000012048")

    # Test with hooks disabled
    result_no_hooks = test_tool_call_directly(hooks_enabled=False, timeout=30)

    # Test with hooks enabled (needs more time for summarization processing)
    result_with_hooks = test_tool_call_directly(hooks_enabled=True, timeout=90)

    # Compare results
    print(f"\n{'='*60}")
    print("Test results comparison")
    print(f"{'='*60}")

    print("Hooks disabled:")
    if result_no_hooks["success"]:
        print(
            f"  ✅ Success - Response time: {result_no_hooks['response_time']:.2f}s, Length: {result_no_hooks['result_length']} characters"
        )
        if result_no_hooks["is_summary"]:
            print("  📄 Summary content detected")
        else:
            print("  📄 Original content (not summarized)")
    else:
        print(f"  ❌ Failed - {result_no_hooks.get('error', 'Unknown error')}")

    print("Hooks enabled:")
    if result_with_hooks["success"]:
        print(
            f"  ✅ Success - Response time: {result_with_hooks['response_time']:.2f}s, Length: {result_with_hooks['result_length']} characters"
        )
        if result_with_hooks["is_summary"]:
            print("  ✅ Summary content detected")
        else:
            print("  📄 Original content (not summarized)")
    else:
        print(f"  ❌ Failed - {result_with_hooks.get('error', 'Unknown error')}")

    # Performance comparison
    if result_no_hooks["success"] and result_with_hooks["success"]:
        time_diff = (
            result_with_hooks["response_time"] - result_no_hooks["response_time"]
        )
        length_diff = (
            result_with_hooks["result_length"] - result_no_hooks["result_length"]
        )

        print("\nPerformance comparison:")
        print(
            f"  Time difference: {time_diff:+.2f}s ({'hooks slower' if time_diff > 0 else 'hooks faster'})"
        )
        print(
            f"  Length difference: {length_diff:+d} characters ({'hooks longer' if length_diff > 0 else 'hooks shorter'})"
        )

        if abs(time_diff) < 5.0:
            print("  ✅ Time difference within acceptable range")
        else:
            print("  ⚠️ Large time difference, needs further optimization")

        # Check if hooks are working
        if result_with_hooks["is_summary"] and not result_no_hooks["is_summary"]:
            print("  ✅ Hooks functionality working correctly")
        elif result_with_hooks["is_summary"] == result_no_hooks["is_summary"]:
            print("  ⚠️ Hooks functionality may not be working")


if __name__ == "__main__":
    main()
