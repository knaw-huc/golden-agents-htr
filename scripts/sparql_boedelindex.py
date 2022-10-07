#!/usr/bin/env python3

import sys

from sparql_common import query

if __name__ == "__main__":
    URL = "https://sparql.goldenagents.org/"

    q = """
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX schema: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX roar: <https://data.goldenagents.org/ontology/roar/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?akteIndex ?eventTypeLabel ?scanNaam ?inventoryNumber WHERE {
      GRAPH <https://data.goldenagents.org/datasets/u692bc364e9d7fa97b3510c6c0c8f2bb9a0e5123b/na_20220216> {
        
        # Index op een akte (URI = Stadsarchief)
        ?akteIndex a roar:IndexDocument ;
#  		  rdfs:comment ?onderwerpsomschrijving ;
              roar:indexOf ?akte ;
              roar:mentionsEvent ?event .
        
        # Registratie van een Event van een type
        ?event a ?eventType .
        
        # Eventtype heeft een naam
        ?eventType rdfs:label ?eventTypeLabel .
        
        # Fysieke akte (URI = GA)
        ?akte a <https://data.goldenagents.org/thesaurus/NotarieleArchieven> ;
              roar:createdAt ?date ;
#          roar:createdBy ?notaris ;
              roar:hasScan ?scan ;
              roar:partOf ?inventory .
        
        # Scan heeft een label (naam = bestandsnaam)
        ?scan a roar:Scan ;
              rdfs:label ?scanNaam .
              
        ?inventory a roar:InventoryBook .
        
        ?inventoryIndex roar:indexOf ?inventory ;
                        dcterms:identifier ?inventoryNumber ;
                        rdfs:label ?inventoryName .
      
        # Alleen boedelscheidingen en boedelinventarissen
        FILTER(
            REGEX(?eventTypeLabel, 'boedel', 'i') || 
            ?eventTypeLabel = "Huwelijkse Voorwaarden" || 
            ?eventTypeLabel = "Testament" 
        )
        
      }
    }
"""
    df = query(q, URL)
    df.to_csv(sys.stdout, index=False)
