#!/usr/bin/env python3
import argparse
import json
import os.path
import sys

from golden_agents_ner.ner import NER


def main():
    parser = argparse.ArgumentParser(
        description="Perform NER on a PageXML file using Analiticcl, export results as Web Annotations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', '-c', type=str, help="Configuration file", action='store', required=True)
    parser.add_argument('--destinationdir', '-d', type=str, help="Directory for output files", action='store',
                        required=False)
    parser.add_argument('--infix', type=str, help="infix for output files", action='store', required=False)
    parser.add_argument('--stdout', '-o', help="Output JSON to standard output", action='store_true', required=False)
    parser.add_argument('--rawout', '-r', help="Output raw results from analiticcl to standard output (as JSON)",
                        action='store_true', required=False)
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
        parsefiles(ner, out_root, args, *[x for x in args.pagexmlfiles])



def parsefiles(ner, out_root: str, args, *files):
    for pagexmlfile in sorted(files):
        if pagexmlfile.endswith(".lst") or pagexmlfile.endswith(".index"):
            # not a pagexml file but a file referring to page xml files:
            morefiles = []
            with open(pagexmlfile, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip(): morefiles.append(line.strip())
            parsefiles(ner, out_root, args, *morefiles)
        else:
            (annotations, plain_text, raw_results) = ner.process_pagexml(pagexmlfile)
            basename = os.path.splitext(os.path.basename(pagexmlfile))[0]

            if args.rawout:
                json.dump(obj=raw_results, fp=sys.stdout, indent=4, ensure_ascii=False)
            elif args.stdout:
                json.dump(obj=annotations, fp=sys.stdout, indent=4, ensure_ascii=False)
            else:
                if args.infix:
                    json_file = os.path.join(out_root, f"{basename}.{args.infix}.json")
                    text_file = os.path.join(out_root, f"{basename}.{args.infix}.txt")
                else:
                    json_file = os.path.join(out_root, f"{basename}.json")
                    text_file = os.path.join(out_root, f"{basename}.txt")

                print(f'writing to {json_file}', file=sys.stderr)
                with open(json_file, 'w', encoding='utf8') as f:
                    json.dump(obj=annotations, fp=f, indent=4, ensure_ascii=False)

                print(f'writing to {text_file}', file=sys.stderr)
                with open(text_file, 'w', encoding='utf8') as f:
                    f.write(plain_text)


if __name__ == '__main__':
    main()
