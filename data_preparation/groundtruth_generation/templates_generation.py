"""
 dataset_templates.py

 Master's Thesis
 Seike Appold
 
 - Generate and save a SHACL template with some initial information
 including common prefixes and metadata for a given benefit.
 - Generate and save a markdown file with the requirements text as a
 template for manual decomposition into individual requirements.
 - Templates are intended to facilitate manual modelling, not to be
 further processed as they are.
"""
import os
import json
import sys
from typing import List


def extract_benefit_information(input_file_path: dict) -> List[str]:
    """Extracts information from a full social benefit description.

    :param input_file_path: Path to full benefit description.

    :return: List containing name, IDLB and requirements for the benefit.
    """
    # Load full benefit description
    with open(input_file_path, 'r', encoding='utf-8') as f:
        social_benefit_description = json.load(f)

    # Extract name, IDLB and requirements
    name = social_benefit_description["name"].split(" ")[0].capitalize()
    idlb = social_benefit_description["id"].replace(".", "_")
    requirements = ""
    for detail in social_benefit_description["details"]:
        if detail["title"] == "Voraussetzungen":
            requirements = detail["text"]

    return name, idlb, requirements


def generate_shacl_template(name: str, idlb: str, output_dir: str) -> None:
    """Generates a SHACL template.

    Based on information about a social benefit, generate a template for
    a SHACL shapes graph representing the eligibility requirements and
    save to the specified location.

    :param name: Name of the social benefit.
    :param idlb: Unique ID for the social benefit.
    :param output_dir: Directory where the generated template will be saved.

    :return: None
    """
    template_content = f"""@prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix ff: <https://foerderfunke.org/default#> .

    #################################################################
    #    METADATA
    #################################################################

    ff:{idlb} a ff:SocialBenefit ;
        rdfs:label "{name}" .

    #################################################################
    #    CONSTRAINTS
    #################################################################

    ff:{name}Shape a sh:NodeShape ;
        ff:checksFundingRequirement ff:{idlb} .
    """

    output_path = os.path.join(output_dir, f"{idlb}_true.ttl")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template_content)

    print(f"SHACL template saved successfully at {output_path}")


def generate_decomposition_template(requirements: str, output_dir: str) -> None:
    """Saves the requirements in a Markdown file for manual decomposition.

    :param requirements: Textual requirements for the social benefit.
    :param output_dir: Directory where the markdown file will be saved.

    :return: None
    """
    output_path = os.path.join(output_dir, "requirements.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("<b>Original requirements text</b>\n\n")
        f.write(requirements)
        f.write("\n\n<b>Requirements decomposition</b>\n\n")

    print(f"Decomposition template saved successfully at {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python templates_generation.py <input_filepath> <output_dir_groundtruth> <output_dir_decomposition>")
    else:
        input_filepath = sys.argv[1]
        output_dir_groundtruth = sys.argv[2]
        output_dir_decomposition = sys.argv[3]
        
        # Extract name, idlb and requirements from the full benefit description
        name, idlb, requirements = extract_benefit_information(input_filepath)

        # Generate SHACL template and decomposition template
        generate_shacl_template(name, idlb, output_dir_groundtruth)
        generate_decomposition_template(requirements, output_dir_decomposition)
