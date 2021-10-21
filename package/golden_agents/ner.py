import json
import os.path
import uuid
from datetime import datetime
from typing import List

from analiticcl import VariantModel, Weights, SearchParameters
from icecream import ic
from pagexml.parser import PageXMLTextLine, parse_pagexml_file


def text_line_urn(archive_id: str, scan_id: str, textline_id: str):
    return f"urn:golden-agents:{archive_id}:scan={scan_id}:textline={textline_id}"

def create_scan_id(file) -> str:
    path_parts = file.split('/')
    archive_id = path_parts[-2]
    scan_id = path_parts[-1].replace('.xml', '')
    return f"urn:golden-agents:{archive_id}:scan={scan_id}"


class NER:
    def __init__(self, configfile: str):
        """Instantiates a NER tagger with variantmodel; loads all lexicons"""
        with open(configfile,'rb') as f:
            self.config = json.load(f)
        for key in ("lexicons","searchparameters","alphabet","weights"):
            if key not in self.config:
                raise ValueError(f"Missing required key in configuration file: {key}")
        self.category_dict = { filepath: category for category,filepath in self.config['lexicons'].items() }
        self.params = SearchParameters(**self.config['searchparameters'])
        abcfile = self.config['alphabet']
        if abcfile[0] != '/':
            #relative path:
            abcfile = os.path.join( os.path.dirname(configfile), abcfile)
        self.model = VariantModel(abcfile, Weights(**self.config['weights']), debug=0)
        for filepath in self.config['lexicons'].values():
            if not os.path.exists(filepath):
                raise FileNotFoundError(filepath)
            self.model.read_lexicon(filepath)
        self.model.build()

    def process_pagexml(self, file: str) -> list:
        """Runs the NER tagging on a PageXML file, returns a list of web annotations"""
        scan = parse_pagexml_file(file)
        if not scan.id:
            scan.id = create_scan_id(file)
        #TODO: remove hardcoded urls
        scan.transkribus_uri = "https://files.transkribus.eu/iiif/2/MOQMINPXXPUTISCRFIRKIOIX/full/max/0/default.jpg"
        return self.create_web_annotations(scan, "http://localhost:8080/textrepo/versions/x")

    def process_line(self, text_line: PageXMLTextLine):
        """Invokes analiticcl on a text line from the pagexml"""
        return self.model.find_all_matches(text_line.text, self.params)

    def create_web_annotations(self, scan, version_base_uri: str) -> List[dict]:
        """Find lines in the scan and pass them to the tagger, producing web-annotations"""
        annotations = []
        for tl in [l for l in scan.get_lines() if l.text]:
            ner_results = self.process_line(tl)
            for result in ner_results:
                if (
                        len(result['variants']) > 0
                        and result['variants'][0]['score'] > 0.8
                ):
                    xywh = f"{tl.coords.x},{tl.coords.y},{tl.coords.w},{tl.coords.h}"
                    wa = self.create_web_annotation(scan.id, tl, result, iiif_url=scan.transkribus_uri, xywh=xywh,
                                                    version_base_uri=version_base_uri)
                    annotations.append(wa)
        return annotations

    def create_web_annotation(self, scan_urn: str, text_line: PageXMLTextLine, ner_result, iiif_url, xywh,
                              version_base_uri):
        """Convert analiticcl's output to web annotation"""
        top_variant = ner_result['variants'][0]
        # ic(top_variant)
        lexicons = top_variant['lexicons']
        categories = [self.category_dict[l] for l in lexicons]
        if len(categories) == 1:
            categories = categories[0]
        return {
            "@context": ["http://www.w3.org/ns/anno.jsonld", "https://leonvanwissen.nl/vocab/roar/roar.json"],
            "id": str(uuid.uuid4()),
            "type": "Annotation",
            "motivation": "classifying",
            "created": datetime.today().isoformat(),
            "generator": {
                "id": "https://github.com/knaw-huc/golden-agents-htr",
                "type": "Software",
                "name": "GoldenAgentsNER"
            },
            "body": [
                {
                    "type": "TextualBody",
                    "purpose": "classifying",
                    "value": categories
                },
                {
                    "type": "Dataset",
                    "value": {
                        "match_phrase": ner_result['input'],
                        "match_variant": top_variant['text'],
                        "match_score": top_variant['score'],
                        "category": categories
                    }
                }],
            "target": [
                {
                    "source": f'{scan_urn}:textline={text_line.id}',
                    "selector": {
                        "type": "TextPositionSelector",
                        "start": ner_result['offset']['begin'],
                        "end": ner_result['offset']['end']
                    }
                },
                {
                    "source": f'{scan_urn}:textline={text_line.id}',
                    "selector": {
                        "type": "FragmentSelector",
                        "conformsTo": "http://tools.ietf.org/rfc/rfc5147",
                        "value": f"char={ner_result['offset']['begin']},{ner_result['offset']['end']}"
                    }
                },
                {
                    "source": f'{version_base_uri}/contents',
                    "type": "xml",
                    "selector": {
                        "type": "FragmentSelector",
                        "conformsTo": "http://tools.ietf.org/rfc/rfc3023",
                        "value": f"xpointer(id({text_line.id})/TextEquiv/Unicode)"
                    }
                },
                {
                    "source": f"{version_base_uri}/chars/{ner_result['offset']['begin']}/{ner_result['offset']['end']}"
                },
                {
                    "source": iiif_url,
                    "type": "image",
                    "selector": {
                        "type": "FragmentSelector",
                        "conformsTo": "http://www.w3.org/TR/media-frags/",
                        "value": f"xywh={xywh}"
                    }
                }
            ]
        }
