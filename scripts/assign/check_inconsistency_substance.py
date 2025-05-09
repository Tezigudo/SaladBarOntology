import rdflib
from collections import defaultdict

# Initialize RDF graph
g = rdflib.Graph()
# Load ontology (adjust path to your ontology file)
ontology_file = "salad_ontology.rdf"  # Update with your file path
g.parse(ontology_file, format="xml")

# Define namespaces
S = rdflib.Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")
RDF = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

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

# SPARQL query to retrieve SubstancePortion units
query = """
PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
SELECT ?substance ?unit ?portion
WHERE {
    ?portion a s:SubstancePortion .
    ?portion s:hasSubstance ?substance .
    ?portion s:hasUnit ?unit .
}
"""

# Execute query
results = g.query(query)

# Collect units by substance
unit_by_substance = defaultdict(list)
for row in results:
    substance = str(row.substance).split('#')[-1]
    unit = str(row.unit)
    portion = str(row.portion)
    unit_by_substance[substance].append((unit, portion))

# Check consistency
inconsistencies = []
all_consistent = True

for substance, units in unit_by_substance.items():
    # Get unique units for this substance
    unique_units = set(unit for unit, _ in units)
    
    # Check if substance has an expected unit
    expected_unit = expected_units.get(substance)
    if not expected_unit:
        inconsistencies.append(f"Substance {substance}: No expected unit defined.")
        all_consistent = False
        continue
    
    # Check if all units match the expected unit
    if unique_units != {expected_unit}:
        all_consistent = False
        inconsistencies.append(f"Substance {substance}: Expected unit '{expected_unit}', found units {unique_units}")
        for unit, portion in units:
            if unit != expected_unit:
                inconsistencies.append(f"  - Inconsistent unit '{unit}' in portion {portion}")

# Print results
if all_consistent:
    print("All SubstancePortion units are consistent with expected values.")
else:
    print("Inconsistencies found in SubstancePortion units:")
    for issue in inconsistencies:
        print(issue)

# Summary of units found
print("\nSummary of units by substance:")
for substance, units in sorted(unit_by_substance.items()):
    unique_units = set(unit for unit, _ in units)
    count = len(units)
    print(f"Substance {substance}: {count} instances, Units: {unique_units}")