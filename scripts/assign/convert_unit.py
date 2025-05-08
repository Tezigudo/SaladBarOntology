import rdflib

# Initialize RDF graph
g = rdflib.Graph()
# Load ontology (adjust path to your ontology file)
ontology_file = "salad_ontology.rdf"  # Update with your file path
g.parse(ontology_file, format="xml")

# Define namespace
S = rdflib.Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")
XSD = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")

# SPARQL UPDATE query to convert iu/100g to mg/100g for VitaminA
update_query = """
PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
DELETE { ?portion s:hasAmount ?amount . ?portion s:hasUnit "iu/100g" . }
INSERT { ?portion s:hasAmount ?newAmount . ?portion s:hasUnit "mg/100g" . }
WHERE {
    ?portion a s:SubstancePortion .
    ?portion s:hasSubstance s:VitaminA .
    ?portion s:hasAmount ?amount .
    ?portion s:hasUnit "iu/100g" .
    BIND (?amount * 0.0003 AS ?newAmount)
}
"""

# Execute the SPARQL UPDATE
g.update(update_query)

# Save the modified ontology
output_file = "salad_ontology.rdf"  # Output file path
g.serialize(output_file, format="xml")

print(f"Unit conversion completed. Modified ontology saved to {output_file}")
print("Converted 8 VitaminA instances from 'iu/100g' to 'mg/100g' using conversion factor 1 IU = 0.0003 mg.")
print("Please verify the updated ontology and re-run the consistency check script.")