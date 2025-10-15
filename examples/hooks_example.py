#!/usr/bin/env python3
"""
ToolUniverse Hooks Example

A simple, clear example demonstrating hook functionality.
This example shows how to use SummarizationHook and FileSaveHook
with ToolUniverse for automatic output processing.
"""

import sys
import os
import time
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tooluniverse import ToolUniverse


def basic_hooks_example():
    """Basic hook usage - simple and clear"""
    print("🔧 BASIC HOOKS EXAMPLE")
    print("=" * 50)
    
    # 1. Create ToolUniverse with default SummarizationHook
    print("1. Creating ToolUniverse with default SummarizationHook...")
    tu = ToolUniverse(hooks_enabled=True)
    tu.load_tools()
    
    # 2. Run a tool that produces long output
    print("2. Running tool with long output...")
    result = tu.run({
        "name": "OpenTargets_get_target_gene_ontology_by_ensemblID",
        "arguments": {"ensemblId": "ENSG00000012048"}
    })
    
    # 3. Show results
    print(f"✅ Result type: {type(result).__name__}")
    if isinstance(result, dict) and "summary" in result:
        print(f"📝 Summary length: {len(result['summary'])} characters")
        print(f"📊 Original length: {result.get('original_length', 'N/A')}")
    else:
        print(f"📄 Result length: {len(str(result))} characters")
    
    return result


def file_save_hook_example():
    """FileSaveHook example - saves large outputs to files"""
    print("\n🔧 FILE SAVE HOOK EXAMPLE")
    print("=" * 50)
    
    # Configure FileSaveHook for large outputs
    hook_config = {
        "hooks": [{
            "name": "file_save_hook",
            "type": "FileSaveHook",
            "enabled": True,
            "conditions": {
                "output_length": {"operator": ">", "threshold": 1000}
            },
            "hook_config": {
                "temp_dir": tempfile.gettempdir(),
                "file_prefix": "tool_output",
                "include_metadata": True
            }
        }]
    }
    
    # Create ToolUniverse with FileSaveHook
    print("1. Creating ToolUniverse with FileSaveHook...")
    tu = ToolUniverse(hooks_enabled=True, hook_config=hook_config)
    tu.load_tools()
    
    # Run tool
    print("2. Running tool...")
    result = tu.run({
        "name": "OpenTargets_get_target_gene_ontology_by_ensemblID", 
        "arguments": {"ensemblId": "ENSG00000012048"}
    })
    
    # Show file save results
    if isinstance(result, dict) and "file_path" in result:
        print(f"📁 File saved: {result['file_path']}")
        print(f"📊 Format: {result['data_format']}")
        print(f"📏 Size: {result['file_size']} bytes")
        
        # Verify file exists
        if os.path.exists(result['file_path']):
            print("✅ File verification: SUCCESS")
        else:
            print("❌ File verification: FAILED")
    else:
        print("ℹ️  Output was not large enough to trigger file save")
    
    return result


def performance_comparison():
    """Compare performance with and without hooks"""
    print("\n🔧 PERFORMANCE COMPARISON")
    print("=" * 50)
    
    # Test without hooks
    print("1. Testing without hooks...")
    tu_no_hooks = ToolUniverse(hooks_enabled=False)
    tu_no_hooks.load_tools()
    
    start_time = time.time()
    result_no_hooks = tu_no_hooks.run({
        "name": "OpenTargets_get_target_gene_ontology_by_ensemblID",
        "arguments": {"ensemblId": "ENSG00000012048"}
    })
    time_no_hooks = time.time() - start_time
    
    # Test with hooks
    print("2. Testing with SummarizationHook...")
    tu_with_hooks = ToolUniverse(hooks_enabled=True)
    tu_with_hooks.load_tools()
    
    start_time = time.time()
    result_with_hooks = tu_with_hooks.run({
        "name": "OpenTargets_get_target_gene_ontology_by_ensemblID",
        "arguments": {"ensemblId": "ENSG00000012048"}
    })
    time_with_hooks = time.time() - start_time
    
    # Show comparison
    print("\n📊 PERFORMANCE RESULTS:")
    print("-" * 40)
    print(f"No hooks:     {time_no_hooks:.2f}s")
    print(f"With hooks:   {time_with_hooks:.2f}s")
    
    if time_no_hooks > 0:
        overhead = (time_with_hooks - time_no_hooks) / time_no_hooks * 100
        print(f"Overhead:     +{overhead:.1f}%")
    
    # Show output size comparison
    size_no_hooks = len(str(result_no_hooks))
    size_with_hooks = len(str(result_with_hooks))
    reduction = (1 - size_with_hooks / size_no_hooks) * 100 if size_no_hooks > 0 else 0
    
    print(f"\n📏 OUTPUT SIZE:")
    print(f"No hooks:     {size_no_hooks:,} chars")
    print(f"With hooks:   {size_with_hooks:,} chars")
    print(f"Reduction:    {reduction:.1f}%")
    
    return result_no_hooks, result_with_hooks


def custom_hook_config_example():
    """Custom hook configuration example"""
    print("\n🔧 CUSTOM HOOK CONFIGURATION")
    print("=" * 50)
    
    # Custom configuration with specific settings
    custom_config = {
        "hooks": [{
            "name": "custom_summary_hook",
            "type": "SummarizationHook", 
            "enabled": True,
            "conditions": {
                "output_length": {"operator": ">", "threshold": 5000}
            },
            "hook_config": {
                "max_tokens": 1000,
                "summary_style": "concise",
                "chunk_size": 2000
            }
        }]
    }
    
    print("1. Using custom SummarizationHook configuration...")
    print("   - Only triggers for outputs > 5000 characters")
    print("   - Max 1000 tokens, concise style")
    print("   - 2000 character chunks")
    
    tu = ToolUniverse(hooks_enabled=True, hook_config=custom_config)
    tu.load_tools()
    
    result = tu.run({
        "name": "OpenTargets_get_target_gene_ontology_by_ensemblID",
        "arguments": {"ensemblId": "ENSG00000012048"}
    })
    
    print("2. Custom hook processing completed")
    if isinstance(result, dict) and "summary" in result:
        print(f"✅ Summary generated: {len(result['summary'])} characters")
    
    return result


def main():
    """Run all hook examples"""
    print("🚀 ToolUniverse Hooks Example")
    print("=" * 60)
    print("This example demonstrates hook functionality including:")
    print("• Basic SummarizationHook usage")
    print("• FileSaveHook for large outputs") 
    print("• Performance comparison")
    print("• Custom configuration")
    print("=" * 60)
    
    try:
        # Run examples
        basic_hooks_example()
        file_save_hook_example()
        performance_comparison()
        custom_hook_config_example()
        
        print("\n🎉 All examples completed successfully!")
        print("\n💡 Key Takeaways:")
        print("• Hooks automatically process tool outputs")
        print("• SummarizationHook reduces output size with AI")
        print("• FileSaveHook saves large outputs to files")
        print("• Performance overhead depends on output size and AI processing")
        print("• Custom configurations allow fine-tuned control")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("💡 Make sure you have API keys configured for AI tools")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())