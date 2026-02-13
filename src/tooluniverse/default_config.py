"""Default tool configuration files mapping.

Separated from __init__.py to avoid circular imports.
"""

import os
import json
from pathlib import Path

# Get the current directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))


def _data(*parts):
    """Build an absolute path under the package data directory."""
    return os.path.join(current_dir, "data", *parts)


def _pkg(filename):
    """Build an absolute path under data/packages/."""
    return os.path.join(current_dir, "data", "packages", filename)


# ---------------------------------------------------------------------------
# Default tool configuration files
# ---------------------------------------------------------------------------
# For tools whose JSON filename matches "{key}_tools.json", a compact mapping
# is used.  Non-standard filenames are listed explicitly.
# ---------------------------------------------------------------------------

# Entries where the JSON filename differs from the key
_CUSTOM_FILENAMES = {
    "special_tools": "special_tools.json",
    "tool_finder": "finder_tools.json",
    "opentarget": "opentarget_tools.json",
    "fda_drug_label": "fda_drug_labeling_tools.json",
    "monarch": "monarch_tools.json",
    "clinical_trials": "clinicaltrials_gov_tools.json",
    "fda_drug_adverse_event": "fda_drug_adverse_event_tools.json",
    "fda_drug_adverse_event_detail": "fda_drug_adverse_event_detail_tools.json",
    "ChEMBL": "chembl_tools.json",
    "EuropePMC": "europe_pmc_tools.json",
    "EFO": "efo_tools.json",
    "Enrichr": "enrichr_tools.json",
    "HumanBase": "humanbase_tools.json",
    "OpenAlex": "openalex_tools.json",
    "agents": "agentic_tools.json",
    "smolagents": "smolagent_tools.json",
    "mcp_auto_loader_txagent": "txagent_client_tools.json",
    "mcp_auto_loader_expert_feedback": "expert_feedback_tools.json",
    "adverse_event": "adverse_event_tools.json",
    "go": "gene_ontology_tools.json",
    "mcp_auto_loader_uspto_downloader": "uspto_downloader_tools.json",
    "xml": "xml_tools.json",
    "mcp_auto_loader_boltz": "boltz_mcp_loader_tools.json",
    "url": "url_fetch_tools.json",
    "file_download": "file_download_tools.json",
    "tool_composition": "tool_composition_tools.json",
    "embedding": "embedding_tools.json",
    "output_summarization": "output_summarization_tools.json",
    "guidelines": "unified_guideline_tools.json",
    "compact_mode": "compact_mode_tools.json",
    "optimizer": "optimizer_tools.json",
    "disease_target_score": "disease_target_score_tools.json",
    "visualization_protein_3d": "protein_structure_3d_tools.json",
    "visualization_molecule_2d": "molecule_2d_tools.json",
    "visualization_molecule_3d": "molecule_3d_tools.json",
}

# Keys that follow the standard "{key}_tools.json" naming pattern
_STANDARD_KEYS = [
    "semantic_scholar",
    "pubtator",
    "literature_search",
    "arxiv",
    "crossref",
    "simbad",
    "dblp",
    "pubmed",
    "ncbi_nucleotide",
    "ncbi_sra",
    "doaj",
    "unpaywall",
    "biorxiv",
    "medrxiv",
    "hal",
    "core",
    "pmc",
    "zenodo",
    "openaire",
    "osf_preprints",
    "fatcat",
    "wikidata_sparql",
    "wikipedia",
    "dbpedia",
    "tool_discovery_agents",
    "web_search_tools",
    "package_discovery_tools",
    "pypi_package_inspector_tools",
    "drug_discovery_agents",
    "dataset",
    "dailymed",
    "fda_orange_book",
    "faers_analytics",
    "cdc",
    "nhanes",
    "health_disparities",
    "hpa",
    "reactome",
    "pubchem",
    "medlineplus",
    "rxnorm",
    "loinc",
    "uniprot",
    "cellosaurus",
    "interpro",
    "ebi_search",
    "intact",
    "metabolights",
    "proteins_api",
    "arrayexpress",
    "biostudies",
    "dbfetch",
    "pdbe_api",
    "ena_browser",
    "blast",
    "cbioportal",
    "regulomedb",
    "jaspar",
    "remap",
    "screen",
    "pride",
    "emdb",
    "sasbdb",
    "gtopdb",
    "mpd",
    "worms",
    "paleobiology",
    "python_executor",
    "idmap",
    "uspto",
    "rcsb_pdb",
    "rcsb_search",
    "gwas",
    "admetai",
    "alphafold",
    "odphp",
    "who_gho",
    "umls",
    "icd",
    "euhealth",
    "markitdown",
    "kegg",
    "ensembl",
    "clinvar",
    "geo",
    "dbsnp",
    "gnomad",
    "gbif",
    "obis",
    "wikipathways",
    "rnacentral",
    "encode",
    "gtex",
    "mgnify",
    "gdc",
    "ols",
    "hca_tools",
    "clinical_trials_tools",
    "iedb_tools",
    "pathway_commons_tools",
    "biomodels_tools",
    "biothings",
    "fda_pharmacogenomic_biomarkers",
    "metabolomics_workbench",
    "pharmgkb",
    "dgidb",
    "stitch",
    "civic",
    "cellxgene_census",
    "chipatlas",
    "fourdn",
    "gtex_v2",
    "rfam",
    "bigg_models",
    "ppi",
    "biogrid",
    "nvidia_nim",
    "cosmic",
    "oncokb",
    "omim",
    "orphanet",
    "disgenet",
    "bindingdb",
    "gpcrdb",
    "brenda",
    "sabdab",
    "imgt",
    "hmdb",
    "metacyc",
    "zinc",
    "enamine",
    "emolecules",
    "pharos",
    "alphamissense",
    "cadd",
    "depmap",
    "interproscan",
    "eve",
    "therasabdab",
    "deepgo",
    "clingen",
    "spliceai",
    "impc",
    "complex_portal",
    "expression_atlas",
    "proteinsplus",
    "swissdock",
    "lipidmaps",
    "fooddata_central",
    "compose",
]

# Package (software) tool configs under data/packages/
_PACKAGE_KEYS = {
    "software_bioinformatics": "bioinformatics_core_tools.json",
    "software_genomics": "genomics_tools.json",
    "software_single_cell": "single_cell_tools.json",
    "software_structural_biology": "structural_biology_tools.json",
    "software_cheminformatics": "cheminformatics_tools.json",
    "software_machine_learning": "machine_learning_tools.json",
    "software_visualization": "visualization_tools.json",
    "software_scientific_computing": "scientific_computing_tools.json",
    "software_physics_astronomy": "physics_astronomy_tools.json",
    "software_earth_sciences": "earth_sciences_tools.json",
    "software_image_processing": "image_processing_tools.json",
    "software_neuroscience": "neuroscience_tools.json",
}

# Build the master mapping
default_tool_files = {}

# Custom filenames
for key, filename in _CUSTOM_FILENAMES.items():
    default_tool_files[key] = _data(filename)

# Standard "{key}_tools.json" pattern
for key in _STANDARD_KEYS:
    default_tool_files[key] = _data(f"{key}_tools.json")

# Package tools under data/packages/
for key, filename in _PACKAGE_KEYS.items():
    default_tool_files[key] = _pkg(filename)


# ---------------------------------------------------------------------------
# Auto-load user-provided tools from ~/.tooluniverse/user_tools/
# ---------------------------------------------------------------------------
user_tools_dir = os.path.expanduser("~/.tooluniverse/data/user_tools")

if os.path.exists(user_tools_dir):
    for filename in os.listdir(user_tools_dir):
        if filename.endswith(".json"):
            key = f"user_{filename.replace('.json', '')}"
            default_tool_files[key] = os.path.join(user_tools_dir, filename)


# ---------------------------------------------------------------------------
# Hook configuration helpers
# ---------------------------------------------------------------------------


def _get_hook_config_file_path():
    """Get the path to the hook configuration file."""
    try:
        import importlib.resources as pkg_resources
    except ImportError:
        import importlib_resources as pkg_resources

    try:
        data_files = pkg_resources.files("tooluniverse.template")
        return data_files / "hook_config.json"
    except Exception:
        return Path(__file__).parent / "template" / "hook_config.json"


def get_default_hook_config():
    """Load hook configuration from hook_config.json, with a fallback to defaults."""
    try:
        config_file = _get_hook_config_file_path()
        content = (
            config_file.read_text(encoding="utf-8")
            if hasattr(config_file, "read_text")
            else Path(config_file).read_text(encoding="utf-8")
        )
        return json.loads(content)
    except Exception:
        return {
            "global_settings": {
                "default_timeout": 30,
                "max_hook_depth": 3,
                "enable_hook_caching": True,
                "hook_execution_order": "priority_desc",
            },
            "exclude_tools": [
                "Tool_RAG",
                "ToolFinderEmbedding",
                "ToolFinderLLM",
            ],
            "hook_type_defaults": {
                "SummarizationHook": {
                    "default_output_length_threshold": 5000,
                    "default_chunk_size": 32000,
                    "default_focus_areas": "key_findings_and_results",
                    "default_max_summary_length": 3000,
                },
                "FileSaveHook": {
                    "default_temp_dir": None,
                    "default_file_prefix": "tool_output",
                    "default_include_metadata": True,
                    "default_auto_cleanup": False,
                    "default_cleanup_age_hours": 24,
                },
            },
            "hooks": [
                {
                    "name": "default_summarization_hook",
                    "type": "SummarizationHook",
                    "enabled": True,
                    "priority": 1,
                    "conditions": {
                        "output_length": {"operator": ">", "threshold": 5000}
                    },
                    "hook_config": {
                        "composer_tool": "OutputSummarizationComposer",
                        "chunk_size": 32000,
                        "focus_areas": "key_findings_and_results",
                        "max_summary_length": 3000,
                    },
                }
            ],
            "tool_specific_hooks": {},
            "category_hooks": {},
        }
