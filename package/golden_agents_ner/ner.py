import csv
import json
import os.path
import sys
import uuid
from copy import deepcopy
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from analiticcl import VariantModel, Weights, SearchParameters
from golden_agents_ner.corrections import Corrector
from pagexml.parser import PageXMLTextLine, parse_pagexml_file

VARIANT_MATCHING_CONTEXT = "https://brambg.github.io/ns/variant-matching.jsonld"
HTR_CORRECTIONS = 'htr_corrections'
ARCHIVE_IDENTIFIERS = 'archive_identifiers'


def text_line_urn(archive_id: str, scan_id: str, textline_id: str):
    return f"urn:golden-agents:{archive_id}:scan={scan_id}:textline={textline_id}"


def create_scan_id(file: str) -> str:
    path_parts = file.split('/')
    if len(path_parts) >= 2:
        archive_id = path_parts[-2]
    else:
        archive_id = "unknown"
        print(
            f"WARNING: No archive component could be extracted for {file} "
            f"because input file has no archive directory component",
            file=sys.stderr)
    scan_id = path_parts[-1].replace('.xml', '')
    return f"urn:golden-agents:{archive_id}:scan={scan_id}"


def fixpath(filepath: str, configfile: str) -> str:
    """Turns a relative path relative to the config file into a relative path relative to the caller"""
    if filepath[0] != '/':
        # relative path:
        filepath = os.path.join(os.path.dirname(configfile), filepath)
    return filepath


def now():
    return datetime.today().isoformat()


def random_annotation_id() -> str:
    return f'https://data.goldenagents.org/datasets/annotations/{uuid.uuid4()}'


class NER:
    def __init__(self, configfile: str):
        """Instantiates a NER tagger with variantmodel; loads all lexicons specified in the configuration
         (and parameters)"""
        with open(configfile, 'rb') as f:
            self.config = json.load(f)
        for key in ("lexicons", "searchparameters", "alphabet", "weights"):
            if key not in self.config:
                raise ValueError(f"Missing required key in configuration file: {key}")
        self.category_dict = {fixpath(filepath, configfile): category for category, filepath in
                              self.config['lexicons'].items()}
        if 'variantlists' in self.config:
            self.category_dict.update(
                {fixpath(filepath, configfile): category for category, filepath in self.config['variantlists'].items()})
        self.config['searchparameters'][
            'unicodeoffsets'] = True  # force usage of unicode points in offsets (rather than UTF-8 bytes)
        self.params = SearchParameters(**self.config['searchparameters'])
        print("Search Parameters: ", self.params.to_dict(), file=sys.stderr)
        abcfile = self.config['alphabet']
        if abcfile[0] != '/':
            # relative path:
            abcfile = os.path.join(os.path.dirname(configfile), abcfile)
        weights = Weights(**self.config['weights'])
        print("Weights: ", weights.to_dict(), file=sys.stderr)
        print("Debug: ", self.config.get('debug', 0), file=sys.stderr)
        self.model = VariantModel(abcfile, weights, debug=self.config.get('debug', 0))

        if 'lexicons' in self.config:
            for filepath in self.config['lexicons'].values():
                filepath = fixpath(filepath, configfile)
                if not os.path.exists(filepath):
                    raise FileNotFoundError(filepath)
                self.model.read_lexicon(filepath)

        if 'variantlists' in self.config:
            for filepath in self.config['variantlists'].values():
                filepath = fixpath(filepath, configfile)
                if not os.path.exists(filepath):
                    raise FileNotFoundError(filepath)
                self.model.read_variants(filepath, True)

        if 'lm' in self.config:
            for filepath in self.config['lm']:
                filepath = fixpath(filepath, configfile)
                self.model.read_lm(filepath)

        if 'contextrules' in self.config:
            self.model.read_contextrules(self.config['contextrules'])
            self.has_contextrules = True
        else:
            self.has_contextrules = False

        if 'resourceids' in self.config:
            self.resource_ids = self.config['resourceids']
            self.has_resource_ids = True
        else:
            self.has_resource_ids = False

        self.model.build()
        if HTR_CORRECTIONS in self.config:
            corrections_file = self.config[HTR_CORRECTIONS]
            print(f"using htr corrections from {corrections_file}", file=sys.stderr)
            with open(corrections_file) as f:
                corrections_dict = json.load(f)
            self.htr_corrector = Corrector(corrections_dict)

        if ARCHIVE_IDENTIFIERS in self.config:
            index = {}
            with open(self.config[ARCHIVE_IDENTIFIERS]) as f:
                for row in csv.DictReader(f):
                    index[row['title']] = row['identifier']
            self.archive_identifier = index
        else:
            raise Exception(f"config file should have an '{ARCHIVE_IDENTIFIERS}' entry linking to a file like "
                            f"resources/archive_identifiers.tsv.")

    def process_pagexml(self, file: str) -> Tuple[list, str, list]:
        """Runs the NER tagging on a PageXML file, returns a list of web annotations"""
        if os.path.islink(file): 
            #deference symbolic links, we need the full path info
            file = os.path.realpath(file)
        scan = parse_pagexml_file(file)
        if not scan.id:
            scan.id = create_scan_id(file)
        # TODO: remove hardcoded urls
        # scan.transkribus_uri = "https://files.transkribus.eu/iiif/2/MOQMINPXXPUTISCRFIRKIOIX/full/max/0/default.jpg"
        path_parts = file.split('/')
        archive_title = path_parts[-2]
        inv_num = self.archive_identifier[archive_title]
        base_name = path_parts[-1].split('.')[0]
        scan.pid = f"https://data.goldenagents.org/datasets/saa/ead/{inv_num}/scans/{base_name}"
        scan.text_pid = f"https://data.goldenagents.org/datasets/saa/ead/{inv_num}/texts/{base_name}"
        return self.create_web_annotations(scan)

    def create_web_annotation_multispan(self, ner_results, text_line: PageXMLTextLine, line_offset: int,
                                        text_pid: str, scan_pid: str):
        """Extract larger tagged entities from NER results and creates web annotations for them."""
        for i, ner_result in enumerate(ner_results):
            if ner_result['variants']:
                for (tag, seqnr) in zip(ner_result.get('tag', []), ner_result.get('seqnr', [])):
                    # If there are multiple tags we create a complete and a seperate web annotation for each of them
                    if seqnr > 0:
                        # find beginning of sequence, skip otherwise
                        continue
                    length = 1
                    # find the rest of the sequence; aggregate text of the top variants
                    variant_text = ner_result['variants'][0]['text']
                    last_ner_result = ner_result
                    for j, ner_result2 in enumerate(ner_results[i + 1:]):
                        try:
                            idx = ner_result2.get('tag', []).index(tag)
                        except ValueError:
                            break
                        if ner_result2.get('seqnr', [])[idx] == j + 1:
                            length += 1
                            variant_text += " " + ner_result2['variants'][0]['text']
                            last_ner_result = ner_result2
                        else:
                            break
                    if length > 1:
                        xywh = f"{text_line.coords.x},{text_line.coords.y},{text_line.coords.w},{text_line.coords.h}"
                        yield {
                            "@context": "http://www.w3.org/ns/anno.jsonld",
                            "id": random_annotation_id(),
                            "type": "Annotation",
                            "motivation": [
                                "classifying",
                                "editing"
                            ],
                            "generated": now(),
                            "generator": {
                                "id": "https://github.com/knaw-huc/golden-agents-htr",
                                "type": "Software",
                                "name": "GoldenAgentsNER"
                            },
                            "body": [
                                self.tagging_body(label=tag),
                                {
                                    "type": "TextualBody",
                                    "value": variant_text,
                                    "modified": now(),
                                    "purpose": "editing"
                                },
                                self.variantmatch_body(phrase=text_line.text[ner_result['offset']['begin']:last_ner_result['offset']['end']],
                                                       variant=variant_text,
                                                       score=None,
                                                       lexicons=[],
                                                       category=tag, seqnr=seqnr)
                            ],
                            "target": [
                                {
                                    "source": text_pid,
                                    "type": "Text",
                                    "selector": [
                                        {
                                            "type": "TextPositionSelector",
                                            "start": line_offset + ner_result['offset']['begin'],
                                            "end": line_offset + last_ner_result['offset']['end']
                                        },
                                        {
                                            "type": "TextQuoteSelector",
                                            "exact": text_line.text[
                                                     ner_result['offset']['begin']:last_ner_result['offset']['end']],
                                            "prefix": text_line.text[:ner_result['offset']['begin']],
                                            "suffix": text_line.text[last_ner_result['offset']['end']:],
                                        }
                                    ]
                                },
                                {
                                    "source": scan_pid,
                                    "type": "Image",
                                    "selector": {
                                        "type": "FragmentSelector",
                                        "conformsTo": "http://www.w3.org/TR/media-frags/",
                                        "value": f"xywh={xywh}"
                                    }
                                }
                            ]
                        }

    def create_web_annotations(self, scan) -> Tuple[List[dict], str, List[dict]]:
        """Find lines in the scan and pass them to the tagger, producing web-annotations"""
        annotations = []
        plain_text = ''
        raw_results = []
        for tl in [l for l in scan.get_lines() if l.text]:
            text = tl.text
            if hasattr(self, 'htr_corrector') and self.htr_corrector:
                text = self.htr_corrector.correct(text)
            ner_results = self.model.find_all_matches(text, self.params)
            if self.has_contextrules:
                for entity_wa in self.create_web_annotation_multispan(ner_results=ner_results, text_line=tl,
                                                                      line_offset=len(plain_text),
                                                                      scan_pid=scan.pid, text_pid=scan.text_pid):
                    annotations.append(entity_wa)
            for result in ner_results:
                raw_results.append(result)
                if (
                        len(result['variants']) > 0
                        and result['variants'][0]['score'] >= self.config.get('score-threshold', 0)
                ):
                    xywh = f"{tl.coords.x},{tl.coords.y},{tl.coords.w},{tl.coords.h}"
                    annotations += list(
                        self.create_web_annotation(text_line=tl, ner_result=result, scan_pid=scan.pid, xywh=xywh,
                                                   text_pid=scan.text_pid,
                                                   line_offset=len(plain_text)))
            plain_text += f"{text}\n"
        return annotations, plain_text, raw_results

    def create_web_annotation(self, text_line: PageXMLTextLine, ner_result, scan_pid, xywh, text_pid, line_offset: int):
        """Convert analiticcl's output to web annotation, may output multiple web annotations in case of ties
        """
        prev_score = None
        for top_variant in ner_result['variants']:
            if prev_score and top_variant['score'] < prev_score:
                break
            else:
                prev_score = top_variant['score']

            # ic(top_variant)
            lexicons = top_variant['lexicons']
            # note: categories starting with an underscore will not be propagated to output
            # (useful for background lexicons)
            categories = [self.category_dict[lexicon] for lexicon in lexicons if
                          lexicon in self.category_dict and self.category_dict[lexicon][0] != "_"]
            tag_bodies = []
            variantmatch_bodies = []
            if ner_result.get('tag'):
                if isinstance(ner_result['tag'],str) and ner_result['seqnr'] == 0:
                    # new style: tag set by analiticcl < 0.4.2 via contextrules  , one tag only (for backward compatibility only)
                    tag_bodies.append(self.tagging_body(label=ner_result['tag']))
                    variantmatch_bodies.append(self.variantmatch_body(phrase=ner_result['input'], variant=top_variant['text'], score=top_variant['score'], lexicons=top_variant['lexicons'], category=ner_result['tag'], seqnr=0))
                else:
                    # new style: tag set by analiticcl >= 0.4.2 via contextrules  , supports multiple tags, each will get a body
                    for tag, seqnr in zip(ner_result.get('tag',[]), ner_result.get('seqnr',[])):
                        if seqnr == 0:
                            tag_bodies.append(self.tagging_body(label=tag))
                            variantmatch_bodies.append(self.variantmatch_body(phrase=ner_result['input'], variant=top_variant['text'], score=top_variant['score'], lexicons=top_variant['lexicons'], category=tag, seqnr=seqnr))
            elif not self.has_contextrules:
                # old style: tag derived directly from lexicon , no context rules used
                if not categories:
                    continue
                for cat in categories:
                    body = self.tagging_body(label=cat)
                    tag_bodies.append(body)
                    variantmatch_bodies.append(self.variantmatch_body(phrase=ner_result['input'], variant=top_variant['text'], score=top_variant['score'], lexicons=top_variant['lexicons'], category=cat,seqnr=None))
            elif not categories:
                # background lexicon match only, don't output
                continue
            bodies = [
                {
                    "type": "TextualBody",
                    "value": top_variant['text'],
                    "modified": now(),
                    "purpose": "editing",
                },
                *tag_bodies,
                *variantmatch_bodies
            ]
            yield {
                "@context": "http://www.w3.org/ns/anno.jsonld",
                "id": random_annotation_id(),
                "type": "Annotation",
                "motivation": [
                    "classifying",
                    "editing"
                ],
                "generated": now(),
                "generator": {
                    "id": "https://github.com/knaw-huc/golden-agents-htr",
                    "type": "Software",
                    "name": "GoldenAgentsNER"
                },
                "body": bodies,
                "target": [
                    {
                        "source": text_pid,
                        "type": "Text",
                        "selector": [
                            {
                                "type": "TextPositionSelector",
                                "start": line_offset + ner_result['offset']['begin'],
                                "end": line_offset + ner_result['offset']['end']
                            }, {
                                "type": "TextQuoteSelector",
                                "exact": text_line.text[ner_result['offset']['begin']:ner_result['offset']['end']],
                                "prefix": text_line.text[:ner_result['offset']['begin']],
                                "suffix": text_line.text[ner_result['offset']['end']:],
                            }
                        ]
                    },
                    {
                        "source": scan_pid,
                        "type": "Image",
                        "selector": {
                            "type": "FragmentSelector",
                            "conformsTo": "http://www.w3.org/TR/media-frags/",
                            "value": f"xywh={xywh}"
                        }
                    }]

            }
            if self.has_contextrules:
                # ties are already resolved by analiticcl if there are context rules
                # no need to consider further top variants
                break

    def tagging_body(self, label: str, confidence: Optional[float] = None, provenance: Optional[str] = None) -> Dict[
        str, Any]:
        if self.has_resource_ids:
            if label not in self.resource_ids:
                raise Exception(f"no resourceid defined for '{label}': check config file.")
            body = {
                "type": "SpecificResource",
                "purpose": "tagging",
                "modified": now(),
                "source": {
                    "id": self.resource_ids[label],
                    "label": label
                }
            }
            if confidence:
                body['confidence'] = confidence
            if provenance:
                body['provenance'] = provenance
            return body
        else:
            return {
                "type": "TextualBody",
                "value": label,
                "modified": now(),
                "purpose": "tagging"
            }

    def variantmatch_body(self, phrase:str, variant: str, score: Optional[float], lexicons: list, category: Optional[str], seqnr: Optional[int]) -> Dict:
        d = {
            "@context": VARIANT_MATCHING_CONTEXT,
            "type": "Match",
            # the text in the input
            "phrase": phrase,
            # the variant in the lexicon that matched with the input
            "variant": variant,
        }
        if score is not None:
            # the score of the match as reported by the system (no intrinsic meaning, only to be judged relatively)
            d['score'] = score
        if lexicons:
            # the sources (lexicons/variants lists) where the match was found
            d['source'] = [os.path.basename(x) for x in lexicons]
        if category is not None:
            d['category'] = category
        if seqnr is not None:
            d['seqnr'] = int(seqnr + 1)
        elif category is not None:
            d['seqnr'] = 1
        return d
