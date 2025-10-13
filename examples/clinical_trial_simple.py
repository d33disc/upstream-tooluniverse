#!/usr/bin/env python3
"""
Clinical Trial Analysis Example

Simple example showing how to use ToolUniverse's direct import functionality
for clinical trial analysis with proper data flow.
"""

# Direct imports from tooluniverse.tools
from tooluniverse.tools import (
    search_clinical_trials,
    get_clinical_trial_descriptions,
    get_clinical_trial_conditions_and_interventions,
    get_clinical_trial_eligibility_criteria,
    get_clinical_trial_locations,
    get_clinical_trial_outcome_measures,
    get_clinical_trial_references,
    get_clinical_trial_status_and_dates,
    extract_clinical_trial_adverse_events,
    extract_clinical_trial_outcomes,
    FDA_get_drug_names_by_indication,
    FDA_get_adverse_reactions_by_drug_name,
    FAERS_count_reactions_by_drug_event,
    FAERS_count_seriousness_by_drug_event,
    FAERS_count_outcomes_by_drug_event
)

# Complete Clinical Trial Analysis Workflow
print("=== Complete Clinical Trial Analysis Workflow ===")

# Step 1: Search for clinical trials
print("\n1. Searching for clinical trials...")
trials = search_clinical_trials(
    query_term="diabetes metformin",
    condition="diabetes",
    intervention="metformin",
    pageSize=5
)
print(f"Found {len(trials['results']) if trials and 'results' in trials else 0} clinical trials")

# Step 2: Analyze the first trial in detail
trial_id = None
if trials and 'results' in trials and len(trials['results']) > 0:
    first_trial = trials['results'][0]
    trial_id = first_trial['nct_id']
    print(f"\n2. Analyzing trial: {trial_id}")
    print(f"Title: {first_trial['brief_title']}")
    print(f"Status: {first_trial['overall_status']}")
    print(f"Phase: {first_trial['phase']}")
    
    # Get detailed trial information
    print("\n3. Getting detailed trial information...")
    description = get_clinical_trial_descriptions(nct_id=trial_id)
    conditions_interventions = get_clinical_trial_conditions_and_interventions(nct_id=trial_id)
    eligibility = get_clinical_trial_eligibility_criteria(nct_id=trial_id)
    locations = get_clinical_trial_locations(nct_id=trial_id)
    outcomes = get_clinical_trial_outcome_measures(nct_id=trial_id)
    references = get_clinical_trial_references(nct_id=trial_id)
    status_dates = get_clinical_trial_status_and_dates(nct_id=trial_id)
    
    print(f"Description retrieved: {description is not None}")
    print(f"Conditions/Interventions: {conditions_interventions is not None}")
    print(f"Eligibility criteria: {eligibility is not None}")
    print(f"Locations: {locations is not None}")
    print(f"Outcomes: {outcomes is not None}")
    print(f"References: {references is not None}")
    print(f"Status/Dates: {status_dates is not None}")
    
    # Extract adverse events and outcomes
    print("\n4. Extracting adverse events and outcomes...")
    adverse_events = extract_clinical_trial_adverse_events(nct_id=trial_id)
    trial_outcomes = extract_clinical_trial_outcomes(nct_id=trial_id)
    
    print(f"Adverse events extracted: {adverse_events is not None}")
    print(f"Trial outcomes extracted: {trial_outcomes is not None}")

# Step 3: Search FDA drugs for comparison
print("\n5. Searching FDA approved drugs...")
fda_drugs = FDA_get_drug_names_by_indication(
    indication="diabetes",
    limit=5,
    skip=0
)
print(f"Found {len(fda_drugs['results']) if fda_drugs and 'results' in fda_drugs else 0} FDA approved diabetes drugs")

# Step 4: Analyze drug safety using FDA data
print("\n6. Analyzing drug safety...")
if fda_drugs and 'results' in fda_drugs and len(fda_drugs['results']) > 0:
    first_drug = fda_drugs['results'][0]
    drug_name = first_drug['openfda']['generic_name'][0] if 'openfda' in first_drug and 'generic_name' in first_drug['openfda'] else "metformin"
    
    print(f"Analyzing safety for: {drug_name}")
    
    # Get adverse reactions
    adverse_reactions = FDA_get_adverse_reactions_by_drug_name(drug_name=drug_name)
    print(f"Adverse reactions retrieved: {adverse_reactions is not None}")
    
    # Get FAERS data
    faers_reactions = FAERS_count_reactions_by_drug_event(
        medicinalproduct=drug_name,
        patientsex="",
        patientagegroup="",
        occurcountry="",
        serious="",
        seriousnessdeath=""
    )
    faers_seriousness = FAERS_count_seriousness_by_drug_event(
        medicinalproduct=drug_name,
        patientsex="",
        patientagegroup="",
        occurcountry=""
    )
    faers_outcomes = FAERS_count_outcomes_by_drug_event(
        medicinalproduct=drug_name,
        patientsex="",
        patientagegroup="",
        occurcountry=""
    )
    
    print(f"FAERS reactions: {faers_reactions is not None}")
    print(f"FAERS seriousness: {faers_seriousness is not None}")
    print(f"FAERS outcomes: {faers_outcomes is not None}")

# Step 5: Search for trials by condition
print("\n7. Searching trials by condition...")
cancer_trials = search_clinical_trials(
    query_term="breast cancer",
    condition="breast cancer",
    pageSize=3
)
print(f"Found {len(cancer_trials['results']) if cancer_trials and 'results' in cancer_trials else 0} breast cancer trials")

# Step 6: Search for trials by intervention
print("\n8. Searching trials by intervention...")
chemotherapy_trials = search_clinical_trials(
    query_term="cancer chemotherapy",
    condition="cancer",
    intervention="chemotherapy",
    pageSize=3
)
print(f"Found {len(chemotherapy_trials['results']) if chemotherapy_trials and 'results' in chemotherapy_trials else 0} chemotherapy trials")

# Step 7: Compare drug safety profiles
print("\n9. Comparing drug safety profiles...")
drugs_to_compare = ["metformin", "insulin", "glipizide"]
safety_comparison = {}

for drug in drugs_to_compare:
    print(f"Analyzing {drug}...")
    
    # Get adverse reactions
    reactions = FDA_get_adverse_reactions_by_drug_name(drug_name=drug)
    
    # Get FAERS data
    faers_rxns = FAERS_count_reactions_by_drug_event(
        medicinalproduct=drug,
        patientsex="",
        patientagegroup="",
        occurcountry="",
        serious="",
        seriousnessdeath=""
    )
    faers_ser = FAERS_count_seriousness_by_drug_event(
        medicinalproduct=drug,
        patientsex="",
        patientagegroup="",
        occurcountry=""
    )
    
    safety_comparison[drug] = {
        'adverse_reactions': reactions is not None,
        'faers_reactions': faers_rxns is not None,
        'faers_seriousness': faers_ser is not None
    }
    
    print(f"  - Adverse reactions: {'Available' if reactions else 'None'}")
    print(f"  - FAERS reactions: {'Available' if faers_rxns else 'None'}")
    print(f"  - FAERS seriousness: {'Available' if faers_ser else 'None'}")

print(f"\nSafety comparison complete for {len(safety_comparison)} drugs.")

print("\n=== Clinical Trial Analysis Workflow Complete ===")
print("Summary:")
print(f"- Clinical trials found: {len(trials['results']) if trials and 'results' in trials else 0}")
print(f"- Trial analyzed in detail: {trial_id or 'None'}")
print(f"- FDA drugs found: {len(fda_drugs['results']) if fda_drugs and 'results' in fda_drugs else 0}")
print(f"- Cancer trials found: {len(cancer_trials['results']) if cancer_trials and 'results' in cancer_trials else 0}")
print(f"- Chemotherapy trials found: {len(chemotherapy_trials['results']) if chemotherapy_trials and 'results' in chemotherapy_trials else 0}")
print(f"- Drugs compared for safety: {len(safety_comparison)}")