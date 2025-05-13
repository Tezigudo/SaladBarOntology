
import rdflib
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, XSD
import shutil

S = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")

def calculate_Iron_for_salad(g, salad_name):
    salad_uri = S[salad_name]
    nutrient_total_name = f"{salad_name}Nutrition"
    nutrient_total_uri = S[nutrient_total_name]

    # Fetch all IngredientPortion and DressingPortion
    query = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?portion ?portionType ?amount ?unit ?component
    WHERE {
        ?salad s:hasIngredientPortion | s:hasDressingPortion ?portion .
        ?portion rdf:type ?portionType .
        ?portion s:hasAmount ?amount .
        ?portion s:hasUnit ?unit .
        ?portion s:hasIngredient | s:hasDressing ?component .
        FILTER (?salad = <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#${salad_name}>)
    }
    """
    results = g.query(query)
    total_amount = 0.0
    expected_unit = "mg/100g"
    nutrient_property = S.hasTotalIron

    for row in results:
        amount = float(row.amount)
        unit = str(row.unit)
        component = row.component

        # Get all substances on that component
        sub_q = """
        PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
        SELECT ?substancePortion ?substance ?amount ?unit
        WHERE {
            ?component s:hasSubstancePortion ?substancePortion .
            ?substancePortion s:hasSubstance ?substance .
            ?substancePortion s:hasAmount ?amount .
            ?substancePortion s:hasUnit ?unit .
            FILTER(?component = <${component}>)
        }
        """.replace("${component}", component)
        for sr in g.query(sub_q):
            name = str(sr.substance).split("#")[-1]
            if name != "Iron":
                continue
            val = float(sr.amount)
            u = str(sr.unit)
            if u != expected_unit:
                print(f"Unit mismatch for {name}: expected {expected_unit}, got {u}")
            factor = amount/100.0 if unit.lower() in ("g","grams","ml","millilitres") else 1.0
            total_amount += val * factor

    # write it out
    sub_uri = S[f"{salad_name}Iron"]
    g.set((sub_uri, RDF.type, S.SaladSubstance))
    g.set((sub_uri, S.hasAmount, Literal(total_amount, datatype=XSD.decimal)))
    display = "cal" if "Iron"=="FoodEnergy" else "mg"
    g.set((sub_uri, S.hasUnit, Literal(display, datatype=XSD.string)))
    g.set((nutrient_total_uri, RDF.type, S.SaladNutrientTotal))
    g.set((salad_uri, S.hasNutrient, nutrient_total_uri))
    g.set((nutrient_total_uri, nutrient_property, sub_uri))

def process_salads():
    g = Graph()
    g.parse("salad_ontology.rdf", format="xml")
    q = """
    PREFIX s: <http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#>
    SELECT ?salad WHERE {
        ?salad a s:Salad .
    }
    """
    for r in g.query(q):
        n = str(r.salad).split("#")[-1]
        calculate_Iron_for_salad(g, n)
    g.serialize("salad_ontology.rdf", format="xml")

if __name__ == "__main__":
    process_salads()
