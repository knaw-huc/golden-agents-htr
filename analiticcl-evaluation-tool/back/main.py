#!/usr/bin/env python3

import json
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:2080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "This is the backend for the analiticcl-evaluation-tool"}

@app.get("/basenames")
async def get_basenames():
    with open('data/ga-selection-basenames.json') as f:
        return json.load(f)

@app.get("/pagedata/{basename}")
async def get_page_data(basename:str):
    with open(f'data/{basename}.txt', encoding='utf8') as f:
        text = f.read()
    with open(f'data/{basename}.json', encoding='utf8') as f:
        annotations = json.load(f)
    return {
        "text": text,
        "annotations": annotations
    }

@app.put("/annotations/{basename}")
async def put_annotations(basename:str, annotations:dict):
    with open(f'data/{basename}.json', 'w', encoding='utf8') as f:
        return json.dump(annotations,f)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
