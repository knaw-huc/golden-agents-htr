#!/usr/bin/env python3

import argparse
import csv
import json
import os
import os.path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict

from dataclasses_json import dataclass_json
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
    classes: List


def extract_target(target: dict) -> Target:
    if "source" in target:
        source = target["source"]
    else:
        source = ""
    start = None
    end = None
    exact = ""
    for s in target['selector']:
        if s['type'] == 'TextPositionSelector':
            start = s['start']
            end = s['end']
        elif s['type'] == 'TextQuoteSelector':
            exact = s['exact']
    if start is None or end is None:
        raise ValueError("No start/end found")
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


def evaluate(eval_dir: str, ref_dir: str, outfile: str) -> EvaluationResults:
    check_paths_exist(eval_dir, ref_dir)

    eval_data = load_annotations(eval_dir)
    ref_data = load_annotations(ref_dir)

    eval_keys = check_file_discrepancy(eval_data, eval_dir, ref_data, ref_dir)

    print_comparison_table(eval_data, eval_keys, ref_data)

    print_categorization_table(eval_data, ref_data, outfile)

    return EvaluationResults("", "", "")


def print_comparison_table(eval_data, eval_keys, ref_data):
    table = ColorTable(["Page ID", "Eval Annotations", "Ref Annotations", "diff"], theme=Themes.OCEAN)
    table.align = 'r'
    table.align["Page ID"] = 'l'
    for basename in sorted(eval_keys):
        if basename in ref_data:
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


def print_categorization_table(eval_data, ref_data, outfile: str):
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
    #         '|'.join(r.normalized_eval),
    #         '|'.join(r.categories_eval),
    #         '|'.join(r.normalized_ref),
    #         '|'.join(r.categories_ref),
    #         diff_str
    #     ])
    # print(table)
    headers = ["Page ID", "Range", "Term",
               "Normalized (eval)", "Normalized (ref)", "Normalization mismatch",
               "Category (eval)", "Category (ref)", "Category mismatch"]
    table = [table_row(evaluation_rows[k]) for k in sorted(evaluation_rows.keys())]

    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

    cn = print_per_category(headers, table)

    write_to_tsv(headers, table, outfile)

    group_by_category(evaluation_rows, cn)


def write_to_tsv(headers, table, outfile: str):
    with open(outfile, 'w', newline='\n') as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(headers)
        writer.writerows(table)


class CategorizationNumbers:
    def __init__(self, total: int, true_positives: int, false_positives: int, false_negatives: int):
        self.total = total
        self.true_positives = true_positives
        self.false_positives = false_positives
        self.false_negatives = false_negatives

    def accuracy(self) -> float:
        divider = (self.true_positives + self.false_positives + self.false_negatives)
        return 0 if divider == 0 \
            else self.true_positives / divider

    def recall(self) -> float:
        divider = (self.true_positives + self.false_negatives)
        return 0 if divider == 0 \
            else self.true_positives / divider

    def precision(self) -> float:
        divider = (self.true_positives + self.false_positives)
        return 0 if divider == 0 \
            else self.true_positives / divider

    def f1(self) -> float:
        # if self.precision() is None or self.recall() is None:
        #     return None
        divider = (self.precision() + self.recall())
        return 0 if divider == 0 \
            else 2 * ((self.precision() * self.recall()) / divider)


def initialize_confusion_matrix(all_categories: List[str]) -> Dict[str, Dict[str, int]]:
    matrix = {}
    categories = sorted(all_categories)
    for x in categories:
        matrix[x] = {}
        for y in categories:
            matrix[x][y] = 0
    return matrix


def print_per_category(headers, table):
    grouped = defaultdict(list)
    all_categories = set()
    for row in table:
        categories = set((row[6] + "|" + row[7]).split("|"))
        all_categories.update(categories)
        if '' in categories:
            categories.remove('')
        for cat in normalized_categories(list(categories)):
            grouped[cat].append(row)
    confusion = initialize_confusion_matrix(list(all_categories))
    print(confusion)
    categorization_numbers = {}
    for cat in sorted(grouped.keys()):
        cat_rows = grouped[cat]
        type_groups = defaultdict(list)
        true_positive = 'true positive'
        false_positive = 'false positive'
        false_negative = 'false negative'
        for r in cat_rows:
            eval_cats = r[6].split("|")
            ref_cats = r[7].split("|")
            cat_in_eval = cat in eval_cats
            cat_in_ref = cat in ref_cats
            if cat_in_eval and cat_in_ref:
                type_groups[true_positive].append(r)
                confusion[cat][cat] += 1
            elif cat_in_eval:
                type_groups[false_positive].append(r)
                if len(ref_cats) == 0:
                    ref_cats = ['']  # classified as cat in eval, not classified in ref
                for ref_cat in ref_cats:
                    confusion[cat][ref_cat] += 1
            elif cat_in_ref:
                type_groups[false_negative].append(r)
                if len(eval_cats) == 0:  # classified as cat in ref, nog classified in eval
                    eval_cats = ['']
                for eval_cat in eval_cats:
                    confusion[eval_cat][cat] += 1
        total = len(cat_rows)
        true_positive_count = len(type_groups[true_positive])
        false_positive_count = len(type_groups[false_positive])
        false_negative_count = len(type_groups[false_negative])
        cn = CategorizationNumbers(total=total,
                                   true_positives=true_positive_count,
                                   false_positives=false_positive_count,
                                   false_negatives=false_negative_count)
        categorization_numbers[cat] = cn
        print(
            f"{cat} (total: {cn.total} /"
            f" {true_positive}: {cn.true_positives} /"
            f" {false_positive}: {cn.false_positives} /"
            f" {false_negative}: {cn.false_negatives} /"
            f" accuracy: {cn.accuracy()}) /"
            f" precision: {cn.precision()} /"
            f" recall: {cn.recall()} /"
            f" f1: {cn.f1()}:")
        # print(tabulate(cat_rows, headers=headers, tablefmt="fancy_grid"))
        # print()
        for m_type in [true_positive, false_positive, false_negative]:
            sub_total = len(type_groups[m_type])
            if sub_total > 0:
                print(f"{cat} ({sub_total} {m_type}):")
                print(tabulate(type_groups[m_type], headers=headers, tablefmt="fancy_grid"))
                print()

    display_confusion_matrix(confusion)
    return categorization_numbers


def filter_zero(num: int) -> str:
    return "" if num == 0 else str(num)


def display_confusion_matrix(confusion: dict):
    sorted_categories = sorted(confusion.keys())
    matrix = [['↓eval \\ ref→', *sorted_categories]]
    for eval_cat in sorted(confusion.keys()):
        row = [filter_zero(confusion[eval_cat][ref_cat]) for ref_cat in sorted_categories]
        row.insert(0, eval_cat)
        matrix.append(row)
    print("confusion matrix:")
    print(tabulate(matrix, tablefmt="fancy_grid"))
    print()


def table_row(row):
    n_mismatch = "" if row.normalized_ref == row.normalized_eval \
        or set(row.normalized_ref).intersection(set(row.normalized_eval)) \
        else "X"
    c_mismatch = "" if row.categories_ref == row.categories_eval \
        or set(row.categories_ref).intersection(set(row.categories_eval)) \
        else "X"
    return [row.page_id,
            row.range,
            row.term,
            '|'.join(row.normalized_eval),
            '|'.join(row.normalized_ref),
            n_mismatch,
            '|'.join(row.categories_eval),
            '|'.join(normalized_categories(row.categories_ref)),
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


def create_row(category: str, rows_for_eval_category: dict, rows_for_ref_category: dict, cn: CategorizationNumbers):
    return [
        category,
        len(rows_for_eval_category[category]),
        len(rows_for_ref_category[category]),
        cn.total,
        cn.true_positives,
        cn.false_positives,
        cn.false_negatives,
        cn.accuracy(),
        cn.precision(),
        cn.recall(),
        cn.f1()
    ]


def group_by_category(evaluation_rows, categorization_numbers):
    rows_for_category = defaultdict(list)
    for r in evaluation_rows.values():
        cats = set(normalized_categories(r.categories_eval + r.categories_ref))
        for c in cats:
            rows_for_category[c].append(r)

    rows_for_eval_category = defaultdict(list)
    for r in evaluation_rows.values():
        cats = set(normalized_categories(r.categories_eval))
        for c in cats:
            rows_for_eval_category[c].append(r)

    rows_for_ref_category = defaultdict(list)
    for r in evaluation_rows.values():
        cats = set(normalized_categories(r.categories_ref))
        for c in cats:
            rows_for_ref_category[c].append(r)
    all_cats = sorted(set(list(rows_for_ref_category.keys()) + list(rows_for_eval_category.keys())))
    headers = ["category", "# in eval", "# in ref", "total", "TP", "FP", "FN", "accuracy", "precision", "recall", "F1"]
    table = [create_row(c, rows_for_eval_category, rows_for_ref_category, categorization_numbers[c]) for c in all_cats]
    print("categorization numbers:")
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
        description="Evaluate auto-generated webannotations against a ground truth, produces precision, recall,"
                    " class confusion matrix metrics",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--evaluation-set', '-e', type=str, help="Directory with the web annotations to evaluate",
                        action='store', required=True)
    parser.add_argument('--reference-set', '-r', type=str, help="Directory with the reference web annotations",
                        action='store',
                        required=True)
    parser.add_argument('--out', '-o', type=str, help="Output file (TSV)",
                        action='store',
                        default='evaluation_results.tsv')
    args = parser.parse_args()
    # ic(args)
    results = evaluate(eval_dir=args.evaluation_set, ref_dir=args.reference_set, outfile=args.out)
    # print(json.dumps(results.to_dict(), indent=4))


if __name__ == '__main__':
    main()
