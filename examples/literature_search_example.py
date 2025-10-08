#!/usr/bin/env python3
"""
Literature Search Tools Example

This example demonstrates how to use all literature search tools
available in ToolUniverse for finding academic papers and preprints.
"""

from tooluniverse import ToolUniverse


def literature_search_examples():
    """Demonstrate all literature search tools."""

    # Initialize ToolUniverse
    tu = ToolUniverse()
    tu.load_tools()

    print("🔍 Literature Search Tools Example")
    print("=" * 50)

    # Define all literature search tools with their test examples
    tools = [
        # New tools we added
        {
            "name": "ArXiv_search_papers",
            "description": "ArXiv preprints",
            "examples": [
                {"query": "machine learning", "limit": 2,
                 "sort_by": "relevance"},
                {"query": "quantum physics", "limit": 1,
                 "sort_by": "submittedDate",
                 "sort_order": "descending"}
            ]
        },
        {
            "name": "Crossref_search_works",
            "description": "Crossref articles",
            "examples": [
                {"query": "artificial intelligence", "limit": 2},
                {"query": "machine learning", "limit": 1,
                 "filter": "type:journal-article,from-pub-date:2020-01-01"}
            ]
        },
        {
            "name": "DBLP_search_publications",
            "description": "DBLP computer science publications",
            "examples": [
                {"query": "computer science", "limit": 2},
                {"query": "machine learning", "limit": 1}
            ]
        },
        {
            "name": "PubMed_search_articles",
            "description": "PubMed medical articles",
            "examples": [
                {"query": "cancer research", "limit": 2},
                {"query": "COVID-19", "limit": 1}
            ]
        },
        {
            "name": "DOAJ_search_articles",
            "description": "DOAJ open access articles/journals",
            "examples": [
                {"query": "open access", "max_results": 2,
                 "type": "articles"},
                {"query": "biology", "max_results": 1,
                 "type": "journals"}
            ]
        },
        {
            "name": "Unpaywall_check_oa_status",
            "description": "Unpaywall open access status",
            "examples": [
                {"doi": "10.1038/nature12373",
                 "email": "test@example.com"},
                {"doi": "10.1126/science.1234567",
                 "email": "user@example.com"}
            ]
        },
        {
            "name": "BioRxiv_search_preprints",
            "description": "BioRxiv biology preprints",
            "examples": [
                {"query": "genetics", "max_results": 2},
                {"query": "CRISPR", "max_results": 1}
            ]
        },
        {
            "name": "MedRxiv_search_preprints",
            "description": "MedRxiv medical preprints",
            "examples": [
                {"query": "COVID", "max_results": 2},
                {"query": "vaccine", "max_results": 1}
            ]
        },
        {
            "name": "HAL_search_archive",
            "description": "HAL French research archive",
            "examples": [
                {"query": "mathematics", "max_results": 2},
                {"query": "physics", "max_results": 1}
            ]
        },
        # Existing tools
        {
            "name": "SemanticScholar_search_papers",
            "description": "Semantic Scholar papers",
            "examples": [
                {"query": "deep learning", "limit": 2},
                {"query": "natural language processing", "limit": 1}
            ]
        },
        {
            "name": "openalex_literature_search",
            "description": "OpenAlex literature search",
            "examples": [
                {"search_keywords": "artificial intelligence",
                 "max_results": 2},
                {"search_keywords": "machine learning", "max_results": 1,
                 "year_from": 2020}
            ]
        },
        {
            "name": "EuropePMC_search_articles",
            "description": "Europe PMC articles",
            "examples": [
                {"query": "bioinformatics", "limit": 2},
                {"query": "genomics", "limit": 1}
            ]
        },
        {
            "name": "CORE_search_papers",
            "description": "CORE open access papers",
            "examples": [
                {"query": "machine learning", "limit": 2},
                {"query": "artificial intelligence", "limit": 1,
                 "year_from": 2020}
            ]
        },
        {
            "name": "PMC_search_papers",
            "description": "PMC full-text biomedical literature",
            "examples": [
                {"query": "cancer research", "limit": 2},
                {"query": "COVID-19", "limit": 1,
                 "date_from": "2020/01/01"}
            ]
        },
        {
            "name": "Zenodo_search_records",
            "description": "Zenodo research data repository",
            "examples": [
                {"query": "machine learning", "max_results": 2},
                {"query": "climate change", "max_results": 1}
            ]
        },
        # New tools we added
        {
            "name": "OpenAIRE_search_publications",
            "description": "OpenAIRE European research products",
            "examples": [
                {
                    "query": "machine learning",
                    "max_results": 2,
                    "type": "publications"
                },
                {
                    "query": "climate change",
                    "max_results": 1,
                    "type": "datasets"
                }
            ]
        },
        {
            "name": "OSF_search_preprints",
            "description": "OSF Preprints research preprints",
            "examples": [
                {"query": "psychology", "max_results": 2},
                {
                    "query": "neuroscience",
                    "max_results": 1,
                    "provider": "psyarxiv"
                }
            ]
        },
        {
            "name": "Fatcat_search_scholar",
            "description": "Internet Archive Scholar via Fatcat",
            "examples": [
                {"query": "artificial intelligence", "max_results": 2},
                {"query": "quantum physics", "max_results": 1}
            ]
        },
        {
            "name": "Wikidata_SPARQL_query",
            "description": "Wikidata SPARQL queries for academic data",
            "examples": [
                {
                    "sparql": (
                        "SELECT ?item ?itemLabel WHERE { "
                        "?item wdt:P31 wd:Q11424 . "
                        "?item rdfs:label ?itemLabel . "
                        "FILTER(LANG(?itemLabel) = 'en') } LIMIT 3"
                    )
                },
                {
                    "sparql": (
                        "SELECT ?author ?authorLabel WHERE { "
                        "?author wdt:P31 wd:Q5 . "
                        "?author wdt:P106 wd:Q188094 . "
                        "?author rdfs:label ?authorLabel . "
                        "FILTER(LANG(?authorLabel) = 'en') } LIMIT 2"
                    )
                }
            ]
        }
    ]

    # Test each tool
    for i, tool in enumerate(tools, 1):
        print(f"\n{i}. Testing {tool['description']}...")

        for j, example in enumerate(tool['examples'], 1):
            print(f"   Example {j}: {example}")

            try:
                result = tu.run({
                    "name": tool['name'],
                    "arguments": example
                })

                if isinstance(result, list):
                    print(f"   ✅ Found {len(result)} results")
                    if result and len(result) > 0:
                        first_result = result[0]
                        title = first_result.get('title', 'No title')[:60]
                        print(f"   📄 Sample: {title}...")
                elif isinstance(result, dict):
                    if 'error' in result:
                        print(f"   ❌ Error: {result['error']}")
                    else:
                        print(f"   ✅ Result: {list(result.keys())}")
                else:
                    result_str = str(result)[:100]
                    print(f"   📝 Result: {result_str}...")

            except Exception as e:
                error_str = str(e)[:100]
                print(f"   ❌ Exception: {error_str}...")

    print(f"\n✅ Tested {len(tools)} literature search tools!")


if __name__ == "__main__":
    literature_search_examples()
