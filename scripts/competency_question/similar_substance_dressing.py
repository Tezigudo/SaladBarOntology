import os
import rdflib.graph as g
from pathlib import Path
from prettytable import PrettyTable


name = Path(__file__).stem
ontology = "salad_ontology.rdf"
outfile = f"output/{name}.html"

graph = g.Graph()
graph.parse(ontology, format='xml')

def rename_uri(uri):
    try:
        return uri.replace(
            "http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#", ""
        )
    except:
        return uri


def similar_substance():
    return """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>

    SELECT DISTINCT ?dressingX ?substancesX ?dressingY ?substancesY
    WHERE {
        {
            SELECT ?saladX ?dressingX (GROUP_CONCAT(DISTINCT ?substanceX; SEPARATOR=",") AS ?substancesX)
            WHERE {
                ?saladX rdf:type s:Salad .
                ?saladX s:hasDressingPortion ?dressingPortionX .
                ?dressingPortionX s:hasDressing ?dressingX .
                ?dressingX s:hasSubstancePortion ?substancePortionX .
                ?substancePortionX s:hasSubstance ?substanceX .
            }
            GROUP BY ?saladX ?dressingX
        }


        {
            SELECT ?saladY ?dressingY (GROUP_CONCAT(DISTINCT ?substanceY; SEPARATOR=",") AS ?substancesY)
            WHERE {
                ?saladY rdf:type s:Salad .
                ?saladY s:hasDressingPortion ?dressingPortionY .
                ?dressingPortionY s:hasDressing ?dressingY .
                ?dressingY s:hasSubstancePortion ?substancePortionY .
                ?substancePortionY s:hasSubstance ?substanceY .
            }
            GROUP BY ?saladY ?dressingY
        }
        BIND(STRAFTER(STR(?substancesX), ",") AS ?substancesX)
        BIND(STRAFTER(STR(?substancesY), ",") AS ?substancesY)
        FILTER (?dressingX != ?dressingY && CONTAINS(?substancesY, ?substancesX))
    }
    """

if __name__ == "__main__":
    table = PrettyTable()
    table.field_names = [
        "dressingX",
        "substancesX",
        "dressingY",
        "substancesY"

    ]
    table.align = "l"
    
    query_str = similar_substance()
    result = graph.query(query_str)
    print(f"Found {len(result)} results.")

    for row in result:
        table.add_row([
            rename_uri(row.dressingX),
            rename_uri(row.substancesX),
            rename_uri(row.dressingY),
            rename_uri(row.substancesY)
        ])
    
    print(table.get_string())
    
    with open(outfile, "w+") as s:
        s.write(table.get_html_string())