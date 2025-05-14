from rdflib import Graph, Namespace, OWL, RDF, RDFS
from rdflib.term import BNode, Literal
import random

# Load the ontology
g = Graph()
g.parse("salad_ontology.rdf", format="xml")

# Define namespaces
sbo = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")
g.bind("s", sbo)

with open("ontology_summary_focused.txt", "w", encoding="utf8") as output_file:
    def print_n3(item):
        return item.n3(g.namespace_manager)
    
    # Build subclass and superclass maps
    classes = set(g.subjects(RDF.type, OWL.Class))
    subclass_map = {}
    superclass_map = {}
    for sub, sup in g.subject_objects(RDFS.subClassOf):
        if isinstance(sub, BNode) or isinstance(sup, BNode):
            continue
        subclass_map.setdefault(sup, []).append(sub)
        superclass_map.setdefault(sub, []).append(sup)
    
    # Find root classes (those that are not a subclass of any class)
    roots = [cls for cls in classes if cls not in superclass_map]
    if OWL.Thing not in roots:
        roots.append(OWL.Thing)
    
    # Function to check if a class is a subclass of another (including itself)
    def is_subclass(cls, target_class):
        if cls == target_class:
            return True
        visited = set()
        to_check = [cls]
        while to_check:
            current = to_check.pop()
            if current in visited:
                continue
            visited.add(current)
            for sup in superclass_map.get(current, []):
                if sup == target_class:
                    return True
                to_check.append(sup)
        return False
    
    # Write class hierarchy recursively with restrictions
    def write_class_tree(class_uri, indent=0, visited=None):
        if visited is None:
            visited = set()
        if class_uri in visited:
            return
        visited.add(class_uri)
        
        output_file.write("  " * indent + f"- {print_n3(class_uri)}\n")
        
        # Get class label if available
        for label in g.objects(class_uri, RDFS.label):
            output_file.write("  " * (indent + 1) + f"Label: {label}\n")
        
        # Class restrictions
        for s, p, restriction in g.triples((class_uri, RDFS.subClassOf, None)):
            if isinstance(restriction, BNode):
                types = list(g.objects(restriction, RDF.type))
                if OWL.Restriction in types:
                    on_property = next(g.objects(restriction, OWL.onProperty), None)
                    
                    # Check for all possible restriction types
                    restriction_types = [
                        (OWL.allValuesFrom, "allValuesFrom"),
                        (OWL.someValuesFrom, "someValuesFrom"),
                        (OWL.hasValue, "hasValue"),
                        (OWL.minCardinality, "minCardinality"),
                        (OWL.maxCardinality, "maxCardinality"),
                        (OWL.cardinality, "cardinality")
                    ]
                    
                    for restriction_type, type_name in restriction_types:
                        restriction_value = next(g.objects(restriction, restriction_type), None)
                        if on_property and restriction_value is not None:
                            output_file.write("  " * (indent + 1) + 
                                            f"Restriction: {print_n3(on_property)} {type_name} {print_n3(restriction_value)}\n")
        
        # Class properties (via domain)
        for prop in g.subjects(RDFS.domain, class_uri):
            prop_range = next(g.objects(prop, RDFS.range), None)
            range_str = f" → {print_n3(prop_range)}" if prop_range else ""
            output_file.write("  " * (indent + 1) + f"Property: {print_n3(prop)}{range_str}\n")
 
        # Recurse into subclasses
        for sub in sorted(subclass_map.get(class_uri, []), key=lambda x: print_n3(x)):
            write_class_tree(sub, indent + 1, visited)
    
    # Find a salad instance for detailed exploration
    def find_salad_instance():
        # Explicitly look for instances of sbo:Salad
        salad_class = sbo.Salad
        instances = list(g.subjects(RDF.type, salad_class))
        if instances:
            output_file.write(f"Found salad instance of class {print_n3(salad_class)}\n")
            return random.choice(instances)
        
        # If no direct instances of sbo:Salad, look for subclasses of sbo:Salad
        salad_subclasses = list(g.subjects(RDFS.subClassOf, salad_class))
        for subclass in salad_subclasses:
            if isinstance(subclass, BNode):
                continue
            instances = list(g.subjects(RDF.type, subclass))
            if instances:
                output_file.write(f"Found salad subclass instance of {print_n3(subclass)}\n")
                return random.choice(instances)
        
        # If no salad instances found, search for any instance with "Salad" in its URI
        for subject in g.subjects(RDF.type, OWL.NamedIndividual):
            if "Salad" in str(subject):
                output_file.write(f"Found instance with 'Salad' in name: {print_n3(subject)}\n")
                return subject
        
        # If no salad instances found at all, explicitly tell the user
        output_file.write("No salad instances found in the ontology. Using an alternative instance.\n")
        
        # Try classes that might be salad components
        potential_component_classes = []
        for cls in classes:
            class_str = str(cls).lower()
            if any(term in class_str for term in ["vegetable", "ingredient", "topping", "dressing"]):
                potential_component_classes.append(cls)
        
        # Try to find instances of potential component classes
        for component_cls in potential_component_classes:
            instances = list(g.subjects(RDF.type, component_cls))
            if instances:
                return random.choice(instances)
        
        # Last resort: return any random instance
        all_instances = list(g.subjects(RDF.type, OWL.NamedIndividual))
        if all_instances:
            return random.choice(all_instances)
                
        return None
    
    # Recursively explore an instance and its related instances
    def explore_instance(instance, depth=0, max_depth=3, visited=None):
        if visited is None:
            visited = set()
            
        if depth > max_depth or instance in visited:
            return
            
        visited.add(instance)
        
        # Get instance types
        types = list(g.objects(instance, RDF.type))
        type_str = ", ".join([print_n3(t) for t in types if not isinstance(t, BNode)])
        output_file.write("  " * depth + f"{print_n3(instance)} (Types: {type_str})\n")
        
        # Get instance label if available
        for label in g.objects(instance, RDFS.label):
            output_file.write("  " * (depth + 1) + f"Label: {label}\n")
        
        # Check if instance is Ingredient or Dressing (including subclasses)
        is_ingredient_or_dressing = any(is_subclass(t, sbo.Ingredient) or is_subclass(t, sbo.Dressing) for t in types if not isinstance(t, BNode))
        
        # Collect substance portions and other properties
        substance_portions = []
        other_properties = []
        
        for p, o in g.predicate_objects(instance):
            # Skip type, already displayed above
            if p == RDF.type:
                continue
                
            # Check if this is a substance portion link
            if p == sbo.hasSubstancePortion and not isinstance(o, Literal):
                substance_portions.append((p, o))
            else:
                other_properties.append((p, o))
        
        # Process substance portions for Ingredient or Dressing (randomized, max 4)
        if is_ingredient_or_dressing and substance_portions:
            random.shuffle(substance_portions)
            substance_portions = substance_portions[:4]
        
        # Combine properties for processing (substance portions first, then others)
        properties = substance_portions + sorted(other_properties, key=lambda x: print_n3(x[0]))
        
        for p, o in properties:
            # Get property label if available
            prop_label = next(g.objects(p, RDFS.label), None)
            prop_display = f"{print_n3(p)}" + (f" ({prop_label})" if prop_label else "")
            
            if isinstance(o, Literal):
                output_file.write("  " * (depth + 1) + f"{prop_display}: {o}\n")
            else:
                # Get object label if available
                obj_label = next(g.objects(o, RDFS.label), None)
                obj_display = f"{print_n3(o)}" + (f" ({obj_label})" if obj_label else "")
                
                # Get object types
                obj_types = list(g.objects(o, RDF.type))
                obj_type_str = ", ".join([print_n3(t) for t in obj_types if not isinstance(t, BNode)])
                if obj_type_str:
                    obj_display += f" [Types: {obj_type_str}]"
                
                output_file.write("  " * (depth + 1) + f"{prop_display}: {obj_display}\n")
                
                # Recursively explore this object
                explore_instance(o, depth + 2, max_depth, visited)
    
    def print_property(prop, indent=0, visited=None):
        if visited is None:
            visited = set()
        
        if prop in visited:
            return
        
        visited.add(prop)
        
        indent_str = "  " * indent
        output_file.write(f"{indent_str}Property: {print_n3(prop)}\n")
        
        # Get label if available
        for label in g.objects(prop, RDFS.label):
            output_file.write(f"{indent_str}  Label: {label}\n")
        
        # Get domains
        domains = list(g.objects(prop, RDFS.domain))
        if domains:
            domain_str = ", ".join([print_n3(d) for d in domains])
            output_file.write(f"{indent_str}  Domain: {domain_str}\n")
        
        # Get ranges
        ranges = list(g.objects(prop, RDFS.range))
        if ranges:
            range_str = ", ".join([print_n3(r) for r in ranges])
            output_file.write(f"{indent_str}  Range: {range_str}\n")
        
        # Get property characteristics (for object properties)
        characteristics = []
        if (prop, RDF.type, OWL.FunctionalProperty) in g:
            characteristics.append("Functional")
        if (prop, RDF.type, OWL.TransitiveProperty) in g:
            characteristics.append("Transitive")
        if (prop, RDF.type, OWL.SymmetricProperty) in g:
            characteristics.append("Symmetric")
        if (prop, RDF.type, OWL.AsymmetricProperty) in g:
            characteristics.append("Asymmetric")
        if (prop, RDF.type, OWL.ReflexiveProperty) in g:
            characteristics.append("Reflexive")
        if (prop, RDF.type, OWL.IrreflexiveProperty) in g:
            characteristics.append("Irreflexive")
        
        if characteristics:
            output_file.write(f"{indent_str}  Characteristics: {', '.join(characteristics)}\n")
        
        # Get inverse properties (for object properties)
        for inv in g.objects(prop, OWL.inverseOf):
            output_file.write(f"{indent_str}  Inverse Of: {print_n3(inv)}\n")
        
        output_file.write("\n")
        
        # Get subproperties
        subproperties = list(g.subjects(RDFS.subPropertyOf, prop))
        subproperties.sort(key=lambda x: print_n3(x))
        for subprop in subproperties:
            output_file.write(f"{indent_str}  Subproperty:\n")
            print_property(subprop, indent + 2, visited)

    def list_properties():
        output_file.write("=== OBJECT PROPERTIES ===\n\n")
        
        # Get all object properties that are not subproperties
        object_properties = list(g.subjects(RDF.type, OWL.ObjectProperty))
        top_level_props = [p for p in object_properties if not list(g.objects(p, RDFS.subPropertyOf))]
        top_level_props.sort(key=lambda x: print_n3(x))
        
        for prop in top_level_props:
            print_property(prop)
        
        output_file.write("\n=== DATA PROPERTIES ===\n\n")
        
        # Get all data properties that are not subproperties
        data_properties = list(g.subjects(RDF.type, OWL.DatatypeProperty))
        top_level_data_props = [p for p in data_properties if not list(g.objects(p, RDFS.subPropertyOf))]
        top_level_data_props.sort(key=lambda x: print_n3(x))
        
        for prop in top_level_data_props:
            output_file.write(f"Property: {print_n3(prop)}\n")
            
            # Get label if available
            for label in g.objects(prop, RDFS.label):
                output_file.write(f"  Label: {label}\n")
            
            # Get domains
            domains = list(g.objects(prop, RDFS.domain))
            if domains:
                domain_str = ", ".join([print_n3(d) for d in domains])
                output_file.write(f"  Domain: {domain_str}\n")
            
            # Get ranges
            ranges = list(g.objects(prop, RDFS.range))
            if ranges:
                range_str = ", ".join([print_n3(r) for r in ranges])
                output_file.write(f"  Range: {range_str}\n")
            
            # Check if functional
            if (prop, RDF.type, OWL.FunctionalProperty) in g:
                output_file.write(f"  Characteristic: Functional\n")
            
            # Get subproperties
            subproperties = list(g.subjects(RDFS.subPropertyOf, prop))
            subproperties.sort(key=lambda x: print_n3(x))
            for subprop in subproperties:
                output_file.write(f"  Subproperty:\n")
                print_property(subprop, indent=2)
            
            output_file.write("\n")
        
    # === MAIN EXECUTION ===
    output_file.write(f"The ontology contains {len(g)} triples.\n\n")
    
    # Part 1: Output Class Hierarchy with restrictions
    output_file.write("=== CLASS HIERARCHY ===\n\n")
    visited_classes = set()
    for root in sorted(roots, key=lambda x: print_n3(x)):
        write_class_tree(root, visited=visited_classes)
    
    # Part 2: List all properties with domains and ranges
    output_file.write("\n\n")
    list_properties()
    
    # Part 3: Detailed exploration of a salad instance
    output_file.write("\n\n=== DETAILED SALAD EXPLORATION ===\n\n")
    
    salad_instance = find_salad_instance()
    if salad_instance:
        output_file.write(f"Starting exploration from: {print_n3(salad_instance)}\n\n")
        explore_instance(salad_instance, depth=0, max_depth=10)
    else:
        output_file.write("No suitable salad instance found in the ontology.\n")