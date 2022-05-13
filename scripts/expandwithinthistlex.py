#!/usr/bin/env python3

"""Expand boedeltermen with data from the INT historical lexicon.

The INT historical lexicon maps lemmas to observed word forms (in all diachronical variation).
Boedeltermen maps lemmas to normalized wordforms **and** observed word forms. Normalised wordforms
are therefore missing from the INT lexicon and the challenge is relating their observed forms back to
our normalised forms. We use analiticcl to find the closest 'normalised form' (and hope it's correct).
"""

import sys
from collections import defaultdict

from analiticcl import VariantModel, Weights, SearchParameters, VocabParams

abcfile = "simple.alphabet.tsv"

boedellemmas = defaultdict(list)

with open("boedeltermen.csv", 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            fields = [x.strip() for x in line.split(",")]
            if fields[0]:
                boedellemmas[fields[0]].append(tuple(fields[1:]))

LEMMA = 4
POS = 5
WORD = 6
intlemmas = defaultdict(set)

with open("int_historisch_lexicon.tsv", 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            fields = [x.strip() for x in line.split("\t")]
            if fields[POS] in ("NOU-C", "AA"):
                intlemmas[fields[LEMMA]].add(fields[WORD])

weights = Weights(suffix=0.25, case=0)  # stronger weight to suffix match, ignore case
params = SearchParameters(max_anagram_distance=0.5, max_edit_distance=0.5)
vocabparams = VocabParams()

for lemma, entries in boedellemmas.items():
    if lemma in intlemmas:
        types = {x[0] for x in entries}
        normforms = {x[1] for x in entries}
        observedforms = {x[2] for x in entries if len(x) >= 3}
        model = VariantModel(abcfile, weights)
        for normform in normforms:
            model.add_to_vocabulary(normform, 1, vocabparams)
        model.build()
        for intobservedform in intlemmas[lemma]:
            intobservedform = intobservedform.replace("⊞", " ")
            if intobservedform not in observedforms and intobservedform not in normforms:
                results = model.find_variants(intobservedform, params)
                if results:
                    result = results[0]['text']
                    for t in types:
                        print(f"{lemma},{t},{result},{intobservedform}")
                else:
                    print(f"Unable to match {intobservedform}", file=sys.stderr)
