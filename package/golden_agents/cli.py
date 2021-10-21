#!/usr/bin/env python3
import argparse
import json

from golden_agents.ner import NER

def main():
    parser = argparse.ArgumentParser(
        description="Perform NER on a PageXML file using Analiticcl, export results as Web Annotations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config','-c',type=str, help="Configuration file", action='store', required=True)
    parser.add_argument("pagexmlfiles",
                        nargs="*",
                        help="The PageXML file(s) to extract NER annotations from",
                        type=str)
    args = parser.parse_args()

    ner = NER(args.config)

    if args.pagexmlfiles:
        for pagexmlfile in args.pagexmlfiles:
            annotations = ner.process_pagexml(pagexmlfile)
            print(json.dumps(annotations, indent=4))


if __name__ == '__main__':
    main()
