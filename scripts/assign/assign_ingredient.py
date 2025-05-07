from rdflib import Graph, Namespace, URIRef, RDF

# === CONFIGURATION ===
ONTOLOGY_FILE = 'salad_ontology.rdf'  # Your RDF file
DRY_RUN = False  # Set to False to simulate assignment without saving


# === LOAD GRAPH ===
g = Graph()
g.parse(ONTOLOGY_FILE)

# Define your namespace
DEFAULT_NS = "http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#"
SALAD = Namespace(DEFAULT_NS)

# Define properties
HAS_INGREDIENT_PORTION = SALAD.hasIngredientPortion
HAS_DRESSING_PORTION = SALAD.hasDressingPortion

# === YOUR FULL SALAD STRUCTURE ===
salad_structure = {
    # "ChefSalad": ["RomaineLettuce150g", "IcebergLettuce100g", "Cucumber100g", "GreenBellPepper70g", "Carrots50g", "Tomato100g", "BlackOlives15g", "CookedTurkey28g", "CookedHam28g", "CheddarCheese14g", "RanchDressing30ml"],
    # "CobbSalad": ["IcebergLettuce100g", "CookedChicken150g", "Bacon180g", "HardBoiledEggs150g", "Tomato150g", "BlueCheese75g", "GreenOnion30g", "Avocado150g", "RanchDressing120ml"],
    # "SaladNicoise": ["RedPotato450g", "GreenBeans280g", "HardBoiledEggs200g", "CherryTomato150g", "BostonLettuce200g", "Tuna150g", "WhiteWineVinaigrette60ml", "OliveOil180ml"],
    # "GreekSalad": ["Tomato300g", "Cucumber200g", "GreenBellPepper100g", "RedOnion50g", "KalamataOlives100g", "FetaCheese150g", "OliveOil90ml", "RedWineVinaigrette30ml"],
    # "CaesarSalad": ["RomaineLettuce150g", "ParmesanCheese30g", "Croutons50g", "CaesarDressing60ml"],
    # "WaldorfSalad": ["Apple200g", "Celery100g", "RedGrape100g", "Walnut50g", "Mayonnaise60ml", "LemonJuice15ml"],
    # "PastaSalad": ["CookedPasta200g", "CherryTomato100g", "BellPepper100g", "BlackOlives50g", "Mozzarella75g", "ItalianDressing60ml"],
    # "PotatoSalad": ["BoiledPotatoes300g", "Celery50g", "RedOnion30g", "HardBoiledEggs100g", "Mayonnaise60ml", "DijonMustard15ml", "PickleRelish30g"],
    # "FruitSalad": ["Strawberries100g", "Blueberries100g", "Pineapple100g", "Kiwi100g", "MandarinOranges100g", "Honey15ml", "LimeJuice15ml"],
    # "Tabbouleh": ["Bulgur100g", "Tomato100g", "Cucumber100g", "Parsley150g", "Mint20g", "GreenOnion30g", "OliveOil80ml", "LemonJuice60ml"],
    # "CapreseSalad": ["Tomato680g", "FreshMozzarella340g", "Basil15g", "OliveOil30ml", "BalsamicGlaze15ml"],
    # "Coleslaw": ["GreenCabbage420g", "RedCabbage140g", "Carrots120g", "Mayonnaise180ml", "AppleCiderVinaigrette30ml", "DijonMustard15ml", "MapleSyrup15ml", "CelerySeed3.5g"],
    # "Ambrosia": ["HeavyCream240ml", "PowderedSugar30g", "GreekYogurt120ml", "Coconut85g", "MandarinOranges310g", "Pineapple225g", "MaraschinoCherries150g", "MiniMarshmallows150g"],
    # "Panzanella": ["Bread140g", "Tomato1000g", "RedWineVinaigrette60ml", "OliveOil60ml", "Garlic6g", "DijonMustard5g", "Basil15g", "Shallots30g", "Mozzarella115g"],
    # "Fattoush": ["Bread60g", "RomaineLettuce300g", "Cucumber200g", "Tomato300g", "GreenOnion50g", "Radishes100g", "Parsley60g", "Mint30g", "OliveOil45ml", "LemonJuice30ml", "Sumac4g"],
    # "BeanSalad": ["GarbanzoBeans440g", "KidneyBeans410g", "BlackBeans410g", "GreenBeans410g", "WaxBeans410g", "GreenBellPepper75g", "Onion75g", "Celery75g", "Sugar150g", "Oil120ml", "Vinegar120ml", "Tuna140g", "SaladDressing60ml", "PickleRelish15g"],
    # "ChickenSalad": ["CookedChicken450g", "Celery100g", "RedBellPepper75g", "GreenOlives30g", "RedOnion60g", "Apple120g", "IcebergLettuce100g", "Mayonnaise75ml"],
    "EggSalad_I": ["HardBoiledEggs300g", "Mayonnaise90ml", "DijonMustard15ml", "Celery30g", "Chives10g", "Salt4g", "BlackPepper2g"],
    # "CrabLouie": ["IcebergLettuce200g", "Crabmeat225g", "HardBoiledEggs100g", "Tomato150g", "Asparagus150g", "Avocado150g", "Cucumber100g", "BlackOlives50g", "RedOnion30g", "Mayonnaise120ml", "Ketchup60ml", "PickleRelish30ml", "LemonJuice15ml", "Garlic5g", "WorcestershireSauce5ml", "Horseradish5g", "Paprika1g"]
}

# === FUNCTION: Add relations ===
def add_salad_relations():
    skipped_salads = {}

    for salad_name, items in salad_structure.items():
        salad_uri = URIRef(DEFAULT_NS + salad_name)
        missing_items = []

        for item in items:
            item_uri = URIRef(DEFAULT_NS + item)

            if not (item_uri, RDF.type, None) in g:
                missing_items.append(item)
                continue

            if item.endswith("ml"):
                if not DRY_RUN:
                    g.add((salad_uri, HAS_DRESSING_PORTION, item_uri))
                print(f"Assigning {salad_name} --hasDressingPortion--> {item}")
            elif item.endswith("g"):
                if not DRY_RUN:
                    g.add((salad_uri, HAS_INGREDIENT_PORTION, item_uri))
                print(f"Assigning {salad_name} --hasIngredientPortion--> {item}")
            else:
                print(f"[WARNING] Unknown unit for {item} in {salad_name}")

        if missing_items:
            skipped_salads[salad_name] = missing_items
            print(f"[SKIP] {salad_name} skipped due to missing ingredients: {missing_items}")

    return skipped_salads

# === RUN ===
skipped_salads = add_salad_relations()

# === SAVE UPDATED RDF ===
if not DRY_RUN:
    g.serialize(destination=ONTOLOGY_FILE, format='xml')
    print("\n✅ Finished assigning and saving ingredientPortion and dressingPortion!")
else:
    print("\n✅ Dry run complete. No changes were saved.")

# === SUMMARY OF SKIPPED SALADS ===
if skipped_salads:
    print("\n=== Skipped Salads Summary ===")
    for salad, missing in skipped_salads.items():
        print(f"- {salad}: missing {missing}")
    print("===============================")
else:
    print("\n✅ All salads assigned without missing ingredients!")
