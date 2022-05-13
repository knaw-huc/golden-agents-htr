#!/usr/bin/env python3

"""Dehyphenize a text, joins lines that end in a hyphen"""

import sys

HYPHENS = ("¬", "-")

buffer = ""
for line in sys.stdin:
    line = line.strip()
    if line and line[-1] in HYPHENS:
        buffer += line[:-1]
    elif buffer:
        buffer += line
        print(buffer)
        buffer = ""
    else:
        print(line)

if buffer:
    print(buffer)
