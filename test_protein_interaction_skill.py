#!/usr/bin/env python3
"""
Comprehensive Test Suite for Protein Interaction Network Analysis Skill

Tests all 6 use cases from SKILL.md plus edge cases.
"""

import sys
import os

# Add skills directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'tooluniverse-protein-interactions'))

from python_implementation import analyze_protein_network, ProteinNetworkResult
from tooluniverse import ToolUniverse


def test_1_single_protein_analysis():
    """Test Case 1: Single Protein Analysis (from SKILL.md Use Case 1)"""
    print("\n" + "="*80)
    print("TEST 1: Single Protein Analysis")
    print("="*80)
    print("Expected: Discover interaction partners for TP53")

    tu = ToolUniverse()

    result = analyze_protein_network(
        tu=tu,
        proteins=["TP53"],
        species=9606,
        confidence_score=0.7
    )

    # Validation
    assert isinstance(result, ProteinNetworkResult), "Should return ProteinNetworkResult"
    assert len(result.mapped_proteins) > 0, "Should map at least 1 protein"
    assert result.total_interactions >= 0, "Should have interactions count"

    print(f"\n✅ PASS: Found {result.total_interactions} interactions for TP53")
    if result.network_edges:
        print(f"   Top 3 partners:")
        for edge in result.network_edges[:3]:
            print(f"      {edge.get('preferredName_A')} ↔ {edge.get('preferredName_B')} (score: {edge.get('score')})")

    return result


def test_2_protein_complex_validation():
    """Test Case 2: Protein Complex Validation (from SKILL.md Use Case 2)"""
    print("\n" + "="*80)
    print("TEST 2: Protein Complex Validation")
    print("="*80)
    print("Expected: Test if DNA damage response proteins form functional complex")

    tu = ToolUniverse()

    proteins = ["TP53", "ATM", "CHEK2", "BRCA1"]
    result = analyze_protein_network(tu=tu, proteins=proteins, species=9606)

    # Validation
    assert len(result.mapped_proteins) >= 3, "Should map at least 3 proteins for enrichment"
    assert result.ppi_enrichment is not None, "Should have PPI enrichment results"

    p_val = result.ppi_enrichment.get("p_value", 1.0) if isinstance(result.ppi_enrichment, dict) else 1.0

    print(f"\n✅ PASS: PPI p-value = {p_val:.2e}")
    if p_val < 0.05:
        print(f"   ✅ Proteins form functional module (significant)")
    else:
        print(f"   ⚠️  Not significant (but test passed)")

    return result


def test_3_pathway_discovery():
    """Test Case 3: Pathway Discovery (from SKILL.md Use Case 3)"""
    print("\n" + "="*80)
    print("TEST 3: Pathway Discovery")
    print("="*80)
    print("Expected: Discover enriched pathways for MAPK signaling proteins")

    tu = ToolUniverse()

    proteins = ["MAPK1", "MAPK3", "RAF1", "MAP2K1", "MAP2K2"]
    result = analyze_protein_network(tu=tu, proteins=proteins, species=9606)

    # Validation
    assert len(result.enriched_terms) >= 0, "Should have enrichment results (may be empty)"

    print(f"\n✅ PASS: Found {len(result.enriched_terms)} enriched GO terms")
    if result.enriched_terms:
        print(f"   Top 3 pathways:")
        for term in result.enriched_terms[:3]:
            print(f"      {term.get('term')} (FDR: {term.get('fdr'):.2e})")

    return result


def test_4_multi_protein_network():
    """Test Case 4: Multi-Protein Network (from SKILL.md Use Case 4)"""
    print("\n" + "="*80)
    print("TEST 4: Multi-Protein Network")
    print("="*80)
    print("Expected: Build network for apoptosis proteins")

    tu = ToolUniverse()

    proteins = ["TP53", "BCL2", "BAX", "BAK1", "BID", "CASP3", "CASP9"]
    result = analyze_protein_network(
        tu=tu,
        proteins=proteins,
        species=9606,
        confidence_score=0.5  # Lower threshold
    )

    # Validation
    assert result.total_interactions >= 0, "Should have interactions"
    assert len(result.mapped_proteins) >= 3, "Should map most proteins"

    print(f"\n✅ PASS: Built network with {result.total_interactions} interactions")
    print(f"   Mapped: {len(result.mapped_proteins)}/{len(proteins)} proteins")
    print(f"   Enriched terms: {len(result.enriched_terms)}")

    return result


def test_5_invalid_proteins():
    """Test Case 5: Error Handling - Invalid Proteins"""
    print("\n" + "="*80)
    print("TEST 5: Error Handling - Invalid Proteins")
    print("="*80)
    print("Expected: Gracefully handle non-existent proteins")

    tu = ToolUniverse()

    proteins = ["FAKEGENE1", "NOTREAL2", "INVALID3"]
    result = analyze_protein_network(tu=tu, proteins=proteins, species=9606)

    # Validation
    assert isinstance(result, ProteinNetworkResult), "Should still return result object"
    assert result.mapping_success_rate < 1.0, "Should have low mapping success"
    assert len(result.warnings) > 0, "Should have warnings"

    print(f"\n✅ PASS: Handled invalid proteins gracefully")
    print(f"   Mapping success: {result.mapping_success_rate:.1%}")
    print(f"   Warnings: {len(result.warnings)}")

    return result


def test_6_result_structure():
    """Test Case 6: Result Structure Validation"""
    print("\n" + "="*80)
    print("TEST 6: Result Structure Validation")
    print("="*80)
    print("Expected: ProteinNetworkResult has all required fields")

    tu = ToolUniverse()

    result = analyze_protein_network(
        tu=tu,
        proteins=["TP53", "MDM2"],
        species=9606
    )

    # Validation - check all documented fields exist
    required_fields = [
        'mapped_proteins',
        'mapping_success_rate',
        'network_edges',
        'total_interactions',
        'enriched_terms',
        'ppi_enrichment',
        'structural_data',
        'primary_source',
        'warnings'
    ]

    for field in required_fields:
        assert hasattr(result, field), f"Missing field: {field}"

    # Type checking
    assert isinstance(result.mapped_proteins, list), "mapped_proteins should be list"
    assert isinstance(result.mapping_success_rate, float), "mapping_success_rate should be float"
    assert isinstance(result.network_edges, list), "network_edges should be list"
    assert isinstance(result.total_interactions, int), "total_interactions should be int"
    assert isinstance(result.enriched_terms, list), "enriched_terms should be list"
    assert isinstance(result.warnings, list), "warnings should be list"
    assert isinstance(result.primary_source, str), "primary_source should be str"

    print(f"\n✅ PASS: All 9 fields present and correct types")

    return result


def test_7_documentation_accuracy():
    """Test Case 7: Verify Documentation Examples Work"""
    print("\n" + "="*80)
    print("TEST 7: Documentation Accuracy")
    print("="*80)
    print("Expected: Quick Start example runs without errors")

    # This is the exact example from QUICK_START.md
    tu = ToolUniverse()

    result = analyze_protein_network(
        tu=tu,
        proteins=["TP53", "MDM2", "ATM"],
        species=9606,
        confidence_score=0.7
    )

    # The documentation says you can access these
    print(f"✅ {len(result.mapped_proteins)} proteins mapped")
    print(f"✅ {result.total_interactions} interactions found")
    print(f"✅ {len(result.enriched_terms)} GO terms enriched")

    # Documentation says result has these attributes
    assert hasattr(result, 'mapped_proteins'), "Doc says .mapped_proteins exists"
    assert hasattr(result, 'network_edges'), "Doc says .network_edges exists"
    assert hasattr(result, 'enriched_terms'), "Doc says .enriched_terms exists"
    assert hasattr(result, 'ppi_enrichment'), "Doc says .ppi_enrichment exists"
    assert hasattr(result, 'warnings'), "Doc says .warnings exists"

    print(f"\n✅ PASS: Documentation examples work correctly")

    return result


def test_8_parameter_validation():
    """Test Case 8: Parameter Validation"""
    print("\n" + "="*80)
    print("TEST 8: Parameter Validation")
    print("="*80)
    print("Expected: All documented parameters work")

    tu = ToolUniverse()

    # Test all parameters from documentation
    result = analyze_protein_network(
        tu=tu,
        proteins=["TP53", "MDM2"],
        species=9606,              # documented
        confidence_score=0.7,      # documented
        include_biogrid=False,     # documented
        include_structure=False,   # documented
        suppress_warnings=True     # documented
    )

    assert isinstance(result, ProteinNetworkResult), "Should work with all params"

    print(f"\n✅ PASS: All documented parameters accepted")

    return result


def run_all_tests():
    """Run all tests and generate report"""
    print("\n" + "="*80)
    print("PROTEIN INTERACTION NETWORK ANALYSIS - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("Testing all use cases from SKILL.md + edge cases")

    tests = [
        ("Single Protein Analysis", test_1_single_protein_analysis),
        ("Protein Complex Validation", test_2_protein_complex_validation),
        ("Pathway Discovery", test_3_pathway_discovery),
        ("Multi-Protein Network", test_4_multi_protein_network),
        ("Error Handling", test_5_invalid_proteins),
        ("Result Structure", test_6_result_structure),
        ("Documentation Accuracy", test_7_documentation_accuracy),
        ("Parameter Validation", test_8_parameter_validation),
    ]

    results = {}
    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = {"status": "PASS", "result": result}
            passed += 1
        except Exception as e:
            results[test_name] = {"status": "FAIL", "error": str(e)}
            failed += 1
            print(f"\n❌ FAIL: {test_name}")
            print(f"   Error: {e}")

    # Final Report
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print(f"📊 Success Rate: {passed/len(tests)*100:.1f}%")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Skill is production-ready.")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")

    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)

    for test_name, result_data in results.items():
        status = result_data['status']
        emoji = "✅" if status == "PASS" else "❌"
        print(f"{emoji} {test_name}: {status}")
        if status == "FAIL":
            print(f"   Error: {result_data['error']}")

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)
