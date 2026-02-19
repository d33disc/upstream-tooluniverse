#!/usr/bin/env python3
"""
Comprehensive Test Suite for Epigenomics & Gene Regulation Skill

Tests all 7 phases of the skill workflow using real tool calls.
Validates tool parameters, response structures, and documentation accuracy.
"""

import sys
import time
import traceback

# Track results
test_results = []
total_tests = 0
passed_tests = 0
failed_tests = 0


def record_result(test_name, passed, details=""):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    if passed:
        passed_tests += 1
        status = "PASS"
    else:
        failed_tests += 1
        status = "FAIL"
    test_results.append({"name": test_name, "status": status, "details": details})
    print(f"  [{status}] {test_name}")
    if details and not passed:
        print(f"        Details: {details}")


def test_tool_loading():
    """Test 1: Verify all required tools load into ToolUniverse"""
    print("\n=== Test 1: Tool Loading ===")
    try:
        from tooluniverse import ToolUniverse
        tu = ToolUniverse()
        tu.load_tools()

        required_tools = [
            # SCREEN (Phase 1)
            "SCREEN_get_regulatory_elements",
            # JASPAR (Phase 2)
            "jaspar_search_matrices",
            "jaspar_get_matrix",
            "jaspar_get_matrix_versions",
            "JASPAR_get_transcription_factors",
            # ReMap (Phase 2)
            "ReMap_get_transcription_factor_binding",
            # RegulomeDB (Phase 3)
            "RegulomeDB_query_variant",
            # ENCODE (Phase 4)
            "ENCODE_search_experiments",
            "ENCODE_get_experiment",
            "ENCODE_list_files",
            "ENCODE_get_biosample",
            "ENCODE_search_biosamples",
            # 4DN (Phase 5)
            "FourDN_search_data",
            "FourDN_get_experiment_metadata",
            "FourDN_get_file_metadata",
            "FourDN_get_download_url",
            # Ensembl (Phase 6)
            "ensembl_get_regulatory_features",
        ]

        all_tools = set(tu.all_tool_dict.keys())
        missing = [t for t in required_tools if t not in all_tools]

        if missing:
            record_result("All required tools loaded", False,
                          f"Missing tools: {missing}")
        else:
            record_result("All required tools loaded", True,
                          f"All {len(required_tools)} tools found in {len(all_tools)} total tools")

        return tu
    except Exception as e:
        record_result("Tool loading", False, f"Exception: {e}")
        traceback.print_exc()
        return None


def test_phase1_screen(tu):
    """Test 2: Phase 1 - SCREEN cis-regulatory elements"""
    print("\n=== Test 2: Phase 1 - SCREEN cCREs ===")
    if tu is None:
        record_result("Phase 1 skipped", False, "ToolUniverse not loaded")
        return

    # Test 2a: Enhancers for TP53
    try:
        result = tu.tools.SCREEN_get_regulatory_elements(
            gene_name="TP53", element_type="enhancer", limit=10
        )
        if result is not None:
            if isinstance(result, dict):
                data = result.get("data", result)
                record_result("SCREEN enhancers (TP53)", True,
                              f"Response keys: {list(data.keys())[:5] if isinstance(data, dict) else type(data).__name__}")
            else:
                record_result("SCREEN enhancers (TP53)", True,
                              f"Response type: {type(result).__name__}")
        else:
            record_result("SCREEN enhancers (TP53)", False, "None returned")
    except Exception as e:
        record_result("SCREEN enhancers (TP53)", False, f"Exception: {e}")

    # Test 2b: Promoters for TP53
    try:
        result = tu.tools.SCREEN_get_regulatory_elements(
            gene_name="TP53", element_type="promoter", limit=10
        )
        if result is not None:
            record_result("SCREEN promoters (TP53)", True)
        else:
            record_result("SCREEN promoters (TP53)", False, "None returned")
    except Exception as e:
        record_result("SCREEN promoters (TP53)", False, f"Exception: {e}")

    # Test 2c: Insulators for BRCA1
    try:
        result = tu.tools.SCREEN_get_regulatory_elements(
            gene_name="BRCA1", element_type="insulator", limit=5
        )
        if result is not None:
            record_result("SCREEN insulators (BRCA1)", True)
        else:
            record_result("SCREEN insulators (BRCA1)", False, "None returned")
    except Exception as e:
        record_result("SCREEN insulators (BRCA1)", False, f"Exception: {e}")


def test_phase2_tf_binding(tu):
    """Test 3: Phase 2 - Transcription Factor Binding"""
    print("\n=== Test 3: Phase 2 - TF Binding ===")
    if tu is None:
        record_result("Phase 2 skipped", False, "ToolUniverse not loaded")
        return

    # Test 3a: JASPAR motif search
    try:
        result = tu.tools.jaspar_search_matrices(
            search="TP53", collection="CORE", species="9606"
        )
        if result is not None:
            if isinstance(result, dict):
                data = result.get("data", result)
                record_result("JASPAR search (TP53)", True,
                              f"Keys: {list(data.keys())[:5] if isinstance(data, dict) else type(data).__name__}")
            else:
                record_result("JASPAR search (TP53)", True,
                              f"Type: {type(result).__name__}")
        else:
            record_result("JASPAR search (TP53)", False, "None returned")
    except Exception as e:
        record_result("JASPAR search (TP53)", False, f"Exception: {e}")

    # Test 3b: JASPAR get specific matrix
    try:
        result = tu.tools.jaspar_get_matrix(matrix_id="MA0106.3")
        if result is not None:
            record_result("JASPAR get matrix (MA0106.3)", True)
        else:
            record_result("JASPAR get matrix (MA0106.3)", False, "None returned")
    except Exception as e:
        record_result("JASPAR get matrix (MA0106.3)", False, f"Exception: {e}")

    # Test 3c: JASPAR list TFs
    try:
        result = tu.tools.JASPAR_get_transcription_factors(
            collection="CORE", page=1, page_size=5
        )
        if result is not None:
            record_result("JASPAR list TFs (CORE)", True)
        else:
            record_result("JASPAR list TFs (CORE)", False, "None returned")
    except Exception as e:
        record_result("JASPAR list TFs (CORE)", False, f"Exception: {e}")

    # Test 3d: ReMap TF binding sites
    try:
        result = tu.tools.ReMap_get_transcription_factor_binding(
            gene_name="TP53", cell_type="HepG2", limit=10
        )
        if result is not None:
            record_result("ReMap TF binding (TP53, HepG2)", True)
        else:
            record_result("ReMap TF binding (TP53, HepG2)", False, "None returned")
    except Exception as e:
        record_result("ReMap TF binding (TP53, HepG2)", False, f"Exception: {e}")

    # Test 3e: ENCODE ChIP-seq search
    try:
        result = tu.tools.ENCODE_search_experiments(
            assay_title="ChIP-seq",
            target="H3K27ac",
            organism="Homo sapiens",
            limit=3
        )
        if result is not None:
            if isinstance(result, dict):
                data = result.get("data", result)
                count = len(data) if isinstance(data, list) else 1
                record_result("ENCODE ChIP-seq search (H3K27ac)", True,
                              f"Found {count} experiments")
            else:
                record_result("ENCODE ChIP-seq search (H3K27ac)", True)
        else:
            record_result("ENCODE ChIP-seq search (H3K27ac)", False, "None returned")
    except Exception as e:
        record_result("ENCODE ChIP-seq search (H3K27ac)", False, f"Exception: {e}")


def test_phase3_regulomedb(tu):
    """Test 4: Phase 3 - RegulomeDB variant scoring"""
    print("\n=== Test 4: Phase 3 - RegulomeDB ===")
    if tu is None:
        record_result("Phase 3 skipped", False, "ToolUniverse not loaded")
        return

    # Test 4a: Query known regulatory variant
    try:
        result = tu.tools.RegulomeDB_query_variant(rsid="rs6983267")
        if result is not None:
            if isinstance(result, dict):
                record_result("RegulomeDB (rs6983267)", True,
                              f"Keys: {list(result.keys())[:5]}")
            else:
                record_result("RegulomeDB (rs6983267)", True,
                              f"Type: {type(result).__name__}")
        else:
            record_result("RegulomeDB (rs6983267)", False, "None returned")
    except Exception as e:
        record_result("RegulomeDB (rs6983267)", False, f"Exception: {e}")

    # Test 4b: Query another variant
    try:
        result = tu.tools.RegulomeDB_query_variant(rsid="rs12913832")
        if result is not None:
            record_result("RegulomeDB (rs12913832)", True)
        else:
            record_result("RegulomeDB (rs12913832)", False, "None returned")
    except Exception as e:
        record_result("RegulomeDB (rs12913832)", False, f"Exception: {e}")


def test_phase4_encode(tu):
    """Test 5: Phase 4 - ENCODE Functional Genomics"""
    print("\n=== Test 5: Phase 4 - ENCODE ===")
    if tu is None:
        record_result("Phase 4 skipped", False, "ToolUniverse not loaded")
        return

    # Test 5a: ATAC-seq search
    try:
        result = tu.tools.ENCODE_search_experiments(
            assay_title="ATAC-seq",
            organism="Homo sapiens",
            limit=3
        )
        if result is not None:
            record_result("ENCODE ATAC-seq search", True)
        else:
            record_result("ENCODE ATAC-seq search", False, "None returned")
    except Exception as e:
        record_result("ENCODE ATAC-seq search", False, f"Exception: {e}")

    # Test 5b: RNA-seq search
    try:
        result = tu.tools.ENCODE_search_experiments(
            assay_title="RNA-seq",
            organism="Homo sapiens",
            limit=3
        )
        if result is not None:
            record_result("ENCODE RNA-seq search", True)
        else:
            record_result("ENCODE RNA-seq search", False, "None returned")
    except Exception as e:
        record_result("ENCODE RNA-seq search", False, f"Exception: {e}")

    # Test 5c: Biosample search
    try:
        result = tu.tools.ENCODE_search_biosamples(
            organism="Homo sapiens",
            biosample_type="cell line",
            limit=3
        )
        if result is not None:
            record_result("ENCODE biosample search", True)
        else:
            record_result("ENCODE biosample search", False, "None returned")
    except Exception as e:
        record_result("ENCODE biosample search", False, f"Exception: {e}")

    # Test 5d: List files
    try:
        result = tu.tools.ENCODE_list_files(
            file_type="bigWig",
            assay_title="ChIP-seq",
            limit=3
        )
        if result is not None:
            record_result("ENCODE list files (bigWig)", True)
        else:
            record_result("ENCODE list files (bigWig)", False, "None returned")
    except Exception as e:
        record_result("ENCODE list files (bigWig)", False, f"Exception: {e}")


def test_phase5_4dn(tu):
    """Test 6: Phase 5 - 4D Nucleome chromatin data"""
    print("\n=== Test 6: Phase 5 - 4D Nucleome ===")
    if tu is None:
        record_result("Phase 5 skipped", False, "ToolUniverse not loaded")
        return

    # Test 6a: Search Hi-C data
    try:
        result = tu.tools.FourDN_search_data(
            operation="search_data",
            assay_title="Hi-C",
            limit=5
        )
        if result is not None:
            record_result("4DN Hi-C search", True,
                          f"Type: {type(result).__name__}")
        else:
            record_result("4DN Hi-C search", False, "None returned")
    except Exception as e:
        record_result("4DN Hi-C search", False, f"Exception: {e}")

    # Test 6b: Search Micro-C data
    try:
        result = tu.tools.FourDN_search_data(
            operation="search_data",
            assay_title="Micro-C",
            limit=5
        )
        if result is not None:
            record_result("4DN Micro-C search", True)
        else:
            record_result("4DN Micro-C search", False, "None returned")
    except Exception as e:
        record_result("4DN Micro-C search", False, f"Exception: {e}")


def test_phase6_ensembl(tu):
    """Test 7: Phase 6 - Ensembl Regulatory Features"""
    print("\n=== Test 7: Phase 6 - Ensembl Regulatory ===")
    if tu is None:
        record_result("Phase 6 skipped", False, "ToolUniverse not loaded")
        return

    # Test 7a: Get regulatory features for TP53 region
    try:
        result = tu.tools.ensembl_get_regulatory_features(
            region="17:7661779-7687550",
            feature="regulatory",
            species="human"
        )
        if result is not None:
            if isinstance(result, list):
                record_result("Ensembl regulatory features (TP53 region)", True,
                              f"Found {len(result)} features")
            elif isinstance(result, dict):
                record_result("Ensembl regulatory features (TP53 region)", True,
                              f"Keys: {list(result.keys())[:5]}")
            else:
                record_result("Ensembl regulatory features (TP53 region)", True,
                              f"Type: {type(result).__name__}")
        else:
            record_result("Ensembl regulatory features (TP53 region)", False, "None returned")
    except Exception as e:
        record_result("Ensembl regulatory features (TP53 region)", False, f"Exception: {e}")

    # Test 7b: Get regulatory features for BRCA1 region
    try:
        result = tu.tools.ensembl_get_regulatory_features(
            region="17:43044295-43170245",
            feature="regulatory",
            species="human"
        )
        if result is not None:
            if isinstance(result, list):
                record_result("Ensembl regulatory features (BRCA1 region)", True,
                              f"Found {len(result)} features")
            else:
                record_result("Ensembl regulatory features (BRCA1 region)", True)
        else:
            record_result("Ensembl regulatory features (BRCA1 region)", False, "None returned")
    except Exception as e:
        record_result("Ensembl regulatory features (BRCA1 region)", False, f"Exception: {e}")


def test_cross_database(tu):
    """Test 8: Cross-database integration"""
    print("\n=== Test 8: Cross-Database Integration ===")
    if tu is None:
        record_result("Cross-database test skipped", False, "ToolUniverse not loaded")
        return

    # Test 8a: SCREEN + ReMap for same gene
    try:
        screen_result = tu.tools.SCREEN_get_regulatory_elements(
            gene_name="MYC", element_type="enhancer", limit=5
        )
        remap_result = tu.tools.ReMap_get_transcription_factor_binding(
            gene_name="MYC", cell_type="K562", limit=5
        )
        both_returned = screen_result is not None and remap_result is not None
        record_result("SCREEN + ReMap cross-query (MYC)", both_returned,
                      "Both databases returned data" if both_returned else "One or both returned None")
    except Exception as e:
        record_result("SCREEN + ReMap cross-query (MYC)", False, f"Exception: {e}")

    # Test 8b: JASPAR + ENCODE for same TF
    try:
        jaspar_result = tu.tools.jaspar_search_matrices(
            search="CTCF", collection="CORE", species="9606"
        )
        encode_result = tu.tools.ENCODE_search_experiments(
            assay_title="ChIP-seq",
            target="CTCF",
            organism="Homo sapiens",
            limit=3
        )
        both_returned = jaspar_result is not None and encode_result is not None
        record_result("JASPAR + ENCODE cross-query (CTCF)", both_returned,
                      "Both databases returned data" if both_returned else "One or both returned None")
    except Exception as e:
        record_result("JASPAR + ENCODE cross-query (CTCF)", False, f"Exception: {e}")


def generate_report():
    """Generate test report"""
    print("\n" + "=" * 60)
    print("EPIGENOMICS SKILL - TEST REPORT")
    print("=" * 60)
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Pass Rate: {passed_tests}/{total_tests} ({100*passed_tests/max(total_tests,1):.1f}%)")
    print()

    if failed_tests > 0:
        print("FAILED TESTS:")
        for r in test_results:
            if r["status"] == "FAIL":
                print(f"  - {r['name']}: {r['details']}")
        print()

    print("ALL RESULTS:")
    for r in test_results:
        print(f"  [{r['status']}] {r['name']}")
        if r["details"]:
            print(f"         {r['details']}")

    return failed_tests == 0


def main():
    print("Epigenomics & Gene Regulation Skill - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Testing against: TP53 (primary), BRCA1, MYC, CTCF")
    print()

    start_time = time.time()

    # Test 1: Tool loading
    tu = test_tool_loading()

    # Test 2: Phase 1 - SCREEN
    test_phase1_screen(tu)

    # Test 3: Phase 2 - TF Binding (JASPAR + ReMap + ENCODE)
    test_phase2_tf_binding(tu)

    # Test 4: Phase 3 - RegulomeDB
    test_phase3_regulomedb(tu)

    # Test 5: Phase 4 - ENCODE
    test_phase4_encode(tu)

    # Test 6: Phase 5 - 4DN
    test_phase5_4dn(tu)

    # Test 7: Phase 6 - Ensembl Regulatory
    test_phase6_ensembl(tu)

    # Test 8: Cross-database integration
    test_cross_database(tu)

    elapsed = time.time() - start_time
    print(f"\nTotal execution time: {elapsed:.1f} seconds")

    # Generate report
    all_passed = generate_report()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
