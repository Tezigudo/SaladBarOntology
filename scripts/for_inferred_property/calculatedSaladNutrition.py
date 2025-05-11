import rdflib
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD

# Initialize the RDF graph and load the ontology
g = Graph()
g.parse("../../salad_ontology.rdf", format="xml")  # RDF/XML format for .rdf file

# Define namespaces
S = Namespace("http://example.org/salad#")  # Replace with your ontology's namespace if different
g.bind("s", S)

# Expected units for each substance
expected_units = {
    "Calcium": "mg/100g",
    "Carbohydrate": "mg/100g",
    "Cholesterol": "mg/100g",
    "Fat": "mg/100g",
    "FoodEnergy": "cal/100g",
    "Iron": "mg/100g",
    "Lutein": "mg/100g",
    "Omega-3": "mg/100g",
    "Potassium": "mg/100g",
    "Protein": "mg/100g",
    "Sodium": "mg/100g",
    "VitaminA": "mg/100g",
    "VitaminB9": "mg/100g",
    "VitaminC": "mg/100g",
    "VitaminE": "mg/100g",
    "Zeaxanthin": "mg/100g",
    "Zinc": "mg/100g"
}

def calculate_total_nutrition(salad_name):
    """
    Calculate total nutrition for a given salad and update or create SaladNutrientTotal and SaladSubstance instances.
    
    Args:
        salad_name (str): Name of the salad instance (e.g., 'SaladNicoise')
    """
    salad_uri = S[salad_name]
    
    # Check if SaladNutrientTotal already exists
    nutrient_total_name = f"{salad_name}Nutrition"
    nutrient_total_uri = S[nutrient_total_name]
    
    # SPARQL query to retrieve all IngredientPortion and DressingPortion instances
    query_portions = """
    PREFIX s: <http://example.org/salad#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?portion ?portionType ?amount ?unit ?component ?componentType
    WHERE {
        ?salad s:hasIngredientPortion | s:hasDressingPortion ?portion .
        ?portion rdf:type ?portionType .
        ?portion s:hasAmount ?amount .
        ?portion s:hasUnit ?unit .
        ?portion s:hasIngredient | s:hasDressing ?component .
        ?component rdf:type ?componentType .
        FILTER (?salad = <http://example.org/salad#%s>)
        FILTER (?portionType IN (s:IngredientPortion, s:DressingPortion))
    }
    """ % salad_name

    # Execute query to get portions
    results = g.query(query_portions)
    
    # Dictionary to store total nutrient amounts (nutrient_name -> [total_amount, unit])
    nutrient_totals = {}
    
    # Process each portion
    for row in results:
        portion_uri = row.portion
        portion_type = row.portionType
        amount = float(row.amount)
        unit = str(row.unit)
        component_uri = row.component
        
        # SPARQL query to get SubstancePortion instances for the component
        query_substances = """
        PREFIX s: <http://example.org/salad#>
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

        # Execute query to get substance portions
        substance_results = g.query(query_substances)
        
        for sub_row in substance_results:
            substance_uri = sub_row.substance
            substance_amount = float(sub_row.amount)
            substance_unit = str(sub_row.unit)
            substance_name = substance_uri.split("#")[-1]
            
            # Validate substance and assign expected unit
            if substance_name not in expected_units:
                print(f"Warning: Substance {substance_name} not in expected units, skipping.")
                continue
                
            expected_unit = expected_units[substance_name]
            if substance_unit != expected_unit:
                print(f"Warning: Unit mismatch for {substance_name}: expected {expected_unit}, found {substance_unit}")
            
            # Calculate contribution (scale by portion amount, assuming substance_amount is per 100g)
            if unit.lower() in ["grams", "millilitres"]:
                scaling_factor = amount / 100.0
            else:
                print(f"Warning: Unknown unit {unit} for portion {portion_uri}, using scaling factor 1.0")
                scaling_factor = 1.0
                
            total_nutrient = substance_amount * scaling_factor
            
            # Aggregate nutrient totals
            if substance_name in nutrient_totals:
                nutrient_totals[substance_name][0] += total_nutrient
            else:
                nutrient_totals[substance_name] = [total_nutrient, expected_unit]
    
    # Add or update SaladNutrientTotal instance
    if (nutrient_total_uri, RDF.type, S.SaladNutrientTotal) not in g:
        g.add((nutrient_total_uri, RDF.type, S.SaladNutrientTotal))
        print(f"Created new SaladNutrientTotal instance: {nutrient_total_name}")
    else:
        print(f"Updating existing SaladNutrientTotal instance: {nutrient_total_name}")
    
    # Ensure hasNutrient link exists
    if (salad_uri, S.hasNutrient, nutrient_total_uri) not in g:
        g.add((salad_uri, S.hasNutrient, nutrient_total_uri))
        print(f"Added hasNutrient link from {salad_name} to {nutrient_total_name}")
    
    # Create or update SaladSubstance instances and link to SaladNutrientTotal
    for substance_name, (total_amount, unit) in nutrient_totals.items():
        substance_instance_name = f"{salad_name}{substance_name}"
        substance_uri = S[substance_instance_name]
        
        # Add or update SaladSubstance
        if (substance_uri, RDF.type, S.SaladSubstance) not in g:
            g.add((substance_uri, RDF.type, S.SaladSubstance))
            g.add((substance_uri, S.hasAmount, Literal(total_amount, datatype=XSD.decimal)))
            display_unit = "cal" if substance_name == "FoodEnergy" else "mg"
            g.add((substance_uri, S.hasUnit, Literal(display_unit, datatype=XSD.string)))
            print(f"Created new SaladSubstance instance: {substance_instance_name}")
        else:
            # Update amount if it exists
            for s, p, o in g.triples((substance_uri, S.hasAmount, None)):
                g.remove((s, p, o))
                g.add((substance_uri, S.hasAmount, Literal(total_amount, datatype=XSD.decimal)))
            print(f"Updated existing SaladSubstance instance: {substance_instance_name}")
        
        # Link to SaladNutrientTotal if not already linked
        if (nutrient_total_uri, S.hasTotalSubstance, substance_uri) not in g:
            g.add((nutrient_total_uri, S.hasTotalSubstance, substance_uri))
            print(f"Added hasTotalSubstance link from {nutrient_total_name} to {substance_instance_name}")
        
        # Link to specific nutrient property if applicable
        nutrient_property_map = {
            "Carbohydrate": S.hasTotalCarbohydrate,
            "Cholesterol": S.hasTotalCholesterol,
            "Fat": S.hasTotalFat,
            "FoodEnergy": S.hasTotalFoodEnergy,
            "Iron": S.hasTotalIron,
            "Lutein": S.hasTotalLutein,
            "Omega-3": S.hasTotalOmega_3,
            "Potassium": S.hasTotalPotassium,
            "Protein": S.hasTotalProtein,
            "Sodium": S.hasTotalSodium,
            "VitaminA": S.hasTotalVitaminA,
            "VitaminB9": S.hasTotalVitaminB9,
            "VitaminC": S.hasTotalVitaminC,
            "Zeaxanthin": S.hasTotalZeaxanthin,
            "Zinc": S.hasTotalZinc
        }
        if substance_name in nutrient_property_map:
            if (nutrient_total_uri, nutrient_property_map[substance_name], substance_uri) not in g:
                g.add((nutrient_total_uri, nutrient_property_map[substance_name], substance_uri))
                print(f"Added specific property link: {nutrient_property_map[substance_name].split('#')[-1]}")
    
    # Serialize the updated graph back to the ontology file
    g.serialize(destination="../../salad_ontology_updated.rdf", format="xml")
    
    print(f"Total nutrition calculated for {salad_name}. Updated ontology saved as 'salad_ontology_updated.rdf'.")
    print("Nutrient Totals:")
    for substance_name, (total_amount, unit) in nutrient_totals.items():
        display_unit = "cal" if substance_name == "FoodEnergy" else "mg"
        print(f"{substance_name}: {total_amount:.2f} {display_unit}")

# Example usage
if __name__ == "__main__":
    calculate_total_nutrition("SaladNicoise")