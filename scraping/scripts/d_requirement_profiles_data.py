"""
d_eligibiliy_requirements.py

 Master's Thesis
 Seike Appold
 
 - From full service descriptions in JSON format, extract the relevant objects,
 including identificatory information, eligibility requirements in text and
 legal basis. Save the extracted information to a CSV file.
"""
import os
import re
import csv
import json
from utils import remove_html_tags, save_path_exists, report_delimiter_conflict

def report_delimiter_conflict(legal_basis_title: str, legal_basis_link: str) -> None:
    if "<>" in legal_basis_title or "|" in legal_basis_title:
        raise ValueError(f"Illegal character found in legal basis title: '{legal_basis_title}'")
    if "<>" in legal_basis_link or "|" in legal_basis_link:
        raise ValueError(f"Illegal character found in legal basis link: '{legal_basis_link}'")
    
def extract_req_profile_data(filepath: str) -> dict:
    """Extract data for requirement profiles from full description of administrative service.

    The extracted data includes the name of the service, the ID-LB, a matching ARS,
    the eligibility requirements, the legal basis and a link to the full service description
    on the Portverbund Online Gateway website.

    :param filepath: Path to the full description of administrative service.
    :return: Dictionary with extracted information for requirement profiles.
    """
    req_profile_data = {}

    with open(filepath, 'r') as file:
        full_description = json.load(file)
    
    legal_bases = []

    for detail in full_description["details"]:
        # Extract eligibility requirements
        if detail["title"] == "Voraussetzungen":
            eligibility_req = remove_html_tags(detail["text"])

        # Extract legal bases, if stored in "links"
        elif detail["title"] == "Rechtsgrundlage(n)" and detail["links"]:
            for law in detail["links"]:
                legal_basis_title = law["title"]
                legal_basis_link = law["uri"]

                report_delimiter_conflict(legal_basis_title, legal_basis_link)
        
                legal_bases.append(f"{legal_basis_title}<>{legal_basis_link}")
        
        # Extract legal bases, if stored in "text"
        elif detail["title"] == "Rechtsgrundlage(n)" and detail["text"] and not detail["links"]:
            # Find title and matching link for legal bases with regex pattern
            link_title_pattern = r'<a href="(.*?)">(.*?)</a>'
            link_title_matches = re.findall(link_title_pattern, detail["text"])
            if not link_title_matches:
                legal_bases_text = remove_html_tags(detail["text"])
                legal_bases.append(legal_bases_text)
                continue

            for legal_basis_link, legal_basis_title in link_title_matches:
                report_delimiter_conflict(legal_basis_title, legal_basis_link)
                legal_bases.append(f"{legal_basis_title}<>{legal_basis_link}")
    
    legal_bases_str = "|".join(legal_bases)

    ars = full_description["ars"][0]
    idlb = full_description["id"].replace('_', '.')
    # see_also = f"https://pvog.fitko.de/#/de/result/{ars}/{idlb}"
    
    req_profile_data = {
    "Name": full_description["name"],
    "ID-LB": idlb,
    "ARS": ars,
    "Eligibility Requirements": eligibility_req,
    "Legal Basis": legal_bases_str,
    # "See also": see_also
    }
    
    return req_profile_data

def save_reqs_to_csv(services: list, save_dir: str, filename: str) -> None:
    """Save data for requirement profiles to a CSV file.

    :param services: List of dictionaries where each item represents the information
    relevant to generate the requirement profile for a specifi social service.
    :param save_dir: Directory to save the CSV file.
    :param filename: Name of the CSV file.
    :return: None
    """
    save_path = os.path.join(save_dir, filename)

    # If file already exists, do not generate it again
    if save_path_exists(save_dir, save_path, "save eligibility requirements to CSV"):
        return save_path

    try:
        with open(save_path, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=services[0].keys(), quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for service in services:
                writer.writerow(service)
        print(f"Eligibility requirements saved to {save_path}.")
    except Exception as e:
        print(f"Failed to save eligibility requirements to {save_path}: {e}")

if __name__ == "__main__":
    descriptions_dir = "scraping/data/raw/social_services"
    requirements = []

    # For each service description, extract data for requirement profiles
    for filename in os.listdir(descriptions_dir):
        description_path = os.path.join(descriptions_dir, filename)
        requirements_dict = extract_req_profile_data(description_path)
        
        # If no requirements are provided, skip the service
        if requirements_dict["Eligibility Requirements"] == "nicht angegeben":
            continue

        requirements.append(requirements_dict)
    
    save_dir = "scraping/data/processed"
    filename = os.path.join("requirement_profiles_social_services.csv")
    save_reqs_to_csv(requirements, save_dir, filename)