import unittest
from unittest.mock import patch, MagicMock
try:
    from tooluniverse.hca_tool import HCATool
except ImportError:
    # If using src structure directly without PYTHONPATH
    import sys
    import os
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    from tooluniverse.hca_tool import HCATool

class TestHCATool(unittest.TestCase):
    def setUp(self):
        dummy_config = {
            "name": "hca_search_projects",
            "type": "HCATool",
            "description": "Test",
            "parameter": {}
        }
        self.tool = HCATool(tool_config=dummy_config)

    @patch('tooluniverse.hca_tool.requests.get')
    def test_search_projects(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [
                {
                    "entryId": "test-id",
                    "projects": [{"projectTitle": "Test Project"}],
                    "modelOrgan": {"terms": ["heart"]},
                    "donorDisease": {"terms": ["normal"]}
                }
            ],
            "pagination": {"total": 1}
        }
        mock_get.return_value = mock_response

        result = self.tool.run({
            "action": "search_projects",
            "organ": "heart",
            "limit": 5
        })

        self.assertEqual(result["total_hits"], 1)
        self.assertEqual(result["projects"][0]["entryId"], "test-id")
        self.assertEqual(result["projects"][0]["projectTitle"], "Test Project")
        
        # Verify call arguments
        args, kwargs = mock_get.call_args
        self.assertIn("filters", kwargs["params"])
        self.assertIn('"organ":', kwargs["params"]["filters"])

    @patch('tooluniverse.hca_tool.requests.get')
    def test_get_file_manifest(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [
                {
                    "files": [
                        {
                            "name": "test.h5",
                            "format": "h5",
                            "size": 1024,
                            "azul_url": "http://download.link"
                        }
                    ]
                }
            ],
            "pagination": {"total": 1}
        }
        mock_get.return_value = mock_response

        result = self.tool.run({
            "action": "get_file_manifest",
            "project_id": "test-id"
        })

        self.assertEqual(result["total_files"], 1)
        self.assertEqual(result["files"][0]["name"], "test.h5")
        self.assertEqual(result["files"][0]["url"], "http://download.link")

if __name__ == "__main__":
    unittest.main()
