"""Resolve diff3 conflict hunks in a file, keeping all non-conflicting merged text.

Usage: hunks.py <file> <choices>   choices: one letter per hunk, o=ours t=theirs
       b=both (ours then theirs), or a single letter applied to every hunk.
       hunks.py <file> show        prints each hunk numbered.
"""

import re
import sys

path, choice = sys.argv[1], sys.argv[2]
text = open(path).read()
pat = re.compile(
    r"^<<<<<<< [^\n]*\n(.*?)^\|\|\|\|\|\|\| [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n",
    re.S | re.M,
)
hunks = list(pat.finditer(text))
if choice == "show":
    for i, m in enumerate(hunks):
        print(
            f"### hunk {i} OURS\n{m.group(1)}### BASE\n{m.group(2)}### THEIRS\n{m.group(3)}"
        )
    sys.exit()
choices = choice * len(hunks) if len(choice) == 1 else choice
assert len(choices) == len(hunks), f"{len(hunks)} hunks, got {len(choices)} choices"
it = iter(choices)


def pick(m):
    c = next(it)
    return {"o": m.group(1), "t": m.group(3), "b": m.group(1) + m.group(3)}[c]


out = pat.sub(pick, text)
assert "<<<<<<<" not in out and ">>>>>>>" not in out
open(path, "w").write(out)
print(f"{path}: resolved {len(hunks)} hunks as {choices}")
