# API Discovery Report

Generated: 2026-02-12

## Executive Summary

- **Total tools in ToolUniverse**: 1,311
- **Config files analyzed**: 160+
- **Gap domains identified**: 14 completely missing or severely underrepresented
- **APIs discovered and evaluated**: 6
- **High priority APIs selected for implementation**: 2 (LIPID MAPS, USDA FoodData Central)

## Coverage Analysis

| Domain | Tool Count | Status |
|--------|-----------|--------|
| Clinical & Disease | 365 | OK |
| Software Packages | 163 | OK |
| Proteomics & Structural Biology | 140 | OK |
| Genomics & Variants | 132 | OK |
| Drug Discovery & Pharmacology | 101 | OK |
| Pathways & Interactions | 66 | OK |
| Data & Utilities | 56 | OK |
| Literature & Knowledge | 55 | OK |
| Public Health & Epidemiology | 43 | OK |
| Ontologies & Vocabularies | 34 | OK |
| Metabolomics | 33 | OK |
| Immunology | 21 | OK |
| Systems Biology & Modeling | 12 | MODERATE GAP |
| Ecology & Environment | 9 | MODERATE GAP |
| **Lipidomics** | **0** | **CRITICAL GAP** |
| **Food & Nutrition Science** | **0** | **CRITICAL GAP** |
| **Glycomics** | **0** | **CRITICAL GAP** |
| **Toxicology & Chemical Safety** | **0** | **CRITICAL GAP** |
| **Neuroscience Databases** | **0** | **CRITICAL GAP** |
| **Agricultural / Plant Biology** | **0** | **CRITICAL GAP** |
| **Synthetic Biology** | **0** | **CRITICAL GAP** |

## Prioritized API Candidates

### High Priority

#### 1. LIPID MAPS Structure Database REST API
- **Domain**: Lipidomics (CRITICAL GAP - 0 tools)
- **Score**: 88/100
- **Base URL**: https://www.lipidmaps.org/rest
- **Auth**: Public (no key required)
- **Endpoints**: 4 contexts (compound, gene, protein, mass spectrometry)
- **Rationale**: Only comprehensive lipidomics database; fills entirely missing domain
- **Scoring Breakdown**:
  - Documentation Quality: 18/20 (well-documented REST patterns)
  - API Stability: 14/15 (versioned, stable endpoints)
  - Authentication: 15/15 (fully public)
  - Coverage: 13/15 (lipid structures, genes, proteins, MS data)
  - Maintenance: 10/10 (updated 2024, NAR paper 2024)
  - Community: 8/10 (widely used in lipidomics)
  - License: 8/10 (academic/research use)
  - Rate Limits: 2/5 (no documented limits but no SLA)
- **Example Operations**:
  - Search compound by LMID, PubChem CID, formula, abbreviation
  - Get lipid classification and physical-chemical properties
  - Search lipid-related genes by symbol/name
  - Search lipid-related proteins by UniProt ID
  - Mass spectrometry m/z search

#### 2. USDA FoodData Central API
- **Domain**: Food & Nutrition Science (CRITICAL GAP - 0 tools)
- **Score**: 85/100
- **Base URL**: https://api.nal.usda.gov/fdc/v1
- **Auth**: Required API key (free, via data.gov signup)
- **Endpoints**: 4 (food search, food details, food list, batch food details)
- **Rationale**: Premier nutrition database; fills entirely missing domain
- **Scoring Breakdown**:
  - Documentation Quality: 20/20 (OpenAPI/Swagger spec available)
  - API Stability: 15/15 (versioned v1, government-maintained)
  - Authentication: 10/15 (requires free API key)
  - Coverage: 13/15 (comprehensive nutrient data for 1M+ foods)
  - Maintenance: 10/10 (government-maintained, actively updated)
  - Community: 8/10 (widely used in nutrition research)
  - License: 5/10 (public domain but key required)
  - Rate Limits: 4/5 (1000 req/hr, generous for research)

#### 3. GlyGen API
- **Domain**: Glycomics (CRITICAL GAP - 0 tools)
- **Score**: 75/100
- **Base URL**: https://api.glygen.org
- **Auth**: Public for read endpoints (no key required)
- **Endpoints**: 142 total (glycan, protein, motif, biomarker, disease, etc.)
- **Rationale**: Fills entirely missing glycomics domain
- **Note**: Deferred to next batch due to API complexity (all POST, many endpoints)

### Medium Priority

#### 4. EPA CompTox Dashboard APIs (CTX APIs)
- **Domain**: Toxicology & Chemical Safety
- **Score**: 68/100
- **Base URL**: https://api-ccte.epa.gov/
- **Auth**: Requires API key
- **Note**: Complex multi-domain API, better suited for dedicated batch

#### 5. CTD (Comparative Toxicogenomics Database)
- **Domain**: Toxicology & Chemical Safety
- **Score**: 52/100
- **Note**: Batch query web interface only, no true REST API - lower priority

#### 6. Allen Brain Atlas API
- **Domain**: Neuroscience Databases
- **Score**: 65/100
- **Base URL**: https://api.brain-map.org
- **Note**: Complex RMA query system, needs dedicated integration effort

## Implementation Plan

### Batch 1 (This Session)
1. **LIPID MAPS** - 5 tools (compound search, compound details, gene search, protein search, mass search)
2. **USDA FoodData Central** - 4 tools (food search, food details, food list, nutrient search)

### Batch 2 (Future)
3. **GlyGen** - 6 tools (glycan search, glycan detail, protein search, biomarker search, ID mapping, global search)
4. **EPA CompTox** - 4 tools
5. **Allen Brain Atlas** - 4 tools

## Appendix: Search Methodology

### Search Queries Used
- "[domain] API REST JSON"
- "[domain] database API documentation"
- "[domain] web services programmatic access 2025 2026"
- Site-specific: NAR database issue, PMC

### Sources Consulted
- Official API documentation pages
- OpenAPI/Swagger specifications
- R/Python client packages
- NAR Database Issues (2024, 2025)
- PubMed Central publications

### API Verification
All high-priority APIs were tested with real requests to verify:
- Endpoints respond correctly
- Data format matches documentation
- Real test IDs produce valid results
