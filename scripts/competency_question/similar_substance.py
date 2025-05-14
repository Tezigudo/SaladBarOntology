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


def similar_substance():
    return """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX f: <http://www.semanticweb.org/nappaskorn/ontologies/2023/10/food-for-people-with-chronic-disease#>
    
    SELECT DISTINCT ?ingredientX ?substancesX ?ingredientY ?substancesY
    WHERE {
        {
            SELECT ?foodX ?ingredientX (GROUP_CONCAT(DISTINCT ?substanceX; SEPARATOR=",") AS ?substancesX)
            WHERE {
                ?foodX rdf:type f:Food .
                ?foodX f:hasIngredientPortion ?ingredientPortionX .
                ?ingredientPortionX f:hasIngredient ?ingredientX .
                ?ingredientX f:hasSubstancePortion ?substancePortionX .
                ?substancePortionX f:hasSubstance ?substanceX .
            }
            GROUP BY ?foodX ?ingredientX
        }

        {
            SELECT ?foodY ?ingredientY (GROUP_CONCAT(DISTINCT ?substanceY; SEPARATOR=",") AS ?substancesY)
            WHERE {
                ?foodY rdf:type f:Food .
                ?foodY f:hasIngredientPortion ?ingredientPortionY .
                ?ingredientPortionY f:hasIngredient ?ingredientY .
                ?ingredientY f:hasSubstancePortion ?substancePortionY .
                ?substancePortionY f:hasSubstance ?substanceY .
            }
            GROUP BY ?foodY ?ingredientY
        }
        BIND(STRAFTER(STR(?substancesX), ",") AS ?substancesX)
        BIND(STRAFTER(STR(?substancesY), ",") AS ?substancesY)

        FILTER (?ingredientX != ?ingredientY && CONTAINS(?substancesY, ?substancesX))
        
    }

    """
if __name__ == "__main__":
    table = PrettyTable()
    table.field_names = [
        "ingredientX",
        "substancesX",
        "ingredientY",
        "substancesY"

    ]
    table.align = "l"
    
    query_str = similar_substance()
    result = graph.query(query_str)

    for row in result:
        table.add_row([
            rename_uri(row.ingredientX),
            rename_uri(row.substancesX),
            rename_uri(row.ingredientY),
            rename_uri(row.substancesY)
        ])
    
    print(table.get_string())
    
    with open(outfile, "w+") as f:
        f.write(table.get_html_string())