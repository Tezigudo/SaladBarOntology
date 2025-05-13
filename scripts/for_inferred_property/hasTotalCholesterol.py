import rdflib
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD
import shutil

# Define namespaces
S = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# Constants for Cholesterol
NUTRIENT_NAME = "Cholesterol"
EXPECTED_UNIT = "mg/100g"
PROPERTY = S.hasTotalCholesterol

def update_nutrient_for_salad(g, salad_name, nutrient_name=NUTRIENT_NAME):
    """
    Update the total amount for a specific nutrient (Cholesterol) for a given salad by creating or updating SaladSubstance and linking it.
    
    Args:
        g (Graph): The RDF graph to work with
        salad_name (str): Name of the salad instance (e.g., 'CapreseSalad')
        nutrient_name (str): Name of the nutrient to update (default: 'Cholesterol')
    """
    salad_uri = S[salad_name]
    nutrient_total_name = f"{salad_name}Nutrition"
    nutrient_total_uri = S[nutrient_total_name]
    
    # Debug: Check for existing SaladSubstance instance for this nutrient
    substance_instance_name = f"{salad_name}{nutrient_name}"
    substance_uri = S[substance_instance_name]
    existing_substance = None
    for s, p, o in g.triples((substance_uri, RDF.type, S.SaladSubstance)):
        existing_substance = str(s).split("#")[-1]
    print(f"Existing SaladSubstance for {salad_name} {nutrient_name} at start: {existing_substance if existing_substance else 'None'}")

    # SPARQL query to retrieve all IngredientPortion and DressingPortion instances
    query_portions = f"""
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?portion ?portionType ?amount ?unit ?component ?componentType
    WHERE {{
        ?salad s:hasIngredientPortion | s:hasDressingPortion ?portion .
        ?portion rdf:type ?portionType .
        ?portion s:hasAmount ?amount .
        ?portion s:hasUnit ?unit .
        ?portion s:hasIngredient | s:hasDressing ?component .
        ?component rdf:type ?componentType .
        FILTER (?salad = <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#{salad_name}>)
        FILTER (?portionType IN (s:IngredientPortion, s:DressingPortion))
    }}
    """

    results = g.query(query_portions)
    nutrient_totals = {}
    
    for row in results:
        portion_uri = row.portion
        portion_type = row.portionType
        amount = float(row.amount)
        unit = str(row.unit)
        component_uri = row.component
        
        query_substances = f"""
        PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?substancePortion ?substance ?amount ?unit
        WHERE {{
            ?component s:hasSubstancePortion ?substancePortion .
            ?substancePortion s:hasSubstance ?substance .
            ?substancePortion s:hasAmount ?amount .
            ?substancePortion s:hasUnit ?unit .
            FILTER (?component = <{component_uri}>)
        }}
        """

        substance_results = g.query(query_substances)
        
        for sub_row in substance_results:
            substance_uri = sub_row.substance
            substance_amount = float(sub_row.amount)
            substance_unit = str(sub_row.unit)
            substance_name = substance_uri.split("#")[-1]
            
            if substance_name != nutrient_name:  # Only process Cholesterol
                continue
                
            if substance_name != NUTRIENT_NAME:
                print(f"Warning: Unexpected substance {substance_name}, expected {NUTRIENT_NAME}, skipping.")
                continue
                
            if substance_unit != EXPECTED_UNIT:
                print(f"Warning: Unit mismatch for {substance_name}: expected {EXPECTED_UNIT}, found {substance_unit}")
            
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
                nutrient_totals[substance_name] = [total_nutrient, EXPECTED_UNIT]
    
    # Clear existing property link
    for s, p, o in g.triples((nutrient_total_uri, PROPERTY, None)):
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
    
    if nutrient_name in nutrient_totals:
        total_amount, unit = nutrient_totals[nutrient_name]
        # Create or update SaladSubstance instance
        g.add((substance_uri, RDF.type, S.SaladSubstance))
        g.add((substance_uri, S.hasAmount, Literal(total_amount, datatype=XSD.decimal)))
        display_unit = "cal" if nutrient_name == "FoodEnergy" else "mg"
        g.add((substance_uri, S.hasUnit, Literal(display_unit, datatype=XSD.string)))
        print(f"Created/Updated SaladSubstance instance: {substance_instance_name} with amount {total_amount} {display_unit}")
        
        link_tuple = (nutrient_total_uri, PROPERTY, substance_uri)
        if link_tuple not in added_links:
            g.add(link_tuple)
            added_links.add(link_tuple)
            print(f"Added specific property link: {PROPERTY.split('#')[-1]} to {substance_instance_name}")

def process_all_salads_for_nutrient(nutrient_name=NUTRIENT_NAME):
    """
    Retrieve all Salad instances and update their total for a specific nutrient (Cholesterol).
    
    Args:
        nutrient_name (str): Name of the nutrient to update (default: 'Cholesterol')
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
        print(f"Processing salad: {salad_name} for {nutrient_name}")
        update_nutrient_for_salad(g, salad_name, nutrient_name)
    
    # Save to a temporary file first, then copy to ensure proper update
    temp_file = "salad_ontology.rdf"
    g.serialize(destination=temp_file, format="xml")
    print(f"All salads processed for {nutrient_name}. Updated ontology saved as 'salad_ontology.rdf'.")

if __name__ == "__main__":
    process_all_salads_for_nutrient(NUTRIENT_NAME)
