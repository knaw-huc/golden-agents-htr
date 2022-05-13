#!/usr/bin/env python3

"""
Enrich a variant list with frequency information
"""

import sys
from collections import defaultdict
from itertools import pairwise

FIELD_TYPE = 0
FIELD_LEMMA = 4
FIELD_FORM = 6

variantlist = defaultdict(dict)
freqlist = defaultdict(int)

if len(sys.argv) != 3:
    print("Usage: inthistlex2variantlist.py int_historisch_lexicon.tsv freqlist.tsv", file=sys.stderr)


def pairs(iterator):
    skip = False
    for pair in pairwise(iterator):
        if skip:
            skip = False
        else:
            yield pair
            skip = True


with open(sys.argv[1], 'r', encoding='utf-8') as f:
    for line in f:
        if line:
            fields = line.split("\t")
            variantlist[fields[0]] = {k: float(v) for k, v in pairs(fields[1:])}

with open(sys.argv[2], 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            key, freq = line.split("\t")
            freqlist[key] = max(freqlist[key], int(freq))

for key, forms in sorted(variantlist.items()):
    freq = freqlist[key]
    if freq == 0: freq = 1
    print(f"{key}\t{freq}", end="")
    if forms:
        for form, score in sorted(forms.items()):
            if form != key:
                freq = freqlist[form]
                if freq == 0: freq = 1
                print(f"\t{form}\t{score}\t{freq}", end="")
    print()
