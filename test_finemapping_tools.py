#!/usr/bin/env python3
"""
Test fine-mapping and causal variant prioritization tools.

Tests Open Targets Genetics tools for GWAS fine-mapping:
- OpenTargets_get_variant_credible_sets
- OpenTargets_get_credible_set_detail
- OpenTargets_get_variant_info
- OpenTargets_search_gwas_studies_by_disease
- OpenTargets_get_study_credible_sets

And GWAS Catalog tools:
- gwas_search_snps
- gwas_get_snp_by_id
- gwas_get_associations_for_snp
"""

from tooluniverse import ToolUniverse

def test_apoe_alzheimers():
    """Test APOE locus for Alzheimer's disease - rs429358 (APOE4)."""
    print("\n" + "="*80)
    print("TEST 1: APOE Locus (Alzheimer's Disease)")
    print("="*80)

    tu = ToolUniverse()
    tu.load_tools()

    # Step 1: Get variant info for rs429358 (APOE4)
    print("\n1. Getting variant info for rs429358 (APOE4)...")
    variant_id = "19_44908684_T_C"  # rs429358
    result = tu.run_one_function({"name": "OpenTargets_get_variant_info", "arguments": {"variantId": variant_id}})

    if "data" in result and result["data"].get("variant"):
        variant = result["data"]["variant"]
        print(f"   Variant ID: {variant['id']}")
        print(f"   rsIDs: {variant.get('rsIds', [])}")
        print(f"   Position: chr{variant['chromosome']}:{variant['position']}")
        print(f"   Alleles: {variant['referenceAllele']} > {variant['alternateAllele']}")
        print(f"   Most severe consequence: {variant.get('mostSevereConsequence', {}).get('label', 'N/A')}")
        print(f"   Allele frequencies: {len(variant.get('alleleFrequencies', []))} populations")
    else:
        print(f"   ERROR: {result}")
        return False

    # Step 2: Get credible sets for this variant
    print("\n2. Getting credible sets containing rs429358...")
    result = tu.run_one_function({"name": "OpenTargets_get_variant_credible_sets", "arguments": {
        "variantId": variant_id,
        "size": 5
    }})

    if "data" in result and result["data"].get("variant"):
        credible_sets = result["data"]["variant"].get("credibleSets", {})
        count = credible_sets.get("count", 0)
        rows = credible_sets.get("rows", [])

        print(f"   Found {count} credible sets")
        for i, cs in enumerate(rows[:3], 1):
            study = cs.get("study", {})
            diseases = study.get("diseases", [])
            disease_names = [d["name"] for d in diseases]

            # Calculate p-value
            p_mantissa = cs.get("pValueMantissa", 0)
            p_exponent = cs.get("pValueExponent", 0)
            p_value = p_mantissa * (10 ** p_exponent) if p_mantissa and p_exponent else None

            print(f"\n   Credible Set {i}:")
            print(f"      Study: {cs.get('studyId', 'N/A')}")
            print(f"      Trait: {study.get('traitFromSource', 'N/A')}")
            print(f"      Diseases: {', '.join(disease_names) if disease_names else 'N/A'}")
            print(f"      P-value: {p_value:.2e}" if p_value else "      P-value: N/A")
            print(f"      Beta: {cs.get('beta', 'N/A')}")
            print(f"      Fine-mapping method: {cs.get('finemappingMethod', 'N/A')}")

            # L2G predictions
            l2g = cs.get("l2GPredictions", {}).get("rows", [])
            if l2g:
                top_gene = l2g[0]["target"]["approvedSymbol"]
                top_score = l2g[0]["score"]
                print(f"      Top L2G gene: {top_gene} (score: {top_score:.3f})")
    else:
        print(f"   ERROR: {result}")
        return False

    # Step 3: Search for Alzheimer's GWAS studies
    print("\n3. Searching for Alzheimer's disease GWAS studies...")
    result = tu.run_one_function({"name": "OpenTargets_search_gwas_studies_by_disease", "arguments": {
        "diseaseIds": ["EFO_0000249"],  # Alzheimer's disease
        "size": 3
    }})

    if "data" in result and result["data"].get("studies"):
        studies_data = result["data"]["studies"]
        print(f"   Found {studies_data.get('count', 0)} studies total")
        for study in studies_data.get("rows", [])[:3]:
            print(f"\n      Study: {study['id']}")
            print(f"         Trait: {study.get('traitFromSource', 'N/A')}")
            print(f"         Author: {study.get('publicationFirstAuthor', 'N/A')}")
            print(f"         Sample size: {study.get('nSamples', 'N/A')}")
    else:
        print(f"   ERROR: {result}")

    print("\n✓ APOE Alzheimer's test completed successfully")
    return True


def test_tcf7l2_diabetes():
    """Test TCF7L2 locus for type 2 diabetes - rs7903146."""
    print("\n" + "="*80)
    print("TEST 2: TCF7L2 Locus (Type 2 Diabetes)")
    print("="*80)

    tu = ToolUniverse()
    tu.load_tools()

    # Step 1: Search for SNPs in TCF7L2 gene using GWAS Catalog
    print("\n1. Searching for SNPs in TCF7L2 gene...")
    result = tu.run_one_function({"name": "gwas_search_snps", "arguments": {
        "mapped_gene": "TCF7L2",
        "size": 5
    }})

    if "data" in result and isinstance(result["data"], list):
        snps = result["data"]
        print(f"   Found {len(snps)} SNPs")
        for snp in snps[:3]:
            print(f"\n      rs_id: {snp.get('rs_id', 'N/A')}")
            print(f"         Consequence: {snp.get('most_severe_consequence', 'N/A')}")
            print(f"         MAF: {snp.get('maf', 'N/A')}")
            print(f"         Functional class: {snp.get('functional_class', 'N/A')}")
    else:
        print(f"   ERROR: {result}")
        return False

    # Step 2: Get detailed info for rs7903146
    print("\n2. Getting detailed info for rs7903146...")
    result = tu.run_one_function({"name": "gwas_get_snp_by_id", "arguments": {
        "rs_id": "rs7903146"
    }})

    if "rs_id" in result:
        print(f"   rs_id: {result['rs_id']}")
        locations = result.get('locations', [])
        if locations:
            loc = locations[0]
            print(f"   Location: chr{loc.get('chromosome_name', 'N/A')}:{loc.get('chromosome_position', 'N/A')}")
        print(f"   Consequence: {result.get('most_severe_consequence', 'N/A')}")
        print(f"   MAF: {result.get('maf', 'N/A')}")
    else:
        print(f"   ERROR: {result}")
        return False

    # Step 3: Get associations for rs7903146
    print("\n3. Getting associations for rs7903146...")
    result = tu.run_one_function({"name": "gwas_get_associations_for_snp", "arguments": {
        "rs_id": "rs7903146",
        "sort": "p_value",
        "direction": "asc",
        "size": 5
    }})

    if "data" in result and isinstance(result["data"], list):
        assocs = result["data"]
        print(f"   Found {len(assocs)} associations")
        for i, assoc in enumerate(assocs[:3], 1):
            traits = assoc.get('reported_trait', [])
            print(f"\n   Association {i}:")
            print(f"      Trait: {', '.join(traits) if traits else 'N/A'}")
            print(f"      P-value: {assoc.get('p_value', 'N/A')}")
            print(f"      Beta: {assoc.get('beta', 'N/A')}")
            print(f"      Study: {assoc.get('accession_id', 'N/A')}")
    else:
        print(f"   ERROR: {result}")
        return False

    # Step 4: Get credible sets for rs7903146 from Open Targets
    print("\n4. Getting Open Targets credible sets for rs7903146...")
    variant_id = "10_112998590_C_T"  # rs7903146
    result = tu.run_one_function({"name": "OpenTargets_get_variant_credible_sets", "arguments": {
        "variantId": variant_id,
        "size": 3
    }})

    if "data" in result and result["data"].get("variant"):
        credible_sets = result["data"]["variant"].get("credibleSets", {})
        count = credible_sets.get("count", 0)
        print(f"   Found {count} credible sets in Open Targets")

        for i, cs in enumerate(credible_sets.get("rows", [])[:2], 1):
            study = cs.get("study", {})
            print(f"\n   Credible Set {i}:")
            print(f"      Trait: {study.get('traitFromSource', 'N/A')}")
            print(f"      Fine-mapping method: {cs.get('finemappingMethod', 'N/A')}")

            l2g = cs.get("l2GPredictions", {}).get("rows", [])
            if l2g:
                top_genes = [f"{g['target']['approvedSymbol']} ({g['score']:.3f})" for g in l2g[:3]]
                print(f"      Top L2G genes: {', '.join(top_genes)}")
    else:
        print(f"   Note: No Open Targets credible sets found (this is OK)")

    print("\n✓ TCF7L2 diabetes test completed successfully")
    return True


def test_fto_obesity():
    """Test FTO locus for obesity - rs9939609."""
    print("\n" + "="*80)
    print("TEST 3: FTO Locus (Obesity)")
    print("="*80)

    tu = ToolUniverse()
    tu.load_tools()

    # Step 1: Get SNPs for FTO gene
    print("\n1. Getting SNPs for FTO gene...")
    result = tu.run_one_function({"name": "gwas_search_snps", "arguments": {
        "mapped_gene": "FTO",
        "size": 3
    }})

    if "data" in result and isinstance(result["data"], list):
        snps = result["data"]
        print(f"   Found {len(snps)} SNPs")
        for snp in snps:
            print(f"      {snp.get('rs_id', 'N/A')}: {snp.get('most_severe_consequence', 'N/A')}")
    else:
        print(f"   ERROR: {result}")
        return False

    # Step 2: Get associations for rs9939609
    print("\n2. Getting associations for rs9939609...")
    result = tu.run_one_function({"name": "gwas_get_associations_for_snp", "arguments": {
        "rs_id": "rs9939609",
        "size": 5
    }})

    if "data" in result and isinstance(result["data"], list):
        assocs = result["data"]
        print(f"   Found {len(assocs)} associations")

        # Group by trait
        traits_found = set()
        for assoc in assocs[:5]:
            traits = assoc.get('reported_trait', [])
            for trait in traits:
                if 'obesity' in trait.lower() or 'bmi' in trait.lower() or 'body mass' in trait.lower():
                    traits_found.add(trait)

        print(f"   Obesity-related traits found: {len(traits_found)}")
        for trait in list(traits_found)[:3]:
            print(f"      - {trait}")
    else:
        print(f"   ERROR: {result}")
        return False

    print("\n✓ FTO obesity test completed successfully")
    return True


def test_credible_set_detail():
    """Test getting detailed credible set information."""
    print("\n" + "="*80)
    print("TEST 4: Credible Set Detail")
    print("="*80)

    tu = ToolUniverse()
    tu.load_tools()

    # First get a credible set ID from rs7903146
    print("\n1. Finding credible set for rs7903146...")
    variant_id = "10_112998590_C_T"
    result = tu.run_one_function({"name": "OpenTargets_get_variant_credible_sets", "arguments": {
        "variantId": variant_id,
        "size": 1
    }})

    if "data" in result and result["data"].get("variant"):
        rows = result["data"]["variant"].get("credibleSets", {}).get("rows", [])
        if rows:
            study_locus_id = rows[0].get("studyLocusId")
            print(f"   Found credible set: {study_locus_id}")

            # Step 2: Get detailed info
            print("\n2. Getting detailed credible set information...")
            result = tu.run_one_function({"name": "OpenTargets_get_credible_set_detail", "arguments": {
                "studyLocusId": study_locus_id
            }})

            if "data" in result and result["data"].get("credibleSet"):
                cs = result["data"]["credibleSet"]
                print(f"   Region: {cs.get('region', 'N/A')}")
                print(f"   Fine-mapping method: {cs.get('finemappingMethod', 'N/A')}")
                print(f"   Sample size: {cs.get('sampleSize', 'N/A')}")

                variant = cs.get("variant", {})
                if variant:
                    print(f"\n   Lead variant:")
                    print(f"      {variant.get('id', 'N/A')}")
                    print(f"      rsIDs: {variant.get('rsIds', [])}")
                    print(f"      Consequence: {variant.get('mostSevereConsequence', {}).get('label', 'N/A')}")

                study = cs.get("study", {})
                if study:
                    print(f"\n   Study:")
                    print(f"      {study.get('id', 'N/A')}")
                    print(f"      Trait: {study.get('traitFromSource', 'N/A')}")
                    print(f"      Author: {study.get('publicationFirstAuthor', 'N/A')}")

                l2g = cs.get("l2GPredictions", {}).get("rows", [])
                if l2g:
                    print(f"\n   L2G predictions (top 3):")
                    for pred in l2g[:3]:
                        gene = pred["target"]["approvedSymbol"]
                        score = pred["score"]
                        print(f"      {gene}: {score:.3f}")
            else:
                print(f"   ERROR: {result}")
                return False
        else:
            print("   Note: No credible sets found for this variant")
    else:
        print(f"   ERROR: {result}")
        return False

    print("\n✓ Credible set detail test completed successfully")
    return True


def test_study_credible_sets():
    """Test getting all credible sets for a study."""
    print("\n" + "="*80)
    print("TEST 5: Study Credible Sets")
    print("="*80)

    tu = ToolUniverse()
    tu.load_tools()

    # Use a known T2D study
    print("\n1. Getting credible sets for GCST90029024 (T2D study)...")
    result = tu.run_one_function({"name": "OpenTargets_get_study_credible_sets", "arguments": {
        "studyIds": ["GCST90029024"],
        "size": 5
    }})

    if "data" in result and result["data"].get("credibleSets"):
        cs_data = result["data"]["credibleSets"]
        count = cs_data.get("count", 0)
        rows = cs_data.get("rows", [])

        print(f"   Found {count} credible sets total")
        print(f"   Showing first {len(rows)} credible sets")

        for i, cs in enumerate(rows[:3], 1):
            variant = cs.get("variant", {})
            l2g = cs.get("l2GPredictions", {}).get("rows", [])

            print(f"\n   Credible Set {i}:")
            print(f"      Region: {cs.get('region', 'N/A')}")
            print(f"      Position: chr{cs.get('chromosome', 'N/A')}:{cs.get('position', 'N/A')}")
            print(f"      Lead variant: {variant.get('rsIds', ['N/A'])[0] if variant.get('rsIds') else 'N/A'}")

            if l2g:
                top_gene = l2g[0]["target"]["approvedSymbol"]
                top_score = l2g[0]["score"]
                print(f"      Top L2G gene: {top_gene} (score: {top_score:.3f})")
    else:
        print(f"   ERROR: {result}")
        return False

    print("\n✓ Study credible sets test completed successfully")
    return True


if __name__ == "__main__":
    print("\n" + "="*80)
    print("GWAS FINE-MAPPING & CAUSAL VARIANT PRIORITIZATION TOOL TESTING")
    print("="*80)

    results = []

    # Run all tests
    results.append(("APOE Alzheimer's", test_apoe_alzheimers()))
    results.append(("TCF7L2 Diabetes", test_tcf7l2_diabetes()))
    results.append(("FTO Obesity", test_fto_obesity()))
    results.append(("Credible Set Detail", test_credible_set_detail()))
    results.append(("Study Credible Sets", test_study_credible_sets()))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n✓ All tests passed! Tools are ready for skill creation.")
    else:
        print("\n✗ Some tests failed. Please review errors above.")

    exit(0 if all_passed else 1)
