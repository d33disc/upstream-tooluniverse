#!/usr/bin/env python3
"""
Literature Search Example

Simple example showing how to use ToolUniverse's direct import functionality
for literature search with proper data flow.
"""

# Direct imports from tooluniverse.tools
from tooluniverse.tools import (
    ArXiv_search_papers,
    PubMed_search_articles,
    EuropePMC_search_articles,
    SemanticScholar_search_papers,
    openalex_literature_search
)

# Complete Literature Search Workflow
print("=== Complete Literature Search Workflow ===")

# Step 1: Search ArXiv for recent AI papers
print("\n1. Searching ArXiv for recent AI papers...")
arxiv_results = ArXiv_search_papers(
    query="AI in medicine",
    limit=3,
    sort_by="relevance",
    sort_order="descending"
)
print(f"Found {len(arxiv_results['entries']) if arxiv_results and 'entries' in arxiv_results else 0} ArXiv papers")

# Step 2: Search PubMed using keywords from ArXiv results
print("\n2. Searching PubMed for related medical literature...")
pubmed_results = PubMed_search_articles(
    query="artificial intelligence medical diagnosis",
    limit=3,
    api_key=""
)
print(f"Found {len(pubmed_results) if pubmed_results else 0} PubMed articles")

# Step 3: Search Europe PMC for comprehensive coverage
print("\n3. Searching Europe PMC for comprehensive coverage...")
europepmc_results = EuropePMC_search_articles(
    query="machine learning healthcare",
    limit=3
)
print(f"Found {len(europepmc_results) if europepmc_results else 0} Europe PMC articles")

# Step 4: Search Semantic Scholar for academic papers
print("\n4. Searching Semantic Scholar for academic papers...")
semantic_results = SemanticScholar_search_papers(
    query="deep learning medical imaging",
    limit=3,
    api_key=""
)
print(f"Found {len(semantic_results) if semantic_results else 0} Semantic Scholar papers")

# Step 5: Search OpenAlex for open access papers
print("\n5. Searching OpenAlex for open access papers...")
openalex_results = openalex_literature_search(
    search_keywords="neural networks clinical decision support",
    max_results=3,
    year_from=2020,
    year_to=2024,
    open_access=True
)
print(f"Found {len(openalex_results) if openalex_results else 0} OpenAlex papers")

# Step 6: Analyze and summarize results
print("\n6. Analyzing search results...")
total_papers = 0
sources = []

if arxiv_results and 'entries' in arxiv_results:
    total_papers += len(arxiv_results['entries'])
    sources.append("ArXiv")

if pubmed_results:
    total_papers += len(pubmed_results)
    sources.append("PubMed")

if europepmc_results:
    total_papers += len(europepmc_results)
    sources.append("Europe PMC")

if semantic_results:
    total_papers += len(semantic_results)
    sources.append("Semantic Scholar")

if openalex_results:
    total_papers += len(openalex_results)
    sources.append("OpenAlex")

print(f"Total papers found: {total_papers}")
print(f"Sources searched: {', '.join(sources)}")

# Step 7: Extract key information from results
print("\n7. Extracting key information...")
if arxiv_results and 'entries' in arxiv_results and len(arxiv_results['entries']) > 0:
    first_paper = arxiv_results['entries'][0]
    print(f"First ArXiv paper: {first_paper['title']}")
    print(f"Authors: {', '.join([author['name'] for author in first_paper['authors']])}")
    print(f"Published: {first_paper['published']}")

if pubmed_results and len(pubmed_results) > 0:
    first_pubmed = pubmed_results[0]
    print(f"First PubMed article: {first_pubmed.get('title', 'No title')}")

print("\n=== Literature Search Workflow Complete ===")
print("Summary:")
print(f"- Total papers found: {total_papers}")
print(f"- Sources: {', '.join(sources)}")
print(f"- Search terms used: AI in medicine, artificial intelligence medical diagnosis, machine learning healthcare, deep learning medical imaging, neural networks clinical decision support")