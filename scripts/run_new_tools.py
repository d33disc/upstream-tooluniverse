#!/usr/bin/env python3
"""
Smoke-test the newly added bioscience tools against their live APIs.

The script imports the tool classes directly (without loading the full
ToolUniverse package) and prints representative responses. It respects
the following environment variables when present:

    IUCN_RED_LIST_TOKEN
    CBIOPORTAL_API_TOKEN
"""

from __future__ import annotations

import os
import pprint
import sys
from pathlib import Path


def _bootstrap_path() -> None:
    """Ensure the local src/ directory is importable."""
    repo_root = Path(__file__).resolve().parent.parent
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    os.environ.setdefault("TOOLUNIVERSE_LIGHT_IMPORT", "true")


def main() -> None:
    _bootstrap_path()

    from tooluniverse.interpro_tool import InterProTool
    from tooluniverse.kegg_tool import KEGGTool
    from tooluniverse.iucn_tool import IUCNRedListTool
    from tooluniverse.jaspar_tool import JASPARRestTool
    from tooluniverse.marine_species_tool import MarineSpeciesTool
    from tooluniverse.cbioportal_tool import CBioPortalTool
    from tooluniverse.phenome_jax_tool import PhenomeJaxTool

    results = {
        "interpro": InterProTool({"name": "InterPro_search_entries"}).run(
            {"query": "kinase", "page_size": 2}
        ),
        "kegg": KEGGTool({"name": "KEGG_find_entries"}).run(
            {"query": "glucose", "database": "pathway", "max_results": 2}
        ),
        "jaspar": JASPARRestTool({"name": "JASPAR_search_motifs"}).run(
            {"query": "Arnt", "page_size": 2}
        ),
        "marine_species": MarineSpeciesTool({"name": "MarineSpecies_lookup"}).run(
            {"scientific_name": "Delphinus delphis", "like": True}
        ),
        "cbioportal": CBioPortalTool({"name": "cBioPortal_search_studies"}).run(
            {"keyword": "breast", "page_size": 2}
        ),
        "phenome_jax": PhenomeJaxTool({"name": "PhenomeJax_list_projects"}).run(
            {"keyword": "glucose", "limit": 2}
        ),
    }

    try:
        results["iucn"] = IUCNRedListTool({"name": "IUCN_get_species_status"}).run(
            {"species": "Panthera leo"}
        )
    except Exception as exc:  # pragma: no cover - best-effort reporting
        results["iucn"] = {"error": str(exc)}

    for key, value in results.items():
        print(f"=== {key.upper()} ===")
        pprint.pprint(value)
        print()


if __name__ == "__main__":
    main()
