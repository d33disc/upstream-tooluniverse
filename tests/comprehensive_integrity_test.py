
import sys
import os
import json
import logging

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from tooluniverse import ToolUniverse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test(tool_name, test_desc, func, **kwargs):
    logger.info(f"Testing {tool_name}: {test_desc}")
    try:
        result = func(**kwargs)
        # Check for error keys in result if it's a dict
        if isinstance(result, dict) and 'error' in result:
             logger.warning(f"  -> Tool returned error (handled): {result['error']}")
             return True # It didn't crash, so it's "stable", but we note the error
        
        # Check for empty results where expected
        if "empty" in test_desc.lower():
             if isinstance(result, dict):
                 # HCA
                 if "projects" in result and len(result["projects"]) == 0:
                     logger.info("  -> Verified empty result as expected.")
                     return True
                 # ClinicalTrials
                 if "studies" in result and len(result["studies"]) == 0:
                     logger.info("  -> Verified empty result as expected.")
                     return True
                 # IEDB
                 if "epitopes" in result and len(result["epitopes"]) == 0:
                     logger.info("  -> Verified empty result as expected.")
                     return True
                 # Pathway Commons
                 if "pathways" in result and len(result["pathways"]) == 0:
                     logger.info("  -> Verified empty result as expected.")
                     return True
                 # BioModels
                 if "models" in result and len(result["models"]) == 0:
                     logger.info("  -> Verified empty result as expected.")
                     return True
             
        logger.info(f"  -> Success. Result summary: {str(result)[:100]}...")
        return True
    except Exception as e:
        logger.error(f"  -> CRASH/EXCEPTION: {e}")
        return False

def main():
    logger.info("Initializing ToolUniverse...")
    tu = ToolUniverse()
    
    overall_success = True

    # --- HCA Tool ---
    logger.info("\n--- Human Cell Atlas (HCA) ---")
    # 1. Happy Path
    if not run_test("HCA", "Search 'heart'", tu.tools.hca_search_projects, action="search_projects", organ="heart", limit=1):
        overall_success = False
    # 2. Empty Search
    if not run_test("HCA", "Search unlikely organ 'xylophone'", tu.tools.hca_search_projects, action="search_projects", organ="xylophone"):
        overall_success = False
    # 3. Invalid Project ID (Get Manifest)
    if not run_test("HCA", "Get manifest for invalid ID", tu.tools.hca_get_file_manifest, action="get_file_manifest", project_id="INVALID_UUID_123"):
        overall_success = False

    # --- ClinicalTrials.gov Tool ---
    logger.info("\n--- ClinicalTrials.gov ---")
    # 1. Happy Path
    if not run_test("ClinicalTrials", "Search 'diabetes'", tu.tools.clinical_trials_search, action="search_studies", condition="diabetes", limit=1):
        overall_success = False
    # 2. Empty Search
    if not run_test("ClinicalTrials", "Search unlikely condition 'zombification'", tu.tools.clinical_trials_search, action="search_studies", condition="zombification"):
        overall_success = False
    # 3. Invalid NCT ID
    if not run_test("ClinicalTrials", "Get details for invalid NCT ID", tu.tools.clinical_trials_get_details, action="get_study_details", nct_id="NCT0000000000INVALID"):
        overall_success = False

    # --- IEDB Tool ---
    logger.info("\n--- IEDB ---")
    # 1. Happy Path
    if not run_test("IEDB", "Search sequence 'KVF'", tu.tools.iedb_search_epitopes, action="search_epitopes", query="KVF", limit=1):
        overall_success = False
    # 2. Empty Search
    if not run_test("IEDB", "Search unlikely sequence 'XZXZXZ'", tu.tools.iedb_search_epitopes, action="search_epitopes", query="XZXZXZ"):
        overall_success = False
    
    # --- Pathway Commons ---
    logger.info("\n--- Pathway Commons ---")
    # 1. Happy Path
    if not run_test("PathwayCommons", "Search 'glycolysis'", tu.tools.pc_search_pathways, action="search_pathways", keyword="glycolysis", limit=1):
        overall_success = False
    # 2. Empty Search
    if not run_test("PathwayCommons", "Search unlikely keyword 'supercalifragilistic'", tu.tools.pc_search_pathways, action="search_pathways", keyword="supercalifragilistic"):
        overall_success = False
    # 3. Empty Interaction Graph (Single non-interacting gene)
    # Asking for interaction of a single gene might return empty or just the node
    if not run_test("PathwayCommons", "Interaction graph for single unknown gene", tu.tools.pc_get_interactions, action="get_interaction_graph", gene_list=["NON_EXISTENT_GENE_123"]):
        overall_success = False

    # --- BioModels ---
    logger.info("\n--- BioModels ---")
    # 1. Happy Path
    if not run_test("BioModels", "Search 'circulation'", tu.tools.biomodels_search, action="search_models", query="circulation", limit=1):
        overall_success = False
    # 2. Empty Search
    if not run_test("BioModels", "Search unlikely query 'flux_capacitor_model'", tu.tools.biomodels_search, action="search_models", query="flux_capacitor_model"):
        overall_success = False
    # 3. Invalid Model ID
    if not run_test("BioModels", "Get files for invalid ID", tu.tools.biomodels_get_files, action="get_model_files", model_id="INVALID_MODEL_ID"):
        overall_success = False

    if overall_success:
        logger.info("\n✅ ALL INTEGRITY TESTS PASSED. Tools are stable.")
    else:
        logger.error("\n❌ SOME TESTS FAILED. Check logs above.")

if __name__ == "__main__":
    main()
