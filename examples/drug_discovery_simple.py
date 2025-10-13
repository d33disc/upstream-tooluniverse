#!/usr/bin/env python3
"""
Drug Discovery Research Example

Simple example showing how to use ToolUniverse's direct import functionality
for drug discovery research with proper data flow.
"""

# Direct imports from tooluniverse.tools
from tooluniverse.tools import (
    OpenTargets_get_disease_id_description_by_name,
    OpenTargets_get_associated_targets_by_disease_efoId,
    ChEMBL_search_similar_molecules,
    PubChem_get_CID_by_compound_name,
    ADMETAI_predict_toxicity,
    ADMETAI_predict_bioavailability,
    FDA_get_drug_names_by_indication,
    EuropePMC_search_articles,
    visualize_molecule_2d
)

# Complete Drug Discovery Workflow
print("=== Complete Drug Discovery Workflow ===")

# Step 1: Find disease targets
print("\n1. Finding disease targets...")
disease_info = OpenTargets_get_disease_id_description_by_name(
    diseaseName="Type 2 diabetes"
)
print(f"Disease info: {disease_info}")

# Step 2: Get targets using EFO ID from disease info
targets = None
if disease_info and 'data' in disease_info:
    hits = disease_info['data']['search']['hits']
    if hits:
        efo_id = hits[0]['id']
        print(f"Using EFO ID: {efo_id}")
        targets = OpenTargets_get_associated_targets_by_disease_efoId(
            efoId=efo_id
        )
        print(f"Found {len(targets['data']['disease']['associatedTargets']['rows'])} targets")

# Step 3: Search for similar compounds to known diabetes drug
print("\n2. Searching for similar compounds...")
metformin_compounds = ChEMBL_search_similar_molecules(
    query="metformin",
    similarity_threshold=70,
    max_results=3
)
print(f"Found {len(metformin_compounds)} similar compounds")

# Step 4: Get compound properties and predict ADMET
print("\n3. Analyzing compound properties...")
if metformin_compounds and len(metformin_compounds) > 0:
    # Get the first compound
    top_compound = metformin_compounds[0]
    compound_smiles = top_compound['smiles']
    compound_name = top_compound['pref_name'] or "Unknown"
    
    print(f"Analyzing compound: {compound_name}")
    print(f"SMILES: {compound_smiles}")
    
    # Get PubChem CID
    cid_result = PubChem_get_CID_by_compound_name(name=compound_name)
    print(f"PubChem CID: {cid_result}")
    
    # Predict ADMET properties
    toxicity = ADMETAI_predict_toxicity(smiles=[compound_smiles])
    bioavailability = ADMETAI_predict_bioavailability(smiles=[compound_smiles])
    
    print(f"Toxicity prediction: {toxicity}")
    print(f"Bioavailability prediction: {bioavailability}")
    
    # Visualize molecule
    print("\n4. Creating molecular visualization...")
    viz_result = visualize_molecule_2d(
        smiles=compound_smiles,
        inchi="",  # Will be resolved by the tool
        molecule_name=compound_name,
        output_format='png'
    )
    print(f"Visualization created: {viz_result}")

# Step 5: Search FDA approved drugs for comparison
print("\n5. Searching FDA approved drugs...")
fda_drugs = FDA_get_drug_names_by_indication(
    indication="diabetes", 
    limit=5, 
    skip=0
)
print(f"Found {len(fda_drugs['results'])} FDA approved diabetes drugs")

# Step 6: Search relevant literature
print("\n6. Searching literature...")
literature = EuropePMC_search_articles(
    query="metformin diabetes drug discovery",
    limit=3
)
print(f"Found {len(literature)} relevant papers")

print("\n=== Drug Discovery Workflow Complete ===")
print("Summary:")
print(f"- Disease: Type 2 diabetes")
print(f"- Targets found: {len(targets['data']['disease']['associatedTargets']['rows']) if targets else 0}")
print(f"- Similar compounds: {len(metformin_compounds) if metformin_compounds else 0}")
print(f"- FDA drugs: {len(fda_drugs['results']) if fda_drugs else 0}")
print(f"- Literature papers: {len(literature) if literature else 0}")