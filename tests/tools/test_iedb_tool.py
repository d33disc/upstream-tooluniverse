import unittest
from unittest.mock import patch, MagicMock
try:
    from tooluniverse.iedb_tool import IEDBTool
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    from tooluniverse.iedb_tool import IEDBTool

class TestIEDBTool(unittest.TestCase):
    def setUp(self):
        dummy_config = {
            "name": "iedb_search_epitopes",
            "type": "IEDBTool",
            "description": "Test",
            "parameter": {}
        }
        self.tool = IEDBTool(tool_config=dummy_config)

    @patch('tooluniverse.iedb_tool.requests.get')
    def test_search_epitopes(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "structure_id": 1,
                "structure_type": "Linear peptide",
                "linear_sequence": "AAAAA",
                "structure_descriptions": ["Test Epitope"],
                "curated_source_antigens": [{"name": "Test Antigen"}]
            }
        ]
        mock_get.return_value = mock_response

        result = self.tool.run({
            "action": "search_epitopes",
            "query": "test",
            "structure_type": "Linear peptide"
        })

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["epitopes"][0]["id"], 1)
        self.assertEqual(result["epitopes"][0]["sequence"], "AAAAA")
        
        args, kwargs = mock_get.call_args
        self.assertIn("ilike.*test*", kwargs["params"]["linear_sequence"])
        self.assertEqual(kwargs["params"]["structure_type"], "eq.Linear peptide")

if __name__ == "__main__":
    unittest.main()
