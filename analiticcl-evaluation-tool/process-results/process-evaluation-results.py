#!/bin/env python3

import argparse
import os.path
from dataclasses import dataclass

from icecream import ic


@dataclass
class EvaluationResults:
    precision: str
    recall: str
    class_confusion_matrix: str


@dataclass(frozen=True)
class Target:
    source: str
    start: int
    end: int
    exact: str


@dataclass
class Classification:
    target: Target
    classes: []


def extract_target(target: dict) -> Target:
    for s in target['selector']:
        if (s['type'] == 'TextPositionSelector'):
            start = s['start']
            end = s['end']
        elif (s['type'] == 'TextQuoteSelector'):
            exact = s['exact']
    return Target(source=target['source'], start=start, end=end, exact=exact)


def evaluate(evaldir: str, refdir: str) -> EvaluationResults:
    ic(evaldir, refdir)
    if not os.path.isdir(evaldir):
        raise Exception(f"directory not found: {evaldir}")
    if not os.path.isdir(refdir):
        raise Exception(f"directory not found: {refdir}")
    return EvaluationResults("", "", "")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate auto-generated webannotations against a ground truth, produces precision, recall, class confusion matrix metrics",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--evaluation-set', '-e', type=str, help="Directory with the web annotations to evaluate",
                        action='store', required=True)
    parser.add_argument('--reference-set', '-r', type=str, help="Directory with the reference web annotations",
                        action='store',
                        required=True)
    args = parser.parse_args()
    ic(args)
    results = evaluate(evaldir=(args.evaluation_set), refdir=(args.reference_set))
    print(results)


if __name__ == '__main__':
    main()
