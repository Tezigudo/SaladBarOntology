from rdflib import Graph, Namespace, URIRef, Literal, RDF
import re
from termcolor import colored

# Configuration
DRY_RUN = True  # Set to False to actually modify RDF

# Load your RDF graph
g = Graph()
g.parse("salad_ontology.rdf", format="xml")

# Define Namespace
SALAD = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# Property URIs
HAS_INGREDIENT_PORTION = SALAD.hasIngredientPortion

# Helper functions
def get_local_name(uri):
    return uri.split("#")[-1]

# Mapping from user
salad_ingredients_mapping = {
    "ChefSalad": [
        "RomaineLettuce150g", "IcebergLettuce100g", "Cucumber100g", "GreenBellPepper70g",
        "Carrots50g", "Tomato100g", "BlackOlives15g", "CookedTurkey28g", "CookedHam28g",
        "CheddarCheese14g", "RanchDressing30ml"
    ],
    "CobbSalad": [
        "IcebergLettuce100g", "CookedChicken150g", "Bacon180g", "HardBoiledEggs150g",
        "Tomato150g", "BlueCheese75g", "GreenOnions30g", "Avocado150g", "RanchDressing120ml"
    ],
    "SaladNicoise": [
        "RedPotatoes450g", "GreenBeans280g", "HardBoiledEggs200g", "CherryTomato150g",
        "BostonLettuce200g", "Tuna150g", "WhiteWineVinaigrette60ml", "OliveOil180ml"
    ],
    "GreekSalad": [
        "Tomato300g", "Cucumber200g", "GreenBellPepper100g", "RedOnion50g", "KalamataOlives100g",
        "FetaCheese150g", "OliveOil90ml", "RedWineVinaigrette30ml"
    ],
    "CaesarSalad": [
        "RomaineLettuce150g", "ParmesanCheese30g", "Croutons50g", "CaesarDressing60ml"
    ],
    "EggSalad_i": [
        "HardBoiledEggs300g", "Mayonnaise90ml", "DijonMustard15ml", "Celery30g", "Chives10g",
        "Salt4g", "BlackPepper2g"
    ],
    "CrabLouie": [
        "IcebergLettuce200g", "Crabmeat225g", "HardBoiledEggs100g", "Tomatoes150g", "Asparagus150g",
        "Avocado150g", "Cucumber100g", "BlackOlives50g", "RedOnion30g", "Mayonnaise120ml",
        "Ketchup60ml", "PickleRelish30ml", "LemonJuice15ml", "Garlic5g", "WorcestershireSauce5ml",
        "Horseradish5g", "Paprika1g"
    ]
}

# Step: Assign hasIngredientPortion
assign_count = 0
missing_links = []

for salad_name, ingredients in salad_ingredients_mapping.items():
    salad_uri = SALAD[salad_name]
    for ingredient_portion_name in ingredients:
        cleaned_portion_name = ingredient_portion_name.replace("\u200b", "").strip()
        ingredient_portion_uri = SALAD[cleaned_portion_name]
        if (salad_uri, None, None) not in g:
            print(colored(f"[Warning] Salad not found: {salad_name}", "red"))
            missing_links.append((salad_name, cleaned_portion_name))
            continue
        if (ingredient_portion_uri, None, None) not in g:
            print(colored(f"[Warning] IngredientPortion not found: {cleaned_portion_name}", "red"))
            missing_links.append((salad_name, cleaned_portion_name))
            continue
        if DRY_RUN:
            print(colored(f"[DRY-RUN] Would assign: {salad_name} --> {cleaned_portion_name}", "yellow"))
        else:
            g.add((salad_uri, HAS_INGREDIENT_PORTION, ingredient_portion_uri))
            assign_count += 1

# Save back if not dry run
if not DRY_RUN:
    g.serialize(destination="salad_ontology.rdf", format="xml")

# Final report
print("\n✅", colored("hasIngredientPortion assignment completed!", "green"))
print(f"- Total hasIngredientPortion links assigned: {assign_count}")
if missing_links:
    print(colored(f"\n⚠️ Missing or inconsistent links found ({len(missing_links)}):", "red"))
    for salad, ingredient in missing_links:
        print(f"- {salad} --> {ingredient}")
print(colored(f"\n🎯 Finished! (Dry Run Mode: {DRY_RUN})", "cyan"))