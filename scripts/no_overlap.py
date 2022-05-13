#!/usr/bin/env python3

import sys

filename = sys.argv[1]
delimiter = "," if filename.endswith(".csv") else "\t"

data = set()
with open(filename, 'r', encoding="utf-8") as f:
    for line in f:
        fields = line.strip().split(delimiter)
        cat = fields[1]
        word = fields[2]
        if word and cat != "eigennaam":
            print(word.lower(), file=sys.stderr)
            data.add(word.lower())

print(f"read {len(data)} items", file=sys.stderr)

# always tsv
for line in sys.stdin:
    fields = line.strip("\n").split("\t")
    if fields[0].lower() not in data:
        print(line, end="")
