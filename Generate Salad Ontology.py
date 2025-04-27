import json
from rdflib import Graph, Namespace, RDF, OWL, Literal, XSD

# Load input JSON
data_file = "sample_salad_data.json"
output_owl_file = "generated_salad.owl"

with open(data_file) as f:
    data = json.load(f)

# Set up RDF graph and namespaces
g = Graph()
EX = Namespace("http://example.org/salad#")
g.bind("ex", EX)
g.bind("owl", OWL)

# Define Classes
classes = [
    "Salad", "Ingredient", "IngredientPortion", "Dressing", "DressingPortion",
    "Substance", "SubstancePortion"
]
for cls in classes:
    g.add((EX[cls], RDF.type, OWL.Class))

# Define Object Properties
object_properties = [
    "hasIngredientPortion", "hasIngredient", "hasDressingPortion", "hasDressing",
    "hasSubstancePortion", "hasSubstance"
]
for prop in object_properties:
    g.add((EX[prop], RDF.type, OWL.ObjectProperty))

# Define Data Properties
data_properties = ["hasAmount", "hasUnit"]
for prop in data_properties:
    g.add((EX[prop], RDF.type, OWL.DatatypeProperty))

# Index declared entities
declared_ingredients = set(data.get("ingredients", []))
declared_dressings = set(data.get("dressings", []))
declared_substances = set(data.get("substances", []))

# For logging
missing_ingredients = set()
missing_dressings = set()
missing_substances = set()
missing_owners = set()

# Create salads and portions
for salad in data["salads"]:
    salad_uri = EX[salad["name"]]
    g.add((salad_uri, RDF.type, EX.Salad))
    print(f"Generating Salad: {salad['name']}")

    for ip in salad.get("ingredientPortions", []):
        ip_uri = EX[ip["name"]]
        ing_uri = EX[ip["ingredient"]]

        g.add((ip_uri, RDF.type, EX.IngredientPortion))
        g.add((salad_uri, EX.hasIngredientPortion, ip_uri))
        g.add((ip_uri, EX.hasIngredient, ing_uri))
        g.add((ip_uri, EX.hasAmount, Literal(ip["amount"], datatype=XSD.integer)))
        g.add((ip_uri, EX.hasUnit, Literal(ip["unit"], datatype=XSD.string)))
        print(f"  Adding IngredientPortion: {ip['name']} -> {ip['ingredient']}")

        if ip["ingredient"] not in declared_ingredients:
            missing_ingredients.add(ip["ingredient"])
        else:
            g.add((ing_uri, RDF.type, EX.Ingredient))

    for dp in salad.get("dressingPortions", []):
        dp_uri = EX[dp["name"]]
        dr_uri = EX[dp["dressing"]]

        g.add((dp_uri, RDF.type, EX.DressingPortion))
        g.add((salad_uri, EX.hasDressingPortion, dp_uri))
        g.add((dp_uri, EX.hasDressing, dr_uri))
        g.add((dp_uri, EX.hasAmount, Literal(dp["amount"], datatype=XSD.integer)))
        g.add((dp_uri, EX.hasUnit, Literal(dp["unit"], datatype=XSD.string)))
        print(f"  Adding DressingPortion: {dp['name']} -> {dp['dressing']}")

        if dp["dressing"] not in declared_dressings:
            missing_dressings.add(dp["dressing"])
        else:
            g.add((dr_uri, RDF.type, EX.Dressing))

# Create SubstancePortions
for sp in data.get("substancePortions", []):
    owner_uri = EX[sp["owner"]]
    subs_uri = EX[sp["substance"]]
    sp_uri = EX[f"{sp['owner']}{sp['substance']}"]

    g.add((subs_uri, RDF.type, EX.Substance))
    g.add((sp_uri, RDF.type, EX.SubstancePortion))
    g.add((sp_uri, EX.hasSubstance, subs_uri))
    g.add((sp_uri, EX.hasAmount, Literal(sp["amount"], datatype=XSD.float)))
    g.add((sp_uri, EX.hasUnit, Literal(sp["unit"], datatype=XSD.string)))
    g.add((owner_uri, EX.hasSubstancePortion, sp_uri))
    print(f"Generating SubstancePortion: {sp['owner']} -> {sp['substance']}")

    if sp["substance"] not in declared_substances:
        missing_substances.add(sp["substance"])

# Save output
g.serialize(destination=output_owl_file, format="pretty-xml")
print(f"\nOWL file successfully created: {output_owl_file}")

# Log missing definitions
if missing_ingredients or missing_dressings or missing_substances:
    print("\nMissing class declarations:")
    if missing_ingredients:
        print("  Missing Ingredients:", ", ".join(missing_ingredients))
    if missing_dressings:
        print("  Missing Dressings:", ", ".join(missing_dressings))
    if missing_substances:
        print("  Missing Substances:", ", ".join(missing_substances))
else:
    print("\nAll classes correctly defined!")
