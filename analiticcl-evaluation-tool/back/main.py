#!/usr/bin/env python3

import json
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
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
        default = {"jirsi": False, "judith": False}
        for a in load_basenames():
            checks[a] = default


def save_checks():
    with open(checkfile_path, 'w') as f:
        return json.dump(checks, f)


@app.get("/")
async def root():
    return {"message": "This is the backend for the analiticcl-evaluation-tool"}


@app.get("/basenames")
async def get_basenames():
    return load_basenames()


def load_basenames():
    with open('data/ga-selection-basenames.json') as f:
        return json.load(f)


@app.get("/pagedata/{basename}/{version}")
async def get_page_data(basename: str,version:str):
    with open(f'data/{basename}.txt', encoding='utf8') as f:
        text = f.read()
    with open(f'data/{basename}.{version}.json', encoding='utf8') as f:
        annotations = json.load(f)
    return {
        "text": text,
        "annotations": annotations,
        "checked": {
            "jirsi": False,
            "judith": False
        }
    }


@app.put("/annotations/{basename}")
async def put_annotations(basename: str, body: dict):
    annotation = body['annotation']
    with open(f'data/{basename}.json', 'w', encoding='utf8') as f:
        json.dump(annotation, f)
    load_checks()
    checks[basename] = body['checked']
    save_checks()
    return body


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
