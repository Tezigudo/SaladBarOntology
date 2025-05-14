import os
import rdflib.graph as g
from pathlib import Path
from prettytable import PrettyTable


name = Path(__file__).stem
directory = os.path.dirname(__file__)
ontology = os.path.abspath(os.path.join(directory, "..", "", "ke2_project.rdf"))
outfile = os.path.abspath(os.path.join(directory, "..", "output", f"{name}.html"))

graph = g.Graph()
graph.parse(ontology, format='xml')

def rename_uri(uri):
    try:
        return uri.replace(
            "http://www.semanticweb.org/nappaskorn/ontologies/2023/10/food-for-people-with-chronic-disease#", ""
        )
    except:
        return uri

def substance_contain_in_food():
    return """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX f: <http://www.semanticweb.org/nappaskorn/ontologies/2023/10/food-for-people-with-chronic-disease#>

    SELECT ?substance ?food
    WHERE {
        ?food rdf:type f:Food .
        ?food f:hasIngredientPortion ?ingredientPortion .
        ?ingredientPortion f:hasIngredient ?ingredient .
        ?ingredient f:hasSubstancePortion ?substancePortion .
        ?substancePortion f:hasSubstance ?substance .
    }
    GROUP BY ?substance ?food
"""

if __name__ == "__main__":
    table = PrettyTable()
    table.field_names = [
        "food",
        "substance"
    ]
    table.align = "l"
    
    query_str = substance_contain_in_food()
    result = graph.query(query_str)
    
    for row in result:
        table.add_row([
            rename_uri(row.food),
            rename_uri(row.substance)
        ])
    
    print(table.get_string())
    
    with open(outfile, "w+") as f:
        f.write(table.get_html_string())