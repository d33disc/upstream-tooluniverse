"""Tests for USPTO_get_enriched_citation_fields -- request construction and schema coverage.

The GET /fields endpoint (list-searchable-fields) returns the searchable field
list for the enriched_cited_reference_metadata v3 dataset. This test suite:

  1. exercises request construction against the real config from uspto_tools.json
  2. pins the response-field set of USPTO_search_enriched_citations so its
     return_schema cannot silently under-declare the API response again

Field list provenance (verified 2026-03-02, not assumed):
  - GET /fields live probe (X-API-KEY from ~/.env.secure): 22 searchable fields
  - POST /records live probe (criteria patentApplicationNumber:15739603): docs
    whose field union across actual responses = 22 fields (user sample + probe)
  The union of RESPONSE fields is the authority for return_schema, not the
  searchable list alone (they differ: citedDocumentIdentifier and
  inventorNameText are searchable but absent from some response docs).
"""

import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "src" / "tooluniverse" / "data"

# UNION of fields observed across ALL actual POST /records response docs:
#   (a) user-provided sample for app 15739603 (22 fields, includes
#       citedDocumentIdentifier + inventorNameText)
#   (b) live probe 2026-03-02, same criteria (20 fields, doc-dependent)
# Response docs are doc-dependent: some fields are absent from individual
# docs. The union is the authority for return_schema -- every field that CAN
# appear must be declared; a field absent from one doc is still valid.
RESPONSE_FIELDS = [
    "applicantCitedExaminerReferenceIndicator",
    "citationCategoryCode",
    "citedDocumentIdentifier",
    "countryCode",
    "createDateTime",
    "createUserIdentifier",
    "examinerCitedReferenceIndicator",
    "groupArtUnitNumber",
    "id",
    "inventorNameText",
    "kindCode",
    "nplIndicator",
    "obsoleteDocumentIdentifier",
    "officeActionCategory",
    "officeActionDate",
    "passageLocationText",
    "patentApplicationNumber",
    "publicationNumber",
    "qualitySummaryText",
    "relatedClaimNumberText",
    "techCenter",
    "workGroupNumber",
]


def _load_config(data_file: str, tool_name: str) -> dict:
    configs = json.loads((DATA_DIR / data_file).read_text())
    for cfg in configs:
        if cfg.get("name") == tool_name:
            return cfg
    raise AssertionError(f"tool {tool_name} not found in {data_file}")


class TestFieldsToolRequestConstruction:
    @pytest.fixture
    def tool(self, monkeypatch):
        monkeypatch.setenv("USPTO_API_KEY", "test-key-for-unit-tests")
        from tooluniverse.uspto_tool import USPTOOpenDataPortalTool

        config = _load_config("uspto_tools.json", "USPTO_get_enriched_citation_fields")
        return USPTOOpenDataPortalTool(config)

    def test_get_url_uses_fields_endpoint(self, tool, monkeypatch):
        captured = {}

        def fake_get(url, **kwargs):
            captured["url"] = url

            class FakeResponse:
                status_code = 200
                headers = {}


                def raise_for_status(self):
                    pass

                def json(self):
                    return {"fieldCount": 22, "fields": []}

            return FakeResponse()

        monkeypatch.setattr(tool.session, "get", fake_get)
        tool.run({})
        assert captured["url"].endswith(
            "patent/oa/enriched_cited_reference_metadata/v3/fields"
        )

    def test_sends_api_key_header(self, tool, monkeypatch):
        captured = {}

        def fake_get(url, **kwargs):
            captured["headers"] = kwargs.get("headers", {})

            class FakeResponse:
                status_code = 200
                headers = {}


                def raise_for_status(self):
                    pass

                def json(self):
                    return {}

            return FakeResponse()

        monkeypatch.setattr(tool.session, "get", fake_get)
        tool.run({})
        assert captured["headers"]["X-API-KEY"] == "test-key-for-unit-tests"

    def test_response_passed_through(self, tool, monkeypatch):
        payload = {
            "apiVersionNumber": "v3",
            "apiStatus": "PUBLISHED",
            "fieldCount": 22,
            "fields": RESPONSE_FIELDS,
        }

        def fake_get(url, **kwargs):
            class FakeResponse:
                status_code = 200
                headers = {}


                def raise_for_status(self):
                    pass

                def json(self):
                    return payload

            return FakeResponse()

        monkeypatch.setattr(tool.session, "get", fake_get)
        result = tool.run({})
        assert result["status"] == "success"
        assert result["data"] == payload


class TestEnrichedCitationSchemaCoverage:
    """The search tool's return_schema must declare every response field."""

    def test_search_tool_schema_covers_all_response_fields(self):
        cfg = _load_config("dsapi_tools.json", "USPTO_search_enriched_citations")
        declared = cfg["return_schema"]["properties"]["docs"]["items"]["properties"]
        missing = [f for f in RESPONSE_FIELDS if f not in declared]
        assert missing == [], f"return_schema missing fields: {missing}"

    def test_search_tool_declares_all_response_fields_in_schema(self):
        cfg = _load_config("dsapi_tools.json", "USPTO_search_enriched_citations")
        declared = set(
            cfg["return_schema"]["properties"]["docs"]["items"]["properties"]
        )
        assert declared == set(RESPONSE_FIELDS)



class TestCsvDownloadHandling:
    """The download endpoints return text/csv; the class must pass it through."""

    def test_csv_response_returned_as_text(self, monkeypatch):
        monkeypatch.setenv("USPTO_API_KEY", "test-key-for-unit-tests")
        from tooluniverse.uspto_tool import USPTOOpenDataPortalTool

        config = {
            "name": "USPTO_download_bulk_dataset_file",
            "api_endpoint": "datasets/products/files/{productIdentifier}/{fileName}",
        }
        tool = USPTOOpenDataPortalTool(config)
        csv_body = "col1,col2\n1,2\n"

        def fake_get(url, **kwargs):
            class FakeResponse:
                status_code = 200
                headers = {"Content-Type": "text/csv"}

                def raise_for_status(self):
                    pass

                def json(self):
                    raise ValueError("should not be called for CSV")

                @property
                def text(self):
                    return csv_body

            return FakeResponse()

        monkeypatch.setattr(tool.session, "get", fake_get)
        result = tool.run({"productIdentifier": "PTGRXML", "fileName": "x.csv"})
        assert result["status"] == "success"
        assert result["data"]["csv"] == csv_body

    def test_json_response_unaffected_by_header_check(self, monkeypatch):
        monkeypatch.setenv("USPTO_API_KEY", "test-key-for-unit-tests")
        from tooluniverse.uspto_tool import USPTOOpenDataPortalTool

        config = {
            "name": "USPTO_get_patent_application",
            "api_endpoint": "patent/applications/{applicationNumberText}",
        }
        tool = USPTOOpenDataPortalTool(config)
        payload = {"count": 1, "patentFileWrapperDataBag": []}

        def fake_get(url, **kwargs):
            class FakeResponse:
                status_code = 200
                headers = {"Content-Type": "application/json"}

                def raise_for_status(self):
                    pass

                def json(self):
                    return payload

            return FakeResponse()

        monkeypatch.setattr(tool.session, "get", fake_get)
        result = tool.run({"applicationNumberText": "14966067"})
        assert result["status"] == "success"
        assert result["data"] == payload
