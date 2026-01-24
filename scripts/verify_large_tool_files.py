#!/usr/bin/env python3
"""
Verification script for large tool files:
- RCSB PDB (39 tools)
- OpenTargets (54 tools)
- FDA Drug Labeling (155 tools)

This script checks:
1. Tool count and structure
2. Return schema completeness
3. Test examples presence
4. Basic functionality (sample tests)
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tooluniverse import ToolUniverse


def analyze_tool_file(file_path, tool_type):
    """Analyze a tool JSON file for completeness"""
    with open(file_path, 'r') as f:
        tools = json.load(f)
    
    stats = {
        'total_tools': len(tools),
        'has_return_schema': 0,
        'missing_return_schema': [],
        'has_test_examples': 0,
        'missing_test_examples': [],
        'has_description': 0,
        'missing_description': [],
        'has_parameters': 0,
        'missing_parameters': [],
    }
    
    for tool in tools:
        tool_name = tool.get('name', 'unknown')
        
        # Check return_schema
        if tool.get('return_schema'):
            stats['has_return_schema'] += 1
        else:
            stats['missing_return_schema'].append(tool_name)
        
        # Check test_examples
        if tool.get('test_examples'):
            stats['has_test_examples'] += 1
        else:
            stats['missing_test_examples'].append(tool_name)
        
        # Check description
        if tool.get('description'):
            stats['has_description'] += 1
        else:
            stats['missing_description'].append(tool_name)
        
        # Check parameters
        if tool.get('parameter'):
            stats['has_parameters'] += 1
        else:
            stats['missing_parameters'].append(tool_name)
    
    return stats, tools


def test_sample_tools(tu, tools_config, tool_type, max_tests=3):
    """Test a sample of tools to verify functionality"""
    results = []
    
    # Select tools with test_examples
    testable_tools = [t for t in tools_config if t.get('test_examples')]
    
    # Test up to max_tests tools
    for tool in testable_tools[:max_tests]:
        tool_name = tool.get('name')
        test_example = tool.get('test_examples', [{}])[0]
        
        # Convert test_example to query format
        query = {
            'name': tool_name,
            'arguments': test_example
        }
        
        try:
            result = tu.run(query)
            if result and 'error' not in str(result).lower():
                results.append((tool_name, True, None))
            else:
                error_msg = str(result)[:150] if result else 'No result'
                results.append((tool_name, False, error_msg))
        except Exception as e:
            results.append((tool_name, False, str(e)[:150]))
    
    return results


def main():
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "src" / "tooluniverse" / "data"
    
    # Tool files to verify
    tool_files = {
        'rcsb_pdb': {
            'file': data_dir / 'rcsb_pdb_tools.json',
            'type': 'RCSBTool',
            'category': 'rcsb_pdb'
        },
        'opentargets': {
            'file': data_dir / 'opentarget_tools.json',
            'type': 'OpenTarget',
            'category': 'opentarget'
        },
        'fda_drug_labeling': {
            'file': data_dir / 'fda_drug_labeling_tools.json',
            'type': 'FDADrugLabel',
            'category': 'fda_drug_label'
        }
    }
    
    print("=" * 80)
    print("Large Tool Files Verification Report")
    print("=" * 80)
    print()
    
    all_results = {}
    
    # Initialize ToolUniverse
    print("Initializing ToolUniverse...")
    tu = ToolUniverse()
    
    for tool_name, config in tool_files.items():
        file_path = config['file']
        
        if not file_path.exists():
            print(f"❌ {tool_name}: File not found at {file_path}")
            continue
        
        print(f"\n{'=' * 80}")
        print(f"Verifying: {tool_name.upper()}")
        print(f"File: {file_path}")
        print(f"{'=' * 80}\n")
        
        # Analyze tool file
        stats, tools_config = analyze_tool_file(file_path, config['type'])
        
        print(f"Total tools: {stats['total_tools']}")
        print(f"Return schemas: {stats['has_return_schema']}/{stats['total_tools']} ({stats['has_return_schema']/stats['total_tools']*100:.1f}%)")
        print(f"Test examples: {stats['has_test_examples']}/{stats['total_tools']} ({stats['has_test_examples']/stats['total_tools']*100:.1f}%)")
        print(f"Descriptions: {stats['has_description']}/{stats['total_tools']} ({stats['has_description']/stats['total_tools']*100:.1f}%)")
        print(f"Parameters: {stats['has_parameters']}/{stats['total_tools']} ({stats['has_parameters']/stats['total_tools']*100:.1f}%)")
        
        # Show missing items
        if stats['missing_return_schema']:
            print(f"\n⚠️  Missing return_schema ({len(stats['missing_return_schema'])}):")
            for name in stats['missing_return_schema'][:5]:
                print(f"   - {name}")
            if len(stats['missing_return_schema']) > 5:
                print(f"   ... and {len(stats['missing_return_schema']) - 5} more")
        
        if stats['missing_test_examples']:
            print(f"\n⚠️  Missing test_examples ({len(stats['missing_test_examples'])}):")
            for name in stats['missing_test_examples'][:5]:
                print(f"   - {name}")
            if len(stats['missing_test_examples']) > 5:
                print(f"   ... and {len(stats['missing_test_examples']) - 5} more")
        
        # Load tools and test
        print(f"\nLoading {tool_name} tools...")
        try:
            tu.load_tools(tool_type=[config['category']])
            print(f"✅ Loaded {len([t for t in tu.all_tools if t.get('type') == config['type']])} tools")
            
            # Test sample tools
            print(f"\nTesting sample tools (max 3)...")
            test_results = test_sample_tools(tu, tools_config, config['type'], max_tests=3)
            
            passed = sum(1 for _, success, _ in test_results if success)
            print(f"Test results: {passed}/{len(test_results)} passed")
            
            for tool_name_test, success, error in test_results:
                status = "✅" if success else "❌"
                print(f"  {status} {tool_name_test}")
                if error:
                    print(f"     Error: {error[:100]}")
            
            all_results[tool_name] = {
                'stats': stats,
                'test_results': test_results
            }
        except Exception as e:
            print(f"❌ Error loading/testing tools: {str(e)}")
            all_results[tool_name] = {
                'stats': stats,
                'test_results': [],
                'error': str(e)
            }
    
    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}\n")
    
    for tool_name, results in all_results.items():
        stats = results['stats']
        test_results = results.get('test_results', [])
        
        print(f"{tool_name.upper()}:")
        print(f"  Tools: {stats['total_tools']}")
        print(f"  Return schemas: {stats['has_return_schema']}/{stats['total_tools']}")
        print(f"  Test examples: {stats['has_test_examples']}/{stats['total_tools']}")
        if test_results:
            passed = sum(1 for _, success, _ in test_results if success)
            print(f"  Functional tests: {passed}/{len(test_results)} passed")
        print()
    
    tu.close()
    print("Verification complete!")


if __name__ == "__main__":
    main()
