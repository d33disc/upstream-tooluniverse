#!/usr/bin/env python3
"""
Tests for drug discovery simple example
"""

import unittest

from tooluniverse.tools import (
    OpenTargets_get_disease_id_description_by_name,
    ChEMBL_search_similar_molecules,
    ADMETAI_predict_toxicity,
    EuropePMC_search_articles
)


class TestDrugDiscoverySimple(unittest.TestCase):
    """Test drug discovery simple example functions."""
    
    def test_find_disease_targets(self):
        """Test finding disease targets."""
        from examples.drug_discovery_simple import find_disease_targets
        
        # Test with a known disease
        targets = find_disease_targets("Alzheimer's disease")
        
        # Should return results or None
        self.assertTrue(targets is None or isinstance(targets, dict))
    
    def test_find_similar_compounds(self):
        """Test finding similar compounds."""
        from examples.drug_discovery_simple import find_similar_compounds
        
        # Test with a known compound
        compounds = find_similar_compounds("aspirin")
        
        # Should return results or None
        self.assertTrue(compounds is None or isinstance(compounds, dict))
    
    def test_predict_admet_properties(self):
        """Test ADMET property prediction."""
        from examples.drug_discovery_simple import predict_admet_properties
        
        # Test with a simple SMILES
        smiles = "CCO"  # Ethanol
        admet = predict_admet_properties(smiles)
        
        # Should return a dictionary
        self.assertIsInstance(admet, dict)
        self.assertIn('toxicity', admet)
        self.assertIn('bioavailability', admet)
    
    def test_search_literature(self):
        """Test literature search."""
        from examples.drug_discovery_simple import search_literature
        
        # Test with a simple query
        papers = search_literature("drug discovery")
        
        # Should return results or None
        self.assertTrue(papers is None or isinstance(papers, dict))
    
    def test_drug_discovery_workflow(self):
        """Test complete drug discovery workflow."""
        from examples.drug_discovery_simple import drug_discovery_workflow
        
        # Test with known parameters
        results = drug_discovery_workflow("diabetes", "metformin")
        
        # Should return a dictionary
        self.assertIsInstance(results, dict)
        
        # Should have expected keys
        expected_keys = ['targets', 'compounds']
        for key in expected_keys:
            self.assertIn(key, results)


class TestDirectImports(unittest.TestCase):
    """Test direct imports work correctly."""
    
    def test_open_targets_import(self):
        """Test OpenTargets import."""
        self.assertIsNotNone(OpenTargets_get_disease_id_description_by_name)
    
    def test_chembl_import(self):
        """Test ChEMBL import."""
        self.assertIsNotNone(ChEMBL_search_similar_molecules)
    
    def test_admet_import(self):
        """Test ADMET import."""
        self.assertIsNotNone(ADMETAI_predict_toxicity)
    
    def test_literature_import(self):
        """Test literature search import."""
        self.assertIsNotNone(EuropePMC_search_articles)


if __name__ == "__main__":
    unittest.main()
