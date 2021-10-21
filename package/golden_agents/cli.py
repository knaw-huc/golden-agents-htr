#!/usr/bin/env python3
import argparse
import json

from golden_agents.ner import NER

def main():
    parser = argparse.ArgumentParser(
        description="Perform NER on a PageXML file using Analiticcl, export results as Web Annotations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("pagexmlfile",
                        help="The PageXML file to extract NER annotations from",
                        type=str)
    args = parser.parse_args()

    ner = NER()

    if args.pagexmlfile:
        annotations = ner.process_pagexml(args.pagexmlfile)
        print(json.dumps(annotations, indent=4))


if __name__ == '__main__':
    main()
