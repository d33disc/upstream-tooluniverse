#!/usr/bin/env python3
"""
Examples for PPI (Protein-Protein Interaction) tools
Demonstrates how to use STRING and BioGRID tools for real data access
"""

import sys
import os
import json
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tooluniverse.string_tool import STRINGRESTTool
from tooluniverse.biogrid_tool import BioGRIDRESTTool


def example_string_tool():
    """Example usage of STRING tool for protein-protein interactions"""
    print("🧬 STRING Database Tool Example")
    print("=" * 50)
    
    # Initialize tool
    tool_config = {
        "type": "STRINGRESTTool",
        "name": "STRING_get_protein_interactions",
        "description": "Query protein-protein interactions from STRING database",
        "parameter": {
            "required": ["protein_ids"],
            "properties": {
                "protein_ids": {"type": "array", "items": {"type": "string"}},
                "species": {"type": "integer", "default": 9606},
                "confidence_score": {"type": "number", "default": 0.4},
                "limit": {"type": "integer", "default": 50}
            }
        },
        "fields": {
            "endpoint": "/tsv/network",
            "return_format": "TSV"
        }
    }
    
    tool = STRINGRESTTool(tool_config)
    
    # Example 1: Query cancer-related proteins
    print("\n📊 Example 1: Cancer-related protein interactions")
    print("-" * 40)
    
    cancer_proteins = ["TP53", "BRCA1", "MDM2", "MYC", "RB1"]
    arguments = {
        "protein_ids": cancer_proteins,
        "species": 9606,  # Human
        "confidence_score": 0.4,  # Medium confidence
        "limit": 20
    }
    
    try:
        result = tool.run(arguments)
        
        if "data" in result and not result.get("error"):
            print(f"✅ Found {len(result['data'])} interactions")
            print(f"📋 Header: {result['header']}")
            
            # Show first few interactions
            for i, interaction in enumerate(result["data"][:5]):
                protein_a = interaction.get("preferredName_A", "Unknown")
                protein_b = interaction.get("preferredName_B", "Unknown")
                score = interaction.get("score", "0")
                print(f"  {i+1}. {protein_a} - {protein_b} (score: {score})")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Example 2: Query with different confidence levels
    print("\n📊 Example 2: High confidence interactions only")
    print("-" * 40)
    
    arguments_high_conf = {
        "protein_ids": ["TP53", "BRCA1"],
        "species": 9606,
        "confidence_score": 0.7,  # High confidence
        "limit": 10
    }
    
    try:
        result = tool.run(arguments_high_conf)
        
        if "data" in result and not result.get("error"):
            print(f"✅ Found {len(result['data'])} high-confidence interactions")
            for i, interaction in enumerate(result["data"][:3]):
                protein_a = interaction.get("preferredName_A", "Unknown")
                protein_b = interaction.get("preferredName_B", "Unknown")
                score = interaction.get("score", "0")
                print(f"  {i+1}. {protein_a} - {protein_b} (score: {score})")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def example_biogrid_tool():
    """Example usage of BioGRID tool for protein interactions"""
    print("\n🧬 BioGRID Database Tool Example")
    print("=" * 50)
    
    # Initialize tool
    tool_config = {
        "type": "BioGRIDRESTTool",
        "name": "BioGRID_get_interactions",
        "description": "Query protein and genetic interactions from BioGRID database",
        "parameter": {
            "required": ["gene_names"],
            "properties": {
                "gene_names": {"type": "array", "items": {"type": "string"}},
                "organism": {"type": "string", "default": "Homo sapiens"},
                "interaction_type": {"type": "string", "default": "both"},
                "limit": {"type": "integer", "default": 100}
            }
        },
        "fields": {
            "endpoint": "/interactions/",
            "return_format": "JSON"
        }
    }
    
    tool = BioGRIDRESTTool(tool_config)
    
    # Example 1: Query with API key (simulated)
    print("\n📊 Example 1: Gene interactions with API key")
    print("-" * 40)
    
    # Note: In real usage, you would need to get an API key from BioGRID
    # For this example, we'll show the expected format
    print("🔑 API Key Required: Register at https://webservice.thebiogrid.org/")
    print("📝 Set environment variable: export BIOGRID_API_KEY='your_key_here'")
    
    # Example arguments (would work with real API key)
    example_arguments = {
        "gene_names": ["TP53", "BRCA1", "MDM2"],
        "api_key": "your_api_key_here",  # Replace with real key
        "organism": "Homo sapiens",
        "interaction_type": "physical",  # or "genetic" or "both"
        "limit": 50
    }
    
    print(f"📋 Example arguments: {json.dumps(example_arguments, indent=2)}")
    
    # Example 2: Show parameter building
    print("\n📊 Example 2: Parameter building demonstration")
    print("-" * 40)
    
    try:
        # This will raise an error because no API key is provided
        # But it demonstrates the parameter building logic
        params = tool._build_params(example_arguments)
        print("✅ Parameters built successfully:")
        for key, value in params.items():
            if key != "accesskey":  # Don't show the actual API key
                print(f"  {key}: {value}")
    except ValueError as e:
        print(f"⚠️ Expected error (no API key): {e}")
    
    # Example 3: Different organism queries
    print("\n📊 Example 3: Different organism queries")
    print("-" * 40)
    
    organisms = [
        ("Homo sapiens", 9606),
        ("Mus musculus", 10090),
        ("Drosophila melanogaster", 7227)
    ]
    
    for org_name, tax_id in organisms:
        print(f"  {org_name}: Taxonomy ID {tax_id}")


def example_combined_workflow():
    """Example of combining both tools for comprehensive analysis"""
    print("\n🔄 Combined Workflow Example")
    print("=" * 50)
    
    print("📋 Workflow: Comprehensive protein interaction analysis")
    print("1. Use STRING for initial interaction discovery")
    print("2. Use BioGRID for detailed experimental evidence")
    print("3. Cross-reference results for validation")
    
    # Step 1: STRING analysis
    print("\n🔍 Step 1: STRING analysis")
    print("-" * 30)
    
    string_config = {
        "type": "STRINGRESTTool",
        "parameter": {"required": ["protein_ids"]},
        "fields": {"endpoint": "/tsv/network", "return_format": "TSV"}
    }
    string_tool = STRINGRESTTool(string_config)
    
    # Query for cancer-related proteins
    cancer_genes = ["TP53", "BRCA1", "MDM2"]
    string_args = {
        "protein_ids": cancer_genes,
        "species": 9606,
        "confidence_score": 0.5,
        "limit": 10
    }
    
    try:
        string_result = string_tool.run(string_args)
        if "data" in string_result and not string_result.get("error"):
            print(f"✅ STRING found {len(string_result['data'])} interactions")
            
            # Extract interacting proteins
            interacting_proteins = set()
            for interaction in string_result["data"]:
                interacting_proteins.add(interaction.get("preferredName_A", ""))
                interacting_proteins.add(interaction.get("preferredName_B", ""))
            
            print(f"📊 Proteins involved: {sorted(interacting_proteins)}")
        else:
            print(f"❌ STRING error: {string_result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ STRING exception: {e}")
    
    # Step 2: BioGRID analysis (would require API key)
    print("\n🔍 Step 2: BioGRID analysis (requires API key)")
    print("-" * 30)
    print("📝 To complete this step:")
    print("1. Get API key from https://webservice.thebiogrid.org/")
    print("2. Set environment variable: export BIOGRID_API_KEY='your_key'")
    print("3. Run BioGRID queries for experimental validation")
    
    # Step 3: Analysis recommendations
    print("\n📊 Step 3: Analysis recommendations")
    print("-" * 30)
    print("✅ Use STRING for:")
    print("  - Initial interaction discovery")
    print("  - Functional annotation")
    print("  - Confidence scoring")
    print("  - Pathway analysis")
    
    print("✅ Use BioGRID for:")
    print("  - Experimental evidence")
    print("  - Publication references")
    print("  - Detailed interaction types")
    print("  - Cross-species comparisons")


def main():
    """Run all examples"""
    print("🧬 PPI Tools Examples")
    print("=" * 50)
    print("This script demonstrates the usage of STRING and BioGRID tools")
    print("for protein-protein interaction analysis.")
    
    # Run examples
    example_string_tool()
    example_biogrid_tool()
    example_combined_workflow()
    
    print("\n🎯 Summary")
    print("=" * 50)
    print("✅ STRING tool: Ready to use (no API key required)")
    print("⚠️  BioGRID tool: Requires API key registration")
    print("📚 Both tools provide complementary data for comprehensive analysis")
    
    print("\n📖 Next Steps:")
    print("1. Test STRING tool with your protein lists")
    print("2. Register for BioGRID API key if needed")
    print("3. Combine results for comprehensive analysis")
    print("4. Integrate with other ToolUniverse tools")


if __name__ == "__main__":
    main()
