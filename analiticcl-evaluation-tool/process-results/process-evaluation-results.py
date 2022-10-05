#!/usr/bin/env python3

import argparse
import csv
import json
import os
import os.path
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Union, Set

from dataclasses_json import dataclass_json
from prettytable.colortable import ColorTable, Themes
from tabulate import tabulate

# Selection of categories that we are actually interested in (only used for computation of SUBTOTAL)
CAT_SELECTION = ("object", "person", "location", "street", "room")


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


def extract_target(target: Union[list, dict]) -> Target:
    if isinstance(target, list):
        for t in target:
            if t['type'] == 'Text':
                return extract_target(t)
        raise Exception("Unable to extract target")
    else:
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

    # returns the keys that exist both in reference data and evaluation data
    keys = check_file_discrepancy(eval_data, eval_dir, ref_data, ref_dir)

    print_comparison_table(eval_data, keys, ref_data)

    print_categorization_table(eval_data, keys, ref_data, outfile)

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
    return [extract_category(b) for b in annotation['body'] if isinstance(b, dict) and b.get('purpose') == 'tagging' and 'source' in b and not b['source']['id'].startswith("https://data.goldenagents.org/boedellexicon/") and not b['source']['id'].startswith("https://www.vondel.humanities.uva.nl/ecartico/occupations/") ]


def extract_category(annotation_body: dict) -> str:
    if "value" in annotation_body:
        return annotation_body["value"]
    else:
        return annotation_body["source"]["label"]


def extract_normalizations(annotation: dict) -> List[str]:
    return [b['value'] for b in annotation['body'] if isinstance(b, dict) and b.get('purpose') in {'commenting', 'editing'}]


@dataclass
class Row:
    page_id: str
    range: str
    term: str
    normalized_eval: List[str]
    categories_eval: List[str]
    normalized_ref: List[str]
    categories_ref: List[str]


def extract_persons(evaluation_rows: Dict[str, Row]):
    """Extract persons from reference data (no longer used)"""
    firstname_start = defaultdict(dict)
    lastname_start = defaultdict(dict)
    for row in evaluation_rows.values():
        start, end = [int(x) for x in row.range.split("-")]
        if 'firstname' in row.categories_ref:
            firstname_start[row.page_id][start] = row
        if 'familyname' in row.categories_ref:
            lastname_start[row.page_id][start] = row

    for page_id, firstnames_offsets in firstname_start.items():
        for start, firstname in firstnames_offsets.items():
            end = int(firstname.range.split("-")[1]) + 1
            for lastname_offset in (end, end + 1):
                if lastname_offset in lastname_start[page_id]:
                    lastname = lastname_start[page_id][lastname_offset]
                    normalized_ref = (firstname.normalized_ref[0] + " " + lastname.normalized_ref[0]).strip()
                    end = int(lastname.range.split("-")[1])
                    key = f"{page_id}.{start:05d}-{end:05d}"
                    if key in evaluation_rows:
                        if not normalized_ref in evaluation_rows[key].normalized_ref:
                            evaluation_rows[key].normalized_ref.append(normalized_ref)
                        if not "person" in evaluation_rows[key].categories_ref:
                            evaluation_rows[key].categories_ref.append("person")
                    else:
                        range_str = f"{start}-{end}"
                        evaluation_rows[key] = Row(
                            page_id=page_id,
                            range=range_str,
                            term=firstname.term + " " + lastname.term,
                            normalized_eval=[],
                            categories_eval=[],
                            normalized_ref=[normalized_ref],
                            categories_ref=["person"]
                        )
                    print(f"(Extracted person '{normalized_ref}' in ground truth: {key})")


def print_categorization_table(eval_data, keys, ref_data, outfile: str):
    evaluation_rows = {}
    for page_id in keys:
        annotations = eval_data[page_id]
        for a in annotations:
            target = extract_target(a['target'])
            range_str = f"{target.start}-{target.end}"
            key = f"{page_id}.{target.start:05d}-{target.end:05d}"
            categories = sorted(extract_categories(a))
            normalizations = sorted(extract_normalizations(a))
            if not normalizations:
                # no normalizations outputted by system, copy input term
                normalizations = [target.exact]
            evaluation_rows[key] = Row(
                page_id=page_id,
                range=range_str,
                term=target.exact,
                normalized_eval=normalizations,
                categories_eval=normalized_categories(categories),
                normalized_ref=[],
                categories_ref=[]
            )
    for page_id in keys:
        annotations = ref_data[page_id]
        for a in annotations:
            target = extract_target(a['target'])
            range_str = f"{target.start}-{target.end}"
            key = f"{page_id}.{target.start:05d}-{target.end:05d}"
            categories = sorted(extract_categories(a))
            normalizations = sorted(extract_normalizations(a))
            if not normalizations:
                # no normalizations provided by annotator, copy input term
                normalizations = [target.exact]
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
    #extract_persons(evaluation_rows)
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
    def __init__(self, total: int, true_positives: int, strict_true_positives: int, false_positives: int,
                 false_negatives: int):
        self.total = total
        self.true_positives = true_positives
        self.strict_true_positives = strict_true_positives  # these is a subset of the true positives where also the normalisation matches
        self.false_positives = false_positives
        self.false_negatives = false_negatives

    def accuracy(self, strict: bool = False) -> float:
        tp = self.strict_true_positives if strict else self.true_positives
        divider = (self.true_positives + self.false_positives + self.false_negatives)
        return 0 if divider == 0 \
            else tp / divider

    def recall(self, strict: bool = False) -> float:
        tp = self.strict_true_positives if strict else self.true_positives
        divider = (self.true_positives + self.false_negatives)
        return 0 if divider == 0 \
            else tp / divider

    def precision(self, strict: bool = False) -> float:
        tp = self.strict_true_positives if strict else self.true_positives
        divider = (self.true_positives + self.false_positives)
        return 0 if divider == 0 \
            else tp / divider

    def f1(self, strict: bool = False) -> float:
        # if self.precision() is None or self.recall() is None:
        #     return None
        divider = (self.precision(strict) + self.recall(strict))
        return 0 if divider == 0 \
            else 2 * ((self.precision(strict) * self.recall(strict)) / divider)

    def __iadd__(self, other):
        self.total += other.total
        self.true_positives += other.true_positives
        self.strict_true_positives += other.strict_true_positives
        self.false_positives += other.false_positives
        self.false_negatives += other.false_negatives
        return self


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
        strict_true_positive = 'strict true positive'
        false_positive = 'false positive'
        false_negative = 'false negative'
        for r in cat_rows:
            eval_norm = set(r[3].split("|"))
            ref_norm = set(r[4].split("|"))
            norm_match = match_normalization(ref_norm, eval_norm)
            eval_cats = r[6].split("|")
            ref_cats = r[7].split("|")
            cat_in_eval = cat in eval_cats
            cat_in_ref = cat in ref_cats
            if match_category(ref_cats, eval_cats):
                type_groups[true_positive].append(r)
                if norm_match:
                    type_groups[strict_true_positive].append(r)
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
        strict_true_positive_count = len(type_groups[strict_true_positive])
        false_positive_count = len(type_groups[false_positive])
        false_negative_count = len(type_groups[false_negative])
        cn = CategorizationNumbers(total=total,
                                   true_positives=true_positive_count,
                                   strict_true_positives=strict_true_positive_count,
                                   false_positives=false_positive_count,
                                   false_negatives=false_negative_count)
        categorization_numbers[cat] = cn
        print(
            f"{cat} (total: {cn.total} /"
            f" {true_positive}: {cn.true_positives} /"
            f" strict {true_positive}: {cn.strict_true_positives} /"
            f" {false_positive}: {cn.false_positives} /"
            f" {false_negative}: {cn.false_negatives} /"
            f" accuracy: {cn.accuracy():.3f} ({cn.accuracy(strict=True):.3f}) /"
            f" precision: {cn.precision():.3f} ({cn.precision(strict=True):.3f}) /"
            f" recall: {cn.recall():.3f} ({cn.recall(strict=True):.3f}) /"
            f" f1: {cn.f1():.3f} ({cn.f1(strict=True):.3f}):")
        # print(tabulate(cat_rows, headers=headers, tablefmt="fancy_grid"))
        # print()
        for m_type in (true_positive, strict_true_positive, false_positive, false_negative):
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


def match_normalization_row(row: Row) -> bool:
    return match_normalization(row.normalized_ref, row.normalized_eval)


def match_normalization(normalized_ref: Union[List[str], Set[str]],
                        normalized_eval: Union[List[str], Set[str]]) -> bool:
    return normalized_ref == normalized_eval \
           or bool(set(normalized_ref).intersection(set(normalized_eval)))


def match_category_row(row: Row) -> bool:
    return match_category(row.categories_ref, row.categories_eval)


def match_category(categories_ref: Union[List[str], Set[str]], categories_eval: Union[List[str], Set[str]]) -> bool:
    return categories_ref == categories_eval \
           or bool(set(categories_ref).intersection(set(categories_eval)))
           #or ('firstname' in categories_eval and ('firstname' in categories_ref or 'familyname' in categories_ref)) \

def table_row(row):
    n_mismatch = "" if match_normalization_row(row) else "X"
    c_mismatch = "" if match_category_row(row) else "X"
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
    """normalize category names from the reference data so it equals the categories in the system output"""
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
        f"{cn.true_positives} ({cn.strict_true_positives})",
        cn.false_positives,
        cn.false_negatives,
        f"{cn.accuracy():.3f} ({cn.accuracy(strict=True):.3f})",
        f"{cn.precision():.3f} ({cn.precision(strict=True):.3f})",
        f"{cn.recall():.3f} ({cn.recall(strict=True):.3f})",
        f"{cn.f1():.3f} ({cn.f1(strict=True):.3f})"
    ]


def group_by_category(evaluation_rows, categorization_numbers):
    rows_for_category = defaultdict(list)
    for r in evaluation_rows.values():
        cats = set(normalized_categories(r.categories_eval + r.categories_ref))
        for c in cats:
            rows_for_category[c].append(r)
            rows_for_category["TOTAL"].append(r)
            if c in CAT_SELECTION:
                rows_for_category["SUBTOTAL"].append(r)

    rows_for_eval_category = defaultdict(list)
    for r in evaluation_rows.values():
        cats = set(normalized_categories(r.categories_eval))
        for c in cats:
            rows_for_eval_category[c].append(r)
            rows_for_eval_category["TOTAL"].append(r)
            if c in CAT_SELECTION:
                rows_for_eval_category["SUBTOTAL"].append(r)

    rows_for_ref_category = defaultdict(list)
    for r in evaluation_rows.values():
        cats = set(normalized_categories(r.categories_ref))
        for c in cats:
            rows_for_ref_category[c].append(r)
            rows_for_ref_category["TOTAL"].append(r)
            if c in CAT_SELECTION:
                rows_for_ref_category["SUBTOTAL"].append(r)

    cn = CategorizationNumbers(0, 0, 0, 0, 0)
    assert cn is not None
    for c in CAT_SELECTION:
        if c in categorization_numbers:
            cn += categorization_numbers[c]
    categorization_numbers["SUBTOTAL"] = cn

    all_cats = set(list(rows_for_ref_category.keys()) + list(rows_for_eval_category.keys()))

    cn = CategorizationNumbers(0, 0, 0, 0, 0)
    for c in all_cats - {"SUBTOTAL"}:
        if c in categorization_numbers:
            cn += categorization_numbers[c]
    categorization_numbers["TOTAL"] = cn

    headers = ["category", "# in eval", "# in ref", "total", "TP (+strict)", "FP", "FN", "accuracy", "precision",
               "recall", "F1"]
    table = [create_row(c, rows_for_eval_category, rows_for_ref_category, categorization_numbers[c]) for c in
             sorted(all_cats)]
    print("categorization numbers: (strict values that take normalisation into account are in parentheses)")
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


def check_file_discrepancy(eval_data, eval_dir, ref_data, ref_dir):
    eval_keys = eval_data.keys()
    ref_keys = ref_data.keys()
    diff = list(sorted(eval_keys - ref_keys))
    if diff:
        print(f"some files in {eval_dir} have no corresponding reference files in {ref_dir}: {diff}")
    return eval_keys & ref_keys


def check_paths_exist(eval_dir, ref_dir):
    if not os.path.isdir(eval_dir):
        raise Exception(f"directory not found: {eval_dir}")
    if not os.path.isdir(ref_dir):
        raise Exception(f"directory not found: {ref_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate auto-generated web annotations against a ground truth, produces precision, recall,"
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
    results = evaluate(eval_dir=args.evaluation_set, ref_dir=args.reference_set, outfile=args.out)
    # print(json.dumps(results.to_dict(), indent=4))


if __name__ == '__main__':
    main()
