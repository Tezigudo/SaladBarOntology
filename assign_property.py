from rdflib import Graph, Namespace, URIRef, Literal, RDF
import os
import re

# Load your RDF graph
g = Graph()
g.parse("salad_ontology.rdf", format="xml")

# Define Namespace
SALAD = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# Property URIs
HAS_INGREDIENT = SALAD.hasIngredient
HAS_DRESSING = SALAD.hasDressing
HAS_AMOUNT = SALAD.hasAmount
HAS_UNIT = SALAD.hasUnit

# Helper functions
def get_local_name(uri):
    return uri.split("#")[-1]

def extract_base_and_info(portion_name):
    match = re.match(r"([A-Za-z]+)([0-9]+)([a-zA-Z]*)", portion_name)
    if match:
        base = match.group(1)
        amount = match.group(2)
        unit = match.group(3)
        return base, amount, unit
    else:
        return portion_name, None, None

# Step 1: Identify IngredientPortion and DressingPortion
ingredient_portions = []
dressing_portions = []

for s, p, o in g.triples((None, RDF.type, None)):
    local_class = get_local_name(o)
    if local_class == "IngredientPortion":
        ingredient_portions.append(s)
    elif local_class == "DressingPortion":
        dressing_portions.append(s)

# Counters
ingredient_assigned = 0
dressing_assigned = 0
missing_ingredient = []
missing_dressing = []

# Step 2: Auto-match and add hasIngredient / hasDressing, hasAmount, hasUnit
for portion_uri in ingredient_portions:
    portion_name = get_local_name(portion_uri)
    base, amount, unit = extract_base_and_info(portion_name)
    ingredient_uri = SALAD[base]
    if (ingredient_uri, None, None) in g:
        g.add((portion_uri, HAS_INGREDIENT, ingredient_uri))
        ingredient_assigned += 1
    else:
        missing_ingredient.append(portion_name)
    if amount:
        g.add((portion_uri, HAS_AMOUNT, Literal(int(amount))))
    if unit:
        g.add((portion_uri, HAS_UNIT, Literal(unit)))

for portion_uri in dressing_portions:
    portion_name = get_local_name(portion_uri)
    base, amount, unit = extract_base_and_info(portion_name)
    dressing_uri = SALAD[base]
    if (dressing_uri, None, None) in g:
        g.add((portion_uri, HAS_DRESSING, dressing_uri))
        dressing_assigned += 1
    else:
        missing_dressing.append(portion_name)
    if amount:
        g.add((portion_uri, HAS_AMOUNT, Literal(int(amount))))
    if unit:
        g.add((portion_uri, HAS_UNIT, Literal(unit)))

# Step 3: Save back to original RDF file
g.serialize(destination="salad_ontology.rdf", format="xml")

# Final report
print("\n✅ Assignment Summary:")
print(f"- hasIngredient assigned: {ingredient_assigned}")
print(f"- hasDressing assigned: {dressing_assigned}")
if missing_ingredient:
    print(f"\n⚠️ Missing Ingredient matches ({len(missing_ingredient)}): {missing_ingredient}")
if missing_dressing:
    print(f"\n⚠️ Missing Dressing matches ({len(missing_dressing)}): {missing_dressing}")
print("\n🎯 Finished assigning hasIngredient, hasDressing, hasAmount, and hasUnit!")
