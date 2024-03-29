#!/usr/bin/env python3

from sparql_common import query

if __name__ == "__main__":
    URL = "https://api.druid.datalegend.net/datasets/AdamNet/Heritage/services/Heritage/sparql"

    q = """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX hg: <http://rdf.histograph.io/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?street ?label WHERE {

      ?street a hg:Building ;
        skos:altLabel ?label .

    }
    """

    df = query(q, URL)
    df.to_csv('buildingsAdamlink.csv', index=False)
