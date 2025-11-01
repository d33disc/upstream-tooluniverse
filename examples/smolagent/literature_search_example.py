"""
Advanced Literature Search Agent Example

This example demonstrates how to use the advanced_literature_search_agent,
a sophisticated multi-agent system that performs comprehensive literature
searches across multiple academic databases with intelligent deduplication,
relevance scoring, and trend analysis.

The agent automatically determines search strategy, database selection,
filters, and result limits based on the query content - you just provide
the research query.
"""

from tooluniverse import ToolUniverse


def main():
    tu = ToolUniverse()
    tu.load_tools()

    # Example: Interdisciplinary topic
    print("\n" + "=" * 80)
    print("Example: Interdisciplinary Research Topic")
    print("=" * 80)

    result = tu.run(
        {
            "name": "advanced_literature_search_agent",
            "arguments": {
                "query": (
                    "single-cell RNA sequencing analysis methods "
                    "and computational tools"
                ),
            },
        }
    )
    print(result)
    # print(f"\nSuccess: {result.get('success', False)}")
    # if result.get("execution_time"):
    #     print(f"Execution Time: {result.get('execution_time'):.2f}s")
    # if result.get("success") and result.get("output"):
    #     output = result.get("output", "")
    #     if isinstance(output, str) and len(output) > 500:
    #         print("\nOutput preview (first 500 chars):")
    #         print(output[:500] + "...")


if __name__ == "__main__":
    main()
