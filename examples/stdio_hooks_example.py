#!/usr/bin/env python3
"""
Test MCP stdio mode with hooks enabled and disabled
"""
import subprocess
import json
import time
import sys
import select


def read_with_timeout(process, timeout=5):
    """Read from process with timeout"""
    if sys.platform == "win32":
        # Windows doesn't support select for pipes
        return process.stdout.readline()
    else:
        ready, _, _ = select.select([process.stdout], [], [], timeout)
        if ready:
            return process.stdout.readline()
        return None


def run_stdio_test(hooks_enabled=False, timeout=60):
    """Run stdio test"""
    print(f"\n{'='*60}")
    print(
        f"Test mode: {'hooks enabled' if hooks_enabled else 'hooks disabled'}"
    )
    print(f"Timeout: {timeout} seconds")
    print(f"{'='*60}")

    # Build command
    cmd = [
        sys.executable,
        "-c",
        f"""
import sys
sys.path.insert(0, 'src')
from tooluniverse.smcp_server import run_stdio_server
sys.argv = ['tooluniverse-stdio'] + (['--hooks'] if {hooks_enabled} else [])
run_stdio_server()
""",
    ]

    print(f"Starting command: {' '.join(cmd[:3])} ...")

    # Start server process
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,
    )

    try:
        # Wait for server to start and read startup logs
        print("Waiting for server to start...")
        time.sleep(3)

        # Read and discard startup logs
        print("Reading startup logs...")
        startup_timeout = 10
        start_time = time.time()
        while time.time() - start_time < startup_timeout:
            line = read_with_timeout(process, 1)
            if not line:
                continue
            print(f"Startup log: {line.strip()}")
            if (
                "Starting ToolUniverse SMCP Server" in line
                or "Server started" in line
            ):
                break

        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        print("Sending initialization request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Read initialization response
        init_response = read_with_timeout(process, 5)
        if init_response:
            print(f"Initialization response: {init_response.strip()}")
        else:
            print("⚠️ No initialization response received")

        # Send initialized notification per MCP before listing tools
        initialized_notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        process.stdin.write(json.dumps(initialized_notif) + "\n")
        process.stdin.flush()

        # Send tools/list request (with empty params)
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }

        print("Sending tools/list request...")
        process.stdin.write(json.dumps(list_request) + "\n")
        process.stdin.flush()

        # Read tools/list response
        list_response = read_with_timeout(process, 10)
        if list_response:
            print(
                f"tools/list response length: {len(list_response)} characters"
            )
            print(f"tools/list response content: {list_response}")
            try:
                tools_data = json.loads(list_response)
                if "result" in tools_data and "tools" in tools_data["result"]:
                    tools = tools_data["result"]["tools"]
                    print(f"Available tools: {len(tools)}")
                    # Show first few tool names
                    for i, tool in enumerate(tools[:5]):
                        print(f"  {i+1}. {tool.get('name', 'Unknown')}")
                    if len(tools) > 5:
                        print(f"  ... and {len(tools) - 5} more tools")
                elif "error" in tools_data:
                    print(
                        f"⚠️ tools/list error: {tools_data['error']}"
                    )
                else:
                    print("⚠️ Unexpected tools/list response format")
                    print(f"Response keys: {list(tools_data.keys())}")
            except json.JSONDecodeError:
                print("⚠️ Could not parse tools/list response as JSON")
        else:
            print("⚠️ No tools/list response received")

        # Send test tool call request
        test_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_server_info",
                "arguments": {},
            },
        }

        print("Sending test tool call request...")
        process.stdin.write(json.dumps(test_request) + "\n")
        process.stdin.flush()

        # Read tool call response with timeout
        print("Waiting for tool call response...")
        start_time = time.time()
        tool_response = ""
        response_timeout = timeout - 20  # Reserve 20 seconds for other operations

        while time.time() - start_time < response_timeout:
            line = read_with_timeout(process, 2)
            if not line:
                continue

            tool_response += line
            print(f"Received response line: {repr(line)}")

            # Check if it's a JSON response
            try:
                json.loads(line.strip())
                print("✅ Found JSON response")
                break
            except json.JSONDecodeError:
                continue

        end_time = time.time()
        response_time = end_time - start_time
        response_length = len(tool_response)

        print(f"Tool call response time: {response_time:.2f} seconds")
        print(
            f"Tool call response length: {response_length} characters"
        )

        # Try to parse JSON response
        json_response = None
        for line in tool_response.split("\n"):
            if line.strip().startswith('{"jsonrpc"'):
                try:
                    json_response = json.loads(line.strip())
                    break
                except json.JSONDecodeError:
                    continue

        if json_response:
            print("✅ Successfully parsed JSON response")
            print(f"Response ID: {json_response.get('id')}")
            if "result" in json_response:
                print("✅ Tool call successful")
                result_content = json_response["result"]
                if "content" in result_content:
                    content_text = str(result_content["content"])
                    content_length = len(content_text)
                    print(
                        f"Tool response content length: {content_length} characters"
                    )

                    # Check if it's a summary
                    if "summary" in content_text.lower() or "摘要" in content_text:
                        print("✅ Summary content detected")
                    else:
                        print("📄 Original content (not summarized)")
                else:
                    print("⚠️ No content field in tool response")
            elif "error" in json_response:
                print(f"❌ Tool call failed: {json_response['error']}")
        else:
            print("⚠️ No valid JSON response found")

        return {
            "hooks_enabled": hooks_enabled,
            "response_time": response_time,
            "response_length": response_length,
            "success": True,
        }

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return {
            "hooks_enabled": hooks_enabled,
            "response_time": None,
            "response_length": None,
            "success": False,
            "error": str(e),
        }
    finally:
        # Clean up process
        try:
            process.terminate()
            process.wait(timeout=5)
        except Exception:
            process.kill()


def main():
    """Main function"""
    print("MCP stdio mode hooks test")
    print("Test tool: get_server_info")
    print("Test parameters: none")

    # Test with hooks disabled
    result_no_hooks = run_stdio_test(hooks_enabled=False, timeout=60)

    # Test with hooks enabled
    result_with_hooks = run_stdio_test(hooks_enabled=True, timeout=120)

    # Compare results
    print(f"\n{'='*60}")
    print("Test results comparison")
    print(f"{'='*60}")

    print("Hooks disabled:")
    if result_no_hooks["success"]:
        print(
            f"  ✅ Success - Response time: {result_no_hooks['response_time']:.2f}s, "
            f"Length: {result_no_hooks['response_length']} characters"
        )
    else:
        print(f"  ❌ Failed - {result_no_hooks.get('error', 'Unknown error')}")

    print("Hooks enabled:")
    if result_with_hooks["success"]:
        print(
            f"  ✅ Success - Response time: {result_with_hooks['response_time']:.2f}s, "
            f"Length: {result_with_hooks['response_length']} characters"
        )
    else:
        print(f"  ❌ Failed - {result_with_hooks.get('error', 'Unknown error')}")

    # Performance comparison
    if result_no_hooks["success"] and result_with_hooks["success"]:
        time_diff = (
            result_with_hooks["response_time"] - result_no_hooks["response_time"]
        )
        length_diff = (
            result_with_hooks["response_length"] - result_no_hooks["response_length"]
        )

        print("\nPerformance comparison:")
        print(f"  Time difference: {time_diff:+.2f}s "
              f"({'hooks slower' if time_diff > 0 else 'hooks faster'})")
        print(f"  Length difference: {length_diff:+d} characters "
              f"({'hooks longer' if length_diff > 0 else 'hooks shorter'})")

        if abs(time_diff) < 5.0:
            print("  ✅ Time difference within acceptable range")
        else:
            print("  ⚠️ Large time difference, needs further optimization")


if __name__ == "__main__":
    main()
