import os
import rdflib.graph as g
from pathlib import Path
from prettytable import PrettyTable


name = Path(__file__).stem
directory = os.path.dirname(__file__)
ontology = os.path.abspath(os.path.join(directory, "..", "", "ke2_project.rdf"))
outfile = os.path.abspath(os.path.join(directory, "..", "output", f"{name}.html"))

graph = g.Graph()
graph.parse(ontology, format='xml')

def rename_uri(uri):
    try:
        return uri.replace(
            "http://www.semanticweb.org/nappaskorn/ontologies/2023/10/food-for-people-with-chronic-disease#", ""
        )
    except:
        return uri

def high_low_substance():
    return """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX f: <http://www.semanticweb.org/nappaskorn/ontologies/2023/10/food-for-people-with-chronic-disease#>
    
    SELECT ?food 

    (SUM(?energy) AS ?totalEnergy) 
    (IF(SUM(?energy) > ?highEnergyThreshold, "High", IF(SUM(?energy) < ?lowEnergyThreshold, "Low", "Normal")) AS ?energyStatus)
    
    (SUM(?fat) AS ?totalFat) 
    (IF(SUM(?fat) > ?highFatThreshold, "High", IF(SUM(?fat) < ?lowFatThreshold, "Low", "Normal")) AS ?fatStatus)
    
    (SUM(?cholesterol) AS ?totalCholesterol) 
    (IF(SUM(?cholesterol) > ?highCholesterolThreshold, "High", IF(SUM(?cholesterol) < ?lowCholesterolThreshold, "Low", "Normal")) AS ?cholesterolStatus)
    
    (SUM(?sodium) AS ?totalSodium) 
    (IF(SUM(?sodium) > ?highSodiumThreshold, "High", IF(SUM(?sodium) < ?lowSodiumThreshold, "Low", "Normal")) AS ?sodiumStatus)
    
    (SUM(?carbohydrate) AS ?totalCarbohydrate) 
    (IF(SUM(?carbohydrate) > ?highCarbohydrateThreshold, "High", IF(SUM(?carbohydrate) < ?lowCarbohydrateThreshold, "Low", "Normal")) AS ?carbohydrateStatus)
    
    (SUM(?protein) AS ?totalProtein) 
    (IF(SUM(?protein) > ?highProteinThreshold, "High", IF(SUM(?protein) < ?lowProteinThreshold, "Low", "Normal")) AS ?proteinStatus)
    
    (SUM(?calcium) AS ?totalCalcium) 
    (IF(SUM(?calcium) > ?highCalciumThreshold, "High", IF(SUM(?calcium) < ?lowCalciumThreshold, "Low", "Normal")) AS ?calciumStatus)
    
    (SUM(?potassium) AS ?totalPotassium) 
    (IF(SUM(?potassium) > ?highPotassiumThreshold, "High", IF(SUM(?potassium) < ?lowPotassiumThreshold, "Low", "Normal")) AS ?potassiumStatus)
    
    (SUM(?vitaminA) AS ?totalVitaminA) 
    (IF(SUM(?vitaminA) > ?highVitaminAThreshold, "High", IF(SUM(?vitaminA) < ?lowVitaminAThreshold, "Low", "Normal")) AS ?vitaminAStatus)
    
    (SUM(?vitaminC) AS ?totalVitaminC) 
    (IF(SUM(?vitaminC) > ?highVitaminCThreshold, "High", IF(SUM(?vitaminC) < ?lowVitaminCThreshold, "Low", "Normal")) AS ?vitaminCStatus)
    
    (SUM(?iron) AS ?totalIron)
    (IF(SUM(?iron) > ?highIronThreshold, "High", IF(SUM(?iron) < ?lowIronThreshold, "Low", "Normal")) AS ?ironStatus)
    
    WHERE {
        ?food rdf:type f:Food .
        ?food f:hasIngredientPortion ?ingredientPortion .
        ?ingredientPortion f:hasAmount ?amount .
        ?ingredientPortion f:hasIngredient ?ingredient .
        ?ingredient f:hasSubstancePortion ?substancePortion .
        ?substancePortion f:hasSubstance ?substance .

        OPTIONAL {
            FILTER(?substance = f:FoodEnergy)
            ?substancePortion f:hasAmount ?energy .
        }
        BIND(IF(BOUND(?energy), ?energy * ?amount/100, 0) AS ?energy)

        OPTIONAL {
            FILTER(?substance = f:Fat)
            ?substancePortion f:hasAmount ?fat .
        }
        BIND(IF(BOUND(?fat), ?fat * ?amount/100, 0) AS ?fat)

        OPTIONAL {
            FILTER(?substance = f:Cholesterol)
            ?substancePortion f:hasAmount ?cholesterol .
        }
        BIND(IF(BOUND(?cholesterol), ?cholesterol * ?amount/100, 0) AS ?cholesterol)

        OPTIONAL {
            FILTER(?substance = f:Sodium)
            ?substancePortion f:hasAmount ?sodium .
        }
        BIND(IF(BOUND(?sodium), ?sodium * ?amount/100, 0) AS ?sodium)

        OPTIONAL {
            FILTER(?substance = f:Carbohydrate)
            ?substancePortion f:hasAmount ?carbohydrate .
        }
        BIND(IF(BOUND(?carbohydrate), ?carbohydrate * ?amount/100, 0) AS ?carbohydrate)

        OPTIONAL {
            FILTER(?substance = f:Protein)
            ?substancePortion f:hasAmount ?protein .
        }
        BIND(IF(BOUND(?protein), ?protein * ?amount/100, 0) AS ?protein)

        OPTIONAL {
            FILTER(?substance = f:Calcium)
            ?substancePortion f:hasAmount ?calcium .
        }
        BIND(IF(BOUND(?calcium), ?calcium * ?amount/100, 0) AS ?calcium)

        OPTIONAL {
            FILTER(?substance = f:Potassium)
            ?substancePortion f:hasAmount ?potassium .
        }
        BIND(IF(BOUND(?potassium), ?potassium * ?amount/100, 0) AS ?potassium)

        OPTIONAL {
            FILTER(?substance = f:VitaminA)
            ?substancePortion f:hasAmount ?vitaminA .
        }
        BIND(IF(BOUND(?vitaminA), ?vitaminA * ?amount/100, 0) AS ?vitaminA)

        OPTIONAL {
            FILTER(?substance = f:VitaminC)
            ?substancePortion f:hasAmount ?vitaminC .
        }
        BIND(IF(BOUND(?vitaminC), ?vitaminC * ?amount/100, 0) AS ?vitaminC)

        OPTIONAL {
            FILTER(?substance = f:Iron)
            ?substancePortion f:hasAmount ?iron .
        }
        BIND(IF(BOUND(?iron), ?iron * ?amount/100, 0) AS ?iron)

        BIND(600 AS ?highEnergyThreshold)
        BIND(200 AS ?lowEnergyThreshold)
        BIND(25000 AS ?highFatThreshold)
        BIND(16000 AS ?lowFatThreshold)
        BIND(200000 AS ?highCholesterolThreshold)
        BIND(100000 AS ?lowCholesterolThreshold)
        BIND(1475 AS ?highSodiumThreshold)
        BIND(400 AS ?lowSodiumThreshold)
        BIND(100000 AS ?highCarbohydrateThreshold)
        BIND(40000 AS ?lowCarbohydrateThreshold)
        BIND(26000 AS ?highProteinThreshold)
        BIND(14000 AS ?lowProteinThreshold)
        BIND(500 AS ?highCalciumThreshold)
        BIND(300 AS ?lowCalciumThreshold)
        BIND(1133 AS ?highPotassiumThreshold)
        BIND(866 AS ?lowPotassiumThreshold)
        BIND(1 AS ?highVitaminAThreshold)
        BIND(0.8 AS ?lowVitaminAThreshold)
        BIND(33 AS ?highVitaminCThreshold)
        BIND(23 AS ?lowVitaminCThreshold)
        BIND(4 AS ?highIronThreshold)
        BIND(1 AS ?lowIronThreshold)
    }
    GROUP BY ?food
"""

if __name__ == "__main__":
    table = PrettyTable()
    table.field_names = [
        "food",
        "totalEnergy",
        "energyStatus",
        "totalFat",
        "fatStatus",
        "totalCholesterol",
        "cholesterolStatus",
        "totalSodium",
        "sodiumStatus",
        "totalCarbohydrate",
        "carbohydrateStatus",
        "totalProtein",
        "proteinStatus",
        "totalCalcium",
        "calciumStatus",
        "totalPotassium",
        "potassiumStatus",
        "totalVitaminA",
        "vitaminAStatus",
        "totalVitaminC",
        "vitaminCStatus",
        "totalIron",
        "ironStatus"
    ]
    table.align = "l"
    
    query_str = high_low_substance()
    result = graph.query(query_str)
    
    for row in result:
        table.add_row([
            rename_uri(row.food),
            row.totalEnergy,
            row.energyStatus,
            row.totalFat,
            row.fatStatus,
            row.totalCholesterol,
            row.cholesterolStatus,
            row.totalSodium,
            row.sodiumStatus,
            row.totalCarbohydrate,
            row.carbohydrateStatus,
            row.totalProtein,
            row.proteinStatus,
            row.totalCalcium,
            row.calciumStatus,
            row.totalPotassium,
            row.potassiumStatus,
            row.totalVitaminA,
            row.vitaminAStatus,
            row.totalVitaminC,
            row.vitaminCStatus,
            row.totalIron,
            row.ironStatus
        ])
    
    print(table.get_string())
    
    with open(outfile, "w+") as f:
        f.write(table.get_html_string())
                         