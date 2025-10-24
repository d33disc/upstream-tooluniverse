from unittest.mock import MagicMock

import pytest

from tooluniverse.interpro_tool import InterProTool
from tooluniverse.kegg_tool import KEGGTool
from tooluniverse.iucn_tool import IUCNRedListTool, IUCN_TOKEN_ENV
from tooluniverse.jaspar_tool import JASPARRestTool
from tooluniverse.marine_species_tool import MarineSpeciesTool
from tooluniverse.cbioportal_tool import CBioPortalTool
from tooluniverse.phenome_jax_tool import PhenomeJaxTool


def _mock_session_get(monkeypatch, target, payload=None, text=None, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    if payload is not None:
        response.json.return_value = payload
    if text is not None:
        response.text = text
    response.raise_for_status.return_value = None

    def factory(self, *args, **kwargs):
        return response

    monkeypatch.setattr(target, factory)
    return response


@pytest.mark.unit
def test_interpro_tool(monkeypatch):
    payload = {
        "count": 2,
        "results": [
            {"metadata": {"accession": "IPR000001", "name": "Example A", "type": "family"}},
            {"metadata": {"accession": "IPR000002", "name": "Example B", "type": "domain"}},
        ],
    }
    _mock_session_get(monkeypatch, "requests.Session.get", payload=payload)
    tool = InterProTool({"name": "InterPro_search_entries"})
    result = tool.run({"query": "kinase"})
    assert result["count"] == 2
    assert result["results"][0]["accession"] == "IPR000001"


@pytest.mark.unit
def test_kegg_tool(monkeypatch):
    text = "path:map00010\tGlycolysis / Gluconeogenesis\n"
    _mock_session_get(monkeypatch, "requests.Session.get", text=text)
    tool = KEGGTool({"name": "KEGG_find_entries"})
    result = tool.run({"query": "glucose", "database": "pathway"})
    assert result[0]["id"] == "path:map00010"


@pytest.mark.unit
def test_iucn_tool_requires_token(monkeypatch):
    tool = IUCNRedListTool({"name": "IUCN_get_species_status"})
    result = tool.run({"species": "Panthera leo"})
    assert "error" in result


@pytest.mark.unit
def test_iucn_tool(monkeypatch):
    payload = {"result": [{"scientific_name": "Panthera leo", "category": "VU"}]}
    _mock_session_get(monkeypatch, "requests.Session.get", payload=payload)
    monkeypatch.setenv(IUCN_TOKEN_ENV, "dummy")
    tool = IUCNRedListTool({"name": "IUCN_get_species_status"})
    result = tool.run({"species": "Panthera leo"})
    assert result["results"][0]["category"] == "VU"


@pytest.mark.unit
def test_jaspar_tool(monkeypatch):
    payload = {
        "count": 1,
        "results": [{"matrix_id": "MA0004.1", "name": "Arnt", "collection": "CORE"}],
    }
    _mock_session_get(monkeypatch, "requests.Session.get", payload=payload)
    tool = JASPARRestTool({"name": "JASPAR_search_motifs"})
    result = tool.run({"query": "Arnt"})
    assert result["results"][0]["matrix_id"] == "MA0004.1"


@pytest.mark.unit
def test_marine_species_tool(monkeypatch):
    payload = [{"AphiaID": 137094, "scientificname": "Delphinus delphis"}]
    _mock_session_get(monkeypatch, "requests.Session.get", payload=payload)
    tool = MarineSpeciesTool({"name": "MarineSpecies_lookup"})
    result = tool.run({"scientific_name": "Delphinus delphis"})
    assert result[0]["AphiaID"] == 137094


@pytest.mark.unit
def test_cbioportal_tool(monkeypatch):
    payload = [
        {"studyId": "brca_tcga", "name": "Breast Cancer", "description": "Example"}
    ]
    _mock_session_get(monkeypatch, "requests.Session.get", payload=payload)
    tool = CBioPortalTool({"name": "cBioPortal_search_studies"})
    result = tool.run({"keyword": "breast"})
    assert result["results"][0]["studyId"] == "brca_tcga"


@pytest.mark.unit
def test_phenome_jax_tool(monkeypatch):
    payload = {
        "count": 2,
        "projects": [
            {"projid": 1, "title": "Glucose tolerance", "species": "mouse"},
            {"projid": 2, "title": "Insulin", "species": "mouse"},
        ],
    }
    _mock_session_get(monkeypatch, "requests.Session.get", payload=payload)
    tool = PhenomeJaxTool({"name": "PhenomeJax_list_projects"})
    result = tool.run({"keyword": "glucose", "limit": 1})
    assert result["count"] == 2
    assert result["projects"][0]["projid"] == 1
