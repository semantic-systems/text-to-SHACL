"""
 dataset_templates.py
 
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
import textwrap
from typing import List


def extract_benefit_information(input_file_path: dict) -> List[str]:
    """Extracts information from a social benefit description.

    :param input_file_path: Path to benefit description.

    :return: List with name, IDLB, and requirements text for the benefit.
    """
    # Load full benefit description
    with open(input_file_path, 'r', encoding='utf-8') as json_file:
        benefit_description = json.load(json_file)

    # Extract name, IDLB and requirements
    name = benefit_description["short_name"]
    idlb = benefit_description["idlb"]
    requirements = benefit_description["requirements"]

    return name, idlb, requirements


def generate_shacl_template(name: str, idlb: str, output_dir: str) -> None:
    """Generates a SHACL template with some standard components.

    :param name: Name of the social benefit.
    :param idlb: Unique ID for the social benefit.
    :param output_dir: Directory where the generated template will be saved.
    """
    template_content = textwrap.dedent(f"""\
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix ff: <https://foerderfunke.org/default#> .

        # METADATA

        ff:{idlb} a ff:SocialBenefit ;
            rdfs:label "{name}" .

        # CONSTRAINTS

        ff:{name}Shape a sh:NodeShape ;
            ff:checksFundingRequirement ff:{idlb} .
        """)

    output_path = os.path.join(output_dir, f"{name.lower()}_gold.ttl")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template_content)

    print(f"SHACL template saved successfully at {output_path}")


def generate_decomposition_template(name: str, requirements: str, output_dir: str) -> None:
    """Saves the requirements in a Markdown file for manual decomposition.

    :param requirements: Textual requirements for the social benefit.
    :param output_dir: Directory where the markdown file will be saved.
    """
    output_path = os.path.join(output_dir, f"{name.lower()}_decomposed.md")
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
        generate_decomposition_template(name, requirements, output_dir_decomposition)
