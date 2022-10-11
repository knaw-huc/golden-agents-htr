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
        df = pd.concat([df, new_df])

    return df
