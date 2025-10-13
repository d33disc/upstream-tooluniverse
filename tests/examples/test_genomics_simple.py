#!/usr/bin/env python3
"""
Tests for genomics simple example
"""

import unittest

from tooluniverse.tools import (
    HPA_search_genes_by_query,
    HPA_get_comprehensive_gene_details_by_ensembl_id,
    GO_get_annotations_for_gene,
    enrichr_gene_enrichment_analysis
)


class TestGenomicsSimple(unittest.TestCase):
    """Test genomics simple example functions."""
    
    def test_search_genes(self):
        """Test gene search."""
        from examples.genomics_simple import search_genes
        
        # Test with a known gene
        genes = search_genes("BRCA1")
        
        # Should return results or None
        self.assertTrue(genes is None or isinstance(genes, dict))
    
    def test_get_gene_details(self):
        """Test getting gene details."""
        from examples.genomics_simple import get_gene_details
        
        # Test with a known Ensembl ID
        ensembl_id = "ENSG00000012048"  # BRCA1
        details = get_gene_details(ensembl_id)
        
        # Should return results or None
        self.assertTrue(details is None or isinstance(details, dict))
    
    def test_analyze_expression(self):
        """Test expression analysis."""
        from examples.genomics_simple import analyze_expression
        
        # Test with a known Ensembl ID
        ensembl_id = "ENSG00000012048"  # BRCA1
        expression = analyze_expression(ensembl_id)
        
        # Should return results or None
        self.assertTrue(expression is None or isinstance(expression, dict))
    
    def test_find_protein_interactions(self):
        """Test finding protein interactions."""
        from examples.genomics_simple import find_protein_interactions
        
        # Test with a known Ensembl ID
        ensembl_id = "ENSG00000012048"  # BRCA1
        interactions = find_protein_interactions(ensembl_id)
        
        # Should return results or None
        self.assertTrue(interactions is None or isinstance(interactions, dict))
    
    def test_get_go_annotations(self):
        """Test getting GO annotations."""
        from examples.genomics_simple import get_go_annotations
        
        # Test with a known Ensembl ID
        ensembl_id = "ENSG00000012048"  # BRCA1
        annotations = get_go_annotations(ensembl_id)
        
        # Should return results or None
        self.assertTrue(annotations is None or isinstance(annotations, dict))
    
    def test_pathway_enrichment(self):
        """Test pathway enrichment analysis."""
        from examples.genomics_simple import pathway_enrichment
        
        # Test with a list of genes
        gene_list = ["BRCA1", "TP53", "ATM"]
        enrichment = pathway_enrichment(gene_list)
        
        # Should return results or None
        self.assertTrue(enrichment is None or isinstance(enrichment, dict))
    
    def test_genomics_analysis(self):
        """Test complete genomics analysis."""
        from examples.genomics_simple import genomics_analysis
        
        # Test with a known gene
        results = genomics_analysis("BRCA1")
        
        # Should return a dictionary
        self.assertIsInstance(results, dict)
        
        # Should have expected keys or error
        if 'error' not in results:
            expected_keys = ['gene_info', 'details', 'expression', 'interactions', 'go_annotations', 'literature', 'associations']
            for key in expected_keys:
                self.assertIn(key, results)
    
    def test_pathway_analysis(self):
        """Test pathway analysis."""
        from examples.genomics_simple import pathway_analysis
        
        # Test with a list of genes
        gene_list = ["BRCA1", "TP53", "ATM"]
        results = pathway_analysis(gene_list)
        
        # Should return a dictionary
        self.assertIsInstance(results, dict)
        
        # Should have expected keys
        expected_keys = ['enrichment', 'gene_results']
        for key in expected_keys:
            self.assertIn(key, results)


class TestDirectImports(unittest.TestCase):
    """Test direct imports work correctly."""
    
    def test_hpa_import(self):
        """Test HPA import."""
        self.assertIsNotNone(HPA_search_genes_by_query)
        self.assertIsNotNone(HPA_get_comprehensive_gene_details_by_ensembl_id)
    
    def test_go_import(self):
        """Test GO import."""
        self.assertIsNotNone(GO_get_annotations_for_gene)
    
    def test_enrichr_import(self):
        """Test Enrichr import."""
        self.assertIsNotNone(enrichr_gene_enrichment_analysis)


if __name__ == "__main__":
    unittest.main()
