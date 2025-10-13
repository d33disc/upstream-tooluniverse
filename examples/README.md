# ToolUniverse Scientific Research Examples

This directory contains professional scientific research examples demonstrating the use of ToolUniverse's direct import functionality for real-world scientific applications.

## Overview

The examples showcase how to use `tooluniverse.tools` direct imports to build comprehensive scientific research workflows with proper data flow and scientific rigor.

## Available Examples

### 1. Scientific Research Example (`scientific_research_example.py`)

A comprehensive example demonstrating three key scientific research workflows:

#### Drug Discovery Workflow
- **Purpose**: Complete drug discovery pipeline for precision medicine
- **Key Features**:
  - Disease target identification using OpenTargets
  - Drug similarity search using ChEMBL
  - ADMET property prediction
  - Clinical evidence synthesis
  - FDA drug comparison
- **Example**: Type 2 diabetes drug discovery using Metformin as reference

#### Biomarker Discovery Workflow
- **Purpose**: Cancer biomarker discovery and validation
- **Key Features**:
  - Gene expression analysis using HPA
  - GO annotation analysis
  - Literature search for biomarker evidence
  - Clinical trial identification
- **Example**: Breast cancer biomarker discovery for BRCA1, BRCA2, TP53, PTEN, PIK3CA

#### Drug Repurposing Workflow
- **Purpose**: Drug repurposing for precision medicine
- **Key Features**:
  - Disease analysis and target identification
  - Existing drug mechanism analysis
  - Repurposing literature search
  - FDA drug comparison
- **Example**: Alzheimer's disease drug repurposing for Donepezil, Memantine, Rivastigmine, Galantamine

### 2. Simplified Examples

#### Drug Discovery Simple (`drug_discovery_simple.py`)
- Streamlined drug discovery workflow
- Direct tool usage without complex wrappers
- Proper data flow between steps

#### Genomics Simple (`genomics_simple.py`)
- Genomics research workflow
- Gene expression and pathway analysis
- Literature integration

#### Literature Search Simple (`literature_search_simple.py`)
- Multi-database literature search
- Integration of ArXiv, PubMed, Europe PMC, Semantic Scholar, OpenAlex
- Evidence synthesis

#### Protein Structure Simple (`protein_structure_simple.py`)
- Protein structure analysis workflow
- PDB data retrieval and analysis
- 3D visualization

#### Clinical Trial Simple (`clinical_trial_simple.py`)
- Clinical trial analysis pipeline
- FDA drug data integration
- Safety analysis

## Key Features

### Professional Quality
- **Scientific Rigor**: Examples demonstrate real-world scientific research methodologies
- **Data Flow**: Proper use of output from one step as input for the next
- **Error Handling**: Robust error handling for production use
- **Documentation**: Comprehensive docstrings and comments

### Direct Tool Usage
- **No Wrappers**: Direct import and use of `tooluniverse.tools` functions
- **Clean Code**: Minimal, readable code without unnecessary abstractions
- **Efficient**: Direct function calls without overhead

### Comprehensive Coverage
- **Multiple Domains**: Drug discovery, genomics, literature, protein structure, clinical trials
- **Tool Integration**: Seamless integration of multiple scientific tools
- **Real Data**: Uses actual scientific databases and APIs

## Usage

### Running Examples

```bash
# Run the comprehensive scientific research example
python examples/scientific_research_example.py

# Run individual simplified examples
python examples/drug_discovery_simple.py
python examples/genomics_simple.py
python examples/literature_search_simple.py
python examples/protein_structure_simple.py
python examples/clinical_trial_simple.py
```

### Key Dependencies

```python
from tooluniverse.tools import (
    OpenTargets_get_disease_id_description_by_name,
    OpenTargets_get_associated_targets_by_disease_efoId,
    ChEMBL_search_similar_molecules,
    FDA_get_drug_names_by_indication,
    EuropePMC_search_articles,
    HPA_search_genes_by_query,
    GO_get_annotations_for_gene,
    search_clinical_trials,
    ADMETAI_predict_toxicity,
    ADMETAI_predict_bioavailability
)
```

## Scientific Value

These examples demonstrate:

1. **Real Research Applications**: Actual scientific workflows used in research
2. **Tool Integration**: How to combine multiple scientific tools effectively
3. **Data Pipeline**: Proper data flow and processing
4. **Professional Standards**: Code quality suitable for scientific publications
5. **Reproducibility**: Clear, documented workflows that can be reproduced

## Best Practices Demonstrated

- **Direct Tool Usage**: Import and use tools directly without unnecessary wrappers
- **Error Handling**: Robust error handling for production use
- **Data Validation**: Proper checking of tool outputs before use
- **Scientific Methodology**: Following established scientific research practices
- **Code Quality**: Clean, readable, and maintainable code

## Target Audience

- **Researchers**: Scientists looking to integrate multiple tools in their research
- **Developers**: Software developers building scientific applications
- **Students**: Graduate students learning scientific computing
- **Professionals**: Industry professionals in biotech and pharma

## Contributing

When adding new examples:

1. Follow the established patterns for direct tool usage
2. Ensure proper data flow between steps
3. Include comprehensive error handling
4. Add clear documentation and comments
5. Test thoroughly before submission

## License

These examples are part of the ToolUniverse project and follow the same licensing terms.