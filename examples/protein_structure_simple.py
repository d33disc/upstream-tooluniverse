#!/usr/bin/env python3
"""
Protein Structure Analysis Example

Simple example showing how to use ToolUniverse's direct import functionality
for protein structure analysis with proper data flow.
"""

# Direct imports from tooluniverse.tools
from tooluniverse.tools import (
    get_sequence_by_pdb_id,
    get_protein_metadata_by_pdb_id,
    get_structure_title_by_pdb_id,
    get_taxonomy_by_pdb_id,
    get_refinement_resolution_by_pdb_id,
    alphafold_get_prediction,
    visualize_protein_structure_3d,
    UniProt_get_entry_by_accession
)

# Complete Protein Structure Analysis Workflow
print("=== Complete Protein Structure Analysis Workflow ===")

# Step 1: Start with a PDB ID
pdb_id = "1CRN"  # Crambin
print(f"\n1. Analyzing protein structure for PDB ID: {pdb_id}")

# Step 2: Get basic protein information
print("\n2. Getting basic protein information...")
sequence = get_sequence_by_pdb_id(pdb_id=pdb_id)
metadata = get_protein_metadata_by_pdb_id(pdb_id=pdb_id)
title = get_structure_title_by_pdb_id(pdb_id=pdb_id)
taxonomy = get_taxonomy_by_pdb_id(pdb_id=pdb_id)
resolution = get_refinement_resolution_by_pdb_id(pdb_id=pdb_id)

print(f"Sequence length: {len(sequence['sequence']) if sequence and 'sequence' in sequence else 'Unknown'}")
print(f"Title: {title}")
print(f"Taxonomy: {taxonomy}")
print(f"Resolution: {resolution}")

# Step 3: Get UniProt information using the PDB metadata
uniprot_id = None
if metadata and 'uniprot_id' in metadata:
    uniprot_id = metadata['uniprot_id']
    print(f"\n3. Found UniProt ID: {uniprot_id}")
    
    # Get UniProt entry
    uniprot_entry = UniProt_get_entry_by_accession(accession=uniprot_id)
    print(f"UniProt entry retrieved: {uniprot_entry is not None}")
    
    # Get AlphaFold prediction using UniProt ID
    print("\n4. Getting AlphaFold prediction...")
    alphafold_prediction = alphafold_get_prediction(uniprot_id=uniprot_id)
    print(f"AlphaFold prediction retrieved: {alphafold_prediction is not None}")

# Step 4: Visualize protein structure
print("\n5. Creating 3D visualization...")
viz_result = visualize_protein_structure_3d(
    pdb_id=pdb_id,
    pdb_content="",  # Using PDB ID instead
    style="cartoon",
    color_scheme="spectrum"
)
print(f"3D visualization created: {viz_result is not None}")

# Step 5: Analyze another protein for comparison
print("\n6. Analyzing another protein for comparison...")
comparison_pdb = "1A8M"  # Another protein
comparison_sequence = get_sequence_by_pdb_id(pdb_id=comparison_pdb)
comparison_metadata = get_protein_metadata_by_pdb_id(pdb_id=comparison_pdb)
comparison_title = get_structure_title_by_pdb_id(pdb_id=comparison_pdb)

print(f"Comparison protein: {comparison_title}")
print(f"Comparison sequence length: {len(comparison_sequence['sequence']) if comparison_sequence and 'sequence' in comparison_sequence else 'Unknown'}")

# Step 6: Summary analysis
print("\n7. Summary analysis...")
print(f"Primary protein: {pdb_id}")
print(f"  - Title: {title}")
print(f"  - Sequence length: {len(sequence['sequence']) if sequence and 'sequence' in sequence else 'Unknown'}")
print(f"  - Resolution: {resolution}")
print(f"  - UniProt ID: {uniprot_id or 'Not found'}")

print(f"Comparison protein: {comparison_pdb}")
print(f"  - Title: {comparison_title}")
print(f"  - Sequence length: {len(comparison_sequence['sequence']) if comparison_sequence and 'sequence' in comparison_sequence else 'Unknown'}")

print("\n=== Protein Structure Analysis Workflow Complete ===")
print("Summary:")
print(f"- Primary protein analyzed: {pdb_id}")
print(f"- Comparison protein analyzed: {comparison_pdb}")
print(f"- UniProt integration: {'Yes' if uniprot_id else 'No'}")
print(f"- AlphaFold prediction: {'Yes' if uniprot_id else 'No'}")
print(f"- 3D visualization: {'Created' if viz_result else 'Failed'}")