#!/usr/bin/env python3
import sys
import argparse
import json
import os.path

from golden_agents.ner import NER


def main():
    parser = argparse.ArgumentParser(
        description="Perform NER on a PageXML file using Analiticcl, export results as Web Annotations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', '-c', type=str, help="Configuration file", action='store', required=True)
    parser.add_argument('--destinationdir', '-d', type=str, help="Directory for output files", action='store',
                        required=False)
    parser.add_argument('--stdout','-o',help="Output JSON to standard output", action='store_true', required=False)
    parser.add_argument("pagexmlfiles",
                        nargs="*",
                        help="The PageXML file(s) to extract NER annotations from",
                        type=str)
    args = parser.parse_args()

    ner = NER(args.config)

    if args.pagexmlfiles:
        out_root = "."
        if args.destinationdir:
            os.makedirs(args.destinationdir, exist_ok=True)
            out_root = args.destinationdir

        for pagexmlfile in args.pagexmlfiles:
            (annotations, plain_text) = ner.process_pagexml(pagexmlfile)
            basename = os.path.splitext(os.path.basename(pagexmlfile))[0]

            if args.stdout:
                json.dump(obj=annotations, fp=sys.stdout, indent=4)
            else:
                json_file = os.path.join(out_root, f"{basename}.json")
                print(f'writing to {json_file}',file=sys.stderr)
                with open(json_file, 'w', encoding='utf8') as f:
                    json.dump(obj=annotations, fp=f, indent=4)

                text_file = os.path.join(out_root, f"{basename}.txt")
                print(f'writing to {text_file}',file=sys.stderr)
                with open(text_file, 'w', encoding='utf8') as f:
                    f.write(plain_text)


if __name__ == '__main__':
    main()
