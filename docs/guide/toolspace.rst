Space & Workspace
=================

**space.yaml** is how you configure ToolUniverse — which tools to load, how the cache behaves, LLM settings, and more. A **workspace** is a local folder (``.tooluniverse/``) where your space.yaml and API keys live, loaded automatically on every startup.

Quick Start
-----------

.. code-block:: bash

   mkdir .tooluniverse

   # API keys — never commit this file
   echo "OPENAI_API_KEY=sk-..." > .tooluniverse/.env

   # Tool config — safe to share
   cat > .tooluniverse/space.yaml << 'EOF'
   name: my-workspace
   version: "1.0"
   tools:
     categories: [literature, drug]
   EOF

   tooluniverse-smcp-stdio   # both files load automatically

Or load any space file on the fly:

.. code-block:: bash

   tooluniverse-smcp-stdio --load ./life-science.yaml
   tooluniverse-smcp-stdio --load "https://raw.githubusercontent.com/mims-harvard/ToolUniverse/main/examples/spaces/life-science.yaml"

---

space.yaml Reference
---------------------

.. code-block:: yaml

   name: my-space     # required
   version: "1.0"     # required
   description: "..."
   tags: [research, biology]

   # ── Tools ────────────────────────────────────────────────────────
   tools:
     categories: [literature, drug, gwas]   # load whole categories
     include_tools: [UniProt_search]         # add specific tools by name
     exclude_tools: [slow_tool]              # remove specific tools by name
     include_tool_types: [api]              # filter by type
     exclude_tool_types: [agentic]

   # ── Cache ────────────────────────────────────────────────────────
   cache:
     enabled: true        # default: true
     memory_size: 256     # LRU slots in memory, default: 256
     persist: true        # write to disk (SQLite), default: true
     ttl: 3600            # seconds before expiry; omit = cache forever

   # ── LLM (only needed for agentic tools) ─────────────────────────
   llm_config:
     default_provider: CHATGPT   # CHATGPT | GEMINI | OPENROUTER | VLLM
     models:
       default: gpt-4o
     temperature: 0.2

   # ── Hooks ────────────────────────────────────────────────────────
   hooks:
     - type: SummarizationHook
       enabled: true
       config:
         max_length: 500
     - type: FileSaveHook
       enabled: true
       config:
         output_dir: ./outputs

   # ── External sources ─────────────────────────────────────────────
   sources:
     - hf:community/genomics-tools
     - ./my-local-tools/

   # ── Inherit from another space ───────────────────────────────────
   extends: hf:community/base-bio-tools

   # ── Logging ──────────────────────────────────────────────────────
   log_level: WARNING   # DEBUG | INFO | WARNING | ERROR | CRITICAL

   # ── Document required keys (warns at startup if missing) ─────────
   required_env:
     - OPENAI_API_KEY

.. note::
   Put API key *values* in ``.tooluniverse/.env``, not in space.yaml.
   space.yaml is safe to commit; ``.env`` is not.

---

Workspace
---------

The workspace is a folder ToolUniverse watches on every startup.

**Layout:**

.. code-block:: text

   .tooluniverse/
   ├── .env         ← API keys (add to .gitignore)
   ├── space.yaml   ← auto-loaded on startup (seeded from defaults on first run)
   └── tools/       ← custom tool configs (JSON or Python)

**Local vs. global:**

.. code-block:: bash

   tooluniverse-smcp-stdio              # local:  ./.tooluniverse/
   tooluniverse-smcp-stdio --global     # global: ~/.tooluniverse/
   tooluniverse-smcp-stdio --workspace /path/to/ws   # explicit path

Priority (first match wins): ``--workspace`` → ``TOOLUNIVERSE_HOME`` env → ``--global`` → ``./.tooluniverse/``

**Merging:** when you ``--load`` a file, your workspace ``space.yaml`` is the base and the loaded file overrides only what it specifies.

.. code-block:: text

   .tooluniverse/space.yaml  (base defaults)
            +
   life-science.yaml         (overrides)
            =
   merged config that runs

**Python API:**

.. code-block:: python

   from tooluniverse import ToolUniverse

   tu = ToolUniverse()                         # local workspace (default)
   tu = ToolUniverse(use_global=True)          # global workspace
   tu = ToolUniverse(workspace="/path/to/ws")  # explicit path
   tu = ToolUniverse(space="./life-science.yaml")  # load + merge over workspace

---

Ready-made Space
----------------

`examples/spaces/life-science.yaml <https://github.com/mims-harvard/ToolUniverse/blob/main/examples/spaces/life-science.yaml>`_ — loads all life science and general-purpose tools organized by domain:

- **Proteins & Structure** — UniProt, RCSB PDB, AlphaFold, PDBe, InterPro, SWISS-MODEL, CATH, GPCRdb, BRENDA, SAbDab, and more
- **Genomics & Variants** — Ensembl, ClinVar, gnomAD, GWAS Catalog, ENCODE, GTEx, ClinGen, COSMIC, CIViC, UCSC, NCBI, and more
- **Drug Discovery** — Open Targets, ChEMBL, PubChem, FDA, DrugBank, PharmGKB, BindingDB, ZINC, ADMET AI, and more
- **Metabolomics** — HMDB, LIPID MAPS, MetaboLights, GNPS, MetaCyc, BiGG, Rhea, and more
- **Pathways & Ontologies** — Reactome, KEGG, WikiPathways, GO, Enrichr, OmniPath, MSigDB, HPO, MeSH, and more
- **Disease & Clinical** — OMIM, Orphanet, DisGeNET, Monarch, ClinicalTrials.gov, WHO, CDC, clinical guidelines, and more
- **Expression & Single-Cell** — GEO, ArrayExpress, Expression Atlas, Human Cell Atlas, CellxGene, MGnify, and more
- **Proteomics & Imaging** — PRIDE, IntAct, STRING, BioGRID, BioImage Archive, Cancer Imaging Archive, and more
- **Neuroscience** — Allen Brain Atlas, NeuroMorpho, NeuroVault, OpenNeuro, ModelDB, and more
- **Model Organisms** — SGD (yeast), WormBase, FlyBase, ZFIN, MouseMine, IMPC, Alliance Genome, and more
- **Biodiversity & Ecology** — GBIF, OBIS, iDigBio, iNaturalist, WoRMS, ITIS, EOL, Plants of the World, and more
- **Literature & Data** — PubMed, Europe PMC, arXiv, bioRxiv, Semantic Scholar, Zenodo, Dryad, and more
- **Software & Tools** — Bioconductor, CRAN, Bioinformatics/Genomics/ML software registries, and more
