#!/usr/bin/env python3

"""Merges lines in a TSV file that have the same value in the first column, outputs sorted by first columns and removes duplicates"""

import sys

data = {}

for line in sys.stdin:
    line = line.strip()
    fields = line.split("\t")
    if fields[0] in data:
        data[fields[0]] += fields[1:]
    else:
        data[fields[0]] = fields[1:]

for key, values in sorted(data.items()):
    print(f"{key}\t" + "\t".join(sorted(set(values))))
