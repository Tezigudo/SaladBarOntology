from rdflib import Graph, Namespace, RDF

# Load your ontology
g = Graph()
g.parse("salad_ontology.rdf", format="xml")

# Define your namespace
SALAD = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# Collect all individuals (instances)
instances_to_remove = []

for s, p, o in g.triples((None, RDF.type, None)):
    # Remove only individuals (i.e., not Classes or Properties)
    if not (str(o).startswith("http://www.w3.org/2002/07/owl#Class") or
            str(o).startswith("http://www.w3.org/2002/07/owl#ObjectProperty") or
            str(o).startswith("http://www.w3.org/2002/07/owl#DatatypeProperty")):
        instances_to_remove.append(s)

# Remove triples related to instances
for instance in instances_to_remove:
    g.remove((instance, None, None))
    g.remove((None, None, instance))

# Save cleaned ontology
g.serialize(destination="salad_ontology.rdf", format="xml")

print("\n✅ All individuals deleted successfully!")
