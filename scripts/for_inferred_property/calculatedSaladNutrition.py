import rdflib
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD
import shutil

# Define namespaces
S = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

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
    "Zeaxanthin": "mg/100g",
    "Zinc": "mg/100g"
}

# Nutrient property map (specific properties, no superproperty)
nutrient_property_map = {
    "Calcium": S.hasTotalCalcium,
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

def calculate_total_nutrition_for_salad(g, salad_name):
    """
    Calculate total nutrition for a given salad using SPARQL queries
    """
    salad_uri = S[salad_name]
    nutrient_total_name = f"{salad_name}Nutrition"
    nutrient_total_uri = S[nutrient_total_name]
    
    # Debug: Check for existing SaladSubstance instances using SPARQL
    check_query = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?substance
    WHERE {
        ?substance rdf:type s:SaladSubstance .
        FILTER(STRSTARTS(STR(?substance), STR(s:%s)))
    }
    """ % salad_name
    
    existing_substances = [str(row.substance).split("#")[-1] for row in g.query(check_query)]
    print(f"Existing SaladSubstance instances for {salad_name} at start: {existing_substances}")

    # Create a comma-separated list of all nutrient names for the SPARQL filter
    nutrient_names_list = ", ".join([f'"{name}"' for name in nutrient_property_map.keys()])

    # Comprehensive SPARQL query to calculate nutrition totals in one go
    calc_query = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT ?substanceName (SUM(?scaledAmount) as ?totalAmount) ?substanceUnit
    WHERE {
      # Get all ingredient and dressing portions for this salad
      <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#%s> 
          s:hasIngredientPortion|s:hasDressingPortion ?portion .
      
      ?portion s:hasAmount ?portionAmount ;
               s:hasUnit ?portionUnit ;
               (s:hasIngredient|s:hasDressing) ?component .
      
      # Get substance portions from the components
      ?component s:hasSubstancePortion ?substancePortion .
      ?substancePortion s:hasSubstance ?substance ;
                        s:hasAmount ?substanceAmount ;
                        s:hasUnit ?substanceUnit .
      
      # Extract substance name from URI
      BIND(STRAFTER(STR(?substance), "#") AS ?substanceName)
      
      # Calculate scaling factor based on portion units
      BIND(
        IF(LCASE(?portionUnit) = "grams" || (STRENDS(STR(?portion), "IngredientPortion") && LCASE(?portionUnit) = "g"),
           ?portionAmount / 100.0,
           IF(LCASE(?portionUnit) = "millilitres" || (STRENDS(STR(?portion), "DressingPortion") && LCASE(?portionUnit) = "ml"),
              ?portionAmount / 100.0,
              1.0)
        ) AS ?scalingFactor
      )
      
      # Apply scaling to substance amount
      BIND(?substanceAmount * ?scalingFactor AS ?scaledAmount)
      
      # Filter to only include substances we're interested in
      FILTER(?substanceName IN (%s))
    }
    GROUP BY ?substanceName ?substanceUnit
    """ % (salad_name, nutrient_names_list)
    
    nutrient_results = g.query(calc_query)
    nutrient_totals = {}
    
    for row in nutrient_results:
        substance_name = str(row.substanceName)
        total_amount = float(row.totalAmount)
        substance_unit = str(row.substanceUnit)
        
        if substance_name in expected_units:
            expected_unit = expected_units[substance_name]
            if substance_unit != expected_unit:
                print(f"Warning: Unit mismatch for {substance_name}: expected {expected_unit}, found {substance_unit}")
        
        nutrient_totals[substance_name] = [total_amount, substance_unit]
    
    # SPARQL Update to remove all existing SaladSubstance instances for this salad
    delete_query = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    DELETE {
      ?substance ?p ?o .
    }
    WHERE {
      ?substance rdf:type s:SaladSubstance .
      ?substance ?p ?o .
      FILTER(STRSTARTS(STR(?substance), STR(s:%s)))
    }
    """ % salad_name
    
    # Execute the delete query
    g.update(delete_query)
    print(f"Removed existing SaladSubstance instances for {salad_name}")
    
    # SPARQL Update to clear nutrition links
    for prop in list(nutrient_property_map.values()):
        prop_name = str(prop).split('#')[-1]
        clear_query = """
        PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
        
        DELETE {
          <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#%s> s:%s ?o .
        }
        WHERE {
          <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#%s> s:%s ?o .
        }
        """ % (nutrient_total_name, prop_name, nutrient_total_name, prop_name)
        
        g.update(clear_query)
    
    # Check if SaladNutrientTotal instance exists and create if needed
    check_nutrient_total = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    ASK {
      s:%s rdf:type s:SaladNutrientTotal .
    }
    """ % nutrient_total_name
    
    if not g.query(check_nutrient_total).askAnswer:
        create_nutrient_total = """
        PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        INSERT DATA {
          s:%s rdf:type s:SaladNutrientTotal .
        }
        """ % nutrient_total_name
        
        g.update(create_nutrient_total)
        print(f"Created new SaladNutrientTotal instance: {nutrient_total_name}")
    else:
        print(f"Updating existing SaladNutrientTotal instance: {nutrient_total_name}")
    
    # Check and create hasNutrient link if needed
    check_has_nutrient = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    
    ASK {
      s:%s s:hasNutrient s:%s .
    }
    """ % (salad_name, nutrient_total_name)
    
    if not g.query(check_has_nutrient).askAnswer:
        create_has_nutrient = """
        PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
        
        INSERT DATA {
          s:%s s:hasNutrient s:%s .
        }
        """ % (salad_name, nutrient_total_name)
        
        g.update(create_has_nutrient)
        print(f"Added hasNutrient link from {salad_name} to {nutrient_total_name}")
    
    # Create new SaladSubstance instances and link them
    for substance_name, (total_amount, unit) in nutrient_totals.items():
        substance_instance_name = f"{salad_name}{substance_name}"
        display_unit = "cal" if substance_name == "FoodEnergy" else "mg"
        
        create_substance = """
        PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        INSERT DATA {
          s:%s rdf:type s:SaladSubstance ;
                s:hasAmount "%s"^^xsd:decimal ;
                s:hasUnit "%s"^^xsd:string .
          
          s:%s s:%s s:%s .
        }
        """ % (
            substance_instance_name, 
            total_amount, 
            display_unit,
            nutrient_total_name,
            nutrient_property_map[substance_name].split('#')[-1],
            substance_instance_name
        ) if substance_name in nutrient_property_map else ""
        
        if create_substance:
            g.update(create_substance)
            print(f"Created SaladSubstance instance: {substance_instance_name} and linked with property")

def process_all_salads():
    """
    Retrieve all Salad instances using SPARQL and calculate their total nutrition.
    """
    g = Graph()
    try:
        g.parse("salad_ontology.rdf", format="xml")
    except FileNotFoundError:
        print("Error: salad_ontology.rdf not found. Starting with an empty graph.")
    
    # SPARQL query to get all salads
    query_salads = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?saladName
    WHERE {
        ?salad rdf:type s:Salad .
        BIND(STRAFTER(STR(?salad), "#") AS ?saladName)
    }
    """
    
    results = g.query(query_salads)
    salad_names = [str(row.saladName) for row in results]
    
    print(f"Found {len(salad_names)} salads: {salad_names}")
    
    for salad_name in salad_names:
        print(f"\nProcessing salad: {salad_name}")
        calculate_total_nutrition_for_salad(g, salad_name)
    
    # Save the updated ontology
    g.serialize(destination="salad_ontology.rdf", format="xml")
    print("\nAll salads processed. Updated ontology saved as 'salad_ontology.rdf'.")

if __name__ == "__main__":
    process_all_salads()