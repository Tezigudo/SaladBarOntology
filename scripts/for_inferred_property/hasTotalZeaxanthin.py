import rdflib
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD

# Define namespaces
S = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# Constant for Zeaxanthin unit
ZEAXANTHIN_UNIT = "mg/100g"

# Constant for Zeaxanthin property
ZEAXANTHIN_PROPERTY = S.hasTotalZeaxanthin

def calculate_nutrient_for_salad(g, salad_name, nutrient_name="Zeaxanthin", unit=ZEAXANTHIN_UNIT, property=ZEAXANTHIN_PROPERTY):
    """
    Calculate total amount for Zeaxanthin for a given salad and update or create SaladSubstance instances.
    
    Args:
        g (Graph): The RDF graph to work with
        salad_name (str): Name of the salad instance (e.g., 'CapreseSalad')
        nutrient_name (str): Name of the nutrient to calculate (default: 'Zeaxanthin')
        unit (str): Unit for the nutrient (default: 'mg/100g')
        property (URIRef): Property for the nutrient (default: hasTotalZeaxanthin)
    """
    salad_uri = S[salad_name]
    nutrient_total_name = f"{salad_name}Nutrition"
    nutrient_total_uri = S[nutrient_total_name]
    
    # Debug: Check for existing SaladSubstance instances for this nutrient at the start
    substance_instance_name = f"{salad_name}{nutrient_name}"
    substance_uri = S[substance_instance_name]
    existing_substance = None
    for s, p, o in g.triples((substance_uri, RDF.type, S.SaladSubstance)):
        existing_substance = str(s).split("#")[-1]
    print(f"Existing SaladSubstance for {salad_name} {nutrient_name} at start: {existing_substance if existing_substance else 'None'}")

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
    total_amount = 0.0
    
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
            
            if substance_name != nutrient_name:
                continue
                
            if substance_unit != unit:
                print(f"Warning: Unit mismatch for {substance_name}: expected {unit}, found {substance_unit}")
                continue
            
            if unit.lower() == "grams" or (portion_type == S.IngredientPortion and unit.lower() == "g"):
                scaling_factor = amount / 100.0
            elif unit.lower() == "millilitres" or (portion_type == S.DressingPortion and unit.lower() == "ml"):
                scaling_factor = amount / 100.0  # 1ml ≈ 1g for simplicity
            else:
                print(f"Warning: Unknown unit {unit} for portion {portion_uri}, using scaling factor 1.0")
                scaling_factor = 1.0
                
            total_amount += substance_amount * scaling_factor
    
    # Remove existing SaladSubstance instance for this nutrient
    if (substance_uri, RDF.type, S.SaladSubstance) in g:
        g.remove((substance_uri, None, None))
        print(f"Removed existing SaladSubstance for {substance_instance_name}")

    # Clear existing property link
    for s, p, o in g.triples((nutrient_total_uri, property, None)):
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
    
    if total_amount > 0:
        g.add((substance_uri, RDF.type, S.SaladSubstance))
        g.add((substance_uri, S.hasAmount, Literal(total_amount, datatype=XSD.decimal)))
        g.add((substance_uri, S.hasUnit, Literal("mg", datatype=XSD.string)))  # Using 'mg' as display unit for most nutrients
        print(f"Created new SaladSubstance instance: {substance_instance_name}")
        
        link_tuple = (nutrient_total_uri, property, substance_uri)
        if link_tuple not in added_links:
            g.add(link_tuple)
            added_links.add(link_tuple)
            print(f"Added specific property link: {property.split('#')[-1]} to {substance_instance_name}")

def process_all_salads_for_nutrient(nutrient_name="Zeaxanthin", unit=ZEAXANTHIN_UNIT, property=ZEAXANTHIN_PROPERTY):
    """
    Retrieve all Salad instances and calculate their total for a specific nutrient (Zeaxanthin).
    
    Args:
        nutrient_name (str): Name of the nutrient to calculate (default: 'Zeaxanthin')
        unit (str): Unit for the nutrient (default: 'mg/100g')
        property (URIRef): Property for the nutrient (default: hasTotalZeaxanthin)
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
        calculate_nutrient_for_salad(g, salad_name, nutrient_name, unit, property)
    
    # Save to a temporary file first, then copy to ensure proper update
    temp_file = "salad_ontology.rdf"
    g.serialize(destination=temp_file, format="xml")
    print(f"All salads processed for {nutrient_name}. Updated ontology saved as 'salad_ontology.rdf'.")

if __name__ == "__main__":
    process_all_salads_for_nutrient("Zeaxanthin", ZEAXANTHIN_UNIT, ZEAXANTHIN_PROPERTY)
