#!/usr/bin/env python3

import argparse
import gzip
import json
import sys
from http.client import RemoteDisconnected

from rdflib import Graph, URIRef
from typing import List, Union

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
    parser.add_argument('-v', '--vocab', help="add default vocabulary uri", action='store', required=False)

    args = parser.parse_args()
    if args.format not in export_formats:
        raise Exception(f"format '{args.format}' not recognized: use one of {sorted_formats}")
    if args.jsonld_file:
        if args.vocab:
            export_graph(args.jsonld_file, args.format, args.compress, args.vocab)
        else:
            export_graph(args.jsonld_file, args.format, args.compress)
    else:
        parser.print_usage()


def export_graph(input_files, output_format, compress, vocab=None):
    graph = setup_graph(input_files, vocab)
    out = graph.serialize(format=output_format)
    if compress:
        sys.stdout.buffer.write(gzip.compress(bytes(out, 'utf-8')))
    else:
        print(out)


def setup_graph(jsonld_files: List[str], vocab: Union[str, None] = None):
    g = Graph()
    g.namespace_manager.bind("ana", URIRef("http://purl.org/analiticcl/terms#"))
    g.namespace_manager.bind("as", URIRef("http://www.w3.org/ns/activitystreams#"))
    g.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))
    g.namespace_manager.bind("foaf", URIRef("http://xmlns.com/foaf/0.1/"))
    g.namespace_manager.bind("oa", URIRef("http://www.w3.org/ns/oa#"))
    g.namespace_manager.bind("rpp", URIRef("https://data.goldenagents.org/ontology/rpp/"))
    g.namespace_manager.bind("vm", URIRef("https://humanities.knaw.nl/ns/variant-matching#"))

    total = len(jsonld_files)
    missed_files = []
    for i, jf in enumerate(jsonld_files):
        print(f"loading {jf} ({i + 1}/{total}) ...", file=sys.stderr)
        with open(jf) as f:
            jsonld = f.read()
        if vocab:
            g.namespace_manager.bind("", URIRef(vocab))
            jsonld = add_default_vocabulary_to_context(vocab, json.loads(jsonld))
        try:
            g.parse(data=jsonld, format='json-ld')
        except (RemoteDisconnected, ConnectionResetError):
            print("error, skipping...", file=sys.stderr)
            missed_files.append(jf)
    print(missed_files, file=sys.stderr)
    return g


def add_default_vocabulary_to_context(vocab, annotations):
    new_annotations = list()
    for a in annotations:
        context = a.get("@context")
        context_list = []
        if isinstance(context, str):
            context_list.append(context)
        else:
            context_list.extend(context)
        context_list.append({"@vocab": vocab})
        a["@context"] = context_list
        new_annotations.append(a)
    jsonld = json.dumps(new_annotations)
    return jsonld


if __name__ == '__main__':
    main()
