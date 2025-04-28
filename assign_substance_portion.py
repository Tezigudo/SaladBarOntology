from rdflib import Graph, Namespace, RDF

# Configuration
DRY_RUN = True  # Always true now, no auto-create

# Load RDF
g = Graph()
g.parse("salad_ontology.rdf", format="xml")

# Define Namespace
SALAD = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# Properties
HAS_SUBSTANCE_PORTION = SALAD.hasSubstancePortion

# Helper
def get_local_name(uri):
    return uri.split("#")[-1].replace('\u200b', '').replace('\xa0', '').strip()

# Step 1: Collect all Ingredients and Dressings
ingredient_or_dressing_individuals = set()

for s, p, o in g.triples((None, RDF.type, None)):
    local_class = get_local_name(o)
    local_name = get_local_name(s)
    if local_class in ["Ingredient", "Dressing"]:
        ingredient_or_dressing_individuals.add((s, local_name))

# Step 2: Check hasSubstancePortion
missing_links = []

for uri, name in ingredient_or_dressing_individuals:
    found = False
    for _, p, o in g.triples((uri, HAS_SUBSTANCE_PORTION, None)):
        found = True
        break
    if not found:
        missing_links.append(name)

# Final Report
print("\n✅ Audit Summary: hasSubstancePortion Check")
print(f"- Total Ingredients/Dressings Checked: {len(ingredient_or_dressing_individuals)}")
if missing_links:
    print(f"\n⚠️ Ingredients/Dressings missing hasSubstancePortion ({len(missing_links)}):")
    for name in missing_links:
        print(f"- {name}")
else:
    print("\n🎯 All Ingredients and Dressings have at least one hasSubstancePortion! Perfect!")

print("\n(Dry Run Mode: {})".format(DRY_RUN))
