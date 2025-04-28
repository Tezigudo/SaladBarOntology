from rdflib import Graph, Namespace, URIRef, Literal, RDF
import re
from termcolor import colored

# Configuration
DRY_RUN = False # Set to True to simulate only (no real write)

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
def normalize_name(name):
    return name.replace('\u200b', '').replace('\xa0', '').replace(' ', '').strip()

def get_local_name(uri):
    return normalize_name(uri.split("#")[-1])

def extract_base_and_info(portion_name):
    portion_name = portion_name.replace('\u200b', '').replace('\xa0', '').replace(' ', '').strip()
    match = re.search(r'(\d+(\.\d+)?)([a-zA-Z]*)$', portion_name)
    if match:
        amount = match.group(1)
        unit = match.group(3)
        base = portion_name[:match.start()]
        return base, amount, unit
    else:
        return portion_name, None, None

def normalize_unit(unit):
    unit = unit.lower()
    if unit == "g":
        return "grams"
    elif unit == "ml":
        return "millilitres"
    return unit

# Step 1: Identify IngredientPortion and DressingPortion
ingredient_portions = []
dressing_portions = []
all_existing_individuals = set()

for s, p, o in g.triples((None, RDF.type, None)):
    local_class = get_local_name(o)
    subject_name = get_local_name(s)
    all_existing_individuals.add(subject_name)

    if local_class == "IngredientPortion":
        ingredient_portions.append(s)
    elif local_class == "DressingPortion":
        dressing_portions.append(s)

# Counters
ingredient_assigned = 0
dressing_assigned = 0
missing_ingredient = []
missing_dressing = []

# Step 2: Auto-match and add hasIngredient / hasDressing / hasAmount / hasUnit
for portion_uri in ingredient_portions:
    portion_name = get_local_name(portion_uri)
    base, amount, unit = extract_base_and_info(portion_name)

    if base in all_existing_individuals:
        if not DRY_RUN:
            g.add((portion_uri, HAS_INGREDIENT, SALAD[base]))
        ingredient_assigned += 1
    else:
        missing_ingredient.append(portion_name)

    if amount:
        if not DRY_RUN:
            g.add((portion_uri, HAS_AMOUNT, Literal(float(amount))))
    if unit:
        normalized_unit = normalize_unit(unit)
        if not DRY_RUN:
            g.add((portion_uri, HAS_UNIT, Literal(normalized_unit)))

for portion_uri in dressing_portions:
    portion_name = get_local_name(portion_uri)
    base, amount, unit = extract_base_and_info(portion_name)

    if base in all_existing_individuals:
        if not DRY_RUN:
            g.add((portion_uri, HAS_DRESSING, SALAD[base]))
        dressing_assigned += 1
    else:
        missing_dressing.append(portion_name)

    if amount:
        if not DRY_RUN:
            g.add((portion_uri, HAS_AMOUNT, Literal(int(amount))))
    if unit:
        normalized_unit = normalize_unit(unit)
        if not DRY_RUN:
            g.add((portion_uri, HAS_UNIT, Literal(normalized_unit)))

# Step 3: Save back to original RDF file
if not DRY_RUN:
    g.serialize(destination="salad_ontology.rdf", format="xml")

# Final report
print("\n✅ Assignment Summary:")
print(f"- hasIngredient assigned: {ingredient_assigned}")
print(f"- hasDressing assigned: {dressing_assigned}")

if missing_ingredient:
    print(f"\n⚠️ Missing Ingredient matches ({len(missing_ingredient)}):")
    for i in missing_ingredient:
        print(f"  - {i}")
if missing_dressing:
    print(f"\n⚠️ Missing Dressing matches ({len(missing_dressing)}):")
    for i in missing_dressing:
        print(f"  - {i}")

print(colored(f"\n🎯 Finished! (Dry Run Mode: {DRY_RUN})", "cyan"))
