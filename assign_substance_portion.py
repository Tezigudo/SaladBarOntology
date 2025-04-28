from rdflib import Graph, Namespace, URIRef, RDF
import os
from collections import defaultdict
import pandas as pd
import re

# === CONFIGURATION ===
ONTOLOGY_FILE = 'salad_ontology.rdf'  # Your RDF file
EXCEL_FILE = 'Salad Instance.xlsx'    # Your Excel ground truth
DRY_RUN = False  # Set to False to actually modify and save

# List of all known Substance names
SUBSTANCE_NAMES = [
    "Calcium", "Carbohydrate", "Cholesterol", "Fat", "FoodEnergy",
    "Iron", "Potassium", "Protein", "Sodium", "VitaminA", "VitaminC",
    "VitaminE", "Lutein", "Zeaxanthin", "Zinc", "Omega-3", "VitaminB9"
]

# === SETUP ===
# Load RDF graph
g = Graph()
g.parse(ONTOLOGY_FILE)

# Load Excel Ingredient base names
df_ingredients = pd.read_excel(EXCEL_FILE, sheet_name="Individual_ingredient_dressing")
allowed_ingredient_bases = set()

for name in df_ingredients['Individual']:
    name = str(name)
    base_name = re.sub(r'[0-9]+(?:\.[0-9]+)?[a-zA-Z]*$', '', name).strip()  # remove trailing amount and unit
    allowed_ingredient_bases.add(base_name)

# Define namespace (hardcoded for reliability)
DEFAULT_NS = "http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#"
SALAD = Namespace(DEFAULT_NS)

# Define your hasSubstancePortion property
HAS_SUBSTANCE_PORTION = SALAD.hasSubstancePortion

from rdflib.namespace import RDFS

def is_ingredient_or_dressing(individual):
    for _, _, obj in g.triples((individual, RDF.type, None)):
        if obj in [SALAD.Ingredient, SALAD.Dressing]:
            return True
        for _, _, super_class in g.triples((obj, RDFS.subClassOf, None)):
            if super_class in [SALAD.Ingredient, SALAD.Dressing]:
                return True
    return False

# === FUNCTION: Find substance portions for an ingredient name ===
def find_substance_portions(base_name, missing_substances_tracker, perfect_ingredients):
    matches = []
    clean_base_name = base_name.replace('(', '').replace(')', '').replace(' ', '').replace('/', '')
    missing = 0

    for substance in SUBSTANCE_NAMES:
        candidate_name = clean_base_name + substance.replace(' ', '')
        candidate_uri = URIRef(DEFAULT_NS + candidate_name)

        if (candidate_uri, RDF.type, SALAD.SubstancePortion) in g:
            matches.append(candidate_uri)
        else:
            missing += 1
            print(f"  ⚠️ Not Found: {candidate_name}")
            missing_substances_tracker[substance] += 1

    if missing == 0:
        perfect_ingredients.append(base_name)

    return matches

# === MAIN: Assign hasSubstancePortion ===
added_triples = []
subject_count = 0
error_count = 0
missing_substances_tracker = defaultdict(int)
perfect_ingredients = []

for subj in g.subjects(RDF.type, None):
    if not is_ingredient_or_dressing(subj):
        continue

    subject_count += 1
    subj_local = str(subj).split("#")[-1]

    if subj_local not in allowed_ingredient_bases:
        print(f"[WARNING] {subj_local} not found in Excel Ingredient list!")

    matched_portions = find_substance_portions(subj_local, missing_substances_tracker, perfect_ingredients)

    if not matched_portions:
        print(f"[WARNING] No SubstancePortion found for {subj_local}")
        error_count += 1

    for portion in matched_portions:
        portion_local = str(portion).split("#")[-1]

        try:
            if not DRY_RUN:
                g.add((subj, HAS_SUBSTANCE_PORTION, portion))
                added_triples.append((subj, HAS_SUBSTANCE_PORTION, portion))
        except Exception as e:
            print(f"[ERROR] Failed to add relation {subj_local} -> {portion_local}: {e}")
            error_count += 1

# === SAVE IF NOT DRY RUN ===
if not DRY_RUN:
    g.serialize(destination=ONTOLOGY_FILE, format='xml')
    print(f"\n✅ Added {len(added_triples)} hasSubstancePortion relations.")
else:
    print("\n✅ Dry run complete. No changes made.")

# === SUMMARY ===
print("\n=== SUMMARY REPORT ===")
print(f"Total Ingredients/Dressings processed: {subject_count}")
print(f"Total Relations (previewed/assigned): {len(added_triples) if not DRY_RUN else subject_count}")
print(f"Total Warnings/Errors: {error_count}")
print("========================")

# === MISSING SUBSTANCES SUMMARY ===
print("\n=== MISSING SUBSTANCES REPORT ===")
for substance, count in missing_substances_tracker.items():
    if count > 0:
        print(f"⚠️ Missing {substance}: {count} times")
print("========================")

# === PERFECT INGREDIENTS SUMMARY ===
print("\n=== FULLY MATCHED INGREDIENTS ===")
for ing in sorted(perfect_ingredients):
    print(f"🟢 {ing}")
print("========================")