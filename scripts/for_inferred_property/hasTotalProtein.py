import rdflib
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, XSD

# Initialize RDF graph
g = rdflib.Graph()
# Load ontology (adjust path to your ontology file)
ontology_file = "salad_ontology.rdf"  # Update with your file path
try:
    g.parse(ontology_file, format="xml")
except Exception as e:
    print(f"Error loading ontology: {e}")
    exit(1)

# Define namespace
S = rdflib.Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# SPARQL query to calculate total protein
query = """
PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
SELECT ?salad (SUM(?scaledAmount) AS ?totalProtein)
WHERE {
    {
        ?salad s:hasIngredientPortion ?portion .
        ?portion s:hasIngredient ?ingredient .
        ?portion s:hasAmount ?portionAmount .
        ?portion s:hasUnit "grams" .
        ?ingredient s:hasSubstancePortion ?subPortion .
        ?subPortion s:hasSubstance s:Protein .
        ?subPortion s:hasAmount ?subAmount .
        BIND (?subAmount * ?portionAmount / 100.0 AS ?scaledAmount)
    } UNION {
        ?salad s:hasDressingPortion ?portion .
        ?portion s:hasDressing ?dressing .
        ?portion s:hasAmount ?portionAmount .
        ?portion s:hasUnit "millilitres" .
        ?dressing s:hasSubstancePortion ?subPortion .
        ?subPortion s:hasSubstance s:Protein .
        ?subPortion s:hasAmount ?subAmount .
        BIND (?subAmount * ?portionAmount / 100.0 AS ?scaledAmount)
    }
}
GROUP BY ?salad
"""

# Execute query and assign values
try:
    results = g.query(query)
    for row in results:
        salad = row.salad
        total_protein = float(row.totalProtein) if row.totalProtein else 0.0
        nutrient_instance = URIRef(f"{S}{str(salad).split('#')[-1]}Nutrition")
        g.add((nutrient_instance, S.hasTotalProtein, Literal(total_protein, datatype=XSD.decimal)))
        print(f"Assigned {total_protein} to {nutrient_instance} for s:hasTotalProtein.")
except Exception as e:
    print(f"Error executing SPARQL query: {e}")
    exit(1)

# Save the updated ontology
output_file = "salad_ontology.rdf"
try:
    g.serialize(output_file, format="xml")
except Exception as e:
    print(f"Error saving ontology: {e}")
    exit(1)

print(f"Ontology updated with s:hasTotalProtein values and saved to {output_file}")