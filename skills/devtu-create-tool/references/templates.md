# JSON Config Templates

Full JSON configuration templates for common ToolUniverse tool patterns.

## Multi-Operation Tool Config

The canonical pattern for a tool class that handles multiple operations via an `operation` field. Each JSON entry corresponds to one operation; the `"const"` value is injected automatically so the user never needs to set it.

```json
[
  {
    "name": "MyAPI_search",
    "class": "MyAPITool",
    "description": "Search MyAPI for items matching a text query. Returns up to 100 results with IDs, names, and scores. Supports partial matching. Example: query='protein' finds all protein-related records.",
    "parameter": {
      "type": "object",
      "required": ["operation"],
      "properties": {
        "operation": {
          "const": "search",
          "description": "Operation type (fixed)"
        },
        "query": {
          "type": "string",
          "description": "Search term. Case-insensitive, partial matches supported."
        },
        "limit": {
          "type": ["integer", "null"],
          "description": "Max results (1-100). Default: 20.",
          "minimum": 1,
          "maximum": 100
        },
        "page": {
          "type": ["integer", "null"],
          "description": "Page number for pagination. Default: 1.",
          "minimum": 1
        }
      }
    },
    "return_schema": {
      "type": "object",
      "properties": {
        "status": {"type": "string", "enum": ["success", "error"]},
        "data": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id":    {"type": "string"},
              "name":  {"type": "string"},
              "score": {"type": "number"}
            },
            "additionalProperties": true
          }
        },
        "count": {"type": "integer"},
        "total": {"type": "integer"},
        "error": {"type": "string"}
      },
      "required": ["status"]
    },
    "test_examples": [
      {"operation": "search", "query": "TP53"},
      {"operation": "search", "query": "BRCA1", "limit": 5}
    ]
  },
  {
    "name": "MyAPI_get_item",
    "class": "MyAPITool",
    "description": "Retrieve full details for a single item by its unique ID. Returns complete record including metadata and related entities. Example: item_id='ITEM001' returns the full record for that item.",
    "parameter": {
      "type": "object",
      "required": ["operation", "item_id"],
      "properties": {
        "operation": {
          "const": "get_item",
          "description": "Operation type (fixed)"
        },
        "item_id": {
          "type": "string",
          "description": "Unique item identifier. Example: 'ITEM001'"
        }
      }
    },
    "return_schema": {
      "type": "object",
      "properties": {
        "status": {"type": "string", "enum": ["success", "error"]},
        "data": {
          "type": "object",
          "properties": {
            "id":          {"type": "string"},
            "name":        {"type": "string"},
            "description": {"type": "string"},
            "created":     {"type": "string"}
          },
          "additionalProperties": true
        },
        "error": {"type": "string"}
      },
      "required": ["status"]
    },
    "test_examples": [
      {"operation": "get_item", "item_id": "ITEM001"}
    ]
  }
]
```

## Mutually Exclusive Parameter Config

When the user may provide EITHER `gene_id` OR `gene_symbol` (but not both), both must be nullable so the unused one doesn't fail schema validation when `None` is passed.

```json
{
  "name": "GeneDB_get_gene",
  "class": "GeneDBTool",
  "description": "Retrieve gene information by Entrez gene ID or gene symbol. Returns gene record with annotations. Examples: gene_id='7157' (TP53), gene_symbol='BRCA1'.",
  "parameter": {
    "type": "object",
    "properties": {
      "gene_id": {
        "type": ["string", "null"],
        "description": "NCBI Entrez gene ID. Example: '7157' for TP53. Alternative to gene_symbol."
      },
      "gene_symbol": {
        "type": ["string", "null"],
        "description": "Official gene symbol. Example: 'TP53'. Alternative to gene_id."
      },
      "tax_id": {
        "type": ["string", "null"],
        "description": "NCBI taxonomy ID. Default: '9606' (human)."
      }
    }
  },
  "return_schema": {
    "type": "object",
    "properties": {
      "status": {"type": "string"},
      "data":   {"type": "object", "additionalProperties": true},
      "error":  {"type": "string"}
    }
  },
  "test_examples": [
    {"gene_id": "7157"},
    {"gene_symbol": "BRCA1", "tax_id": "9606"}
  ]
}
```

## Required vs Optional API Key Config

### Required API Key (tool won't load without it)

```json
{
  "name": "NVIDIA_ESMFold_predict",
  "class": "NVIDIAESMFoldTool",
  "required_api_keys": ["NVIDIA_API_KEY"],
  "description": "Predict protein 3D structure from amino acid sequence using ESMFold via NVIDIA NIM. Requires NVIDIA_API_KEY environment variable.",
  "parameter": {
    "type": "object",
    "required": ["sequence"],
    "properties": {
      "sequence": {
        "type": "string",
        "description": "Amino acid sequence in single-letter code. Example: 'MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL'",
        "minLength": 1,
        "maxLength": 2000
      }
    }
  },
  "test_examples": [
    {"sequence": "MKTAYIAKQRQISFVK"}
  ]
}
```

### Optional API Key (tool works without it, better rate limits with it)

```json
{
  "name": "PubMed_search_articles",
  "class": "PubMedTool",
  "optional_api_keys": ["NCBI_API_KEY"],
  "description": "Search PubMed for biomedical literature. Returns article IDs, titles, and abstracts. Rate limits: 3 req/sec without NCBI_API_KEY, 10 req/sec with key. Example: query='CRISPR gene editing' returns recent papers.",
  "parameter": {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": {
        "type": "string",
        "description": "PubMed search query. Supports MeSH terms and Boolean operators. Example: 'CRISPR AND cancer'"
      },
      "max_results": {
        "type": ["integer", "null"],
        "description": "Max articles to return (1-200). Default: 20."
      }
    }
  },
  "test_examples": [
    {"query": "CRISPR gene editing", "max_results": 5}
  ]
}
```

**Optional key implementation pattern:**
```python
def __init__(self, tool_config):
    super().__init__(tool_config)
    self.api_key = os.environ.get("NCBI_API_KEY", "")

def run(self, arguments):
    headers = {}
    if self.api_key:
        headers["api_key"] = self.api_key
    # tool works either way, just at different rate limits
```

## Paginated List Tool Config

For tools that return paginated collections:

```json
{
  "name": "MyAPI_list_datasets",
  "class": "MyAPITool",
  "description": "List all available datasets in MyAPI. Returns paginated results with dataset IDs and names. Use page/page_size to navigate large result sets.",
  "parameter": {
    "type": "object",
    "properties": {
      "page": {
        "type": ["integer", "null"],
        "description": "Page number (1-based). Default: 1."
      },
      "page_size": {
        "type": ["integer", "null"],
        "description": "Results per page (1-100). Default: 20."
      },
      "sort_by": {
        "type": ["string", "null"],
        "description": "Sort field. Options: 'name', 'date', 'size'. Default: 'name'."
      }
    }
  },
  "return_schema": {
    "type": "object",
    "properties": {
      "status":      {"type": "string"},
      "count":       {"type": "integer"},
      "total":       {"type": "integer"},
      "page":        {"type": "integer"},
      "total_pages": {"type": "integer"},
      "next":        {"type": ["string", "null"]},
      "previous":    {"type": ["string", "null"]},
      "results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id":   {"type": "string"},
            "name": {"type": "string"}
          },
          "additionalProperties": true
        }
      },
      "error": {"type": "string"}
    }
  },
  "test_examples": [
    {"page": 1, "page_size": 10}
  ]
}
```

## return_schema Anti-Patterns

### Too vague — don't do this:
```json
"return_schema": {
  "type": "object",
  "properties": {
    "data": {"type": "object", "additionalProperties": true}
  }
}
```

### Specific enough — do this:
```json
"return_schema": {
  "type": "object",
  "properties": {
    "status": {"type": "string"},
    "count":  {"type": "integer"},
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id":   {"type": "string"},
          "name": {"type": "string"}
        },
        "additionalProperties": true
      }
    },
    "error": {"type": "string"}
  }
}
```

Key rule: specify whether `data` is an object, array, or string. Always include `"error"` field. Use `additionalProperties: true` on nested objects rather than omitting the schema entirely.
