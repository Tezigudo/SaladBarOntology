import rdflib
from collections import defaultdict
from typing import Dict, Set, List, Tuple

# Initialize RDF graph
g = rdflib.Graph()
# Load ontology (adjust path to your ontology file)
ontology_file = "salad_ontology.rdf"  # Update with your file path
g.parse(ontology_file, format="xml")

# Define namespace
S = rdflib.Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")
RDF = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

def query_units_with_count(class_name: str, extra_condition: str = "") -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    """Query unique s:hasUnit values with instance counts and list instance IRIs."""
    query = f"""
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    SELECT ?instance ?unit
    WHERE {{
        ?instance a s:{class_name} .
        ?instance s:hasUnit ?unit .
        {extra_condition}
    }}
    """
    results = g.query(query)
    unit_counts = defaultdict(int)
    unit_instances = defaultdict(list)
    for row in results:
        unit = str(row.unit)
        instance = str(row.instance)
        unit_counts[unit] += 1
        unit_instances[unit].append(instance)
    return unit_counts, unit_instances

def query_substance_units_with_count() -> Tuple[Dict[str, Dict[str, int]], Dict[str, Dict[str, List[str]]]]:
    """Query unique s:hasUnit values for SubstancePortion per substance with counts and instance IRIs."""
    query = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    SELECT ?portion ?substance ?unit
    WHERE {
        ?portion a s:SubstancePortion .
        ?portion s:hasSubstance ?substance .
        ?portion s:hasUnit ?unit .
    }
    """
    results = g.query(query)
    substance_unit_counts = defaultdict(lambda: defaultdict(int))
    substance_unit_instances = defaultdict(lambda: defaultdict(list))
    for row in results:
        substance = str(row.substance).split('#')[-1]  # Extract local name
        unit = str(row.unit)
        portion = str(row.portion)
        substance_unit_counts[substance][unit] += 1
        substance_unit_instances[substance][unit].append(portion)
    return substance_unit_counts, substance_unit_instances

def check_unit_consistency():
    """Check unit consistency for SubstancePortion, IngredientPortion, and DressingPortion."""
    print("=== Unit Consistency Check ===")
    
    # Check IngredientPortion units
    print("\n1. IngredientPortion Units:")
    ingredient_counts, ingredient_instances = query_units_with_count("IngredientPortion")
    print("Unit counts:")
    for unit, count in sorted(ingredient_counts.items()):
        print(f"- '{unit}': {count} instances")
    if len(ingredient_counts) > 1:
        print("WARNING: Multiple units found for IngredientPortion. Expected a single unit (e.g., grams).")
        print("Instances with each unit:")
        for unit, instances in sorted(ingredient_instances.items()):
            print(f"- '{unit}':")
            for instance in instances:
                print(f"  - {instance}")
    elif len(ingredient_counts) == 0:
        print("WARNING: No units found for IngredientPortion.")
    else:
        print(f"Consistent unit: {list(ingredient_counts.keys())[0]}")

    # Check DressingPortion units
    print("\n2. DressingPortion Units:")
    dressing_counts, dressing_instances = query_units_with_count("DressingPortion")
    print("Unit counts:")
    for unit, count in sorted(dressing_counts.items()):
        print(f"- '{unit}': {count} instances")
    if len(dressing_counts) > 1:
        print("WARNING: Multiple units found for DressingPortion. Expected a single unit (e.g., millilitres).")
        print("Instances with each unit:")
        for unit, instances in sorted(dressing_instances.items()):
            print(f"- '{unit}':")
            for instance in instances:
                print(f"  - {instance}")
    elif len(dressing_counts) == 0:
        print("WARNING: No units found for DressingPortion.")
    else:
        print(f"Consistent unit: {list(dressing_counts.keys())[0]}")

    # Check SubstancePortion units per substance
    print("\n3. SubstancePortion Units (by Substance):")
    substance_unit_counts, substance_unit_instances = query_substance_units_with_count()
    if not substance_unit_counts:
        print("WARNING: No SubstancePortion instances found.")
    for substance in sorted(substance_unit_counts.keys()):
        units = substance_unit_counts[substance]
        print(f"- {substance}:")
        print("  Unit counts:")
        for unit, count in sorted(units.items()):
            print(f"  - '{unit}': {count} instances")
        if len(units) > 1:
            print(f"  WARNING: Multiple units found for {substance}. Expected a single unit.")
            print("  Instances with each unit:")
            for unit, instances in sorted(substance_unit_instances[substance].items()):
                print(f"  - '{unit}':")
                for instance in instances:
                    print(f"    - {instance}")
        elif len(units) == 0:
            print(f"  WARNING: No units found for {substance}.")
        else:
            print(f"  Consistent unit: {list(units.keys())[0]}")

if __name__ == "__main__":
    check_unit_consistency()