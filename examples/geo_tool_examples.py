#!/usr/bin/env python3
"""
Examples for GEO (Gene Expression Omnibus) tool
Demonstrates how to use GEO tool for gene expression data search
"""

import sys
import os
import json
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tooluniverse.geo_tool import GEORESTTool


def example_geo_basic_search():
    """Example of basic GEO search functionality"""
    print("🧬 GEO Database Tool - Basic Search Example")
    print("=" * 50)
    
    # Initialize tool
    tool_config = {
        "type": "GEORESTTool",
        "name": "GEO_search_expression_data",
        "description": "Search gene expression data from GEO database",
        "parameter": {
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
                "organism": {"type": "string", "default": "Homo sapiens"},
                "study_type": {"type": "string", "default": "expression"},
                "limit": {"type": "integer", "default": 10}
            }
        },
        "fields": {
            "endpoint": "/esearch.fcgi",
            "return_format": "JSON"
        }
    }
    
    tool = GEORESTTool(tool_config)
    
    # Example 1: Search for cancer-related studies
    print("\n📊 Example 1: Cancer-related gene expression studies")
    print("-" * 40)
    
    arguments = {
        "query": "cancer AND Homo sapiens[organism]",
        "organism": "Homo sapiens",
        "study_type": "expression",
        "limit": 10
    }
    
    try:
        result = tool.run(arguments)
        
        if "esearchresult" in result and not result.get("error"):
            idlist = result["esearchresult"].get("idlist", [])
            count = result["esearchresult"].get("count", "0")
            print(f"✅ Found {count} studies")
            print(f"📋 Study IDs: {idlist[:5]}")  # Show first 5 IDs
            
            if idlist:
                print(f"🔗 Example GEO study: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE{idlist[0]}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def example_geo_organism_specific():
    """Example of organism-specific searches"""
    print("\n🧬 GEO Database Tool - Organism-Specific Search")
    print("=" * 50)
    
    tool_config = {
        "type": "GEORESTTool",
        "parameter": {"required": ["query"]},
        "fields": {"endpoint": "/esearch.fcgi", "return_format": "JSON"}
    }
    tool = GEORESTTool(tool_config)
    
    # Test different organisms
    organisms = [
        ("Homo sapiens", "Human"),
        ("Mus musculus", "Mouse"),
        ("Drosophila melanogaster", "Fruit fly"),
        ("Caenorhabditis elegans", "Nematode")
    ]
    
    for organism, common_name in organisms:
        print(f"\n📊 {common_name} ({organism})")
        print("-" * 30)
        
        arguments = {
            "query": "cancer",
            "organism": organism,
            "limit": 5
        }
        
        try:
            result = tool.run(arguments)
            
            if "esearchresult" in result and not result.get("error"):
                idlist = result["esearchresult"].get("idlist", [])
                count = result["esearchresult"].get("count", "0")
                print(f"  ✅ Found {count} studies")
                if idlist:
                    print(f"  📋 Sample IDs: {idlist[:3]}")
            else:
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")


def example_geo_study_types():
    """Example of different study type searches"""
    print("\n🧬 GEO Database Tool - Study Type Examples")
    print("=" * 50)
    
    tool_config = {
        "type": "GEORESTTool",
        "parameter": {"required": ["query"]},
        "fields": {"endpoint": "/esearch.fcgi", "return_format": "JSON"}
    }
    tool = GEORESTTool(tool_config)
    
    # Different study types
    study_types = [
        ("expression", "Gene Expression"),
        ("methylation", "DNA Methylation"),
        ("chip-seq", "ChIP-seq"),
        ("rna-seq", "RNA-seq"),
        ("microarray", "Microarray")
    ]
    
    for study_type, description in study_types:
        print(f"\n📊 {description} ({study_type})")
        print("-" * 30)
        
        arguments = {
            "query": "cancer",
            "study_type": study_type,
            "organism": "Homo sapiens",
            "limit": 3
        }
        
        try:
            result = tool.run(arguments)
            
            if "esearchresult" in result and not result.get("error"):
                idlist = result["esearchresult"].get("idlist", [])
                count = result["esearchresult"].get("count", "0")
                print(f"  ✅ Found {count} studies")
                if idlist:
                    print(f"  📋 Sample IDs: {idlist[:2]}")
            else:
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")


def example_geo_advanced_queries():
    """Example of advanced query construction"""
    print("\n🧬 GEO Database Tool - Advanced Queries")
    print("=" * 50)
    
    tool_config = {
        "type": "GEORESTTool",
        "parameter": {"required": ["query"]},
        "fields": {"endpoint": "/esearch.fcgi", "return_format": "JSON"}
    }
    tool = GEORESTTool(tool_config)
    
    # Advanced query examples
    advanced_queries = [
        {
            "name": "Cancer + Specific Tissue",
            "query": "cancer AND liver[title] AND Homo sapiens[organism]",
            "description": "Cancer studies in liver tissue"
        },
        {
            "name": "Specific Gene + Disease",
            "query": "TP53 AND cancer AND Homo sapiens[organism]",
            "description": "Studies involving TP53 gene in cancer"
        },
        {
            "name": "Time Series Studies",
            "query": "time series AND expression AND Homo sapiens[organism]",
            "description": "Time series expression studies"
        },
        {
            "name": "Drug Treatment",
            "query": "drug treatment AND cancer AND Homo sapiens[organism]",
            "description": "Drug treatment studies in cancer"
        }
    ]
    
    for query_info in advanced_queries:
        print(f"\n📊 {query_info['name']}")
        print(f"   {query_info['description']}")
        print("-" * 40)
        
        arguments = {
            "query": query_info["query"],
            "limit": 3
        }
        
        try:
            result = tool.run(arguments)
            
            if "esearchresult" in result and not result.get("error"):
                idlist = result["esearchresult"].get("idlist", [])
                count = result["esearchresult"].get("count", "0")
                print(f"  ✅ Found {count} studies")
                if idlist:
                    print(f"  📋 Sample IDs: {idlist[:2]}")
            else:
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")


def example_geo_workflow():
    """Example of a complete GEO analysis workflow"""
    print("\n🔄 GEO Analysis Workflow Example")
    print("=" * 50)
    
    print("📋 Workflow: Comprehensive gene expression analysis")
    print("1. Search for relevant studies")
    print("2. Filter by study type and organism")
    print("3. Extract study metadata")
    print("4. Plan downstream analysis")
    
    tool_config = {
        "type": "GEORESTTool",
        "parameter": {"required": ["query"]},
        "fields": {"endpoint": "/esearch.fcgi", "return_format": "JSON"}
    }
    tool = GEORESTTool(tool_config)
    
    # Step 1: Broad search
    print("\n🔍 Step 1: Broad search for cancer studies")
    print("-" * 40)
    
    broad_arguments = {
        "query": "cancer AND Homo sapiens[organism]",
        "limit": 20
    }
    
    try:
        broad_result = tool.run(broad_arguments)
        if "esearchresult" in broad_result and not broad_result.get("error"):
            broad_count = broad_result["esearchresult"].get("count", "0")
            print(f"✅ Found {broad_count} cancer studies")
        else:
            print(f"❌ Broad search failed: {broad_result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ Broad search exception: {e}")
    
    # Step 2: Specific search
    print("\n🔍 Step 2: Specific search for breast cancer")
    print("-" * 40)
    
    specific_arguments = {
        "query": "breast cancer AND expression AND Homo sapiens[organism]",
        "limit": 10
    }
    
    try:
        specific_result = tool.run(specific_arguments)
        if "esearchresult" in specific_result and not specific_result.get("error"):
            specific_count = specific_result["esearchresult"].get("count", "0")
            specific_ids = specific_result["esearchresult"].get("idlist", [])
            print(f"✅ Found {specific_count} breast cancer studies")
            if specific_ids:
                print(f"📋 Study IDs: {specific_ids[:5]}")
        else:
            print(f"❌ Specific search failed: {specific_result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ Specific search exception: {e}")
    
    # Step 3: Analysis recommendations
    print("\n📊 Step 3: Analysis recommendations")
    print("-" * 40)
    print("✅ Next steps for GEO data analysis:")
    print("  1. Download study metadata using GEOquery R package")
    print("  2. Preprocess expression data")
    print("  3. Perform differential expression analysis")
    print("  4. Visualize results")
    print("  5. Integrate with pathway databases")
    
    print("\n📚 Useful resources:")
    print("  - GEOquery R package: https://bioconductor.org/packages/GEOquery/")
    print("  - GEO2R tool: https://www.ncbi.nlm.nih.gov/geo/geo2r/")
    print("  - GEO database: https://www.ncbi.nlm.nih.gov/geo/")


def main():
    """Run all examples"""
    print("🧬 GEO Tool Examples")
    print("=" * 50)
    print("This script demonstrates the usage of GEO tool")
    print("for gene expression data search and analysis.")
    
    # Run examples
    example_geo_basic_search()
    example_geo_organism_specific()
    example_geo_study_types()
    example_geo_advanced_queries()
    example_geo_workflow()
    
    print("\n🎯 Summary")
    print("=" * 50)
    print("✅ GEO tool: Ready to use (no API key required)")
    print("📊 Provides access to thousands of gene expression studies")
    print("🔍 Supports complex query construction")
    print("🌍 Works with multiple organisms and study types")
    
    print("\n📖 Next Steps:")
    print("1. Use GEO tool to find relevant studies for your research")
    print("2. Download and analyze expression data")
    print("3. Combine with other ToolUniverse tools for comprehensive analysis")
    print("4. Integrate results with pathway and interaction databases")


if __name__ == "__main__":
    main()
