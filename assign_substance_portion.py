from rdflib import Graph, Namespace, URIRef, RDF
from rdflib.namespace import RDFS

# === CONFIGURATION ===
ONTOLOGY_FILE = 'salad_ontology.rdf'  # Your RDF file
DRY_RUN =   False # Set to False to actually modify and save

# === LOAD GRAPH ===
g = Graph()
g.parse(ONTOLOGY_FILE)

# Define namespace
DEFAULT_NS = "http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#"
SALAD = Namespace(DEFAULT_NS)

# Define hasSubstancePortion property
HAS_SUBSTANCE_PORTION = SALAD.hasSubstancePortion

# List of all known Substance names
SUBSTANCE_NAMES = [
    "Calcium", "Carbohydrate", "Cholesterol", "Fat", "FoodEnergy",
    "Iron", "Potassium", "Protein", "Sodium", "VitaminA", "VitaminC",
    "VitaminE", "Lutein", "Zeaxanthin", "Zinc", "Omega-3", "VitaminB9"
]

# === FUNCTION: Recursively find subclasses ===
def get_all_descendants(cls):
    descendants = set()
    for subclass in g.subjects(RDFS.subClassOf, cls):
        descendants.add(subclass)
        descendants.update(get_all_descendants(subclass))
    return descendants

# === FUNCTION: Check if hasSubstancePortion already assigned ===
def has_substance_portion(instance):
    return (instance, HAS_SUBSTANCE_PORTION, None) in g

# === FUNCTION: Assign hasSubstancePortion based on name pattern ===
def assign_substance_portions_to_instance(instance_uri):
    local_name = str(instance_uri).split("#")[-1]
    assigned = 0
    missing = 0

    clean_base_name = local_name.replace('(', '').replace(')', '').replace(' ', '').replace('/', '')

    for substance in SUBSTANCE_NAMES:
        candidate_name = clean_base_name + substance.replace(' ', '')
        candidate_uri = URIRef(DEFAULT_NS + candidate_name)

        if (candidate_uri, RDF.type, SALAD.SubstancePortion) in g:
            if not (instance_uri, HAS_SUBSTANCE_PORTION, candidate_uri) in g:
                if not DRY_RUN:
                    g.add((instance_uri, HAS_SUBSTANCE_PORTION, candidate_uri))
                print(f"Assigning {local_name} --hasSubstancePortion--> {candidate_name}")
                assigned += 1
        else:
            missing += 1
    return assigned, missing

# === MAIN: Start processing ===
processed_instances = 0
new_assignments = 0
already_assigned = 0

for root_class in [SALAD.Ingredient, SALAD.Dressing]:
    all_descendants = get_all_descendants(root_class)

    for descendant in all_descendants:
        for instance in g.subjects(RDF.type, descendant):
            processed_instances += 1
            if has_substance_portion(instance):
                already_assigned += 1
                continue
            assigned, _ = assign_substance_portions_to_instance(instance)
            if assigned > 0:
                new_assignments += 1

# === SAVE UPDATED RDF ===
if not DRY_RUN:
    g.serialize(destination=ONTOLOGY_FILE, format='xml')
    print("\n✅ Finished assigning and saving new hasSubstancePortion relations!")
else:
    print("\n✅ Dry run complete. No changes were saved.")

# === SUMMARY ===
print("\n=== SUMMARY REPORT ===")
print(f"Total Subclass Instances processed: {processed_instances}")
print(f"Total New Assignments made: {new_assignments}")
print(f"Already assigned (skipped): {already_assigned}")
print("========================")
