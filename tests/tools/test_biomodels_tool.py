import unittest
from unittest.mock import patch, MagicMock
try:
    from tooluniverse.biomodels_tool import BioModelsTool
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    from tooluniverse.biomodels_tool import BioModelsTool

class TestBioModelsTool(unittest.TestCase):
    def setUp(self):
        dummy_config = {
            "name": "biomodels_search",
            "type": "BioModelsTool",
            "description": "Test",
            "parameter": {}
        }
        self.tool = BioModelsTool(tool_config=dummy_config)

    @patch('tooluniverse.biomodels_tool.requests.get')
    def test_search_models(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {
                    "id": "BIOMD1",
                    "name": "Test Model",
                    "format": "SBML",
                    "url": "http://url"
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.tool.run({
            "action": "search_models",
            "query": "test",
            "limit": 5
        })

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["models"][0]["id"], "BIOMD1")
        
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["query"], "test")

    def test_get_model_files(self):
        # No API call needed as it constructs URL
        result = self.tool.run({
            "action": "get_model_files",
            "model_id": "BIOMD1"
        })
        self.assertEqual(result["model_id"], "BIOMD1")
        self.assertTrue("download" in result["download_url"])

if __name__ == "__main__":
    unittest.main()
