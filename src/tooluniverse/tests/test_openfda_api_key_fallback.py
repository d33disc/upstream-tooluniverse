import unittest
from unittest import mock


class TestOpenFDAApiKeyFallback(unittest.TestCase):
    def test_search_openfda_retries_without_invalid_api_key(self):
        """
        Ensure we retry once without api_key when OpenFDA responds with
        API_KEY_INVALID. Network-free: mocks requests.get().
        """
        from tooluniverse import openfda_tool

        calls = []

        class _Resp:
            def __init__(self, payload):
                self._payload = payload

            def json(self):
                return self._payload

        def fake_get(url):
            calls.append(url)
            # First call (with api_key) returns API_KEY_INVALID
            if "api_key=" in url:
                return _Resp(
                    {
                        "error": {
                            "code": "API_KEY_INVALID",
                            "message": "invalid api_key",
                        }
                    }
                )
            # Second call (without api_key) returns a normal payload
            return _Resp(
                {
                    "meta": {"results": {"skip": 0, "limit": 1, "total": 0}},
                    "results": [],
                }
            )

        with mock.patch.object(openfda_tool.requests, "get", side_effect=fake_get):
            out = openfda_tool.search_openfda(
                params={"search_fields": {"openfda.brand_name": "Vonjo"}, "limit": 1},
                endpoint_url="https://api.fda.gov/drug/label.json",
                api_key="INVALID",
                return_fields=[],
                exists=None,
                keywords_filter=False,
            )

        self.assertEqual(
            out, {"meta": {"skip": 0, "limit": 1, "total": 0}, "results": []}
        )
        self.assertEqual(len(calls), 2)
        self.assertIn("api_key=", calls[0])
        self.assertNotIn("api_key=", calls[1])
