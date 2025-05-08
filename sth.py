import rdflib
from rdflib import Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL

# Initialize RDF graph
g = rdflib.Graph()
# Load ontology (adjust path to your ontology file)
ontology_file = "salad_ontology.rdf"  # Update with your file path
try:
    g.parse(ontology_file, format="xml")
except Exception as e:
    print(f"Error loading ontology: {e}")
    exit(1)

# Define namespaces
S = rdflib.Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

# Check if CaesarDressing exists and its type
caesar_dressing = S.CaesarDressing
if (caesar_dressing, RDF.type, None) not in g:
    print(f"Error: {caesar_dressing} not found in ontology.")
    exit(1)

# Verify current types of CaesarDressing
current_types = [obj for _, _, obj in g.triples((caesar_dressing, RDF.type, None))]
print(f"Current types of {caesar_dressing}: {current_types}")

# Check if CaesarDressing has SubstancePortion links
substance_portions = list(g.objects(caesar_dressing, S.hasSubstancePortion))
if not substance_portions:
    print(f"Warning: {caesar_dressing} has no s:hasSubstancePortion links.")
    # Add a placeholder SubstancePortion if missing (for demonstration)
    substance_portion = URIRef(f"{S}CaesarDressingSubstancePortion_{str(uuid4()).replace('-', '')}")
    g.add((substance_portion, RDF.type, S.SubstancePortion))
    g.add((substance_portion, S.hasSubstance, S.Calcium))  # Example substance
    g.add((substance_portion, S.hasAmount, Literal("1.0", datatype=XSD.decimal)))
    g.add((substance_portion, S.hasUnit, Literal("mg/100g", datatype=XSD.string)))
    g.add((caesar_dressing, S.hasSubstancePortion, substance_portion))
    print(f"Added placeholder s:hasSubstancePortion {substance_portion} to {caesar_dressing}.")
else:
    print(f"{caesar_dressing} has s:hasSubstancePortion links: {substance_portions}")

# Ensure CaesarDressing is an instance of Creamy
if S.Creamy not in current_types:
    g.add((caesar_dressing, RDF.type, S.Creamy))
    print(f"Added {caesar_dressing} as instance of s:Creamy.")

# Save the updated ontology
output_file = "salad_ontology.rdf"
try:
    g.serialize(output_file, format="xml")
except Exception as e:
    print(f"Error saving ontology: {e}")
    exit(1)

print(f"Ontology updated successfully and saved to {output_file}")
print("Please re-run the reasoner to verify consistency.")