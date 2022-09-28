#!/usr/bin/env python3

from sys import stdin, stderr

LEMMA,TYPE = range(0,2)

typemap = {
    "voorwerp": "object",
    "stofnaam": "material",
    "beroep": "occupation",
    "vertrek": "room",
    "eigenschap": "property",
    "voorstelling": "picture",
    "categorie": "category",
    "munt": "currency",
    "eenheid": "quantifier",
    "onbepaald voornaamwoord": "quantifier",
    "eigennaam": "name", #not used!
    "dier": "animal",
    "vee": "cattle",
    "rest": "misc"
}

for line in stdin.readlines():
    if line.strip():
        fields = [ x.strip() for x in line.split(",")]
        if fields[TYPE] in typemap:
            fields[TYPE] = typemap[fields[TYPE]]
        else:
            print("Unmappable type: " + fields[TYPE],file=stderr)
            fields[TYPE] = ""
        print(",".join(fields))

