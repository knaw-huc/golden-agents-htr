#!/usr/bin/env python3

import sys
import os

terms = set()
with open(sys.argv[1], 'r', encoding="utf-8") as f:
    for line in f:
        terms.add(line.strip())
print(f"Loaded {len(terms)} terms...",file=sys.stderr)

count = 0
output = 0
skipped = set()
matches = set()
for line in sys.stdin:
    count += 1
    term = os.path.basename(line.strip()).replace(".xml","")
    if term in terms:
        matches.add(term)
        print(line.strip())
    else:
        skipped.add(term)
        print(f"No boedel type: {term}",file=sys.stderr)

missing = set()
for term in terms - skipped - skipped:
    missing.add(term)
    print(f"Missing: {term}",file=sys.stderr) #is a boedel type but is not in the data we have

with open("boedel.missing","w", encoding="utf-8") as f:
    for term in sorted(missing):
        print(term, file=f)
print(f"Processed {count} lines, matched {len(matches)}, mismatched {len(skipped)}, missing {len(missing)}...",file=sys.stderr)
    

