import time

import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON


def query(q, endpoint, OFFSET=0, LIMIT=10000):

    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(q + f" OFFSET {OFFSET} LIMIT {LIMIT}")

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    df = pd.DataFrame(results['results']['bindings'])
    df = df.applymap(lambda x: x['value'] if not pd.isna(x) else "")

    if len(df) == LIMIT:

        OFFSET += LIMIT
        time.sleep(1)

        new_df = query(q, endpoint, OFFSET, LIMIT)
        df = df.append(new_df)

    return df


if __name__ == "__main__":

    URL = "https://sparql.goldenagents.org/"

    q = """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX oa: <http://www.w3.org/ns/oa#>
    PREFIX pnv: <https://w3id.org/pnv#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?person ?literalName ?givenName ?surnamePrefix ?baseSurname ?scan ?xywh WHERE {

      # Needs a GRAPH <> when we add more data to the endpoint, now the 20201204 version is used. 

      ?person pnv:hasName ?personName .
      FILTER(CONTAINS(STR(?person), 'archief'))

      ?personName a pnv:PersonName ;
      	pnv:literalName ?literalName

      OPTIONAL { ?personName pnv:givenName ?givenName . }
      OPTIONAL { ?personName pnv:surnamePrefix ?surnamePrefix . }
      OPTIONAL { ?personName pnv:baseSurname ?baseSurname . }

      ?annotation oa:hasBody ?personName ;
                  oa:hasTarget [ oa:hasSource ?source ; oa:hasSelector/rdf:value ?xywh ]
    
      BIND(STRAFTER(STR(?source), 'scan/') AS ?scan)
    }
    """

    df = query(q, URL)
    df.to_csv('personnamesNA_20201204.csv', index=False)
