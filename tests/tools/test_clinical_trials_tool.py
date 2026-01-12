import unittest
from unittest.mock import patch, MagicMock
try:
    from tooluniverse.clinical_trials_tool import ClinicalTrialsGovTool
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    from tooluniverse.clinical_trials_tool import ClinicalTrialsGovTool

class TestClinicalTrialsTool(unittest.TestCase):
    def setUp(self):
        dummy_config = {
            "name": "clinical_trials_search",
            "type": "ClinicalTrialsGovTool",
            "description": "Test",
            "parameter": {}
        }
        self.tool = ClinicalTrialsGovTool(tool_config=dummy_config)

    @patch('tooluniverse.clinical_trials_tool.requests.get')
    def test_search_studies(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "studies": [
                {
                    "protocolSection": {
                        "identificationModule": {
                            "nctId": "NCT123",
                            "officialTitle": "Test Study"
                        },
                        "statusModule": {"overallStatus": "Recruiting"},
                        "conditionsModule": {"conditions": ["Cancer"]}
                    }
                }
            ],
            "totalCount": 1
        }
        mock_get.return_value = mock_response

        result = self.tool.run({
            "action": "search_studies",
            "condition": "cancer",
            "limit": 5
        })

        self.assertEqual(len(result["studies"]), 1)
        self.assertEqual(result["studies"][0]["nctId"], "NCT123")
        self.assertEqual(result["studies"][0]["title"], "Test Study")
        
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["query.cond"], "cancer")
        self.assertEqual(kwargs["params"]["pageSize"], 5)

    @patch('tooluniverse.clinical_trials_tool.requests.get')
    def test_get_study_details(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "protocolSection": {
                "identificationModule": {
                    "officialTitle": "Full Test Study"
                },
                "descriptionModule": {
                    "briefSummary": "Summary"
                },
                "eligibilityModule": {
                    "eligibilityCriteria": "Criteria"
                }
            }
        }
        mock_get.return_value = mock_response

        result = self.tool.run({
            "action": "get_study_details",
            "nct_id": "NCT123"
        })

        self.assertEqual(result["nctId"], "NCT123")
        self.assertEqual(result["title"], "Full Test Study")
        self.assertEqual(result["summary"], "Summary")
        self.assertEqual(result["eligibility"]["eligibilityCriteria"], "Criteria")
        
        args, kwargs = mock_get.call_args
        self.assertTrue(args[0].endswith("NCT123"))

if __name__ == "__main__":
    unittest.main()
