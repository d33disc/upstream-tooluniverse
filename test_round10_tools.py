#!/usr/bin/env python3
"""
Test script for Round 10 tools.
Tests each API endpoint directly with curl-like requests.
Bypasses Python version issues by testing the actual HTTP calls.
"""

import requests
import json
import sys
import traceback

RESULTS = {"passed": 0, "failed": 0, "errors": []}


def test_endpoint(name, url, params=None, headers=None, method="GET",
                  expect_key=None, min_items=None):
    """Test a single API endpoint."""
    try:
        if method == "GET":
            resp = requests.get(url, params=params, headers=headers, timeout=30)
        else:
            resp = requests.post(url, json=params, headers=headers, timeout=30)

        if resp.status_code != 200:
            RESULTS["failed"] += 1
            RESULTS["errors"].append(f"FAIL: {name} -> HTTP {resp.status_code}")
            print(f"  FAIL: {name} -> HTTP {resp.status_code}")
            return False

        data = resp.json()

        if expect_key and expect_key not in str(data):
            RESULTS["failed"] += 1
            RESULTS["errors"].append(f"FAIL: {name} -> missing expected key '{expect_key}'")
            print(f"  FAIL: {name} -> missing expected key")
            return False

        if isinstance(data, dict):
            keys = list(data.keys())[:5]
            print(f"  PASS: {name} -> dict with keys: {keys}")
        elif isinstance(data, list):
            print(f"  PASS: {name} -> list with {len(data)} items")
        else:
            print(f"  PASS: {name} -> {type(data).__name__}")

        RESULTS["passed"] += 1
        return True

    except Exception as e:
        RESULTS["failed"] += 1
        RESULTS["errors"].append(f"ERROR: {name} -> {str(e)}")
        print(f"  ERROR: {name} -> {str(e)[:120]}")
        return False


def test_wormbase():
    """Test WormBase API endpoints."""
    print("\n=== WormBase (C. elegans) ===")

    # Gene overview
    test_endpoint(
        "WormBase_get_gene (unc-26)",
        "https://rest.wormbase.org/rest/widget/gene/WBGene00006763/overview",
        headers={"Accept": "application/json"},
        expect_key="fields"
    )

    # Gene overview - daf-2
    test_endpoint(
        "WormBase_get_gene (daf-2)",
        "https://rest.wormbase.org/rest/widget/gene/WBGene00000898/overview",
        headers={"Accept": "application/json"},
        expect_key="fields"
    )

    # Gene phenotypes
    test_endpoint(
        "WormBase_get_phenotypes (unc-26)",
        "https://rest.wormbase.org/rest/widget/gene/WBGene00006763/phenotype",
        headers={"Accept": "application/json"},
        expect_key="phenotype"
    )

    # Gene expression
    test_endpoint(
        "WormBase_get_expression (unc-26)",
        "https://rest.wormbase.org/rest/widget/gene/WBGene00006763/expression",
        headers={"Accept": "application/json"},
        expect_key="expressed_in"
    )


def test_swissmodel():
    """Test SWISS-MODEL API endpoints."""
    print("\n=== SWISS-MODEL Repository ===")

    test_endpoint(
        "SwissModel_get_models (p53)",
        "https://swissmodel.expasy.org/repository/uniprot/P04637.json",
        expect_key="structures"
    )

    test_endpoint(
        "SwissModel_get_models (EPN1)",
        "https://swissmodel.expasy.org/repository/uniprot/Q9Y6I3.json",
        expect_key="structures"
    )

    test_endpoint(
        "SwissModel_get_summary (EGFR)",
        "https://swissmodel.expasy.org/repository/uniprot/P00533.json",
        expect_key="sequence_length"
    )


def test_proteomexchange():
    """Test ProteomeXchange API endpoints."""
    print("\n=== ProteomeXchange ===")

    test_endpoint(
        "PX_get_dataset (PXD000001)",
        "https://proteomecentral.proteomexchange.org/cgi/GetDataset",
        params={"ID": "PXD000001", "outputMode": "JSON"},
        expect_key="title"
    )

    test_endpoint(
        "PX_get_dataset (PXD000561)",
        "https://proteomecentral.proteomexchange.org/cgi/GetDataset",
        params={"ID": "PXD000561", "outputMode": "JSON"},
        expect_key="title"
    )

    test_endpoint(
        "PX_search_datasets (PROXI)",
        "https://massive.ucsd.edu/ProteoSAFe/proxi/v0.1/datasets",
        params={"resultType": "compact"},
        expect_key="accession"
    )


def test_pdbe_search():
    """Test PDBe Search API endpoints."""
    print("\n=== PDBe Search ===")

    test_endpoint(
        "PDBe_search_structures (insulin)",
        "https://www.ebi.ac.uk/pdbe/search/pdb/select",
        params={"q": "insulin", "rows": 5, "fl": "pdb_id,title,resolution", "wt": "json"},
        expect_key="numFound"
    )

    test_endpoint(
        "PDBe_search_structures (BRCA1)",
        "https://www.ebi.ac.uk/pdbe/search/pdb/select",
        params={"q": "BRCA1", "rows": 5, "fl": "pdb_id,title,resolution", "wt": "json"},
        expect_key="numFound"
    )

    test_endpoint(
        "PDBe_get_compound (ATP)",
        "https://www.ebi.ac.uk/pdbe/api/pdb/compound/summary/ATP",
        expect_key="ADENOSINE"
    )

    test_endpoint(
        "PDBe_get_compound (HEM)",
        "https://www.ebi.ac.uk/pdbe/api/pdb/compound/summary/HEM",
        expect_key="PROTOPORPHYRIN"
    )

    test_endpoint(
        "PDBe_search_by_organism (E.coli ribosome)",
        "https://www.ebi.ac.uk/pdbe/search/pdb/select",
        params={
            "q": 'ribosome AND organism_scientific_name:"Escherichia coli"',
            "rows": 5, "fl": "pdb_id,title,resolution", "wt": "json"
        },
        expect_key="numFound"
    )


def test_nextstrain():
    """Test Nextstrain API endpoints."""
    print("\n=== Nextstrain ===")

    test_endpoint(
        "Nextstrain_list_datasets",
        "https://nextstrain.org/charon/getAvailable",
        expect_key="datasets"
    )

    test_endpoint(
        "Nextstrain_get_dataset (zika)",
        "https://nextstrain.org/charon/getDataset",
        params={"prefix": "zika"},
        expect_key="tree"
    )

    test_endpoint(
        "Nextstrain_get_dataset (ebola)",
        "https://nextstrain.org/charon/getDataset",
        params={"prefix": "ebola"},
        expect_key="tree"
    )


if __name__ == "__main__":
    print("=" * 60)
    print("Round 10 API Endpoint Validation")
    print("=" * 60)

    test_wormbase()
    test_swissmodel()
    test_proteomexchange()
    test_pdbe_search()
    test_nextstrain()

    print("\n" + "=" * 60)
    print(f"RESULTS: {RESULTS['passed']} passed, {RESULTS['failed']} failed")
    print("=" * 60)

    if RESULTS["errors"]:
        print("\nFailed tests:")
        for err in RESULTS["errors"]:
            print(f"  - {err}")

    sys.exit(0 if RESULTS["failed"] == 0 else 1)
