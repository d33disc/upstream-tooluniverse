"""Write <ref>:tests/ into <dest>/tests, bypassing export-ignore. Usage: export_tests.py <ref> <dest>"""

import pathlib
import subprocess
import sys

ref, dest = sys.argv[1:3]
names = subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", ref, "tests"],
    capture_output=True,
    text=True,
    check=True,
).stdout.split("\n")
names = [n for n in names if n]
batch = subprocess.run(
    ["git", "cat-file", "--batch"],
    input="".join(f"{ref}:{n}\n" for n in names).encode(),
    capture_output=True,
    check=True,
).stdout
pos = 0
for n in names:
    header_end = batch.index(b"\n", pos)
    size = int(batch[pos:header_end].split()[2])
    body = batch[header_end + 1 : header_end + 1 + size]
    pos = header_end + 1 + size + 1
    out = pathlib.Path(dest) / n
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body)
print(f"{ref}: wrote {len(names)} test files")
