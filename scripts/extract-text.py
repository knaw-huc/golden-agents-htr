#!/usr/bin/env python3

import argparse

from pagexml.parser import parse_pagexml_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text contents from Page XML", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("files", nargs='*', help="Files")
    args = parser.parse_args()

    for filename in args.files:
        scan = parse_pagexml_file(filename)
        for tl in [l for l in scan.get_lines() if l.text]:
            print(tl.text)

