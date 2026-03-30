#!/bin/bash
# Commit script for Ralph Health batch 1
cd /Users/davis/code/ToolUniverse

# Commit schema fix
git add src/tooluniverse/data/pdbe_ligands_tools.json
git commit -m "fix(PDBe_get_residue_listing): add struct_asym_id to return_schema chains"

# Commit results
git add ralph-health/results_a6.json
git commit -m "health(a6): batch 1 — 17 pass, 10 fail, 3 timeout"

# Show status
git status
