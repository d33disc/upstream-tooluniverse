"""Tests for ODPSearchTool -- JSON-body POST search (ODP, not DSAPI).

ODP search POSTs (patent/applications/search, patent/status-codes, and the
petition/trials/appeals/interferences families) take a JSON body, unlike the
DSAPI endpoints which are form-encoded. This class is the JSON-body adapter.
"""

import pytest


@pytest.fixture
def tool(monkeypatch):
    monkeypatch.setenv("USPTO_API_KEY", "test-key-for-unit-tests")
    from tooluniverse.odp_search_tool import ODPSearchTool

    return ODPSearchTool({"name": "test_odp_search", "api_endpoint": "patent/applications/search"})


class TestODPSearchRequestConstruction:
    def test_query_mapped_to_json_body(self, tool, monkeypatch):
        captured = {}

        def fake_post(url, **kwargs):
            captured["json"] = kwargs.get("json")
            captured["headers"] = kwargs.get("headers", {})

            class FakeResponse:
                status_code = 200

                def raise_for_status(self):
                    pass

                def json(self):
                    return {"count": 0, "patentFileWrapperDataBag": []}

            return FakeResponse()

        monkeypatch.setattr(tool.session, "post", fake_post)
        tool.run({"query": "applicationNumberText:14412875"})
        assert captured["json"] == {"q": "applicationNumberText:14412875"}

    def test_sends_api_key_header(self, tool, monkeypatch):
        captured = {}

        def fake_post(url, **kwargs):
            captured["headers"] = kwargs.get("headers", {})

            class FakeResponse:
                status_code = 200

                def raise_for_status(self):
                    pass

                def json(self):
                    return {}

            return FakeResponse()

        monkeypatch.setattr(tool.session, "post", fake_post)
        tool.run({"query": "test"})
        assert captured["headers"]["X-API-KEY"] == "test-key-for-unit-tests"

    def test_pagination_args_not_sent_in_body(self, tool, monkeypatch):
        """ODP POST bodies accept ONLY q -- offset/limit are GET query params.
        Verified live: every ODP search endpoint 400s on body offset/limit."""
        captured = {}

        def fake_post(url, **kwargs):
            captured["json"] = kwargs.get("json")

            class FakeResponse:
                status_code = 200

                def raise_for_status(self):
                    pass

                def json(self):
                    return {}

            return FakeResponse()

        monkeypatch.setattr(tool.session, "post", fake_post)
        tool.run({"query": "test", "offset": 25, "limit": 25})
        assert captured["json"] == {"q": "test"}

    def test_missing_query_returns_error(self, tool):
        result = tool.run({})
        assert result["status"] == "error"

    def test_response_passed_through(self, tool, monkeypatch):
        payload = {"count": 1, "patentFileWrapperDataBag": [{"id": "x"}]}

        def fake_post(url, **kwargs):
            class FakeResponse:
                status_code = 200

                def raise_for_status(self):
                    pass

                def json(self):
                    return payload

            return FakeResponse()

        monkeypatch.setattr(tool.session, "post", fake_post)
        result = tool.run({"query": "applicationNumberText:14412875"})
        assert result["status"] == "success"
        assert result["data"] == payload
