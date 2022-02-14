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
        self.params = SearchParameters(**self.config['searchparameters'])
        abcfile = self.config['alphabet']
        if abcfile[0] != '/':
            # relative path:
            abcfile = os.path.join(os.path.dirname(configfile), abcfile)
        self.model = VariantModel(abcfile, Weights(**self.config['weights']), debug=0)
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
        self.model.build()
        if HTR_CORRECTIONS in self.config:
            corrections_file = self.config[HTR_CORRECTIONS]
            print(f"using htr corrections from {corrections_file}",file=sys.stderr)
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
            for result in ner_results:
                raw_results.append(result)
                if (
                        len(result['variants']) > 0
                        and result['variants'][0]['score'] >= self.config.get('score-threshold', 0)
                ):
                    xywh = f"{tl.coords.x},{tl.coords.y},{tl.coords.w},{tl.coords.h}"
                    annotations += list(self.create_web_annotation(scan.id, tl, result, iiif_url=scan.transkribus_uri, xywh=xywh,
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
            categories = [self.category_dict[l] for l in lexicons if self.category_dict[l][0] != "_"]
            if not categories:
                continue
            tag_bodies = []
            for cat in categories:
                body = {
                    "type": "TextualBody",
                    "value": cat,
                    "modified": datetime.today().isoformat(),
                    "purpose": "tagging"
                }
                tag_bodies.append(body)
            bodies = [
                *tag_bodies,
                {
                    "type": "TextualBody",
                    "value": top_variant['text'],
                    "modified": datetime.today().isoformat(),
                    "purpose": "commenting",
                },
                {"type": "TextualBody", "value": categories, "purpose": "classifying"},
                {
                    "type": "Dataset",
                    "value": {
                        "match_phrase": ner_result['input'],
                        "match_variant": top_variant['text'],
                        "match_score": top_variant['score'],
                        "category": categories,
                    },
                },
            ]
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
                            "exact": ner_result['input']
                        }
                        ]
                    }
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
        }
