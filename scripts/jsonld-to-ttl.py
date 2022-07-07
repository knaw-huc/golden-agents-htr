#!/usr/bin/env python3

import argparse
from typing import List

from rdflib import Graph, URIRef


def main():
    parser = argparse.ArgumentParser(
        description="Loads a set of JSON-LD files into a data graph, and exports the graph in turtle format to stdout.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("jsonld_files",
                        nargs="*",
                        help="The JSON-LD files to convert",
                        type=str)
    args = parser.parse_args()
    if args.jsonld_files:
        graph = setup_graph(args.jsonld_files)
        ttl = graph.serialize()
        print(ttl)
    else:
        parser.print_usage()


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
