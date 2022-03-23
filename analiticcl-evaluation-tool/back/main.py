#!/usr/bin/env python3

import json
import os
from typing import Dict, Any, List

import markdown
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

origins = [
    # "http://localhost",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

checkfile_path = 'data/checked.json'
checks = {}


def load_checks():
    global checks
    if os.path.exists(checkfile_path):
        with open(checkfile_path) as f:
            checks = json.load(f)
    else:
        default = {"harm": False,"jirsi": False, "judith": False}
        for a in load_basenames():
            checks[a] = default


def save_checks():
    with open(checkfile_path, 'w') as f:
        return json.dump(checks, f)


@app.get("/")
async def root():
    return {"message": "This is the backend for the analiticcl-evaluation-tool"}


@app.get("/versions")
async def get_versions():
    versions = set()
    for annotation_file in os.listdir('data'):
        if annotation_file.endswith('.json'):
            parts = annotation_file.split('.')
            if len(parts) == 3:
                versions.add(parts[1])
    return sorted(list(versions))


@app.get("/basenames")
async def get_basenames():
    return load_basenames()

@app.get("/checks")
async def get_checks():
    load_checks()
    return checks


def load_basenames():
    with open('data/ga-selection-basenames.json') as f:
        return json.load(f)

def load_url_dict():
    with open('data/page-selection.json') as f:
        return json.load(f)


@app.get("/pagedata/{basename}/{version}")
async def get_page_data(basename: str, version: str):
    transkribus_url = load_url_dict()
    load_checks()
    text_file = f'data/{basename}.txt'
    if not os.path.exists(text_file):
        _file_not_found(text_file)
    with open(text_file, encoding='utf8') as f:
        text = f.read()
    annotations_file = f'data/{basename}.{version}.json'
    if not os.path.exists(annotations_file):
        _file_not_found(annotations_file)
    with open(annotations_file, encoding='utf8') as f:
        annotations = json.load(f)
    return {
        "text": text,
        "annotations": annotations,
        "transkribus_url": transkribus_url[basename],
        "checked": {
            "harm": checks[basename]['harm'],
            "jirsi": checks[basename]['jirsi'],
            "judith": checks[basename]['judith']
        }
    }


class AnnotationUpdateBody(BaseModel):
    annotations: List[Dict]
    checked: Dict[str, Any]


@app.put("/annotations/{basename}/{version}")
async def put_annotations(basename: str, version: str, aub: AnnotationUpdateBody):
    annotations = aub.annotations
    with open(f'data/{basename}.{version}.json', 'w', encoding='utf8') as f:
        json.dump(annotations, f, indent=4)
    load_checks()
    checks[basename] = aub.checked
    save_checks()
    return aub


@app.get("/html/{filename}.html", response_class=HTMLResponse)
async def get_html(filename: str):
    filepath = f'doc/{filename}.md'
    if not os.path.exists(filepath):
        _file_not_found(filepath)
    with open(filepath, "r", encoding="utf-8") as input_file:
        text = input_file.read()
    return markdown.markdown(text)


def _file_not_found(filepath: str):
    raise HTTPException(status_code=404, detail=f"File not found: {filepath}")


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
