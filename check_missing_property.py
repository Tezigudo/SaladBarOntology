from rdflib import Graph, Namespace, RDF

# === CONFIGURATION ===
ONTOLOGY_FILE = 'salad_ontology.rdf'  # Path to your RDF file

# === LOAD GRAPH ===
g = Graph()
g.parse(ONTOLOGY_FILE)

# Define your namespace
DEFAULT_NS = "http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#"
SALAD = Namespace(DEFAULT_NS)

# Define property
HAS_SUBSTANCE_PORTION = SALAD.hasSubstancePortion

# === HELPER FUNCTION ===
from rdflib.namespace import RDFS

def is_ingredient_or_dressing(individual):
    for _, _, obj in g.triples((individual, RDF.type, None)):
        if obj in [SALAD.Ingredient, SALAD.Dressing]:
            return True
        for _, _, super_class in g.triples((obj, RDFS.subClassOf, None)):
            if super_class in [SALAD.Ingredient, SALAD.Dressing]:
                return True
    return False

# === MAIN CHECK ===
print("\n=== CHECK: Missing hasSubstancePortion for Ingredients/Dressings ===")
missing_substanceportion = []

total_checked = 0

for subj in g.subjects(RDF.type, None):
    if not is_ingredient_or_dressing(subj):
        continue

    total_checked += 1
    has_substanceportion = False
    for _, p, _ in g.triples((subj, None, None)):
        if p == HAS_SUBSTANCE_PORTION:
            has_substanceportion = True
            break

    if not has_substanceportion:
        subj_local = str(subj).split("#")[-1]
        missing_substanceportion.append(subj_local)

# === REPORT ===
print(f"Total Ingredients/Dressings checked: {total_checked}")
if missing_substanceportion:
    print(f"⚠️ Ingredients/Dressings missing hasSubstancePortion: {len(missing_substanceportion)}")
    for name in sorted(missing_substanceportion):
        print(f" - {name}")
else:
    print("✅ All Ingredients/Dressings have at least one hasSubstancePortion.")
print("========================")