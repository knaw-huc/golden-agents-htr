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


def sanitize_lexicon(lexicon):
    with open(lexicon, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        names = [EntityName(r[0], int(r[1])) for r in reader]

    variants = defaultdict(list)
    for name in names:
        normalized = name.normalized()
        if normalized:
            variants[normalized].append(name)

    for v in sorted(variants):
        preferred = max(variants[v], key=lambda x: x.frequency).original
        total_frequency = sum(x.frequency for x in variants[v])
        print(f"{preferred}\t{total_frequency}")


if __name__ == "__main__":
    sanitize_lexicon(sys.argv[1])
