""" 
Modelling.py

Functions to support the modelling of groundtruth SHACL shapes.
"""
import os
import json
from typing import Tuple
from jinja2 import Environment, FileSystemLoader
from .FileHandling import save_file
from .Logger import setup_logger

logger = setup_logger(__name__, "logs/Modelling.log")


def extract_details(desc_path: str) -> Tuple[str, str, str, str, str]:
    """
    Extract the following details from a social benefit description that
    is a flat dictionary:
    - Name in camel case
    - IDLB
    - Requirements text
    - Legal basis
    - Short description
    - Addressee

    :param desc_path: Path to the social benefit description.
    :return: Tuple of details listed above.
    """
    # Load social benefit description
    with open(desc_path, 'r', encoding='utf-8') as json_file:
        benefit_description = json.load(json_file)

    # Extract name, IDLB and requirements
    full_name = benefit_description["name"].split()
    camel_case_name = full_name[0] + ''.join(word.capitalize() for word in full_name[1:])
    idlb = benefit_description["idlb"]
    requirements = benefit_description["requirements"]
    legal_basis = benefit_description["legal_basis"]
    description = benefit_description["description"]
    addressee = benefit_description["addressees"]

    return camel_case_name, idlb, requirements, legal_basis, description, addressee


def generate_modelling_template(full_desc_path: str, template_path: str, save_dir: str = None) -> str:
    """
    Populate a template for a particular social benefit. Supports
    SHACL gold and requirements decomposition, depending on the provided
    template. Optionally saves the template if save_dir is specified.

    :param full_desc_path: Path to the full benefit description.
    :param template_path: Path to template file.
    :param save_dir: Directory to save the populated template.

    :return: Populated template as a string.
    """
    env = Environment(loader=FileSystemLoader('/'))
    template = env.get_template(template_path)
    
    # Extract details from the social benefit description
    name, idlb, requirements, legal_basis, description, addressee = extract_details(full_desc_path)

    # Load content depending on template type
    if "shacl" in os.path.basename(template_path):
        rendered_content = template.render(name=name, idlb=idlb, requirements=requirements)
        suffix = "ttl"
    else:
        rendered_content = template.render(name=name, idlb=idlb, addressee=addressee, requirements=requirements, legal_basis=legal_basis, description=description)
        suffix = "md"
    
    subfolder = os.path.basename(os.path.normpath(save_dir)) # e.g., shacl_gold, requirements_decomposition
    type = subfolder.split('_', 1)[-1]
    
    # Save the populated template, if it does not yet exist
    if save_dir:
        save_path = os.path.join(save_dir, f"{idlb}_{type}.{suffix}")
        if os.path.exists(save_path):
            logger.info(f"Skipping save. File already exists: {save_path}")
        else:
            save_file(rendered_content, save_path, logger)
    
    return rendered_content