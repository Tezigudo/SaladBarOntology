import rdflib
from rdflib import URIRef, Literal
from rdflib.namespace import RDF

# Initialize RDF graph
g = rdflib.Graph()
# Load ontology (adjust path to your ontology file)
ontology_file = "salad_ontology.rdf"  # Update with your file path
try:
    g.parse(ontology_file, format="xml")
except Exception as e:
    print(f"Error loading ontology: {e}")
    exit(1)

# Define namespace
S = rdflib.Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# Find all Salad instances
salads = [s for s, _, t in g.triples((None, RDF.type, S.Salad)) if t == S.Salad]

# Create SaladNutrientTotal instances and link them
for salad in salads:
    salad_name = str(salad).split('#')[-1]
    nutrient_instance = URIRef(f"{S}{salad_name}Nutrition")
    g.add((nutrient_instance, RDF.type, S.SaladNutrientTotal))
    g.add((salad, S.hasNutrient, nutrient_instance))
    print(f"Added {nutrient_instance} for {salad} with s:hasNutrient link.")

# Save the updated ontology
output_file = "salad_ontology.rdf"
try:
    g.serialize(output_file, format="xml")
except Exception as e:
    print(f"Error saving ontology: {e}")
    exit(1)

print(f"Ontology updated with SaladNutrientTotal instances and saved to {output_file}")
print("Run the reasoner and individual property scripts next.")