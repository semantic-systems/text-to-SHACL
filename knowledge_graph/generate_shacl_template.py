"""
 generate_shacl_template.py

 Master's Thesis
 Seike Appold
 
 - From input JSON with a full service description, generate a Turtle template 
    for a SHACL shapes graph that already includes common namespaces and metadata,
    and a markdown file with the textual prerequisites. 
    Note: Output is intended to speed up modelling but should be veriefied manually.
"""
import json
import os
import textwrap
from typing import List
import argparse

def main(input_file_path, shacl_gold_dir, prerequisites_dir):
    with open(input_file_path, 'r', encoding='utf-8') as f:
        full_description = json.load(f)

    # Extract name, idlb and prerequisites from the full description
    name,idlb,prerequisites = extract_information(full_description)

    # Generate Turtle template with extracted information
    turtle_content = generate_template_content(name, idlb, prerequisites)
    output_path = os.path.join(shacl_gold_dir, f"{idlb}_true.ttl")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(turtle_content)
   
    print(f"Turtle file generated successfully at {shacl_gold_dir}")

    # Generate markdown file with prerequisites
    prerequisites_path = os.path.join(prerequisites_dir, f"{idlb}_{name.lower()}.md")
    with open(prerequisites_path, 'w', encoding='utf-8') as f:
        f.write(prerequisites)

    print(f"Prerequisites file generated successfully at {prerequisites_dir}")
    

def extract_information(full_description:dict) -> List[str]:
    """Extracts name, IDLB and prerequisites from the full description
    of an administrative service.

    :param full_description: Full service description.

    :return: List containing name, IDLB and prerequisites.
    """
    name = full_description["name"].split(" ")[0].capitalize()
    idlb = full_description["id"].replace(".", "_")
    prerequisites = ""

    for detail in full_description["details"]:
        if detail["title"] == "Voraussetzungen":
            prerequisites = detail["text"]
    
    return name, idlb, prerequisites

def generate_template_content(name, idlb, prerequisites):
    return f"""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ff: <https://foerderfunke.org/default#> .

#################################################################
#    METADATA
#################################################################

ff:{idlb} a ff:FundingProgram ;
    rdfs:label "{name}" . 

#################################################################
#    CONSTRAINTS
#################################################################

ff:{name}Shape a sh:NodeShape ;
    ff:checksFundingRequirement ff:{idlb} ;
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a SHACL shapes graph template from a social service description.")
    parser.add_argument("input_file_path", type=str, help="Path to the full service description in JSON.")
    parser.add_argument("shacl_gold_dir", type=str, help="Path to the directory where the generated SHACL template will be saved.")
    parser.add_argument("prerequisites_dir", type=str, help="Path to the directory where the prerequisites text file will be saved.")
    
    args = parser.parse_args()
    
    main(args.input_file_path, args.shacl_gold_dir, args.prerequisites_dir)