#!/usr/bin/env python3

import argparse
import gzip
import sys
from typing import List

from rdflib import Graph, URIRef

export_formats = ("hext", "json-ld", "longturtle", "n3", "nt", "pretty-xml", "trig", "turtle", "xml")


def main():
    sorted_formats = sorted(export_formats)
    parser = argparse.ArgumentParser(
        description="Loads a (set of) JSON-LD file(s) into a data graph, "
                    "and exports the graph to stdout in the given format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("jsonld_file",
                        nargs="*",
                        help="The JSON-LD file(s) to load",
                        type=str)
    parser.add_argument('-c', '--compress', help="gzip-compress the output", action='store_true', required=False)
    parser.add_argument('-f', '--format',
                        help=f"set the export format (options: {sorted_formats})",
                        action='store', required=False, default='turtle')

    args = parser.parse_args()
    if args.format not in export_formats:
        raise Exception(f"format '{args.format}' not recognized: use one of {sorted_formats}")
    if args.jsonld_file:
        export_graph(args.jsonld_file, args.format, args.compress)
    else:
        parser.print_usage()


def export_graph(input_files, output_format, compress):
    graph = setup_graph(input_files)
    out = graph.serialize(format=output_format)
    if compress:
        sys.stdout.buffer.write(gzip.compress(bytes(out, 'utf-8')))
    else:
        print(out)


def setup_graph(jsonld_files: List[str]):
    g = Graph()
    g.namespace_manager.bind("oa", URIRef("http://www.w3.org/ns/oa#"))
    g.namespace_manager.bind("as", URIRef("http://www.w3.org/ns/activitystreams#"))
    g.namespace_manager.bind("ana", URIRef("http://purl.org/analiticcl/terms#"))
    for jf in jsonld_files:
        with open(jf) as f:
            jsonld = f.read()
        g.parse(data=jsonld, format='json-ld')
    return g


if __name__ == '__main__':
    main()
