---
name: setup-tooluniverse
description: Install and configure ToolUniverse with MCP integration for any AI coding client (Cursor, Claude Desktop, Windsurf, VS Code, Codex, Gemini CLI, Trae, Cline, Antigravity, OpenCode, etc.). Covers uv/uvx setup, MCP configuration, API key walkthrough, skill installation, and upgrading. Use when setting up ToolUniverse, configuring MCP servers, troubleshooting installation issues, upgrading versions, or when user mentions installing ToolUniverse or setting up scientific tools.
---

# Setup ToolUniverse

Guide the user step-by-step through setting up ToolUniverse with MCP (Model Context Protocol) integration.

## Agent Behavior

**Be friendly, conversational, and interactive.** This is a setup wizard, not a reference manual.

- **Detect the user's language** from their first message. If they write in Chinese, Japanese, Spanish, etc., respond in that language throughout the entire setup. All explanations, questions, and celebrations should be in their language. Only keep commands, code blocks, URLs, and env variable names in English (those are technical and must stay as-is).
- Go **one step at a time**. Don't dump all steps at once.
- **Ask before proceeding** to the next step. Confirm the previous step worked.
- Use the **AskQuestion tool** for structured choices when available (client selection, research areas, etc.).
- **Explain briefly** what each step does and why, in plain language.
- When something goes wrong, be reassuring and help troubleshoot before moving on.
- **Celebrate small wins** -- when uv installs successfully, when the MCP server appears, when the first tool call works.

## Internal Notes (do not show to user)

⚠️ **ToolUniverse has 1200+ tools** which will cause context window overflow if all exposed directly. The default `tooluniverse` command already enables compact mode automatically.

**Compact mode** exposes only 5 core tools (list_tools, grep_tools, get_tool_info, execute_tool, find_tools) while keeping all 1200+ tools accessible via execute_tool.

**This skill's own URL** (for bootstrapping — see Step 0):
`https://raw.githubusercontent.com/mims-harvard/ToolUniverse/main/skills/setup-tooluniverse/SKILL.md`

## Step 0: Auto-Detect & Quick Start

Start by welcoming the user. Then immediately run these detection commands **before asking any questions**:

```bash
# Detect installed client by checking config file presence
echo "=== Detecting your AI client ===" && \
  ([ -f ~/.cursor/mcp.json ] && echo "✅ Cursor detected") || true && \
  ([ -f ~/Library/Application\ Support/Claude/claude_desktop_config.json ] && echo "✅ Claude Desktop detected") || true && \
  ([ -f ~/.claude.json ] && echo "✅ Claude Code detected") || true && \
  ([ -f ~/.codeium/windsurf/mcp_config.json ] && echo "✅ Windsurf detected") || true && \
  ([ -f ~/.gemini/settings.json ] && echo "✅ Gemini CLI detected") || true && \
  ([ -f ~/.codex/config.toml ] && echo "✅ Codex CLI detected") || true && \
  ([ -f ~/.qwen/settings.json ] && echo "✅ Qwen Code detected") || true && \
  ([ -f opencode.json ] && echo "✅ OpenCode detected") || true && \
  echo "=== Detection complete ==="
```

Based on results:
- **One client detected**: Tell the user "I can see you're using [Client]. I'll set up ToolUniverse for that." Skip Question 1.
- **Multiple detected**: Ask "I see you have Cursor and Windsurf. Which one should I configure?"
- **None detected**: Ask Question 1 below.

**Question 1 (only if not auto-detected): Which app are you using?**

Use AskQuestion if available:
- Cursor
- Claude Desktop
- VS Code / Copilot
- Windsurf
- Claude Code
- Gemini CLI
- Qwen Code
- Codex (OpenAI)
- Cline
- Trae
- Antigravity
- OpenCode
- Other

---

**Bootstrap check for terminal-based clients:**

If the user is on a terminal-based client (OpenCode, Gemini CLI, Codex CLI, Claude Code) and mentions they found this guide from the README or docs — not from a skill already running inside their client — give them this one-liner to paste directly into their client instead:

```
Please read https://raw.githubusercontent.com/mims-harvard/ToolUniverse/main/skills/setup-tooluniverse/SKILL.md and follow it to help me set up ToolUniverse.
```

After they paste that into their client, your job here is done.

---

**Quick Start mode (offer this before Question 2):**

Ask: "Would you like a **quick start** (I'll use defaults and get you running in 2 minutes) or a **full setup** (where I walk you through API keys and options)?"

- **Quick start**: Skip API key questions (Step 4). Just do Steps 1–3, then Step 5 (test). Tell the user they can always run "setup tooluniverse" again later to add API keys.
- **Full setup**: Continue with all steps including API keys.

---

**Question 2: How will you use ToolUniverse?**
- **MCP server** (use scientific tools through chat) -- this is the default for most users
- **Python coding** (write scripts that `import tooluniverse`) -- also needs pip install

For MCP-only users, only `uv` is needed. `uvx` automatically installs and runs ToolUniverse.

For coding use, also ask about Python version (`python3 --version`, needs >=3.10, <3.14).

## Installation Workflow

### Step 1: Make sure uv is installed

Run this check first — **skip the install entirely if uv is already present**:

```bash
which uv && uv --version || echo "NOT_INSTALLED"
```

- **If uv is found**: Say "✅ uv is already installed (version X.X.X) — skipping this step." and go straight to Step 2.
- **If NOT_INSTALLED**: Explain that `uv` is a fast package manager that makes MCP setup simple, then install it:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.zshrc 2>/dev/null || source ~/.bashrc 2>/dev/null

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify it worked: `uvx --version` — if this prints a version number, move on.

### Step 2: Add ToolUniverse to your MCP config

**First, check if the config file already exists:**

```bash
# Replace <CONFIG_PATH> with the path for the detected client (see table below)
cat <CONFIG_PATH> 2>/dev/null || echo "CONFIG_NOT_FOUND"
```

- **CONFIG_NOT_FOUND**: Create the file with the config below — proceed normally.
- **File exists but no `tooluniverse` entry**: Say "I see you already have an MCP config. I'll add ToolUniverse to it." Merge the `tooluniverse` block into the existing `mcpServers` object.
- **File exists and already has `tooluniverse`**: Ask "ToolUniverse is already configured. Skip this step, or overwrite with the latest config?"

---

Now we'll add ToolUniverse to your app's MCP configuration. Based on the client the user chose in Step 0, help them find and edit the right config file. All clients use the same server config -- only the file location differs.

#### MCP Server Configuration (same for all clients)

**Default method: Using uvx (Recommended)**
```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "uvx",
      "args": ["tooluniverse"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

`uvx tooluniverse` automatically installs and runs ToolUniverse with compact mode enabled by default (the `tooluniverse` entry point enables `--compact-mode` automatically). No separate `pip install` step required.

**Alternative: Using a pre-installed command** (if user already has ToolUniverse installed via pip)
```json
{
  "mcpServers": {
    "tooluniverse": {
      "command": "tooluniverse",
      "args": [],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

#### Config File Locations by Client

| Client | Config File (macOS) | How to Access |
|--------|-------------------|---------------|
| **Cursor** | `~/.cursor/mcp.json` | Settings → MCP → Add new global MCP server |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` | Settings → Developer → Edit Config |
| **Claude Code** | `~/.claude.json` (user) or `.mcp.json` (project) | `claude mcp add` CLI or edit directly |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` | MCPs icon in Cascade panel → or Windsurf Settings → Cascade → MCP Servers |
| **VS Code (Copilot)** | `.vscode/mcp.json` (workspace) or user profile `mcp.json` | Cmd Palette → "MCP: Add Server" (see different format below) |
| **Cline** | `cline_mcp_settings.json` (in VS Code extension globalStorage) | MCP Servers icon in top nav → Configure tab → Configure MCP Servers |
| **Codex (OpenAI)** | `~/.codex/config.toml` | `codex mcp add` CLI or edit manually (TOML format, see below) |
| **Gemini CLI** | `~/.gemini/settings.json` (user) or `.gemini/settings.json` (project) | Edit directly |
| **Qwen Code** | `~/.qwen/settings.json` (user) or `.qwen/settings.json` (project) | Edit directly |
| **Antigravity** | `mcp_config.json` | "..." menu at top of Agent panel → MCP Servers → Manage MCP Servers → View raw config |
| **Trae** | `.trae/mcp.json` (project) or global via Trae UI | Ctrl+U → AI Management → MCP → Configure Manually |
| **OpenCode** | `opencode.json` (project) or global config | `opencode mcp add` CLI or edit directly |

**Windows/Linux paths differ** -- check your client's documentation for the exact location.

Most clients use the same JSON `mcpServers` format shown above. **Exceptions**: VS Code uses `"servers"` key, Codex uses TOML, and OpenCode uses a `"mcp"` key -- see below for their specific formats.

#### Clients with Different Config Formats

**VS Code (Copilot)** -- uses `"servers"` key (not `"mcpServers"`) and requires `"type"` field. Add to `.vscode/mcp.json`:
```json
{
  "servers": {
    "tooluniverse": {
      "type": "stdio",
      "command": "uvx",
      "args": ["tooluniverse"],
      "env": { "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```

**Codex (TOML format)** -- one-liner CLI (quickest):
```bash
codex mcp add tooluniverse -- uvx tooluniverse
```

Or add manually to `~/.codex/config.toml`:
```toml
[mcp_servers.tooluniverse]
command = "uvx"
args = ["tooluniverse"]

[mcp_servers.tooluniverse.env]
PYTHONIOENCODING = "utf-8"
```

**OpenCode** -- uses `mcp` key with `type` and `command` as array in `opencode.json`:
```json
{
  "mcp": {
    "tooluniverse": {
      "type": "local",
      "command": ["uvx", "tooluniverse"],
      "enabled": true,
      "environment": { "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```

### Step 3 (Only if user chose coding use): Install Python package

Skip this if the user only needs MCP. For coding use, install into their Python environment:

```bash
pip install tooluniverse
```

Then verify together:
```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
print(f"ToolUniverse version: {tu.__version__}")
```

Let them know this is separate from the MCP server -- `uvx` installs into uv's cache, while `pip install` puts it in their Python environment for importing.

### Step 4: Set up API Keys

Many tools work without API keys, but some unlock powerful features. Before diving into keys, **ask the user about their research interests** to recommend only what's relevant.

Read [API_KEYS_REFERENCE.md](API_KEYS_REFERENCE.md) for detailed per-key info (what it does, step-by-step registration, which tools need it).

#### How to guide API key setup

1. **Ask the user** what research areas they're interested in. Use AskQuestion if available with options like:
   - Literature search & publications
   - Drug discovery & pharmacology
   - Protein structure & interactions
   - Genomics & disease associations
   - Rare diseases & clinical
   - Enzymology & biochemistry
   - Patent search
   - AI-powered analysis (needs LLM key)
   - All of the above
   - Not sure yet / skip for now

2. **Map their answer to recommended keys** using the tiers below. Don't overwhelm -- suggest 2-4 keys to start.

3. **Walk through each key one at a time**:
   - Explain in plain language what it unlocks (e.g., "This lets you search PubMed faster")
   - Give them the registration link
   - Wait for them to sign up and get the key
   - Help them add it to their config file
   - Move to the next key

4. **After all keys are added**, restart the app and test one key with a real tool call.

5. Let them know they can always come back to add more keys later.

#### Tier 1: Core Scientific Keys (Recommended for most users)

| Key | Service | What It Unlocks | Free? | Registration |
|-----|---------|----------------|-------|-------------|
| `NCBI_API_KEY` | NCBI/PubMed | PubMed literature search (raises rate limit 3->10 req/s) | Yes | https://account.ncbi.nlm.nih.gov/settings/ |
| `NVIDIA_API_KEY` | NVIDIA NIM | 16 tools: AlphaFold2 structure prediction, molecular docking, genomics | Yes | https://build.nvidia.com |
| `BIOGRID_API_KEY` | BioGRID | Protein-protein interaction queries | Yes | https://webservice.thebiogrid.org/ |
| `DISGENET_API_KEY` | DisGeNET | 5 gene-disease association tools | Yes (academic) | https://disgenet.com/academic-apply |

#### Tier 2: Specialized Scientific Keys (Based on research needs)

| Key | Service | What It Unlocks | Free? | Registration |
|-----|---------|----------------|-------|-------------|
| `OMIM_API_KEY` | OMIM | 4 Mendelian/rare disease tools | Yes | https://omim.org/api |
| `ONCOKB_API_TOKEN` | OncoKB | Precision oncology annotations | Yes (academic) | https://www.oncokb.org/apiAccess |
| `UMLS_API_KEY` | UMLS/NLM | 5 medical terminology & concept mapping tools | Yes | https://uts.nlm.nih.gov/uts/ |
| `USPTO_API_KEY` | USPTO | 6 patent search & analysis tools | Yes | https://account.uspto.gov/api-manager/ |
| `SEMANTIC_SCHOLAR_API_KEY` | Semantic Scholar | Literature search (raises rate limit 1->100 req/s) | Yes | https://www.semanticscholar.org/product/api |
| `FDA_API_KEY` | openFDA | Drug/food/device adverse event queries (raises limit 240->1000 req/min) | Yes | https://open.fda.gov/apis/authentication/ |
| `BRENDA_EMAIL` + `BRENDA_PASSWORD` | BRENDA | 3 enzyme database tools (both email and password required) | Yes | https://brenda-enzymes.org/register.php |
| `MOUSER_API_KEY` | Mouser Electronics | 4 electronic component search tools (ICs, resistors, capacitors, etc.) | Yes | https://www.mouser.com/api-search/ |
| `DIGIKEY_CLIENT_ID` + `DIGIKEY_CLIENT_SECRET` | Digi-Key Electronics | 4 component search tools with parametric search (both ID and secret required) | Yes | https://developer.digikey.com/ |

#### Tier 3: LLM Provider Keys (For agentic tool features)

At least **one** LLM key is needed for agentic features. The system tries providers in order: Azure OpenAI -> OpenRouter -> Gemini.

| Key | Service | What It Unlocks | Free Tier? | Registration |
|-----|---------|----------------|-----------|-------------|
| `GEMINI_API_KEY` | Google Gemini | Agentic tools via Gemini (good free tier) | Yes | https://aistudio.google.com/apikey |
| `OPENROUTER_API_KEY` | OpenRouter | Agentic tools via 100+ LLM models | Pay-per-use | https://openrouter.ai/ |
| `OPENAI_API_KEY` | OpenAI | Embedding features, LLM-based tool finding | Pay-per-use | https://platform.openai.com/ |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI | Agentic tools via Azure (enterprise) | Pay-per-use | Azure Portal |
| `ANTHROPIC_API_KEY` | Anthropic Claude | Claude-based features | Pay-per-use | https://console.anthropic.com/ |
| `HF_TOKEN` | HuggingFace | Model/dataset access, HF Inference API | Yes | https://huggingface.co/settings/tokens |

#### Adding Keys to Configuration

**Best approach: Add to the `env` block in your MCP config file** (the same file from Step 2). This way keys are passed directly to the MCP server:

```json
"env": {
  "PYTHONIOENCODING": "utf-8",
  "NCBI_API_KEY": "your_key_here",
  "NVIDIA_API_KEY": "your_key_here"
}
```

**Alternative**: Create a `.env` file in your project directory with `KEY=value` pairs.

**After adding keys**: Restart the app for changes to take effect.

#### Verify keys work

Test each configured key with a real tool call:
- `NCBI_API_KEY` -> `execute_tool("PubMed_search_articles", {"query": "CRISPR", "max_results": 1})`
- `NVIDIA_API_KEY` -> `execute_tool("NvidiaNIM_alphafold2_predict", {"sequence": "MKTVRQERLKS"})`
- `BIOGRID_API_KEY` -> `execute_tool("BioGRID_get_interactions", {"geneList": "TP53", "taxId": 9606})`
- `MOUSER_API_KEY` -> `execute_tool("Mouser_search_by_part_number", {"part_number": "STM32F103C8T6"})`
- `DIGIKEY_CLIENT_ID` + `DIGIKEY_CLIENT_SECRET` -> `execute_tool("DigiKey_search_by_keyword", {"keywords": "STM32"})`

### Step 5: Test & Status Check

Ask the user to restart their app, then run through this checklist together. For each item, run the diagnostic command and report ✅ or ❌.

```bash
# 1. Is uv installed?
uvx --version && echo "✅ uv/uvx installed" || echo "❌ uv not found"

# 2. Does ToolUniverse start cleanly?
timeout 5 uvx tooluniverse --help > /dev/null 2>&1 && echo "✅ ToolUniverse starts OK" || echo "❌ ToolUniverse failed to start"

# 3. Does the config file exist?
# (replace path for your client)
[ -f ~/.cursor/mcp.json ] && echo "✅ MCP config exists" || echo "❌ Config file not found"

# 4. Does the config contain tooluniverse?
grep -q "tooluniverse" ~/.cursor/mcp.json 2>/dev/null && echo "✅ tooluniverse in config" || echo "❌ tooluniverse missing from config"
```

After the restart, **show the user this status summary** and fill in each line:

```
Setup Status
─────────────────────────────────────
✅/❌  uv installed         (version: ___)
✅/❌  ToolUniverse starts
✅/❌  MCP config created
✅/❌  Server visible in [client]
✅/❌  Test tool call works
⬜     API keys (optional — add anytime)
─────────────────────────────────────
```

**Run a live test call** to confirm the server is responding (suggest based on their research interests):
- General: `list_tools` or `grep_tools` with keyword "protein"
- Literature: `execute_tool("PubMed_search_articles", {"query": "CRISPR", "max_results": 1})`
- Drug discovery: `execute_tool("ChEMBL_search_compound", {"query": "aspirin"})`

If all items are ✅, celebrate! 🎉 Move to Step 6. If any are ❌, jump to the matching issue in Common Issues & Solutions below.

### Step 6: Install ToolUniverse Skills (Auto-Detected & Highly Recommended)

Invoke the `tooluniverse-install-skills` skill — it handles detection and installation automatically.

- **If skills are already installed**: it will say so; skip to What's Next.
- **If NOT installed**: it will install them from GitHub and confirm.

Skills are pre-built research workflows that turn basic tool calls into expert-level investigations. Explain to the user: "ToolUniverse comes with 65+ research skills that act like expert guides — each one knows exactly which of the 1200+ tools to call, in what order, to build a complete research report."

#### Available Skills

| Skill | What It Does |
|-------|-------------|
| `tooluniverse` | General strategies for using 1200+ tools effectively |
| `tooluniverse-drug-research` | Comprehensive drug profiling (identity, pharmacology, safety, ADMET) |
| `tooluniverse-target-research` | Drug target intelligence (structure, interactions, druggability) |
| `tooluniverse-disease-research` | Systematic disease analysis across 10 research dimensions |
| `tooluniverse-literature-deep-research` | Thorough literature reviews with evidence grading |
| `tooluniverse-drug-repurposing` | Find new therapeutic uses for existing drugs |
| `tooluniverse-precision-oncology` | Mutation-based treatment recommendations for cancer |
| `tooluniverse-rare-disease-diagnosis` | Phenotype-to-diagnosis for suspected rare diseases |
| `tooluniverse-pharmacovigilance` | Drug safety signal analysis from FDA adverse event data |
| `tooluniverse-infectious-disease` | Rapid pathogen characterization & drug repurposing |
| `tooluniverse-protein-structure-retrieval` | Protein 3D structure retrieval & quality assessment |
| `tooluniverse-sequence-retrieval` | DNA/RNA/protein sequence retrieval from NCBI/ENA |
| `tooluniverse-chemical-compound-retrieval` | Chemical compound data from PubChem/ChEMBL |
| `tooluniverse-expression-data-retrieval` | Gene expression & omics datasets |
| `tooluniverse-variant-interpretation` | Genetic variant clinical interpretation |
| `tooluniverse-variant-analysis` | Genomic variant analysis workflows |
| `tooluniverse-protein-therapeutic-design` | AI-guided protein therapeutic design |
| `tooluniverse-binder-discovery` | Small molecule binder discovery via virtual screening |
| `tooluniverse-sdk` | Build research pipelines with the Python SDK |
| `tooluniverse-adverse-event-detection` | Drug adverse event signal detection |
| `tooluniverse-antibody-engineering` | Antibody design and optimization |
| `tooluniverse-cancer-variant-interpretation` | Cancer somatic variant clinical interpretation |
| `tooluniverse-chemical-safety` | Chemical safety and toxicity assessment |
| `tooluniverse-clinical-guidelines` | Clinical guideline retrieval and synthesis |
| `tooluniverse-clinical-trial-design` | Clinical trial design and protocol analysis |
| `tooluniverse-clinical-trial-matching` | Patient-to-trial matching based on eligibility |
| `tooluniverse-crispr-screen-analysis` | CRISPR screen hit identification and analysis |
| `tooluniverse-drug-drug-interaction` | Drug-drug interaction analysis |
| `tooluniverse-drug-target-validation` | Target validation for drug discovery |
| `tooluniverse-epigenomics` | Epigenomic data analysis (ChIP-seq, ATAC-seq) |
| `tooluniverse-gene-enrichment` | Gene set enrichment and pathway analysis |
| `tooluniverse-gwas-drug-discovery` | GWAS-driven drug target discovery |
| `tooluniverse-gwas-finemapping` | GWAS fine-mapping to causal variants |
| `tooluniverse-gwas-snp-interpretation` | GWAS SNP functional interpretation |
| `tooluniverse-gwas-study-explorer` | GWAS study discovery and comparison |
| `tooluniverse-gwas-trait-to-gene` | Trait-to-gene mapping from GWAS |
| `tooluniverse-image-analysis` | Biomedical image analysis workflows |
| `tooluniverse-immune-repertoire-analysis` | Immune repertoire (BCR/TCR) analysis |
| `tooluniverse-immunotherapy-response-prediction` | Immunotherapy response biomarker analysis |
| `tooluniverse-metabolomics` | Metabolomics data analysis and annotation |
| `tooluniverse-metabolomics-analysis` | Advanced metabolomics pathway analysis |
| `tooluniverse-multi-omics-integration` | Multi-omics data integration workflows |
| `tooluniverse-multiomic-disease-characterization` | Disease characterization across omics layers |
| `tooluniverse-network-pharmacology` | Network-based drug-target-disease analysis |
| `tooluniverse-phylogenetics` | Phylogenetic analysis and tree building |
| `tooluniverse-polygenic-risk-score` | Polygenic risk score calculation and interpretation |
| `tooluniverse-precision-medicine-stratification` | Patient stratification for precision medicine |
| `tooluniverse-protein-interactions` | Protein-protein interaction network analysis |
| `tooluniverse-proteomics-analysis` | Proteomics data analysis and interpretation |
| `tooluniverse-rnaseq-deseq2` | RNA-seq differential expression with DESeq2 |
| `tooluniverse-single-cell` | Single-cell RNA-seq analysis workflows |
| `tooluniverse-spatial-omics-analysis` | Spatial omics data analysis |
| `tooluniverse-spatial-transcriptomics` | Spatial transcriptomics analysis |
| `tooluniverse-statistical-modeling` | Statistical modeling for biological data |
| `tooluniverse-structural-variant-analysis` | Structural variant detection and annotation |
| `tooluniverse-systems-biology` | Systems biology network modeling |
| `setup-tooluniverse` | This setup guide |

#### How to Install Skills

**Option A — Ask the user to run this in their terminal:**

```bash
npx skills add mims-harvard/ToolUniverse
```

This auto-detects the client and installs skills into the correct directory. The user must run it themselves — ask them to open a terminal, navigate to their project root, and run the command. Wait for them to confirm it completed successfully.

**Option B — Agent installs directly** (use this if you have shell/terminal access):

```bash
# Download skills folder from GitHub
git clone --depth 1 --filter=blob:none --sparse https://github.com/mims-harvard/ToolUniverse.git /tmp/tu-skills
cd /tmp/tu-skills && git sparse-checkout set skills
```

Then copy to the correct directory based on the user's client:

| Client | Skills Directory |
|--------|----------------|
| **Cursor** | `.cursor/skills/` |
| **Windsurf** | `.windsurf/skills/` |
| **Claude Code** | `.claude/skills/` |
| **Gemini CLI** | `.gemini/skills/` |
| **Qwen Code** | `.qwen/skills/` |
| **Codex (OpenAI)** | `.agents/skills/` |
| **OpenCode** | `.opencode/skills/` |
| **Trae** | `.trae/skills/` |
| **Cline / VS Code** | `.skills/` (reference as needed) |

```bash
# Example for Cursor:
mkdir -p .cursor/skills && cp -r /tmp/tu-skills/skills/* .cursor/skills/
rm -rf /tmp/tu-skills
```

#### How to Use Skills

Explain to the user:
- Skills activate automatically when the AI detects a relevant request
- The user can also trigger them explicitly, e.g., "Research the drug aspirin" will activate the drug-research skill
- Skills guide the AI through multi-step research workflows, calling the right tools in the right order
- The output is typically a comprehensive research report with evidence grading and source citations

**Suggest a skill to try** based on their research interests from Step 4. For example:
- "Try asking: 'Research the drug metformin' -- the drug-research skill will generate a full drug profile"
- "Try asking: 'What does the literature say about CRISPR in cancer?' -- the literature-deep-research skill will do a thorough review"

## Common Issues & Solutions

When something fails, always provide the **exact copy-paste fix command** — don't just say "check the logs."

### Issue 1: Python Version Incompatibility

**Symptom**: Error containing `requires-python = ">=3.10"` or `Python 3.9 is not supported`

**Fix** (copy-paste):
```bash
brew install python@3.12        # macOS
# or: sudo apt install python3.12  # Ubuntu/Debian
python3.12 -m pip install tooluniverse
```

### Issue 2: uvx or uv Not Found

**Symptom**: `uvx: command not found` or `uv: command not found`

**Fix** (copy-paste):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc 2>/dev/null || source ~/.bashrc 2>/dev/null
uvx --version   # verify it worked
```

### Issue 3: Context Window Overflow

**Symptom**: MCP server loads but the client becomes very slow, or gives "context too large" errors

**Fix** (compact mode is already the default, but if needed explicitly):
```json
"args": ["tooluniverse", "--compact-mode"]
```
Or to narrow further to specific tool categories:
```json
"args": ["tooluniverse", "--tool-categories", "uniprot,chembl,pubmed"]
```
Restart the app after editing.

### Issue 4: Import Errors for Specific Tools

**Symptom**: Tool fails with `ModuleNotFoundError: No module named 'rdkit'` (or similar)

**Fix** (copy-paste for most missing deps):
```bash
pip install tooluniverse[all]
# Or just the specific extra needed:
# pip install tooluniverse[visualization]   # rdkit, py3Dmol
# pip install tooluniverse[singlecell]       # cellxgene
# pip install tooluniverse[ml,embedding]     # sentence-transformers, admet-ai
```

### Issue 5: MCP Server Won't Start

**Symptom**: No tooluniverse server appears in the client's server list

**Diagnostic — run these in order, stop at the first failure:**
```bash
# 1. Can uvx find and run it?
uvx tooluniverse --help

# 2. Does it start without errors? (Ctrl+C to stop)
uvx tooluniverse

# 3. Is the config file valid JSON?
python3 -m json.tool ~/.cursor/mcp.json   # replace path for your client

# 4. View the client's MCP logs
tail -50 ~/Library/Logs/Claude/mcp*.log 2>/dev/null   # Claude Desktop (macOS)
ls ~/Library/Application\ Support/Cursor/logs/         # Cursor (macOS)
```

Fix based on where the chain breaks. Common causes: trailing commas in JSON, wrong config file path, `uvx` not on PATH when the app launches.

### Issue 6: API Key Errors (401/403)

**Symptom**: Tool returns `"unauthorized"`, `"forbidden"`, or `"invalid API key"`

**Diagnostic — run this to check what keys are actually visible to the server:**
```bash
# Confirm the key is set in your shell environment
echo $NCBI_API_KEY    # replace with the failing key name
```

**Common fixes**:
```bash
# Wrong: key is in .env file but app doesn't load it
# Right: add the key directly to the "env" block in your MCP config file:
# "env": { "PYTHONIOENCODING": "utf-8", "NCBI_API_KEY": "your_key_here" }
```
- **Wrong key name**: variable must match exactly (e.g., `ONCOKB_API_TOKEN` not `ONCOKB_API_KEY`)
- **Restart required**: after editing the config file, fully restart the app
- **Free tier pending**: DisGeNET and OMIM may take 24–48h for account approval

### Issue 7: Upgrading ToolUniverse

**Symptom**: User wants a newer version, or tools are missing / behavior is outdated

**Fix** (copy-paste):
```bash
uv cache clean tooluniverse   # clears uvx cache
# then restart the MCP client — uvx will download the latest version
```

To pin a specific version in the config:
```json
"args": ["tooluniverse==1.0.19"]
```

For pip users:
```bash
pip install --upgrade tooluniverse
```

### Still stuck?

Run `uvx tooluniverse --help` and share the output. Then open a GitHub issue at https://github.com/mims-harvard/ToolUniverse/issues or reach out to [Shanghua Gao](mailto:shanghuagao@gmail.com), the creator of ToolUniverse.

## What's Next?

After setup is complete, suggest the user try one of these to get started:

- **"Research the drug metformin"** -- triggers the drug-research skill for a full drug profile
- **"What are the known targets of imatinib?"** -- triggers target-research
- **"What does the literature say about CRISPR in sickle cell disease?"** -- triggers literature-deep-research
- **"Find protein structures for human EGFR"** -- triggers protein-structure-retrieval

Point them to the **`tooluniverse` general skill** for tips on getting the most out of 1200+ tools, and remind them they can always come back to add more API keys or skills later.

## Quick Reference

- **Instant setup (bootstrap)**: Open your agent and say: `Please read https://raw.githubusercontent.com/mims-harvard/ToolUniverse/main/skills/setup-tooluniverse/SKILL.md and follow it to help me set up ToolUniverse.`
- **Default setup**: `uvx tooluniverse` -- auto-installs, auto-enables compact mode
- **Upgrade**: `uv cache clean tooluniverse` then restart the app
- **First load**: May take 30-60 seconds (downloads + installs); subsequent loads are fast
- **All scientific API keys are free** to obtain
- **Agentic features** need at least one LLM key (Gemini has a good free tier)
- **Detailed API key docs**: [API_KEYS_REFERENCE.md](API_KEYS_REFERENCE.md)
- **Skills repo**: https://github.com/mims-harvard/ToolUniverse/tree/main/skills
- **Need help?** Open a [GitHub issue](https://github.com/mims-harvard/ToolUniverse/issues) or email [Shanghua Gao](mailto:shanghuagao@gmail.com)
