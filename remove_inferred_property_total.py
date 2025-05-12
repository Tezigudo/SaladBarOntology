import rdflib
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDF
import shutil

# Define namespaces
S = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# List of hasTotal* properties to remove
PROPERTIES_TO_REMOVE = [
    S.hasTotalCalcium,
    S.hasTotalCarbohydrate,
    S.hasTotalCholesterol,
    S.hasTotalFat,
    S.hasTotalFoodEnergy,
    S.hasTotalIron,
    S.hasTotalLutein,
    S.hasTotalOmega_3,
    S.hasTotalPotassium,
    S.hasTotalProtein,
    S.hasTotalSodium,
    S.hasTotalVitaminA,
    S.hasTotalVitaminB9,
    S.hasTotalVitaminC,
    S.hasTotalZeaxanthin,
    S.hasTotalZinc,
    S.hasTotalVitaminE
]

def remove_total_links_and_substances():
    """
    Remove all hasTotal* property links, SaladSubstance instances, and their hasAmount and hasUnit triples from the ontology.
    """
    g = Graph()
    try:
        g.parse("salad_ontology.rdf", format="xml")
    except FileNotFoundError:
        print("Error: salad_ontology.rdf not found. Exiting.")
        return
    
    # Count total triples before removal
    initial_triple_count = len(g)
    print(f"Total triples before removal: {initial_triple_count}")
    
    # Step 1: Remove all hasTotal* property links
    removed_link_count = 0
    for prop in PROPERTIES_TO_REMOVE:
        prop_name = prop.split("#")[-1]
        triples = list(g.triples((None, prop, None)))
        for s, p, o in triples:
            g.remove((s, p, o))
            removed_link_count += 1
            print(f"Removed link: {s.split('#')[-1]} {prop_name} {o.split('#')[-1]}")
    
    print(f"\nRemoved {removed_link_count} hasTotal* links.")
    
    # Step 2: Remove all SaladSubstance instances and their hasAmount, hasUnit triples
    removed_substance_count = 0
    removed_amount_unit_count = 0
    substances = list(g.subjects(RDF.type, S.SaladSubstance))
    for substance in substances:
        substance_name = substance.split("#")[-1]
        
        # Remove hasAmount triples
        for s, p, o in g.triples((substance, S.hasAmount, None)):
            g.remove((s, p, o))
            removed_amount_unit_count += 1
            print(f"Removed hasAmount for {substance_name}")
        
        # Remove hasUnit triples
        for s, p, o in g.triples((substance, S.hasUnit, None)):
            g.remove((s, p, o))
            removed_amount_unit_count += 1
            print(f"Removed hasUnit for {substance_name}")
        
        # Remove the SaladSubstance instance (RDF.type triple and any remaining triples)
        g.remove((substance, None, None))
        removed_substance_count += 1
        print(f"Removed SaladSubstance instance: {substance_name}")
    
    print(f"\nRemoved {removed_substance_count} SaladSubstance instances.")
    print(f"Removed {removed_amount_unit_count} hasAmount/hasUnit triples.")
    
    # Count total triples after removal
    final_triple_count = len(g)
    print(f"Total triples after removal: {final_triple_count}")
    print(f"Total triples removed: {initial_triple_count - final_triple_count}")
    
    # Save to a temporary file first, then copy to ensure proper update
    temp_file = "salad_ontology.rdf"
    g.serialize(destination=temp_file, format="xml")
    print("Updated ontology saved as 'salad_ontology.rdf'.")

if __name__ == "__main__":
    remove_total_links_and_substances()