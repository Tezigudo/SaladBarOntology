from rdflib import Graph, Namespace, URIRef, RDF
import os

# Load your RDF graph
g = Graph()
g.parse("salad_ontology.rdf", format="xml")

# Define Namespace
SALAD = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# Property URIs
HAS_INGREDIENT = SALAD.hasIngredient
HAS_DRESSING = SALAD.hasDressing


# Helper functions
def get_local_name(uri):
    return uri.split("#")[-1]

# Step 1: Identify IngredientPortion and DressingPortion
ingredient_portions = []
dressing_portions = []

for s, p, o in g.triples((None, RDF.type, None)):
    local_class = get_local_name(o)
    if local_class == "IngredientPortion":
        ingredient_portions.append(s)
    elif local_class == "DressingPortion":
        dressing_portions.append(s)

# Step 2: Auto-match and add hasIngredient / hasDressing
for portion_uri in ingredient_portions:
    portion_name = get_local_name(portion_uri)
    # Guess the ingredient name by removing trailing numbers and units (e.g., 150g)
    ingredient_candidate = ''.join([c for c in portion_name if not c.isdigit()]).rstrip("gml")
    ingredient_uri = SALAD[ingredient_candidate]
    # Add triple
    g.add((portion_uri, HAS_INGREDIENT, ingredient_uri))
    print(f"Assigned hasIngredient: {portion_name} --> {ingredient_candidate}")

for portion_uri in dressing_portions:
    portion_name = get_local_name(portion_uri)
    dressing_candidate = ''.join([c for c in portion_name if not c.isdigit()]).rstrip("gml")
    dressing_uri = SALAD[dressing_candidate]
    # Add triple
    g.add((portion_uri, HAS_DRESSING, dressing_uri))
    print(f"Assigned hasDressing: {portion_name} --> {dressing_candidate}")

# Step 3: Save back to original RDF file
g.serialize(destination="salad_ontology.rdf", format="xml")

print("\n✅ Finished assigning hasIngredient and hasDressing!")
