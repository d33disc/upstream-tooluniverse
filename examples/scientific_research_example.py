#!/usr/bin/env python3
"""
Scientific Research Example

Demonstrates professional use of ToolUniverse for scientific research
with proper data flow and scientific rigor.
"""

from tooluniverse.tools import (
    OpenTargets_get_disease_id_description_by_name,
    OpenTargets_get_associated_targets_by_disease_efoId,
    ChEMBL_search_similar_molecules,
    FDA_get_drug_names_by_indication,
    EuropePMC_search_articles,
    HPA_search_genes_by_query,
    GO_get_annotations_for_gene,
    search_clinical_trials,
    ADMETAI_predict_toxicity,
    ADMETAI_predict_bioavailability
)


def drug_discovery_workflow(disease_name: str, reference_drug: str):
    """
    Complete drug discovery workflow with proper data flow.

    Args:
        disease_name: Target disease for drug discovery
        reference_drug: Reference drug for similarity search
    """
    print(f"=== Drug Discovery Workflow for {disease_name} ===")

    # Step 1: Disease target identification
    print("\n1. Identifying disease targets...")
    disease_info = OpenTargets_get_disease_id_description_by_name(
        diseaseName=disease_name
    )

    if disease_info and 'data' in disease_info:
        hits = disease_info['data']['search']['hits']
        if hits:
            efo_id = hits[0]['id']
            print(f"   Disease EFO ID: {efo_id}")

            # Get associated targets
            targets = OpenTargets_get_associated_targets_by_disease_efoId(
                efoId=efo_id
            )

            if targets and 'data' in targets:
                target_data = targets['data']['disease']['associatedTargets']
                target_rows = target_data['rows']
                target_count = len(target_rows)
                print(f"   Found {target_count} disease targets")

    # Step 2: Drug similarity search
    print(f"\n2. Searching for drugs similar to {reference_drug}...")
    similar_drugs = ChEMBL_search_similar_molecules(
        query=reference_drug,
        similarity_threshold=70,
        max_results=5
    )

    if similar_drugs:
        print(f"   Found {len(similar_drugs)} similar compounds")

        # Analyze top compound
        top_compound = similar_drugs[0]
        compound_smiles = top_compound.get('smiles', '')
        compound_name = top_compound.get('pref_name', 'Unknown')

        print(f"   Top compound: {compound_name}")
        print(f"   SMILES: {compound_smiles}")

        # Step 3: ADMET prediction
        print("\n3. Predicting ADMET properties...")
        if compound_smiles:
            toxicity = ADMETAI_predict_toxicity(smiles=[compound_smiles])
            bioavailability = ADMETAI_predict_bioavailability(
                smiles=[compound_smiles]
            )

            print(f"   Toxicity prediction: {toxicity}")
            print(f"   Bioavailability prediction: {bioavailability}")

    # Step 4: Mechanism of action analysis
    print(f"\n4. Analyzing mechanism of action for {reference_drug}...")
    print(f"   Mechanism analysis: Similar molecules found above")

    # Step 5: Clinical evidence search
    print("\n5. Searching clinical evidence...")
    clinical_papers = EuropePMC_search_articles(
        query=f"{reference_drug} {disease_name} clinical trial",
        limit=5
    )

    if clinical_papers:
        print(f"   Found {len(clinical_papers)} clinical papers")

    # Step 6: FDA drug comparison
    print("\n6. Comparing with FDA approved drugs...")
    fda_drugs = FDA_get_drug_names_by_indication(
        indication=disease_name,
        limit=5,
        skip=0
    )

    if fda_drugs and 'results' in fda_drugs:
        print(f"   Found {len(fda_drugs['results'])} FDA approved drugs")

    print("\n=== Drug Discovery Workflow Complete ===")


def biomarker_discovery_workflow(candidate_genes: list, cancer_type: str):
    """
    Biomarker discovery workflow for cancer research.

    Args:
        candidate_genes: List of candidate biomarker genes
        cancer_type: Type of cancer to analyze
    """
    print(f"=== Biomarker Discovery Workflow for {cancer_type} ===")

    # Step 1: Gene expression analysis
    print(f"\n1. Analyzing {len(candidate_genes)} candidate genes...")
    for gene in candidate_genes[:3]:  # Analyze top 3 genes
        print(f"   Analyzing {gene}...")

        # Search for gene information
        gene_search = HPA_search_genes_by_query(search_query=gene)

        if gene_search and 'genes' in gene_search:
            gene_data = gene_search['genes'][0]
            ensembl_id = gene_data['ensembl_id']
            print(f"     Ensembl ID: {ensembl_id}")

            # Get GO annotations
            go_annotations = GO_get_annotations_for_gene(gene_id=ensembl_id)
            if go_annotations:
                print(f"     GO annotations: {len(go_annotations)}")

    # Step 2: Literature search
    print("\n2. Searching biomarker literature...")
    biomarker_papers = EuropePMC_search_articles(
        query=f"{cancer_type} biomarker gene expression",
        limit=10
    )

    if biomarker_papers:
        print(f"   Found {len(biomarker_papers)} biomarker papers")

    # Step 3: Clinical trial search
    print("\n3. Searching clinical trials...")
    trials = search_clinical_trials(
        query_term=f"{cancer_type} biomarker",
        condition=cancer_type,
        pageSize=5
    )

    if trials and 'results' in trials:
        print(f"   Found {len(trials['results'])} clinical trials")

    print("\n=== Biomarker Discovery Workflow Complete ===")


def drug_repurposing_workflow(disease_name: str, existing_drugs: list):
    """
    Drug repurposing workflow for precision medicine.

    Args:
        disease_name: Target disease for repurposing
        existing_drugs: List of existing drugs to evaluate
    """
    print(f"=== Drug Repurposing Workflow for {disease_name} ===")

    # Step 1: Disease analysis
    print("\n1. Analyzing target disease...")
    disease_info = OpenTargets_get_disease_id_description_by_name(
        diseaseName=disease_name
    )

    if disease_info and 'data' in disease_info:
        hits = disease_info['data']['search']['hits']
        if hits:
            efo_id = hits[0]['id']
            print(f"   Disease EFO ID: {efo_id}")

    # Step 2: Drug analysis
    print(f"\n2. Analyzing {len(existing_drugs)} existing drugs...")
    for drug in existing_drugs[:3]:  # Analyze top 3 drugs
        print(f"   Analyzing {drug}...")

        # Get mechanism of action
        print(f"     Mechanism: Analysis based on similar molecules")

        # Search for repurposing literature
        repurposing_papers = EuropePMC_search_articles(
            query=f"{drug} {disease_name} repurposing",
            limit=5
        )

        if repurposing_papers:
            print(f"     Found {len(repurposing_papers)} repurposing papers")

    # Step 3: FDA drug comparison
    print("\n3. Comparing with FDA approved drugs...")
    fda_drugs = FDA_get_drug_names_by_indication(
        indication=disease_name,
        limit=5,
        skip=0
    )

    if fda_drugs and 'results' in fda_drugs:
        print(f"   Found {len(fda_drugs['results'])} FDA approved drugs")

    print("\n=== Drug Repurposing Workflow Complete ===")


def main():
    """
    Main function demonstrating scientific research workflows.
    """
    print("=== Scientific Research Workflows ===")

    # Example 1: Drug Discovery
    print("\n" + "="*50)
    print("DRUG DISCOVERY WORKFLOW")
    print("="*50)
    drug_discovery_workflow("Type 2 diabetes", "Metformin")

    # Example 2: Biomarker Discovery
    print("\n" + "="*50)
    print("BIOMARKER DISCOVERY WORKFLOW")
    print("="*50)
    biomarker_discovery_workflow(
        ["BRCA1", "BRCA2", "TP53", "PTEN", "PIK3CA"],
        "breast cancer"
    )

    # Example 3: Drug Repurposing
    print("\n" + "="*50)
    print("DRUG REPURPOSING WORKFLOW")
    print("="*50)
    drug_repurposing_workflow(
        "Alzheimer's disease",
        ["Donepezil", "Memantine", "Rivastigmine", "Galantamine"]
    )

    print("\n" + "="*50)
    print("ALL WORKFLOWS COMPLETE")
    print("="*50)


if __name__ == "__main__":
    main()
