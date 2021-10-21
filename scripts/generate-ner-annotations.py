#!/usr/bin/env python3
import argparse
import json

from golden_agents.ner import NER

from pagexml.parser import parse_pagexml_file


def create_scan_id(file) -> str:
    path_parts = file.split('/')
    archive_id = path_parts[-2]
    scan_id = path_parts[-1].replace('.xml', '')
    return f"urn:golden-agents:{archive_id}:scan={scan_id}"


def process_pagexml(file: str) -> list:
    scan = parse_pagexml_file(file)
    if not scan.id:
        scan.id = create_scan_id(file)
    scan.transkribus_uri = "https://files.transkribus.eu/iiif/2/MOQMINPXXPUTISCRFIRKIOIX/full/max/0/default.jpg"
    return NER().create_web_annotations(scan, "http://localhost:8080/textrepo/versions/x")


def main():
    parser = argparse.ArgumentParser(
        description="Perform NER on a PageXML file using Analiticcl, export results as Web Annotations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("pagexmlfile",
                        help="The PageXML file to extract NER annotations from",
                        type=str)
    args = parser.parse_args()

    if args.pagexmlfile:
        annotations = process_pagexml(args.pagexmlfile)
        print(json.dumps(annotations, indent=4))


if __name__ == '__main__':
    main()
