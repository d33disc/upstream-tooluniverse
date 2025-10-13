#!/usr/bin/env python3
"""
Genomics Research Example

Simple example showing how to use ToolUniverse's direct import functionality
for genomics research with proper data flow.
"""

# Direct imports from tooluniverse.tools
from tooluniverse.tools import (
    HPA_search_genes_by_query,
    HPA_get_comprehensive_gene_details_by_ensembl_id,
    HPA_get_rna_expression_in_specific_tissues,
    HPA_get_protein_interactions_by_gene,
    GO_get_annotations_for_gene,
    GO_search_terms,
    enrichr_gene_enrichment_analysis,
    EuropePMC_search_articles,
    UniProt_get_entry_by_accession,
    gwas_get_associations_for_snp
)

# Complete Genomics Workflow
print("=== Complete Genomics Workflow ===")

# Step 1: Search for genes
print("\n1. Searching for genes...")
gene_search = HPA_search_genes_by_query(
    search_query="BRCA1"
)
print(f"Gene search results: {gene_search}")

# Step 2: Get gene details using search results
gene_data = None
ensembl_id = None
if gene_search and 'data' in gene_search and len(gene_search['data']) > 0:
    gene_data = gene_search['data'][0]
    ensembl_id = gene_data['ensembl_id']
    print(f"Found gene: {gene_data['gene_symbol']} ({ensembl_id})")
    
    # Get comprehensive gene details
    print("\n2. Getting comprehensive gene details...")
    gene_details = HPA_get_comprehensive_gene_details_by_ensembl_id(
        ensembl_id=ensembl_id,
        include_images=True,
        include_antibodies=True,
        include_expression=True
    )
    print(f"Gene details retrieved: {gene_details is not None}")

# Step 3: Analyze gene expression using the found gene
if ensembl_id:
    print("\n3. Analyzing gene expression...")
    expression = HPA_get_rna_expression_in_specific_tissues(
        ensembl_id=ensembl_id,
        tissue_names=["liver", "brain", "heart"]
    )
    print(f"Expression data retrieved: {expression is not None}")

# Step 4: Find protein interactions using gene symbol
if gene_data and 'gene_symbol' in gene_data:
    print("\n4. Finding protein interactions...")
    interactions = HPA_get_protein_interactions_by_gene(
        gene_name=gene_data['gene_symbol']
    )
    print(f"Protein interactions found: {interactions is not None}")

# Step 5: Get GO annotations using the ensembl_id
if ensembl_id:
    print("\n5. Getting GO annotations...")
    go_annotations = GO_get_annotations_for_gene(
        gene_id=ensembl_id
    )
    print(f"GO annotations retrieved: {go_annotations is not None}")

# Step 6: Search GO terms related to the gene's function
print("\n6. Searching related GO terms...")
go_terms = GO_search_terms(
    query="DNA repair"
)
print(f"Found {len(go_terms) if go_terms else 0} GO terms")

# Step 7: Pathway enrichment analysis using multiple genes
print("\n7. Performing pathway enrichment analysis...")
gene_list = ["BRCA1", "TP53", "ATM", "CHEK2", "PALB2"]
enrichment = enrichr_gene_enrichment_analysis(
    gene_list=gene_list,
    libs=['GO_Biological_Process_2021']
)
print(f"Enrichment analysis completed: {enrichment is not None}")

# Step 8: Search literature using the gene information
if gene_data and 'gene_symbol' in gene_data:
    print("\n8. Searching literature...")
    literature = EuropePMC_search_articles(
        query=f"{gene_data['gene_symbol']} gene expression cancer",
        limit=3
    )
    print(f"Found {len(literature) if literature else 0} relevant papers")

# Step 9: Get UniProt information using the gene symbol
if gene_data and 'gene_symbol' in gene_data:
    print("\n9. Getting UniProt information...")
    # Use a known UniProt ID for BRCA1
    uniprot_id = "P38398"  # BRCA1 UniProt ID
    uniprot_entry = UniProt_get_entry_by_accession(accession=uniprot_id)
    print(f"UniProt entry retrieved: {uniprot_entry is not None}")

# Step 10: Get genetic associations
print("\n10. Getting genetic associations...")
associations = gwas_get_associations_for_snp(
    rs_id="rs1799966"
)
print(f"GWAS associations retrieved: {associations is not None}")

print("\n=== Genomics Workflow Complete ===")
print("Summary:")
print(f"- Gene searched: BRCA1")
print(f"- Ensembl ID: {ensembl_id}")
print(f"- Gene symbol: {gene_data['gene_symbol'] if gene_data else 'Not found'}")
print(f"- Expression data: {'Retrieved' if ensembl_id else 'Not available'}")
print(f"- Protein interactions: {'Found' if gene_data else 'Not available'}")
print(f"- GO annotations: {'Retrieved' if ensembl_id else 'Not available'}")
print(f"- Literature papers: {'Found' if gene_data else 'Not available'}")
print(f"- UniProt entry: {'Retrieved' if gene_data else 'Not available'}")
print(f"- GWAS associations: {'Retrieved' if associations else 'Not available'}")