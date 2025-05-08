import rdflib

# Initialize RDF graph
g = rdflib.Graph()
# Load ontology (adjust path to your ontology file)
ontology_file = "salad_ontology.rdf"  # Update with your file path
g.parse(ontology_file, format="xml")

# Define namespace
S = rdflib.Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")
XSD = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")

# SPARQL UPDATE query to convert millilitres to grams for GreekYogurt120ml
update_query = """
PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
DELETE { ?portion s:hasAmount ?amount . ?portion s:hasUnit "millilitres" . }
INSERT { ?portion s:hasAmount ?newAmount . ?portion s:hasUnit "grams" . }
WHERE {
    ?portion a s:IngredientPortion .
    ?portion s:hasUnit "millilitres" .
    ?portion = s:GreekYogurt120ml .
    ?portion s:hasAmount ?amount .
    BIND (?amount * 1.1 AS ?newAmount)
}
"""

# Execute the SPARQL UPDATE
g.update(update_query)

# Save the modified ontology
output_file = "salad_ontology.rdf"  # Output file path
g.serialize(output_file, format="xml")

print(f"Unit conversion completed. Modified ontology saved to {output_file}")
print("Converted GreekYogurt120ml from 'millilitres' to 'grams' using density 1.1 g/ml.")
print("Please verify the updated ontology and re-run the consistency check script.")