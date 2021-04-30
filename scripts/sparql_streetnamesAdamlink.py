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

    URL = "https://api.druid.datalegend.net/datasets/AdamNet/Heritage/services/Heritage/sparql"

    q = """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX hg: <http://rdf.histograph.io/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?street ?label WHERE {

      ?street a hg:Street ;
        skos:altLabel ?label .

    }
    """

    df = query(q, URL)
    df.to_csv('streetnamesAdamlink.csv', index=False)
