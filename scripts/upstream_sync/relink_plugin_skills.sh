#!/bin/bash
# Rebuild plugin/skills as symlinks-only: union of origin's and upstream's entries,
# each pointing at ../../skills/<name> (the convention PR #76 established on origin).
set -euo pipefail
names=$( { git ls-tree --name-only HEAD plugin/skills/; git ls-tree --name-only upstream/main plugin/skills/; } \
         | sed 's#^plugin/skills/##' | sort -u )
kept=""
for n in $names; do
  if [ -d "skills/$n" ]; then kept="$kept $n"; else echo "drop (no skills/$n; dangling on origin too)"; fi
done
names=$(echo "$kept" | tr ' ' '\n')
git rm -r -q --cached plugin/skills
rm -rf plugin/skills
mkdir -p plugin/skills
for n in $names; do ln -s "../../skills/$n" "plugin/skills/$n"; done
git add plugin/skills
echo "entries: $(echo "$names" | wc -l)  origin: $(git ls-tree --name-only HEAD plugin/skills/ | wc -l)  upstream: $(git ls-tree --name-only upstream/main plugin/skills/ | wc -l)"
echo "non-symlink entries: $(find plugin/skills -mindepth 1 -maxdepth 1 ! -type l | wc -l)"
echo "dangling: $(find -L plugin/skills -mindepth 1 -maxdepth 1 -type l | wc -l)"
