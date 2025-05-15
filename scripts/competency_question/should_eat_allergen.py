import os
from pathlib import Path
from prettytable import PrettyTable

from owlready2 import *
import rdflib

# File setup
name = Path(__file__).stem
ontology_path = "salad_ontology.rdf"
outfile = f"output/{name}.html"

# Step 1: Load ontology and run reasoner
onto = get_ontology(f"file://{os.path.abspath(ontology_path)}").load()
with onto:
    sync_reasoner()  # Runs HermiT-like reasoner to infer new facts

# Step 2: Export inferred ontology to RDFLib Graph
graph = default_world.as_rdflib_graph()

# Step 3: SPARQL query
def rename_uri(uri):
    try:
        return str(uri).replace(
            "http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#", ""
        )
    except:
        return str(uri)

def should_eat_allergen():
    return """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>

SELECT ?safeSalad ?person
WHERE {
  ?safeSalad a s:Salad.
  ?person a s:Person.
  MINUS {
    ?safeSalad s:isNotFor ?person .
    FILTER(?person = s:Preawpan)
  }
}
    }
    """

if __name__ == "__main__":
    table = PrettyTable()
    table.field_names = ["salad"]
    table.align = "l"

    query_str = should_eat_allergen()
    result = graph.query(query_str)

    for row in result:
        table.add_row([rename_uri(row.salad)])

    print(table.get_string())

    with open(outfile, "w+") as f:
        f.write(table.get_html_string())
