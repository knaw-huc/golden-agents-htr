#!/usr/bin/env python3

"""Sanitize a lexicon, remove unwanted characters and use preferred variant"""

import csv
import re
import sys
from collections import defaultdict

from dataclasses import dataclass


@dataclass
class EntityName:
    original: str
    frequency: int

    def normalized(self):
        pattern = r'[\(\)\&#\;\[\]0-9]+'
        return re.sub(pattern, '', self.original.lower())


def sanitize_lexicon(lexicon,topnormitem=None,topnormfreq=None):
    with open(lexicon, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        names = [EntityName(r[0].strip(), int(r[1])) for r in reader]

    variants = defaultdict(list)
    freqratio = None
    for name in names:
        normalized = name.normalized()
        if normalized:
            if topnormitem and topnormitem == name.original and name.frequency:
                freqratio = topnormfreq / name.frequency
            variants[normalized].append(name)

    for v in sorted(variants):
        preferred = max(variants[v], key=lambda x: x.frequency).original
        total_frequency = sum(x.frequency for x in variants[v])
        if freqratio:
            total_frequency = int(round(total_frequency * freqratio))
        if total_frequency >= freqthreshold: #threshold
            print(f"{preferred}\t{total_frequency}")


if __name__ == "__main__":
    try:
        freqthreshold=int(sys.argv[2])
    except IndexError:
        freqthreshold=10
    try:
        topnormitem=sys.argv[3]
        topnormfreq=int(sys.argv[4])
        print(f"normalizing on {topnormitem} ({topnormfreq})",file=sys.stderr)
    except IndexError:
        topnormitem=None
        topnormfreq=None
    sanitize_lexicon(sys.argv[1],topnormitem,topnormfreq)

