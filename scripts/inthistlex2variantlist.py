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

formcount = defaultdict(int) #for how many keys does each form occur? (used to compute mapping probability)
for key, forms in data.items():
    for form in forms:
        formcount[form] += 1

if len(sys.argv) >= 3:
    with open(sys.argv[2],'r',encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                key, freq = line.split("\t")
                freqlist[key] = max(freqlist[key], int(freq))

for key, forms in sorted(data.items()):
    for keypart in key.split("|"):
        freq = freqlist[keypart]
        if freq == 0: freq = 1
        print(f"{keypart}\t{freq}", end="")
        if forms:
            for form in sorted([form for form in forms if form != keypart]):
                freq = freqlist[form]
                if freq == 0: freq = 1
                p = 1.0 / formcount[form] #deliberately kept independent from frequency information!
                print(f"\t{form}\t{p}\t{freq}", end="")
            print()


