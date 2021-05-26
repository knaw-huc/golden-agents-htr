#!/usr/bin/env python3

import argparse

import lxml.etree

parser = argparse.ArgumentParser(description="Extract text contents from Page XML", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("files", nargs='*', help="Files")
args = parser.parse_args()

for filename in args.files:
    doc = lxml.etree.parse(filename).getroot()
    for element in doc.xpath("//pagexml:TextRegion/pagexml:TextLine/pagexml:TextEquiv/pagexml:Unicode",namespaces={'pagexml': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15' }):
        if element.text:
            print(element.text)
