#!/usr/bin/env python3

import argparse
import json
from dataclasses import dataclass
from itertools import groupby


@dataclass(frozen=True)
class Body:
    btype: str
    purpose: str
    value: str


def aggregate(annotations):
    aggregated_annotations = []
    for (id, g) in groupby(annotations, lambda a: a['id']):
        group = list(g)
        if (len(group) == 1):
            aggregated_annotations.append(group[0])
        else:
            aa = group[0]
            for other in group[1:]:
                aa['body'] = aa['body'] + other['body']
            ol = [Body(btype=b['type'], purpose=b['purpose'], value=b['value']) for b in
                  aa['body']]
            ol2 = list(set(ol))
            aa['body'] = [{'type': b.btype, 'purpose': b.purpose, 'value': b.value} for b in
                          ol2]
            aggregated_annotations.append(aa)
    return aggregated_annotations


def trim_annotation(annotation: dict) -> dict:
    new = annotation
    new['@context'] = 'http://www.w3.org/ns/anno.jsonld'
    new['body'] = [b for b in annotation['body'] if b.get('purpose', '') in {'tagging', 'commenting'}]
    source = annotation['target']['source']
    start = annotation['target']['selector'][0]['start']
    end = annotation['target']['selector'][0]['end']
    new['id'] = f"{source.replace('unknown:', '')}:offset={start}-{end}"
    return new


def main():
    parser = argparse.ArgumentParser(description="Prepare annotations for use in a recogito-js powered tool.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("files", nargs='*', help="Files")
    args = parser.parse_args()

    for filename in args.files:
        print(f'simplifying {filename}')
        with open(filename) as f:
            annotations_in = json.load(f)
        trimmed_annotations = [trim_annotation(a) for a in annotations_in]
        aggregated_annotations = aggregate(trimmed_annotations)
        with (open(filename, 'w', encoding='utf8')) as f:
            json.dump(aggregated_annotations, fp=f, indent=2)


if __name__ == '__main__':
    main()
