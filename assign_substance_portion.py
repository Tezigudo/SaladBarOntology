from rdflib import Graph, Namespace, URIRef, Literal, RDF
import pandas as pd
import re

# Configuration
DRY_RUN = False # Set to False to actually modify the RDF

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
HAS_SUBSTANCE = SALAD.hasSubstance

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
substance_portions = []

for s, p, o in g.triples((None, RDF.type, None)):
    local_class = get_local_name(o)
    if local_class == "IngredientPortion":
        ingredient_portions.append(s)
    elif local_class == "DressingPortion":
        dressing_portions.append(s)
    elif local_class == "SubstancePortion":
        substance_portions.append(s)

# Counters
ingredient_assigned = 0
dressing_assigned = 0
substance_assigned = 0
missing_ingredient = []
missing_dressing = []
missing_substance = []

# Step 2: Auto-match and add hasIngredient / hasDressing, hasAmount, hasUnit for IngredientPortion and DressingPortion
for portion_uri in ingredient_portions:
    portion_name = get_local_name(portion_uri)
    base, amount, unit = extract_base_and_info(portion_name)
    ingredient_uri = SALAD[base]
    if (ingredient_uri, None, None) in g:
        if not DRY_RUN:
            g.add((portion_uri, HAS_INGREDIENT, ingredient_uri))
        ingredient_assigned += 1
    else:
        missing_ingredient.append(portion_name)
    if amount:
        if not DRY_RUN:
            g.add((portion_uri, HAS_AMOUNT, Literal(int(amount))))
    if unit:
        normalized_unit = normalize_unit(unit)
        if not DRY_RUN:
            g.add((portion_uri, HAS_UNIT, Literal(normalized_unit)))

for portion_uri in dressing_portions:
    portion_name = get_local_name(portion_uri)
    base, amount, unit = extract_base_and_info(portion_name)
    dressing_uri = SALAD[base]
    if (dressing_uri, None, None) in g:
        if not DRY_RUN:
            g.add((portion_uri, HAS_DRESSING, dressing_uri))
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

# Step 3: Assign hasSubstance, hasAmount, hasUnit for SubstancePortion
# Load Excel Sheet2
df = pd.read_excel("Salad Instance.xlsx", sheet_name=1)

approved_substances = {
    "Calcium", "Carbohydrate", "Cholesterol", "Fat", "FoodEnergy",
    "Iron", "Potassium", "Protein", "Sodium", "VitaminA", "VitaminC"
}

for idx, row in df.iterrows():
    individual_name = str(row['Individual']).strip()
    amount = row['Amount']
    unit = str(row['Unit']).strip()

    portion_uri = SALAD[individual_name]
    if (portion_uri, None, None) not in g:
        missing_substance.append(individual_name)
        continue

    # Find substance
    for substance in approved_substances:
        if individual_name.endswith(substance):
            substance_uri = SALAD[substance]
            if not DRY_RUN:
                g.add((portion_uri, HAS_SUBSTANCE, substance_uri))
            break

    if not DRY_RUN:
        g.add((portion_uri, HAS_AMOUNT, Literal(float(amount))))
        g.add((portion_uri, HAS_UNIT, Literal(unit)))
    substance_assigned += 1

# Step 4: Save back to original RDF file if not dry run
if not DRY_RUN:
    g.serialize(destination="salad_ontology.rdf", format="xml")

# Final report
print("\n✅ Assignment Summary:")
print(f"- hasIngredient assigned: {ingredient_assigned}")
print(f"- hasDressing assigned: {dressing_assigned}")
print(f"- hasSubstance assigned: {substance_assigned}")
if missing_ingredient:
    print(f"\n⚠️ Missing Ingredient matches ({len(missing_ingredient)}): {missing_ingredient}")
if missing_dressing:
    print(f"\n⚠️ Missing Dressing matches ({len(missing_dressing)}): {missing_dressing}")
if missing_substance:
    print(f"\n⚠️ Missing SubstancePortions matches ({len(missing_substance)}): {missing_substance}")
print("\n🎯 Finished assigning (Dry Run mode: {}!)".format(DRY_RUN))
