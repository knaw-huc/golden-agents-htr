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

BOEDELTERMEN_LEMMA, BOEDELTERMEN_TYPE, BOEDELTERMEN_NORMWORDFORM, BOEDELTERMEN_VARWORDFORM, BOEDELTERMEN_URI = range(0,5)
boedellemmas = defaultdict(list)

with open("boedeltermen.csv", 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            fields = [x.strip() for x in line.split(",")]
            if fields[BOEDELTERMEN_LEMMA]:
                boedellemmas[fields[BOEDELTERMEN_LEMMA]].append(tuple(fields[BOEDELTERMEN_TYPE:]))


INT_LEMMA = 4
INT_POS = 5
INT_WORD = 6
intlemmas = defaultdict(set)

with open("int_historisch_lexicon.tsv", 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            fields = [x.strip() for x in line.split("\t")]
            if fields[INT_POS] in ("NOU-C", "AA"):
                intlemmas[fields[INT_LEMMA]].add(fields[INT_WORD])

weights = Weights(suffix=0.25, case=0)  # stronger weight to suffix match, ignore case
params = SearchParameters(max_anagram_distance=0.5, max_edit_distance=0.5)
vocabparams = VocabParams()

for lemma, entries in boedellemmas.items():
    if lemma in intlemmas:
        types = {x[BOEDELTERMEN_TYPE-1] for x in entries}
        normforms = {x[BOEDELTERMEN_NORMWORDFORM-1] for x in entries}
        observedforms = {x[BOEDELTERMEN_VARWORDFORM-1] for x in entries}
        uris = { x[BOEDELTERMEN_TYPE-1]: x[BOEDELTERMEN_URI-1] for x in entries}
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
                        uri = uris.get(t,"")
                        print(f"{lemma},{t},{result},{intobservedform},{uri}")
                else:
                    print(f"Unable to match {intobservedform}", file=sys.stderr)
