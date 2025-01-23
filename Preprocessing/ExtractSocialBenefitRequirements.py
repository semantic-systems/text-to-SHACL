"""
ExtractSocialBenefitRequirements.py

- From all administrative services, select social benefits to be analyzed.
- For the selected benefits, extract and save the relevant information 
    (name, IDLB, requirements text).
"""

import os
import json
import html
import html2text
import argparse
from typing import List, Any
from resources.schemata import service_desc_schema
from Utils.Logger import setup_logger
from Utils.FileHandling import save_dict_to_json

logger = setup_logger(__name__, log_file="logs/ExtractSocialBenefitRequirements.log")

def has_legal_basis(service_desc: json, legal_basis: List[str]) -> bool:
    """ 
    Checks if an administrative service has a given legal basis.
    
    :param service_desc: An administrative service description in JSON format.
    :param legal_basis: List of legal basis to check for.
    :return: True if the service description contains the legal basis, False otherwise.
    """        
    for item in service_desc.get("details", []):
        if item.get("title") == "Rechtsgrundlage(n)" and "links" in item:
            links = item["links"]
            for link in links:
                for basis in legal_basis:
                    if basis in link.get("title", ""):
                        return True
    return False

def has_personal_matter(service_desc: json, personal_matters: List[Any]) -> bool:
    """ 
    Checks if an administrative service has a given personal matter.
    
    :param service_desc: An administrative service description in JSON format.
    :param personal_matters: List of personal matters to check for as string or code.
    :return: True if the service description has the personal matter(s), False otherwise.
    """
    def search_codes(data, codes):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "code" and value in codes:
                    return True
                if search_codes(value, codes):
                    return True
        elif isinstance(data, list):
            for item in data:
                if search_codes(item, codes):
                    return True
        return False
    
    # Convert personal matters to codes, if the titles are provided
    personal_matters_codes = [
        service_desc_schema.personal_matters[matter] if isinstance(matter, str) else matter
        for matter in personal_matters
    ]
    return search_codes(service_desc, personal_matters_codes)

def has_addressee(service_desc: json, addressees = List[Any]) -> bool:
    """ 
    Checks if an administrative service has a given addressee.
    
    :param service_desc: An administrative service description in JSON format.
    :param addressees: List of addressees to check for as name or code.
    :return: True if the service description has the addressee(s), False otherwise.
    """
    # Convert addressees to codes, if the names are provided
    addressees_codes = [
        service_desc_schema.addressees[addressee] if isinstance(addressee, str) else addressee
        for addressee in addressees
    ]
    
    for item in service_desc.get('personalMatters', []):
        if item.get('code') in addressees_codes:
            return True
    return False

def get_social_benefit_paths(all_service_desc_dir: str, matters: List[str] = None, addressees: List[str] = None, legal_bases: List[str] = None) -> List[str]:
    """
    Retrieves IDLBs for selected social benefits based on the provided filters
    
    :param all_service_desc_dir: Directory with all full service descriptions.
    :param matters: List of personal matters to include (e.g. birth, social services...).
    :param addressees: List of addressees to include (e.g. citizens).
    :param legal_bases: List of legal bases to include (e.g. SGB).
    :return: List of paths to selected social benefit descriptions.
    """
    # For each service description, check if it matches the filters
    selected_filepaths = []
    for filename in os.listdir(all_service_desc_dir):
        filepath = os.path.join(all_service_desc_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            try:
                service_desc = json.load(file)
                # Skip services without requirements text
                if any(detail["title"] == "Voraussetzungen" and detail["text"] in ["nicht angegeben", " "] 
                    for detail in service_desc["details"]):
                    # logger.warning(f"Service description has no requirements text: {filename}")
                    continue
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON: {filename}")
                continue
        
        # Select services by both personal matters and addressees
        if has_personal_matter(service_desc, matters) and has_addressee(service_desc, addressees):
            selected_filepaths.append(filepath)
    
    logger.info(f"Selected {len(selected_filepaths)} social benefits based on personal matters {matters} and addressees {addressees}")
    
    # Select federal editorial system only
    selected_filepaths = [path for path in selected_filepaths if os.path.basename(path).startswith("B100019")]
    logger.info(f"Selected {len(selected_filepaths)} social benefits based on federal editorial system")
    return selected_filepaths

def get_social_benefit_dicts(selected_benefits_paths: List[str]) -> List[dict]:
    """  
    Extracts the name, IDLB, and requirements text from full service descriptions.
    
    :param selected_benefits_paths: List of paths to selected social benefit descriptions.
    :return: List of dictionaries with benefit details.
    """
    social_benefit_dicts = []
    for benefit in selected_benefits_paths:
        with open(benefit, 'r', encoding='utf-8') as file:
            full_desc = json.load(file)
        for detail in full_desc["details"]:
            if detail["title"] == "Voraussetzungen":
                requirements_html = detail["text"]
                requirements_text = html2text.html2text(requirements_html)
                requirements_text = requirements_text.rstrip("\n\r")
        benefit_details = {
            "name": full_desc["name"],
            "idlb": full_desc["id"].replace(".", "_"),
            "requirements": requirements_text
        } 
        social_benefit_dicts.append(benefit_details)
    return social_benefit_dicts

def main(all_service_desc_dir: str, save_dir: str, matters: List[str] = None, addressees: List[str] = None, legal_bases: List[str] = None):
    """
    Main function to extract and save social benefit requirements.

    :param all_service_desc_dir: Directory with all service descriptions (JSON).
    :param save_dir: Directory to save the extracted social benefit requirements.
    :side effects: Saves extracted social benefit details to save_dir.
    """
    # Get list of paths to selected social benefits
    selected_benefits_paths = get_social_benefit_paths(all_service_desc_dir=all_service_desc_dir, matters=matters, addressees=addressees, legal_bases=legal_bases)
    
    # Extract the IDLB, name, and requirements text
    social_benefit_dicts = get_social_benefit_dicts(selected_benefits_paths)
    
    logger.info(f"Extracted details for {len(social_benefit_dicts)} social benefits:")
    
    for benefit_dict in social_benefit_dicts:
        logger.info(f"{benefit_dict.get("name")} ({benefit_dict.get("idlb")})")
        save_path = os.path.join(save_dir, f"{benefit_dict['idlb']}.json")
        save_dict_to_json(benefit_dict, save_path)
        
    logger.info(f"Social benefit details saved in {save_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and save social benefit details.")
    parser.add_argument("all_service_desc_dir", type=str, help="Directory containing full service descriptions in JSON format.")
    parser.add_argument("save_dir", type=str, help="Directory to save the extracted social benefit details.")
    parser.add_argument("--matters", type=str, nargs="+", help="Personal matters to include.")
    parser.add_argument("--addressees", type=str, nargs="+", help="Addressees to include.")
    parser.add_argument("--legal_bases", type=str, nargs="+", help="Legal bases to include.")
    
    args = parser.parse_args()
    all_service_desc_dir = args.all_service_desc_dir
    save_dir = args.save_dir
    matters = args.matters
    addressees = args.addressees
    legal_bases = args.legal_bases
    main(all_service_desc_dir, save_dir, matters, addressees, legal_bases)