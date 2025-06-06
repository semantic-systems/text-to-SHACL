"""
AnalyzeDataset.py

Functions for analyzing the four components of the dataset:
- Requirements texts
- SHACL Gold
- Synthetic uesr profiles
- Ontology
"""

import os
import glob
import rdflib
import numpy as np
import ast
import statistics
import matplotlib.pyplot as plt
from typing import Dict
from rdflib.namespace import SH
from rdflib import RDF, RDFS, OWL, Graph, BNode
from collections import Counter, defaultdict

    # Define and clean constraint categories
CONSTRAINT_COMPONENTS = {
        "Value Type": [
            SH["class"], SH["datatype"], SH["nodeKind"]
        ],
        "Cardinality": [
            SH["minCount"], SH["maxCount"]
        ],
        "Value Range": [
            SH["minExclusive"], SH["minInclusive"], SH["maxExclusive"], SH["maxInclusive"]
        ],
        "String-based": [
            SH["minLength"], SH["maxLength"], SH["pattern"], SH["languageIn"], SH["uniqueLang"]
        ],
        "Property Pair": [
            SH["equals"], SH["disjoint"], SH["lessThan"], SH["lessThanOrEquals"]
        ],
        "Logical": [
            SH["not"], SH["and"], SH["or"], SH["xone"]
        ],
        "Shape-based": [
            SH["node"], SH["property"], SH["qualifiedValueShape"],
            SH["qualifiedMinCount"], SH["qualifiedMaxCount"]
        ],
        "Other": [
            SH["closed"], SH["ignoredProperties"], SH["hasValue"], SH["in"]
        ]
    }


def analyze_constraints(folder_path: str):
    """Compute statistics on the constraints extracted from the requirements texts in the specified folder."""
    # Types of constraints
    constraint_types = ['RED', 'GREEN', 'YELLOW']
    type_stats = {color: [] for color in constraint_types}
    
    markdown_files = glob.glob(os.path.join(folder_path, '*.md'))

    if not markdown_files:
        print("No markdown files found in the specified folder.")
        return

    for file_path in markdown_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            for c in constraint_types:
                count = content.count(c)
                type_stats[c].append(count)
    
    print(f"Total number of extracted constraints: {sum(sum(counts) for counts in type_stats.values())}\n")
    
    # Analyze by color
    for c in constraint_types:
        counts = type_stats[c]
        total = sum(counts)
        minimum = min(counts)
        maximum = max(counts)
        average = total / len(counts) if counts else 0
        print(f"{c}:")
        print(f"  Total mentions      : {total}")
        print(f"  Min per file        : {minimum}")
        print(f"  Max per file        : {maximum}")
        print(f"  Average per file    : {average:.2f}\n")
        
    # Analyze by file
    num_files = len(next(iter(type_stats.values())))

    # Compute total constraints per file by summing mentions across all colors
    constraints_per_file = [
        sum(type_stats[color][i] for color in ['RED', 'GREEN', 'YELLOW'])
        for i in range(num_files)
    ]

    # Compute statistics
    min_constraints = min(constraints_per_file)
    max_constraints = max(constraints_per_file)
    avg_constraints = sum(constraints_per_file) / num_files if num_files else 0
    
    print("Summary across all constraint types (RED, GREEN, YELLOW):")
    print(f"  Min total constraints in a single file : {min_constraints}")
    print(f"  Max total constraints in a single file : {max_constraints}")
    print(f"  Avg total constraints per file         : {avg_constraints:.2f}")

def analyze_ontology(file_path:str):
    """Analyze distribution of classes, properties, individuals, and data types in the ontology file."""
    g = rdflib.Graph()
    g.parse(file_path, format="turtle")

    # Data containers
    classes = set()
    object_properties = set()
    data_properties = set()
    individuals = set()
    individuals_per_class = defaultdict(set)
    datatype_ranges = Counter()
    subclasses_per_class = defaultdict(set)

    # Identify classes
    for s in g.subjects(RDF.type, OWL.Class):
        classes.add(s)
    for s in g.subjects(RDF.type, RDFS.Class):
        classes.add(s)

    # Identify object and data properties
    for s in g.subjects(RDF.type, OWL.ObjectProperty):
        object_properties.add(s)
    for s in g.subjects(RDF.type, OWL.DatatypeProperty):
        data_properties.add(s)
        for _, _, range in g.triples((s, RDFS.range, None)):
            datatype_ranges[range] += 1

    # Identify individuals and their classes
    for s, _, o in g.triples((None, RDF.type, None)):
        if o in classes:
            individuals.add(s)
            individuals_per_class[o].add(s)

    # Identify subclasses and their parent classes
    for subclass, _, superclass in g.triples((None, RDFS.subClassOf, None)):
        if superclass in classes:
            subclasses_per_class[superclass].add(subclass)

    # Print results
    print(f"Number of classes: {len(classes)}")
    print(f"Number of object properties: {len(object_properties)}")
    print(f"Number of data properties: {len(data_properties)}")

    print("\nDeclared data types (from rdfs:range):")
    for dtype, count in datatype_ranges.items():
        print(f"  - {dtype}: {count}")

    print(f"\nTotal number of individuals: {len(individuals)}")
    print("Number of individuals per class:")
    for cls, inds in individuals_per_class.items():
        print(f"  - {cls}: {len(inds)}")

    print("\nNumber of subclasses per class:")
    for cls, subs in subclasses_per_class.items():
        print(f"  - {cls}: {len(subs)}")
        

def analyze_data_graphs(file_path):
    """Analyzes the synthetic user profiles in the specified file and prints statistics."""
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()

    parsed = ast.parse(file_content)
    dicts = [node for node in parsed.body if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)]

    total_entries = []
    dict_sizes = {}
    fractions_eligible = []

    print("=== RDF Profiles Analysis ===\n")

    for node in dicts:
        dict_name = node.targets[0].id
        entries = {ast.literal_eval(k): ast.literal_eval(v) for k, v in zip(node.value.keys, node.value.values)}
        eligible = sum(1 for v in entries.values() if v == "eligible")
        ineligible = sum(1 for v in entries.values() if v == "ineligible")
        total = len(entries)

        dict_sizes[dict_name] = total
        total_entries.extend(entries.keys())

        # Calculate fraction eligible for this dictionary (avoid division by zero)
        frac_eligible = eligible / total if total > 0 else 0
        fractions_eligible.append(frac_eligible)

    # Compute summary stats
    total_profiles = len(total_entries)
    min_dict_name, min_size = min(dict_sizes.items(), key=lambda x: x[1])
    max_dict_name, max_size = max(dict_sizes.items(), key=lambda x: x[1])
    mean_size = statistics.mean(dict_sizes.values())
    mean_fraction_eligible = statistics.mean(fractions_eligible)

    print(f"Total number of user profiles: {total_profiles}")
    print(f"Minimum profiles in one dictionary: {min_size} ({min_dict_name})")
    print(f"Maximum profiles in one dictionary: {max_size} ({max_dict_name})")
    print(f"Mean number of profiles per dictionary: {mean_size:.2f}")
    print(f"Mean fraction of eligible profiles per dictionary: {mean_fraction_eligible:.2f}")
        
        
def analyze_shapes(shacl_folder_path: str, shacl_core_vocab: str):
    """Analyze SHACL shapes in the specified folder and print organized results."""
    node_shapes = set()
    property_shapes = set()
    target_distribution = Counter()
    constraint_distribution = Counter()
    constraints_per_file = {}

    targets = {
        SH.targetNode,
        SH.targetClass,
        SH.targetSubjectsOf,
        SH.targetObjectsOf
    }

    constraint_params = extract_shacl_constraint_parameters(shacl_core_vocab)

    for filename in os.listdir(shacl_folder_path):
        if filename.endswith(".ttl"):
            g = Graph()
            g.parse(os.path.join(shacl_folder_path, filename), format="turtle")
            constraint_count = 0

            for s, p, o in g:
                if (p == RDF.type and o == SH.NodeShape) or (p == SH.node and isinstance(o, BNode)):
                    node_shapes.add(s if (p == RDF.type) else o)

                elif (p == RDF.type and o == SH.PropertyShape) or (p == SH.property and isinstance(o, BNode)):
                    property_shapes.add(s if (p == RDF.type) else o)

                if p in targets:
                    target_distribution[p] += 1

            for param in constraint_params:
                for _ in g.triples((None, param, None)):
                    constraint_distribution[param] += 1
                    constraint_count += 1

            constraints_per_file[filename] = constraint_count

    print("=== SHACL Shapes Analysis ===")
    print(f"Total Unique Node Shapes     : {len(node_shapes)}")
    print(f"Total Unique Property Shapes : {len(property_shapes)}\n")

    print("=== Target Declarations Distribution ===")
    for target in targets:
        count = target_distribution.get(target, 0)
        print(f"{target.n3()} : {count}")

    total_constraints = sum(constraint_distribution.values())
    print("\n=== Constraint Parameter Distribution by Category ===")
    print(f"\nTotal nof constraints: {total_constraints}")
    for section, params in CONSTRAINT_COMPONENTS.items():
        print(f"\n{section}")
        for param in params:
            count = constraint_distribution.get(param, 0)
            print(f"  {param.n3()} : {count}")

    used_params = {p for plist in CONSTRAINT_COMPONENTS.values() for p in plist}
    other_params = set(constraint_distribution.keys()) - used_params
    if other_params:
        print("\nUncategorized Constraint Parameters:")
        for param in sorted(other_params):
            print(f"  {param.n3()} : {constraint_distribution[param]}")

    # Constraint per file stats
    if constraints_per_file:
        min_file = min(constraints_per_file, key=constraints_per_file.get)
        max_file = max(constraints_per_file, key=constraints_per_file.get)
        mean_val = np.mean(list(constraints_per_file.values()))
        print("\n=== Constraints Per File Statistics ===")
        print(f"Min:  {constraints_per_file[min_file]} ({min_file})")
        print(f"Max:  {constraints_per_file[max_file]} ({max_file})")
        print(f"Mean: {mean_val:.2f}")
    
    return constraint_distribution


def extract_shacl_constraint_parameters(shacl_vocabulary_file: str) -> set:
    """Return a set of SHACL constraint parameter URIs used in shape graphs."""
    g = Graph()
    g.parse(shacl_vocabulary_file, format='turtle')

    parameters = set()

    for component in g.subjects(RDF.type, SH.ConstraintComponent):
        for param in g.objects(component, SH.parameter):
            for path in g.objects(param, SH.path):
                parameters.add(path)

    return parameters

def plot_constraint_distribution(constraint_distribution: Dict[str, int], save_path: str = None):
    """Plot distribution of SHACL constraint parameters as bar chart."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from rdflib.namespace import SH

    # IBM color palette
    ibm_palette = [
        "#648FFF",  # blue
        "#FFB000",  # yellow
        "#785EF0",  # purple
        "#FE6100",  # orange
        "#DC267F",  # pink
        "#009E73",  # green
    ]

    # Prepare data grouped by section (only used parameters)
    grouped_data = []
    for section, params in CONSTRAINT_COMPONENTS.items():
        used = [p for p in params if constraint_distribution.get(p, 0) > 0]
        if used:
            grouped_data.append((section, used))

    # Plot setup
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_facecolor("#f0f0f0")
    ax.grid(True, axis='y', color="white", linewidth=0.5)
    ax.set_axisbelow(True)

    bar_positions = []
    bar_labels = []
    bar_heights = []
    bar_colors = []

    current_x = 0
    group_gap = 0.5  # space between groups
    legend_patches = []

    # Process each group
    for idx, (group_name, params) in enumerate(grouped_data):
        group_color = ibm_palette[idx % len(ibm_palette)]
        legend_patches.append(mpatches.Patch(color=group_color, label=group_name))

        # Add bars for current group
        for _, param in enumerate(params):
            label = param.split("#")[-1]
            label = "sh:" + label
            count = constraint_distribution.get(param, 0)

            bar_positions.append(current_x)
            bar_labels.append(label)
            bar_heights.append(count)
            bar_colors.append(group_color)

            current_x += 1  # Move to next position without adding space

        current_x += group_gap  # Add space between this group and next

    # Plot bars
    ax.bar(bar_positions, bar_heights,width=1.0, color=bar_colors, edgecolor='black', linewidth=0.5)

    # X-axis settings
    ax.set_xticks(bar_positions)
    ax.set_xticklabels(bar_labels, rotation=45, ha='right', fontsize=9)

    # Y-axis settings
    ax.set_ylabel("Frequency")
    if bar_heights:
        ax.set_ylim(0, max(bar_heights) * 1.2)

    # Annotate values
    for x, h in zip(bar_positions, bar_heights):
        ax.text(x, h + 0.01 * max(bar_heights), str(h), ha='center', va='bottom', fontsize=8)

    # Legend settings
    legend = ax.legend(handles=legend_patches, title="Type of Constraint Components", loc='upper right', frameon=True)
    legend.get_frame().set_facecolor("#f0f0f0")
    legend.get_frame().set_edgecolor("#d0d0d0")
    legend.get_frame().set_linewidth(1.0)

    # Style cleanup
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)

    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Plot saved to {save_path}")
    
    plt.show()