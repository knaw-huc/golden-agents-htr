#!/usr/bin/env python3

"""Extract data from INT Historical Lexicon into a (weighted) variant list usable with analiticcl"""

import sys
from collections import defaultdict

FIELD_TYPE = 0
FIELD_LEMMA = 4
FIELD_FORM = 6

data = defaultdict(set)
freqlist = defaultdict(int)

if len(sys.argv) != 3:
    print("Usage: inthistlex2variantlist.py int_historisch_lexicon.tsv freqlist.tsv",file=sys.stderr)

with open(sys.argv[1],'r',encoding='utf-8') as f:
    for line in f:
        if line:
            fields = line.split("\t")
            if fields[FIELD_TYPE] == "simple":
                    data[fields[FIELD_LEMMA]].add(fields[FIELD_FORM])

with open(sys.argv[2],'r',encoding='utf-8') as f:
    for line in f:
        if line:
            line = line.strip()
            freqlist[line] += 1

for key, forms in sorted(data.items()):
    for keypart in key.split("|"):
        print(f"{keypart}", end="")
        if forms:
            for form in sorted([form for form in forms if form != keypart]):
                freq = freqlist[form]
                if freq == 0: freq = 1
                print(f"\t{form}\t1.0\t{freq}", end="")
            print()


