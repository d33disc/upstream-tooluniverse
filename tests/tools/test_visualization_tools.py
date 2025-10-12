"""
Tests for Visualization Tools
============================

Test cases for all visualization tools in ToolUniverse.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from tooluniverse import ToolUniverse


class TestVisualizationTools:
    """Test cases for visualization tools."""

    def setup_method(self):
        """Set up test environment."""
        self.tu = ToolUniverse()
        self.tu.load_tools()

    def test_protein_structure_3d_tool_exists(self):
        """Test that protein structure 3D tool is registered."""
        tool_names = [tool.get("name") for tool in self.tu.all_tools if isinstance(tool, dict)]
        assert "visualize_protein_structure_3d" in tool_names

    def test_molecule_2d_tool_exists(self):
        """Test that molecule 2D tool is registered."""
        tool_names = [tool.get("name") for tool in self.tu.all_tools if isinstance(tool, dict)]
        assert "visualize_molecule_2d" in tool_names

    def test_molecule_3d_tool_exists(self):
        """Test that molecule 3D tool is registered."""
        tool_names = [tool.get("name") for tool in self.tu.all_tools if isinstance(tool, dict)]
        assert "visualize_molecule_3d" in tool_names

    @patch('requests.get')
    def test_protein_structure_3d_with_pdb_id(self, mock_get):
        """Test protein structure 3D visualization with PDB ID."""
        # Mock PDB response
        mock_response = MagicMock()
        mock_response.text = "ATOM      1  N   ALA A   1      20.154  16.967  23.862  1.00 11.18           N"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock py3Dmol
        with patch('py3Dmol.view') as mock_view:
            mock_viewer = MagicMock()
            mock_viewer.addModel.return_value = None
            mock_viewer.setStyle.return_value = None
            mock_viewer.zoomTo.return_value = None
            mock_viewer._make_html.return_value = "<div>3D Viewer</div>"
            mock_view.return_value = mock_viewer

            result = self.tu.run({
                "name": "visualize_protein_structure_3d",
                "arguments": {
                    "pdb_id": "1CRN",
                    "style": "cartoon",
                    "color_scheme": "spectrum"
                }
            })

            assert result["success"] is True
            assert "visualization" in result
            assert result["visualization"]["type"] == "protein_structure_3d"
            assert "html" in result["visualization"]

    def test_protein_structure_3d_missing_params(self):
        """Test protein structure 3D tool with missing parameters."""
        result = self.tu.run({
            "name": "visualize_protein_structure_3d",
            "arguments": {}
        })

        assert result["success"] is False
        assert "error" in result

    @patch('requests.get')
    def test_molecule_2d_with_smiles(self, mock_get):
        """Test molecule 2D visualization with SMILES."""
        # Mock PubChem response (not used in this test but needed for import)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"PropertyTable": {"Properties": []}}
        mock_get.return_value = mock_response

        # Mock RDKit
        with patch('rdkit.Chem.MolFromSmiles') as mock_mol_from_smiles, \
             patch('rdkit.Chem.Draw.MolToImage') as mock_mol_to_image, \
             patch('rdkit.Chem.rdDepictor.Compute2DCoords') as mock_compute_2d:

            mock_mol = MagicMock()
            mock_mol_from_smiles.return_value = mock_mol
            mock_image = MagicMock()
            mock_image.save.return_value = None
            mock_mol_to_image.return_value = mock_image
            mock_compute_2d.return_value = None

            result = self.tu.run({
                "name": "visualize_molecule_2d",
                "arguments": {
                    "smiles": "CCO",
                    "width": 400,
                    "height": 400
                }
            })

            assert result["success"] is True
            assert "visualization" in result
            assert result["visualization"]["type"] == "molecule_2d"
            assert "html" in result["visualization"]
            assert "static_image" in result["visualization"]

    def test_molecule_2d_missing_params(self):
        """Test molecule 2D tool with missing parameters."""
        result = self.tu.run({
            "name": "visualize_molecule_2d",
            "arguments": {}
        })

        assert result["success"] is False
        assert "error" in result

    @patch('requests.get')
    def test_molecule_3d_with_smiles(self, mock_get):
        """Test molecule 3D visualization with SMILES."""
        # Mock PubChem response (not used in this test but needed for import)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"PropertyTable": {"Properties": []}}
        mock_get.return_value = mock_response

        # Mock RDKit and py3Dmol
        with patch('rdkit.Chem.MolFromSmiles') as mock_mol_from_smiles, \
             patch('rdkit.Chem.AddHs') as mock_add_hs, \
             patch('rdkit.Chem.AllChem.EmbedMolecule') as mock_embed, \
             patch('rdkit.Chem.AllChem.MMFFOptimizeMolecule') as mock_optimize, \
             patch('rdkit.Chem.MolToMolBlock') as mock_mol_to_block, \
             patch('py3Dmol.view') as mock_view:

            mock_mol = MagicMock()
            mock_mol.GetNumConformers.return_value = 1
            mock_mol_from_smiles.return_value = mock_mol
            mock_add_hs.return_value = mock_mol
            mock_embed.return_value = 0
            mock_optimize.return_value = 0
            mock_mol_to_block.return_value = "MOL BLOCK"

            mock_viewer = MagicMock()
            mock_viewer.addModel.return_value = None
            mock_viewer.setStyle.return_value = None
            mock_viewer.zoomTo.return_value = None
            mock_viewer._make_html.return_value = "<div>3D Viewer</div>"
            mock_view.return_value = mock_viewer

            result = self.tu.run({
                "name": "visualize_molecule_3d",
                "arguments": {
                    "smiles": "CCO",
                    "style": "stick",
                    "color_scheme": "default"
                }
            })

            assert result["success"] is True
            assert "visualization" in result
            assert result["visualization"]["type"] == "molecule_3d"
            assert "html" in result["visualization"]

    def test_molecule_3d_missing_params(self):
        """Test molecule 3D tool with missing parameters."""
        result = self.tu.run({
            "name": "visualize_molecule_3d",
            "arguments": {}
        })

        assert result["success"] is False
        assert "error" in result

    def test_tool_configurations_exist(self):
        """Test that tool configuration files exist."""
        config_files = [
            "src/tooluniverse/data/protein_structure_3d_tools.json",
            "src/tooluniverse/data/molecule_2d_tools.json",
            "src/tooluniverse/data/molecule_3d_tools.json"
        ]

        for config_file in config_files:
            assert os.path.exists(config_file)
            with open(config_file, 'r') as f:
                config = json.load(f)
                assert isinstance(config, list)
                assert len(config) > 0
                assert "name" in config[0]
                assert "type" in config[0]
                assert "parameter" in config[0]

    def test_tool_error_handling(self):
        """Test error handling for visualization tools."""
        # Test with invalid SMILES
        result = self.tu.run({
            "name": "visualize_molecule_2d",
            "arguments": {
                "smiles": "invalid_smiles_string"
            }
        })

        # Should handle gracefully (either success with error message or failure)
        assert "success" in result

    def test_tool_parameter_validation(self):
        """Test parameter validation for visualization tools."""
        # Test protein structure tool with invalid style
        result = self.tu.run({
            "name": "visualize_protein_structure_3d",
            "arguments": {
                "pdb_id": "1CRN",
                "style": "invalid_style"
            }
        })

        # Should still work but use default style
        assert "success" in result

    def test_tool_metadata(self):
        """Test that tools have proper metadata."""
        tool_names = [tool.get("name") for tool in self.tu.all_tools if isinstance(tool, dict)]
        
        viz_tools = [tool for tool in tool_names if "visualize" in tool]
        assert len(viz_tools) >= 3

        for tool_name in viz_tools:
            tool_config = next((tool for tool in self.tu.all_tools if isinstance(tool, dict) and tool.get("name") == tool_name), None)
            assert tool_config is not None
            assert "description" in tool_config
            assert "parameter" in tool_config


if __name__ == "__main__":
    pytest.main([__file__])
