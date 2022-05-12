#!/usr/bin/env python3

import argparse
import csv
import json
import os.path
from collections import defaultdict
from dataclasses import dataclass
from itertools import chain
from typing import List

from dataclasses_json import dataclass_json
from icecream import ic
from prettytable.colortable import ColorTable, Themes
from tabulate import tabulate


@dataclass_json
@dataclass(frozen=True)
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
    if "source" in target:
        source = target["source"]
    else:
        source = ""
    for s in target['selector']:
        if s['type'] == 'TextPositionSelector':
            start = s['start']
            end = s['end']
        elif s['type'] == 'TextQuoteSelector':
            exact = s['exact']
    return Target(source=source, start=start, end=end, exact=exact)


def load_annotations(path):
    files = json_files(path)
    data = {}
    for f in files:
        basename = f.split('.')[0]
        with open(path + "/" + f) as file:
            annotations = json.load(file)
        data[basename] = annotations
    return data


def json_files(eval_dir):
    return [f for f in os.listdir(eval_dir) if os.path.isfile(os.path.join(eval_dir, f)) and f.endswith(".json")]


def evaluate(eval_dir: str, ref_dir: str) -> EvaluationResults:
    check_paths_exist(eval_dir, ref_dir)

    eval_data = load_annotations(eval_dir)
    ref_data = load_annotations(ref_dir)

    eval_keys = check_file_discrepancy(eval_data, eval_dir, ref_data, ref_dir)

    print_comparison_table(eval_data, eval_keys, ref_data)

    print_categorization_table(eval_data, ref_data)

    return EvaluationResults("", "", "")


def print_comparison_table(eval_data, eval_keys, ref_data):
    table = ColorTable(["Page ID", "Eval Annotations", "Ref Annotations", "diff"], theme=Themes.OCEAN)
    table.align = 'r'
    table.align["Page ID"] = 'l'
    for basename in sorted(eval_keys):
        eval_size = len(eval_data[basename])
        ref_size = len(ref_data[basename])
        table.add_row([basename, eval_size, ref_size, abs(eval_size - ref_size)])
    print(table)


def extract_categories(annotation: dict) -> List[str]:
    return [extract_category(b) for b in annotation['body'] if b.get('purpose') == 'tagging']


def extract_category(annotation_body: dict) -> str:
    if "value" in annotation_body:
        return annotation_body["value"]
    else:
        return annotation_body["source"]["label"]


def extract_normalizations(annotation: dict) -> List[str]:
    return [b['value'] for b in annotation['body'] if b.get('purpose') == 'commenting']


@dataclass
class Row:
    page_id: str
    range: str
    term: str
    normalized_eval: List[str]
    categories_eval: List[str]
    normalized_ref: List[str]
    categories_ref: List[str]


def print_categorization_table(eval_data, ref_data):
    # table = ColorTable(
    #     ["Page ID", "Range", "Term", "Normalized (eval)", "Category (eval)", "Normalized (ref)", "Category (ref)",
    #      "Diff?"],
    #     theme=Themes.OCEAN)
    # table.align = 'l'
    # table.align["Range"] = 'k'
    evaluation_rows = {}
    for page_id in eval_data.keys():
        annotations = eval_data[page_id]
        for a in annotations:
            target = extract_target(a['target'])
            range_str = f"{target.start}-{target.end}"
            key = f"{page_id}.{target.start:05d}-{target.end:05d}"
            categories = sorted(extract_categories(a))
            normalizations = sorted(extract_normalizations(a))
            evaluation_rows[key] = Row(
                page_id=page_id,
                range=range_str,
                term=target.exact,
                normalized_eval=normalizations,
                categories_eval=normalized_categories(categories),
                normalized_ref=[],
                categories_ref=[]
            )
    for page_id in ref_data.keys():
        annotations = ref_data[page_id]
        for a in annotations:
            target = extract_target(a['target'])
            range_str = f"{target.start}-{target.end}"
            key = f"{page_id}.{target.start:05d}-{target.end:05d}"
            categories = sorted(extract_categories(a))
            normalizations = sorted(extract_normalizations(a))
            if key in evaluation_rows:
                evaluation_rows[key].normalized_ref = normalizations
                evaluation_rows[key].categories_ref = categories
            else:
                evaluation_rows[key] = Row(
                    page_id=page_id,
                    range=range_str,
                    term=target.exact,
                    normalized_eval=[],
                    categories_eval=[],
                    normalized_ref=normalizations,
                    categories_ref=normalized_categories(categories)
                )
    # for k in sorted(evaluation_rows.keys()):
    #     r = evaluation_rows[k]
    #     diff = r.normalized_ref != r.normalized_eval or r.categories_ref != r.categories_eval
    #     diff_str = "X" if diff else ""
    #     table.add_row([
    #         r.page_id,
    #         r.range,
    #         r.term,
    #         ' /\n'.join(r.normalized_eval),
    #         ' /\n'.join(r.categories_eval),
    #         ' /\n'.join(r.normalized_ref),
    #         ' /\n'.join(r.categories_ref),
    #         diff_str
    #     ])
    # print(table)
    headers = ["Page ID", "Range", "Term",
               "Normalized (eval)", "Normalized (ref)", "Normalization mismatch",
               "Category (eval)", "Category (ref)", "Category mismatch"]
    table = [table_row(evaluation_rows[k]) for k in sorted(evaluation_rows.keys())]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))
    with open('evaluation_results.tsv', 'w', newline='\n') as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(headers)
        writer.writerows(table)
    group_by_category(evaluation_rows)


def table_row(row):
    n_mismatch = "" if row.normalized_ref == row.normalized_eval \
        else "/" if len(row.normalized_ref) > 0 and set(row.normalized_ref).issubset(set(row.normalized_eval)) \
        else "X"
    c_mismatch = "" if row.categories_ref == row.categories_eval \
        else "/" if len(row.categories_ref) > 0 and set(row.categories_ref).issubset(set(row.categories_eval)) \
        else "X"
    return [row.page_id,
            row.range,
            row.term,
            ' /\n'.join(row.normalized_eval),
            ' /\n'.join(row.normalized_ref),
            n_mismatch,
            ' /\n'.join(row.categories_eval),
            ' /\n'.join(row.categories_ref),
            c_mismatch]


def normalized_category(raw_category: str):
    if raw_category == 'curr':
        return 'currency'
    if raw_category == 'family':
        return 'familyname'
    if raw_category == 'first':
        return 'firstname'
    if raw_category in ['ob', 'obj']:
        return 'object'
    if raw_category == 'occ':
        return 'occupation'
    if raw_category == 'prop':
        return 'property'
    return raw_category


def normalized_categories(category_list: list):
    return [normalized_category(c) for c in category_list]


def group_by_category(evaluation_rows):
    rows_for_category = defaultdict(list)
    for k, r in evaluation_rows.items():
        cats = set(normalized_categories(r.categories_eval + r.categories_ref))
        for c in cats:
            rows_for_category[c].append(r)

    rows_for_eval_category = defaultdict(list)
    for k, r in evaluation_rows.items():
        cats = set(normalized_categories(r.categories_eval))
        for c in cats:
            rows_for_eval_category[c].append(r)

    rows_for_ref_category = defaultdict(list)
    for k, r in evaluation_rows.items():
        cats = set(normalized_categories(r.categories_ref))
        for c in cats:
            rows_for_ref_category[c].append(r)
    all_cats = sorted(set(list(rows_for_ref_category.keys()) + list(rows_for_eval_category.keys())))
    headers = ["category", "# in eval", "# in ref"]
    table = [[c, len(rows_for_eval_category[c]), len(rows_for_ref_category[c])] for c in all_cats]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


def check_file_discrepancy(eval_data, eval_dir, ref_data, ref_dir):
    eval_keys = eval_data.keys()
    ref_keys = ref_data.keys()
    diff = eval_keys - ref_keys
    if diff:
        print(f"some files in {eval_dir} have no corresponding reference files in {ref_dir}: {diff}")
    return eval_keys


def check_paths_exist(eval_dir, ref_dir):
    if not os.path.isdir(eval_dir):
        raise Exception(f"directory not found: {eval_dir}")
    if not os.path.isdir(ref_dir):
        raise Exception(f"directory not found: {ref_dir}")


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
    # ic(args)
    results = evaluate(eval_dir=args.evaluation_set, ref_dir=args.reference_set)
    # print(json.dumps(results.to_dict(), indent=4))


if __name__ == '__main__':
    main()
