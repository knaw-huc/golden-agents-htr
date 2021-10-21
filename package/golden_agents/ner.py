import uuid
from datetime import datetime
from typing import List

from analiticcl import VariantModel, Weights, SearchParameters
from icecream import ic
from pagexml.parser import PageXMLTextLine

OBJECT_LEXICON = "resources/lexicons/objects.tsv"
LOCATION_LEXICON = "resources/lexicons/locations.tsv"
OCCUPATION_LEXICON = "resources/lexicons/occupations.tsv"


def text_line_urn(archive_id: str, scan_id: str, textline_id: str):
    return f"urn:golden-agents:{archive_id}:scan={scan_id}:textline={textline_id}"


class NER:
    def __init__(self):
        self.category_dict = {
            OBJECT_LEXICON: "object",
            LOCATION_LEXICON: "location",
            OCCUPATION_LEXICON: "occupation"
        }
        self.model = VariantModel("resources/simple.alphabet.tsv", Weights(), debug=False)
        self.model.read_lexicon(OBJECT_LEXICON)
        self.model.read_lexicon(LOCATION_LEXICON)
        self.model.read_lexicon(OCCUPATION_LEXICON)
        self.model.build()

    def process_line(self, text_line: PageXMLTextLine):
        return self.model.find_all_matches(text_line.text, SearchParameters(max_edit_distance=3, max_ngram=1))

    def create_web_annotations(self, scan, version_base_uri: str) -> List[dict]:
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
