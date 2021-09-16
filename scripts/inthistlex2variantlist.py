#!/usr/bin/env python3

"""Extract data from INT Historical Lexicon into a (weighted) variant list usable with analiticcl"""

import sys
from collections import defaultdict

FIELD_TYPE = 0
FIELD_LEMMA = 4
FIELD_FORM = 6

data = defaultdict(set)

with open(sys.argv[1],'r',encoding='utf-8') as f:
    for line in f:
        if line:
            fields = line.split("\t")
            if fields[FIELD_TYPE] == "simple":
                    data[fields[FIELD_LEMMA]].add(fields[FIELD_FORM])

for key, forms in sorted(data.items()):
    for keypart in key.split("|"):
        print(f"{keypart}", end="")
        if forms:
            for form in sorted([form for form in forms if form != keypart]):
                print(f"\t{form}\t1.0", end="")
            print()


