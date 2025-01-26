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

def extract_name_idlb_requirements(full_desc_path: str) -> Tuple[str, str, str]:
    """
    Extracts short name, idlb, and requirements text from a benefit description.

    :param full_desc_path: Path to the full benefit description.
    :return: List with name, IDLB, and requirements text for the benefit.
    """
    # Load full benefit description
    with open(full_desc_path, 'r', encoding='utf-8') as json_file:
        benefit_description = json.load(json_file)

    # Extract name, IDLB and requirements
    full_name = benefit_description["name"].split()
    camel_case_name = full_name[0] + ''.join(word.capitalize() for word in full_name[1:])
    idlb = benefit_description["idlb"]
    requirements = benefit_description["requirements"]

    return camel_case_name, idlb, requirements

def generate_modelling_template(full_desc_path: str, template_path: str, save_dir: str = None) -> str:
    """
    Populate a template for a particular social benefit. Suitable for
    SHACL gold templates and requirements decomposition templates. Optionally
    saves the template to save_dir if it is specified.

    :param full_desc_path: Path to the full benefit description.
    :param template_path: Path to template file.
    :param save_dir: Directory to save the populated template.
    
    :return: Populated template as a string.
    """
    env = Environment(loader=FileSystemLoader('/'))
    template = env.get_template(template_path)
    
    # Load variable values
    name, idlb, requirements = extract_name_idlb_requirements(full_desc_path)
    rendered_content = template.render(name=name, idlb=idlb, requirements=requirements)
    
    suffix = "ttl" if "shacl" in os.path.basename(template_path) else "md"
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