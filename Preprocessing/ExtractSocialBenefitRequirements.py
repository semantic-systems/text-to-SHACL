"""
ExtractSocialBenefitRequirements.py

- From all administrative services, select social benefits to be analyzed.
- Supported filters: addressee, personal matter, legal basis, manually defined
    IDLBs.
- For the selected benefits, extract and save the relevant information
    (name, IDLB, valid to, description, legal basis, requirements text).
"""

import os
import json
import html2text
import argparse
from typing import List, Any, Dict
from resources.schemata import service_desc_schema
from Utils.Logger import setup_logger
from Utils.FileHandling import save_dict_to_json

logger = setup_logger(__name__, log_file="logs/ExtractSocialBenefitRequirements.log")

# Set manually selected IDLBs
MANUAL_SELECTION = ["B100019_LB_576986", "L100040_LB_311291198", "L100040_LB_8665924", "L100040_LB_8664880", "L100040_LB_12280162"]

def has_legal_basis(service_desc: json, legal_basis: List[str]) -> bool:
    """ 
    Checks if an administrative service has a given legal basis.
    
    :param service_desc: An administrative service description in JSON format.
    :param legal_basis: List of legal basis to check for.
    :return: True if the service description contains the legal basis, False otherwise.
    """ 
    if legal_basis is None:
        return True
    
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
    :return: True if the service description has any of the personal matter(s), False otherwise.
    """
    if personal_matters is None:
        return True
    
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
    if addressees is None:
        return True
    
    # Convert addressees to codes, if the names are provided
    addressees_codes = [
        service_desc_schema.addressees[addressee] if isinstance(addressee, str) else addressee
        for addressee in addressees
    ]
    
    for item in service_desc.get('personalMatters', []):
        if item.get('code') in addressees_codes:
            return True
    return False

def get_social_benefit_paths(all_service_descriptions_dir: str, 
                             editorial_system: str, 
                             matters: List[str], 
                             addressees: List[str], 
                             legal_bases: List[str], 
                             manual_selection: List[str]) -> List[str]:
    """
    Retrieves filepaths to full description of selected social benefits.
    
    :param all_service_descriptions_dir: Directory with all full service descriptions.
    :param matters: List of personal matters to include (e.g. birth, social services...).
    :param addressees: List of addressees to include (e.g. citizens).
    :param legal_bases: List of legal bases to include (e.g. SGB).
    :return: List of paths to selected social benefit descriptions.
    """
    # For each service description, check if it matches the filters
    selected_filepaths = []
    for filename in os.listdir(all_service_descriptions_dir):
        filepath = os.path.join(all_service_descriptions_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            try:
                service_desc = json.load(file)
                # Skip services without requirements text
                if any(detail["title"] == "Voraussetzungen" and detail["text"] in ["nicht angegeben", " "] 
                    for detail in service_desc["details"]):
                    continue
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON: {filename}")
                continue
        
        # Select service if it includes one of the personal matters and addressees
        if has_personal_matter(service_desc, matters) and has_addressee(service_desc, addressees):
            selected_filepaths.append(filepath)
    logger.info(f"Applied filter for matters ({matters}) and addressee ({addressees}). {len(selected_filepaths)} files selected.")
    
    # Apply filter by editorial system
    selected_filepaths = [path for path in selected_filepaths if os.path.basename(path).startswith(editorial_system)]
    logger.info(f"Applied filter for editorial system ({editorial_system}). {len(selected_filepaths)} files selected.")
    
    # Append manual selection, that include services from different editorial systems
    selected_filepaths.extend([os.path.join(all_service_descriptions_dir, f"{idlb}.json") for idlb in manual_selection])    
    logger.info(f"Added maunal selection. {len(selected_filepaths)} files selected.")
    
    return selected_filepaths

def get_social_benefit_dicts(selected_benefits_paths: List[str]) -> List[Dict[str,str]]:
    """  
    Extracts relevant information from full descriptions, including name,
    IDLB, validTo, addressees, description, legal basis, and requirements.
    
    :param selected_benefits_paths: List of paths to selected full descriptions.
    :return: List of dictionaries with extracted details for each benefit.
    """
    social_benefit_dicts = []
    for benefit in selected_benefits_paths:
        with open(benefit, 'r', encoding='utf-8') as file:
            full_desc = json.load(file)
        
        # Requirements text and legal basis
        legal_basis_links = set()
        for detail in full_desc["details"]:
            if detail["title"] == "Voraussetzungen":
                requirements_html = detail["text"]
                requirements_text = html2text.html2text(requirements_html)
                requirements_text = requirements_text.rstrip("\n\r")
            elif detail["title"] == "Rechtsgrundlage(n)" and "links" in detail:
                for link in detail["links"]:
                    legal_basis_links.add(link["title"])
        legal_basis = "; ".join(legal_basis_links) if legal_basis_links else ""
        
        # Addressees
        addressee_names = set()
        for addressee in full_desc["personalMatters"]:
            addressee_names.add(addressee["name"])
        addressees = "; ".join(addressee_names) if addressee_names else ""
        
        benefit_details = {
            "name": full_desc["name"],
            "idlb": str(full_desc["id"]).replace(".", "_"),
            "valid_to": full_desc["validTo"],
            "addressees": addressees,
            "legal_basis": legal_basis,
            "description": html2text.html2text(full_desc["description"]).rstrip("\n\r"),
            "requirements": requirements_text
        } 
        social_benefit_dicts.append(benefit_details)
    return social_benefit_dicts

def main(all_service_descriptions_dir: str, 
         social_benefits_dir: str, 
         editorial_system: str = "B100019", 
         matters: List[str] = ["Sozialleistungen"], 
         addressees: List[str] = ["Bürger"], 
         legal_bases: List[str] = None, 
         manual_selection: List[str] = MANUAL_SELECTION):
    """
    Select social benefits from all service descriptions using the specified
    filters and save relevant details from the descriptions to disk.

    :param all_service_descriptions_dir: Directory with all service descriptions.
    :param social_benefits_dir: Directory to save the extracted social benefit requirements.
    :param matters: List of personal matters to include.
    :param addressees: List of addressees to include.
    :param legal_bases: List of legal bases to include.
    :param manual_selection: List of manually selected IDLBs to include.
    """
    # Get list of paths to selected social benefits
    selected_benefits_paths = get_social_benefit_paths(all_service_descriptions_dir=all_service_descriptions_dir,
                                                       editorial_system=editorial_system, 
                                                       matters=matters, 
                                                       addressees=addressees, 
                                                       legal_bases=legal_bases, 
                                                       manual_selection=manual_selection)
    
    # Extract the IDLB, name, and requirements text
    social_benefit_dicts = get_social_benefit_dicts(selected_benefits_paths)
    logger.info(f"Extracted details for {len(social_benefit_dicts)} social benefits:")
    
    for benefit_dict in social_benefit_dicts:
        logger.info(f"{benefit_dict.get('name')} ({benefit_dict.get('idlb')})")
        save_path = os.path.join(social_benefits_dir, f"{benefit_dict['idlb']}.json")
        save_dict_to_json(benefit_dict, save_path)
    logger.info(f"Social benefit details saved to {social_benefits_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and save social benefit details.")
    parser.add_argument("all_service_descriptions_dir", type=str, help="Directory containing full service descriptions in JSON format.")
    parser.add_argument("social_benefits_dir", type=str, help="Directory to save the extracted social benefit details.")
    parser.add_argument("--matters", type=str, nargs="+", help="Personal matters to include.")
    parser.add_argument("--addressees", type=str, nargs="+", help="Addressees to include.")
    parser.add_argument("--legal_bases", type=str, nargs="+", help="Legal bases to include.")
    parser.add_argument("--manual_selection", type=str, nargs="+", help="Manually selected IDLBs to include.")
    
    args = parser.parse_args()
    main(args.all_service_descriptions_dir, args.social_benefits_dir, args.matters, args.addressees, args.legal_bases, args.manual_selection)