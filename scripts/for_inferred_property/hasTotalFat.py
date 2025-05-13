import rdflib
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD
import shutil

# Define namespaces
S = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# Expected units for each substance
expected_units = {
    "Fat": "mg/100g"
}

# Nutrient property map (only specific properties, no superproperty)
nutrient_property_map = {
    "Fat": S.hasTotalFat,
}

def calculate_total_nutrition_for_salad(g, salad_name):
    """
    Calculate total nutrition for a given salad and update or create SaladNutrientTotal and SaladSubstance instances.
    
    Args:
        g (Graph): The RDF graph to work with
        salad_name (str): Name of the salad instance (e.g., 'CapreseSalad')
    """
    salad_uri = S[salad_name]
    nutrient_total_name = f"{salad_name}Nutrition"
    nutrient_total_uri = S[nutrient_total_name]
    
    # Debug: Check for existing SaladSubstance instances at the start
    existing_substances = []
    for s, p, o in g.triples((None, RDF.type, S.SaladSubstance)):
        if str(s).startswith(str(S) + salad_name):
            existing_substances.append(str(s).split("#")[-1])
    print(f"Existing SaladSubstance instances for {salad_name} at start: {existing_substances}")

    # SPARQL query to retrieve all IngredientPortion and DressingPortion instances
    query_portions = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?portion ?portionType ?amount ?unit ?component ?componentType
    WHERE {
        ?salad s:hasIngredientPortion | s:hasDressingPortion ?portion .
        ?portion rdf:type ?portionType .
        ?portion s:hasAmount ?amount .
        ?portion s:hasUnit ?unit .
        ?portion s:hasIngredient | s:hasDressing ?component .
        ?component rdf:type ?componentType .
        FILTER (?salad = <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#%s>)
        FILTER (?portionType IN (s:IngredientPortion, s:DressingPortion))
    }
    """ % salad_name

    results = g.query(query_portions)
    nutrient_totals = {}
    
    for row in results:
        portion_uri = row.portion
        portion_type = row.portionType
        amount = float(row.amount)
        unit = str(row.unit)
        component_uri = row.component
        
        query_substances = """
        PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?substancePortion ?substance ?amount ?unit
        WHERE {
            ?component s:hasSubstancePortion ?substancePortion .
            ?substancePortion s:hasSubstance ?substance .
            ?substancePortion s:hasAmount ?amount .
            ?substancePortion s:hasUnit ?unit .
            FILTER (?component = <%s>)
        }
        """ % component_uri

        substance_results = g.query(query_substances)
        
        for sub_row in substance_results:
            substance_uri = sub_row.substance
            substance_amount = float(sub_row.amount)
            substance_unit = str(sub_row.unit)
            substance_name = substance_uri.split("#")[-1]
            
            if substance_name not in expected_units:
                print(f"Warning: Substance {substance_name} not in expected units, skipping.")
                continue
                
            expected_unit = expected_units[substance_name]
            if substance_unit != expected_unit:
                print(f"Warning: Unit mismatch for {substance_name}: expected {expected_unit}, found {substance_unit}")
            
            if unit.lower() == "grams" or (portion_type == S.IngredientPortion and unit.lower() == "g"):
                scaling_factor = amount / 100.0
            elif unit.lower() == "millilitres" or (portion_type == S.DressingPortion and unit.lower() == "ml"):
                scaling_factor = amount / 100.0  # 1ml ≈ 1g for simplicity
            else:
                print(f"Warning: Unknown unit {unit} for portion {portion_uri}, using scaling factor 1.0")
                scaling_factor = 1.0
                
            total_nutrient = substance_amount * scaling_factor
            
            if substance_name in nutrient_totals:
                nutrient_totals[substance_name][0] += total_nutrient
            else:
                nutrient_totals[substance_name] = [total_nutrient, expected_unit]
    
    # Remove all existing SaladSubstance instances for this salad
    substances_to_remove = []
    for s, p, o in g.triples((None, RDF.type, S.SaladSubstance)):
        if str(s).startswith(str(S) + salad_name):
            substances_to_remove.append(s)
    print(f"Found {len(substances_to_remove)} existing SaladSubstance instances to remove for {salad_name}")
    for substance_uri in substances_to_remove:
        g.remove((substance_uri, None, None))
        print(f"Removed triples for {substance_uri}")

    # Clear all links from nutrient_total_uri
    for prop in list(nutrient_property_map.values()):  # Only clear specific properties
        for s, p, o in g.triples((nutrient_total_uri, prop, None)):
            g.remove((s, p, o))
    
    if (nutrient_total_uri, RDF.type, S.SaladNutrientTotal) not in g:
        g.add((nutrient_total_uri, RDF.type, S.SaladNutrientTotal))
        print(f"Created new SaladNutrientTotal instance: {nutrient_total_name}")
    else:
        print(f"Updating existing SaladNutrientTotal instance: {nutrient_total_name}")
    
    if (salad_uri, S.hasNutrient, nutrient_total_uri) not in g:
        g.add((salad_uri, S.hasNutrient, nutrient_total_uri))
        print(f"Added hasNutrient link from {salad_name} to {nutrient_total_name}")
    
    added_links = set()
    
    for substance_name, (total_amount, unit) in nutrient_totals.items():
        substance_instance_name = f"{salad_name}{substance_name}"
        substance_uri = S[substance_instance_name]
        
        # Since we removed all existing SaladSubstance instances, create new ones
        g.add((substance_uri, RDF.type, S.SaladSubstance))
        g.add((substance_uri, S.hasAmount, Literal(total_amount, datatype=XSD.decimal)))
        display_unit = "cal" if substance_name == "FoodEnergy" else "mg"
        g.add((substance_uri, S.hasUnit, Literal(display_unit, datatype=XSD.string)))
        print(f"Created new SaladSubstance instance: {substance_instance_name}")
        
        if substance_name in nutrient_property_map:
            link_tuple = (nutrient_total_uri, nutrient_property_map[substance_name], substance_uri)
            if link_tuple not in added_links:
                g.add(link_tuple)
                added_links.add(link_tuple)
                print(f"Added specific property link: {nutrient_property_map[substance_name].split('#')[-1]} to {substance_instance_name}")

def process_all_salads():
    """
    Retrieve all Salad instances and calculate their total nutrition.
    """
    g = Graph()
    try:
        g.parse("salad_ontology.rdf", format="xml")
    except FileNotFoundError:
        print("Error: salad_ontology.rdf not found. Starting with an empty graph.")
    
    query_salads = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?salad
    WHERE {
        ?salad rdf:type s:Salad .
    }
    """
    
    results = g.query(query_salads)
    salad_names = [str(row.salad).split("#")[-1] for row in results]
    
    print(f"Found {len(salad_names)} salads: {salad_names}")
    
    for salad_name in salad_names:
        print(f"\nProcessing salad: {salad_name}")
        calculate_total_nutrition_for_salad(g, salad_name)
    
    # Save to a temporary file first, then copy to ensure proper update
    temp_file = "salad_ontology.rdf"
    g.serialize(destination=temp_file, format="xml")
    print("\nAll salads processed. Updated ontology saved as 'salad_ontology.rdf'.")

if __name__ == "__main__":
    process_all_salads()