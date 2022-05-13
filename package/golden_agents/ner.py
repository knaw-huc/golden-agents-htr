import json
import os.path
import sys
import uuid
from datetime import datetime
from typing import List

from analiticcl import VariantModel, Weights, SearchParameters
from golden_agents.corrections import Corrector
from pagexml.parser import PageXMLTextLine, parse_pagexml_file


def text_line_urn(archive_id: str, scan_id: str, textline_id: str):
    return f"urn:golden-agents:{archive_id}:scan={scan_id}:textline={textline_id}"


def create_scan_id(file) -> str:
    path_parts = file.split('/')
    if len(path_parts) >= 2:
        archive_id = path_parts[-2]
    else:
        archive_id = "unknown"
        print(
            f"WARNING: No archive component could be extracted for {file} because input file has no archive directory component",
            file=sys.stderr)
    scan_id = path_parts[-1].replace('.xml', '')
    return f"urn:golden-agents:{archive_id}:scan={scan_id}"


def fixpath(filepath: str, configfile: str) -> str:
    """Turns a relative path relative to the config file into a relative path relative to the caller"""
    if filepath[0] != '/':
        # relative path:
        filepath = os.path.join(os.path.dirname(configfile), filepath)
    return filepath


HTR_CORRECTIONS = 'htr_corrections'


class NER:
    def __init__(self, configfile: str):
        """Instantiates a NER tagger with variantmodel; loads all lexicons specified in the configuration (and parameters)"""
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
        self.model.build()
        if HTR_CORRECTIONS in self.config:
            corrections_file = self.config[HTR_CORRECTIONS]
            print(f"using htr corrections from {corrections_file}", file=sys.stderr)
            with open(corrections_file) as f:
                corrections_dict = json.load(f)
            self.htr_corrector = Corrector(corrections_dict)

    def process_pagexml(self, file: str) -> (list, str, list):
        """Runs the NER tagging on a PageXML file, returns a list of web annotations"""
        scan = parse_pagexml_file(file)
        if not scan.id:
            scan.id = create_scan_id(file)
        # TODO: remove hardcoded urls
        scan.transkribus_uri = "https://files.transkribus.eu/iiif/2/MOQMINPXXPUTISCRFIRKIOIX/full/max/0/default.jpg"
        return self.create_web_annotations(scan, "http://localhost:8080/textrepo/versions/x")

    def create_web_annotation_multispan(self, ner_results, text_line: PageXMLTextLine, line_offset: int, scan_urn: str):
        """Extract larger tagged entities from NER results and creates web annotations for them."""
        for i, ner_result in enumerate(ner_results):
            if 'tag' in ner_result and ner_result.get('seqnr') == 0:
                length = 1
                # aggregate text of the top variants
                variant_text = ner_result['variants'][0]['text']
                last_ner_result = ner_result
                for j, ner_result2 in enumerate(ner_results[i + 1:]):
                    if ner_result2.get('tag') == ner_result.get('tag') and ner_result2.get('seqnr') == j + 1:
                        length += 1
                        variant_text += " " + ner_result2['variants'][0]['text']
                        last_ner_result = ner_result2
                    else:
                        break
                if length > 1:
                    yield {
                        "@context": ["http://www.w3.org/ns/anno.jsonld",
                                     "https://leonvanwissen.nl/vocab/roar/roar.json"],
                        "id": str(uuid.uuid4()),
                        "type": "Annotation",
                        "motivation": "classifying",
                        "generated": datetime.today().isoformat(),
                        "generator": {
                            "id": "https://github.com/knaw-huc/golden-agents-htr",
                            "type": "Software",
                            "name": "GoldenAgentsNER"
                        },
                        "body": [{
                            "type": "TextualBody",
                            "value": ner_result['tag'],
                            "modified": datetime.today().isoformat(),
                            "purpose": "tagging"
                        },
                            {
                                "type": "Dataset",
                                "value": {
                                    # the text in the input
                                    "match_phrase": text_line.text[
                                                    ner_result['offset']['begin']:last_ner_result['offset']['end']],
                                    # aggregate text of the top variants
                                    "match_variant": variant_text,
                                    "category": ner_result['tag']
                                },
                            }],
                        "target":
                            {
                                "source": f'{scan_urn}',
                                "selector": [{
                                    "type": "TextPositionSelector",
                                    "start": line_offset + ner_result['offset']['begin'],
                                    "end": line_offset + last_ner_result['offset']['end']
                                }, {
                                    "type": "TextQuoteSelector",
                                    "exact": text_line.text[
                                             ner_result['offset']['begin']:last_ner_result['offset']['end']],
                                    "prefix": text_line.text[:ner_result['offset']['begin']],
                                    "suffix": text_line.text[last_ner_result['offset']['end']:],
                                }
                                ]
                            }
                    }

    def create_web_annotations(self, scan, version_base_uri: str) -> (List[dict], str, List[dict]):
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
                for entity_wa in self.create_web_annotation_multispan(ner_results, tl, len(plain_text), scan.id):
                    annotations.append(entity_wa)
            for result in ner_results:
                raw_results.append(result)
                if (
                        len(result['variants']) > 0
                        and result['variants'][0]['score'] >= self.config.get('score-threshold', 0)
                ):
                    xywh = f"{tl.coords.x},{tl.coords.y},{tl.coords.w},{tl.coords.h}"
                    annotations += list(
                        self.create_web_annotation(scan.id, tl, result, iiif_url=scan.transkribus_uri, xywh=xywh,
                                                   version_base_uri=version_base_uri, line_offset=len(plain_text)))
            plain_text += f"{text}\n"
        return (annotations, plain_text, raw_results)

    def create_web_annotation(self, scan_urn: str, text_line: PageXMLTextLine, ner_result, iiif_url, xywh,
                              version_base_uri, line_offset: int):
        """Convert analiticcl's output to web annotation, may output multiple web annotations in case of ties
        """
        prevscore = None
        for top_variant in ner_result['variants']:
            if prevscore and top_variant['score'] < prevscore:
                break
            else:
                prevscore = top_variant['score']

            # ic(top_variant)
            lexicons = top_variant['lexicons']
            # note: categories starting with an underscore will not be propagated to output (useful for background lexicons)
            categories = [self.category_dict[l] for l in lexicons if
                          l in self.category_dict and self.category_dict[l][0] != "_"]
            tag_bodies = []
            if 'tag' in ner_result and ner_result.get('seqnr') == 0:
                # new style: tag set by analiticcl via contextrules
                tag_bodies = [{
                    "type": "TextualBody",
                    "value": ner_result['tag'],
                    "modified": datetime.today().isoformat(),
                    "purpose": "tagging"
                }]
            elif not self.has_contextrules:
                # old style: tag derived directly from lexicon
                if not categories:
                    continue
                for cat in categories:
                    body = {
                        "type": "TextualBody",
                        "value": cat,
                        "modified": datetime.today().isoformat(),
                        "purpose": "tagging"
                    }
                    tag_bodies.append(body)
            elif not categories:
                # background lexicon match only, don't output
                continue
            bodies = [
                *tag_bodies,
                {
                    "type": "TextualBody",
                    "value": top_variant['text'],
                    "modified": datetime.today().isoformat(),
                    "purpose": "commenting",
                },
                {
                    "type": "Dataset",
                    "value": {
                        # the text in the input
                        "match_phrase": ner_result['input'],
                        # the variant in the lexicon that matched with the input
                        "match_variant": top_variant['text'],
                        # the score of the match as reported by the system (no intrinsic meaning, only to be judged
                        # relatively)
                        "match_score": top_variant['score'],
                        # the sources (lexicons/variants lists) where the match was found
                        "match_source": [os.path.basename(x) for x in top_variant['lexicons']],
                    },
                },
            ]
            if 'tag' in ner_result:
                # the tag assigned to this match
                bodies[-1]['value']['category'] = ner_result['tag']
                # the sequence number (in case the tagged sequence covers multiple items)
                bodies[-1]['value']['seqnr'] = int(ner_result['seqnr'] + 1) if 'seqnr' in ner_result else 1
            elif not self.has_contextrules:
                # old-style:
                bodies[-1]['value']['category'] = categories
            yield {
                "@context": ["http://www.w3.org/ns/anno.jsonld", "https://leonvanwissen.nl/vocab/roar/roar.json"],
                "id": str(uuid.uuid4()),
                "type": "Annotation",
                "motivation": "classifying",
                "generated": datetime.today().isoformat(),
                "generator": {
                    "id": "https://github.com/knaw-huc/golden-agents-htr",
                    "type": "Software",
                    "name": "GoldenAgentsNER"
                },
                "body": bodies,
                "target":
                    {
                        "source": f'{scan_urn}',
                        "selector": [{
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
                    }
            }
            if self.has_contextrules:
                # ties are already resolved by analiticcl if there are context rules
                break
            # {
            #     "source": f'{scan_urn}:textline={text_line.id}',
            #     "selector": [{
            #         "type": "TextPositionSelector",
            #         "start": ner_result['offset']['begin'],
            #         "end": ner_result['offset']['end']
            #     }, {
            #         "type": "TextQuoteSelector",
            #         "exact": ner_result['input']
            #
            #     }, {
            #         "type": "FragmentSelector",
            #         "conformsTo": "http://tools.ietf.org/rfc/rfc5147",
            #         "value": f"char={ner_result['offset']['begin']},{ner_result['offset']['end']}"
            #     }
            #     ]
            # },
            # {
            #     "source": f'{version_base_uri}/contents',
            #     "type": "xml",
            #     "selector": {
            #         "type": "FragmentSelector",
            #         "conformsTo": "http://tools.ietf.org/rfc/rfc3023",
            #         "value": f"xpointer(id({text_line.id})/TextEquiv/Unicode)"
            #     }
            # },
            # {
            #     "source": f"{version_base_uri}/chars/{ner_result['offset']['begin']}/{ner_result['offset']['end']}"
            # },
            # {
            #     "source": iiif_url,
            #     "type": "image",
            #     "selector": {
            #         "type": "FragmentSelector",
            #         "conformsTo": "http://www.w3.org/TR/media-frags/",
            #         "value": f"xywh={xywh}"
            #     }
            # }
            # ]
