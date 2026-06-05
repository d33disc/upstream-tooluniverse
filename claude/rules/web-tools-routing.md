# Web Tools Routing

Four web tool layers: Tavily (search+extract), Exa (semantic search), Jina (read+search+academic), native (free fallback). ToolUniverse always wins for structured scientific data.

## Decision Tree

| Task | Tool | Why |
|------|------|-----|
| Known URL -> clean markdown | Jina `read_url` | JS rendering, clean output, free without key |
| Known URL -> raw HTML/JSON | `curl` via Bash | APIs, static endpoints, no processing overhead |
| Keyword web search | Tavily `tavily_search` (depth: `fast`) | Best cost/quality: 1 credit, richer snippets than basic |
| Conceptual/semantic search | Exa `web_search_exa` | Neural index finds related content without exact keywords |
| Filtered search (dates, domains) | Exa `web_search_advanced_exa` | Full filter suite: dates, domains, categories, content options |
| Company lookup | Exa `web_search_advanced_exa` category: `company` | Dedicated index returns company entities, not articles |
| People lookup | Exa `web_search_advanced_exa` category: `people` | LinkedIn-focused. Note: disables date/text filters |
| Academic papers (arXiv) | Jina `search_arxiv` | Direct arXiv search, returns full results |
| Academic papers (SSRN) | Jina `search_ssrn` | Social science, economics, law, finance |
| BibTeX citations | Jina `search_bibtex` | Free, no API key. Searches DBLP + Semantic Scholar |
| Site structure discovery | Tavily `tavily_map` | Cheap (1 credit/10 pages), returns URL tree |
| Site content extraction | Tavily `tavily_map` then `tavily_extract` | Never use `tavily_crawl` — it truncates to 200 chars in MCP |
| Documentation/library help | Tavily `tavily_skill` | MCP-only doc search. Supports library, language, task filters |
| Code examples | Exa `web_search_advanced_exa` category: `github` | Or `get_code_context_exa` (deprecated but functional) |
| Deep multi-source research | Tavily `tavily_research` model: `mini` | 4-110 credits. Use `pro` only for broad multi-topic synthesis |
| PDF figure/table extraction | Jina `extract_pdf` | Layout detection for figures, tables, equations |
| Image search | Jina `search_images` | Returns base64 JPEG or URLs |
| Rerank results by relevance | Jina `sort_by_relevance` | Jina Reranker API via MCP |
| Quick fact check | Native `WebSearch` | Free, no rate limit, good enough for simple lookups |
| Scientific databases | ToolUniverse | Always first for bio/chem/clinical/genomic structured data |

## Fallback Chain

If rate-limited or failed: Tavily search <-> Exa search <-> Jina `search_web` <-> native WebSearch.

For URL reading: Jina `read_url` -> native WebFetch -> curl.

## Tavily Reference

### Search Depths

| Depth | Credits | Use when |
|-------|---------|----------|
| `fast` | 1 | **Default.** Rich snippets, low latency |
| `basic` | 1 | Simple queries where speed matters less |
| `advanced` | 2 | Need multiple semantic chunks per source |
| `ultra-fast` | 1 | Autocomplete, real-time UI (not our use case) |

### Credit Costs

| Operation | Credits |
|-----------|---------|
| Search (basic/fast/ultra-fast) | 1 |
| Search (advanced) | 2 |
| Extract (basic, per 5 URLs) | 1 |
| Extract (advanced, per 5 URLs) | 2 |
| Map (per 10 pages) | 1 |
| Map with instructions (per 10 pages) | 2 |
| Research mini | 4-110 |
| Research pro | 15-250 |

### Gotchas

- `topic` is locked to `general` in MCP — no news/finance mode
- `country` requires full name ("United States" not "us")
- `time_range` and `start_date`/`end_date` are mutually exclusive
- `tavily_crawl` truncates content to 200 chars per page in MCP — always use map + extract instead
- Free tier: 1k credits/month, aggressive frequency rate limits

## Exa Reference

### Search Types

| Type | Cost/1k | Speed | Use when |
|------|---------|-------|----------|
| `auto` | $7 | ~1s | Most queries — hybrid semantic + keyword |
| `fast` | $7 | ~450ms | Real-time, quick lookups |
| `neural` | $7 | ~1s | Pure semantic similarity |
| `deep` | $12 | 4-12s | Research, structured outputs with `outputSchema` |
| `deep-reasoning` | $15 | 12-50s | Complex multi-step synthesis |

### Categories

Use with `web_search_advanced_exa`. Each searches a dedicated index.

| Category | Returns | Caveat |
|----------|---------|--------|
| `company` | Company entities | Disables date filters, text filters, excludeDomains |
| `people` | LinkedIn profiles | Disables date filters; includeDomains only accepts LinkedIn |
| `research paper` | Academic papers | arxiv.org, paperswithcode.com, etc. |
| `news` | News articles | Use `maxAgeHours: 0` for breaking news |
| `github` | Repos, code, issues | Good for code examples |
| `pdf` | PDF documents | -- |
| `financial report` | SEC filings, reports | -- |

### Deprecated Parameters (never use)

- `useAutoprompt` — does nothing
- `numSentences`, `highlightsPerUrl` — use `maxCharacters`
- `livecrawl` — use `maxAgeHours` (0 = force fresh)
- `includeUrls`/`excludeUrls` — use `includeDomains`/`excludeDomains`
- `tokensNum` — use `contents.text.maxCharacters`

### Free Tier

1,000 requests/month. Rate limits: 10 QPS search, 100 QPS contents.

## Jina Reference

### Key Tools (21 total, most useful listed)

| Tool | Auth required? | Notes |
|------|---------------|-------|
| `read_url` | No (rate-limited) | Accepts single URL or array. 25k token truncation in Claude Code |
| `search_web` | Yes | General web search via s.jina.ai. Default 30 results |
| `search_arxiv` | Yes | arXiv-specific search |
| `search_ssrn` | Yes | SSRN-specific search |
| `search_bibtex` | **No** | Free. DBLP + Semantic Scholar. Returns BibTeX |
| `search_images` | Yes | Returns base64 JPEG or URLs |
| `extract_pdf` | Yes | Figures, tables, equations from PDFs |
| `sort_by_relevance` | Yes | Reranker API |
| `expand_query` | Yes | Rewrites query into diverse variants |
| `capture_screenshot_url` | No (rate-limited) | Full page or viewport screenshot |

### Time Filters (tbs parameter)

`qdr:h` (hour), `qdr:d` (day), `qdr:w` (week), `qdr:m` (month), `qdr:y` (year)

### Gotchas

- `read_url` truncates to 25k tokens for Claude Code — long pages get silently cut
- `read_url` strips images and links by default — set `withAllImages`/`withAllLinks` to true if needed
- Search defaults to 30 results — set `num` lower to save tokens
- `parallel_*` variants exist but are redundant — the base tools accept arrays
- Shared token pool: Reader, Embeddings, Reranker all draw from the same 10M free tokens
- `search_images` does NOT accept arrays (unlike other search tools)
