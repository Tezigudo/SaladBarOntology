from rdflib import Graph, Namespace, URIRef, Literal, RDF
import pandas as pd
import re

# Configuration
DRY_RUN = False # Set to True for dry run mode (no write)

# Load RDF graph
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
def normalize_name(name):
    return name.replace('\u200b', '').replace('\xa0', '').replace(' ', '').strip()

def get_local_name(uri):
    return normalize_name(uri.split("#")[-1])

def extract_base_and_info(portion_name):
    portion_name = normalize_name(portion_name)
    match = re.search(r'([0-9]+(?:\.[0-9]+)?)([a-zA-Z]*)$', portion_name)
    if match:
        amount = match.group(1)
        unit = match.group(2)
        base = portion_name[:match.start()]
        return base.strip(), amount, unit
    else:
        return portion_name, None, None

def normalize_unit(unit):
    unit = unit.lower()
    if unit == "g":
        return "grams"
    elif unit == "ml":
        return "millilitres"
    elif unit == "μg/100g":
        return "mg/100g"
    return unit

# Step 1: Identify all Portions and Individuals
ingredient_portions = []
dressing_portions = []
substance_portions = []
all_existing_individuals = set()

for s, p, o in g.triples((None, RDF.type, None)):
    local_class = get_local_name(o)
    local_name = get_local_name(s)
    all_existing_individuals.add(local_name)
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

# Step 2: Auto-match hasIngredient and hasDressing
for portion_uri in ingredient_portions:
    portion_name = get_local_name(portion_uri)
    base, amount, unit = extract_base_and_info(portion_name)
    if base in all_existing_individuals:
        if not DRY_RUN:
            g.add((portion_uri, HAS_INGREDIENT, SALAD[base]))
        ingredient_assigned += 1
    else:
        missing_ingredient.append(portion_name)

for portion_uri in dressing_portions:
    portion_name = get_local_name(portion_uri)
    base, amount, unit = extract_base_and_info(portion_name)
    if base in all_existing_individuals:
        if not DRY_RUN:
            g.add((portion_uri, HAS_DRESSING, SALAD[base]))
        dressing_assigned += 1
    else:
        missing_dressing.append(portion_name)

# Step 3: Assign hasSubstance for SubstancePortions
df = pd.read_excel("Salad Instance.xlsx", sheet_name=1)

approved_substances = {
    "Calcium", "Carbohydrate", "Cholesterol", "Fat", "FoodEnergy",
    "Iron", "Potassium", "Protein", "Sodium", "VitaminA", "VitaminC",
    "VitaminE", "Lutein", "Zeaxanthin", "Zinc", "Omega-3", "VitaminB9"
}

for idx, row in df.iterrows():
    individual_name = normalize_name(str(row['Individual']))
    amount = row['Amount']
    unit = normalize_unit(str(row['Unit']))

    if not individual_name or pd.isna(amount) or not unit:
        continue  # Skip incomplete data

    if individual_name not in all_existing_individuals:
        missing_substance.append(individual_name)
        continue

    portion_uri = SALAD[individual_name]

    # Match Substance
    matched = False
    for substance in approved_substances:
        if individual_name.endswith(substance):
            substance_uri = SALAD[substance]
            if not DRY_RUN:
                g.add((portion_uri, HAS_SUBSTANCE, substance_uri))
            matched = True
            break
    if not matched:
        missing_substance.append(individual_name)
        continue

    final_amount = float(amount)

    # Fix units
    if unit == "μg/100g":
        final_amount = final_amount / 1000  # μg ➔ mg
        unit = "mg/100g"
    elif unit == "g/100g":
        final_amount = final_amount * 1000  # g ➔ mg
        unit = "mg/100g"

    if not DRY_RUN:
        g.add((portion_uri, HAS_AMOUNT, Literal(final_amount)))
        g.add((portion_uri, HAS_UNIT, Literal(unit)))

    substance_assigned += 1

# Step 4: Save if not dry run
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
print("\n🎯 Finished assigning! (Dry Run Mode: {})".format(DRY_RUN))
