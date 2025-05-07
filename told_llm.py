from rdflib import Graph, Namespace, OWL, RDF, RDFS
from rdflib.term import BNode, Literal

# Load the ontology
g = Graph()
g.parse("salad_ontology.rdf", format="xml")

# Define namespaces
sbo = Namespace("http://www.semanticweb.org/god/ontologies/2025/3/salad-bar-ontology#")
g.bind("s", sbo)

with open("ontology_summary_full.txt", "w") as output_file:
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

    # Write class hierarchy recursively
    def write_class_tree(class_uri, indent=0, visited=None):
        if visited is None:
            visited = set()
        if class_uri in visited:
            return
        visited.add(class_uri)

        output_file.write("  " * indent + f"- {print_n3(class_uri)}\n")

        # Class restrictions
        for _, restriction in g.predicate_objects(subject=class_uri):
            if isinstance(restriction, BNode):
                types = list(g.objects(restriction, RDF.type))
                if OWL.Restriction in types:
                    on_property = next(g.objects(restriction, OWL.onProperty), None)
                    restriction_type = next((p for p in [OWL.allValuesFrom, OWL.someValuesFrom, OWL.hasValue]
                                             if (restriction, p, None) in g), None)
                    restriction_value = next(g.objects(restriction, restriction_type), None) if restriction_type else None
                    if on_property and restriction_type and restriction_value:
                        output_file.write("  " * (indent + 1) +
                                          f"(Restriction) {print_n3(on_property)} {print_n3(restriction_type)} {print_n3(restriction_value)}\n")

        # Class properties (via domain)
        for prop in g.subjects(RDFS.domain, class_uri):
            output_file.write("  " * (indent + 1) + f"(Has Property) {print_n3(prop)}\n")

        # Recurse into subclasses
        for sub in sorted(subclass_map.get(class_uri, []), key=lambda x: print_n3(x)):
            write_class_tree(sub, indent + 1, visited)

    # Write instances for each class
    def write_instances_for_class(class_uri):
        output_file.write(f"\nInstances of {print_n3(class_uri)} (up to 2):\n")

        q_instances = f"""
        SELECT DISTINCT ?instance
        WHERE {{
            ?instance a {class_uri.n3()} .
        }}
        LIMIT 2
        """
        try:
            instances = [row['instance'] for row in g.query(q_instances)]
        except Exception as e:
            output_file.write(f"  Query error: {e}\n")
            return

        if not instances:
            output_file.write("  No instances found.\n")
            return

        visited = set()

        def write_properties(instance, indent=1):
            if instance in visited:
                output_file.write("  " * indent + f"Individual: {print_n3(instance)} (already visited)\n")
                return
            visited.add(instance)
            output_file.write("  " * indent + f"Individual: {print_n3(instance)}\n")
            for p, o in g.predicate_objects(instance):
                if isinstance(o, Literal):
                    output_file.write("  " * (indent + 1) + f"{print_n3(p)}: {o}\n")
                else:
                    output_file.write("  " * (indent + 1) + f"{print_n3(p)}: {print_n3(o)}\n")
                    if (o, RDF.type, OWL.NamedIndividual) in g or (o, RDF.type, None) in g:
                        write_properties(o, indent + 2)

        for instance in instances:
            write_properties(instance)
            output_file.write("\n")

    # === MAIN EXECUTION ===
    output_file.write(f"The ontology contains {len(g)} triples.\n\n")
    output_file.write("Class Hierarchy (Protégé-style):\n\n")
    visited_classes = set()
    for root in sorted(roots, key=lambda x: print_n3(x)):
        write_class_tree(root, visited=visited_classes)

    output_file.write("\nInstance Details:\n")
    for class_uri in sorted(classes, key=lambda x: str(x)):
        write_instances_for_class(class_uri)
