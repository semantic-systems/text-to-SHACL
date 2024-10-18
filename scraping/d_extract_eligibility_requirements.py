"""
 c_extract_service_description.py

 Master's Thesis
 Seike Appold
 
 - From descriptions of administrative services in JSON format, extract
 only the eligibility requirements and save them in a csv file.
"""

import os
import json
from bs4 import BeautifulSoup 
from a_extract_ars import save_path_exists

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.text.strip()

def extract_properties(filepath: str) -> dict:
    """
    Extract properties, in particular the eligibility requirements, from
    full description of an administrative service in JSON format. Return
    a dictionary with the extracted information.
    """
    properties = {}

    with open(filepath, 'r') as file:
        full_description = json.load(file)

    # Extract the eligibility requirements
    for detail in full_description["details"]:
        if detail["title"] == "Voraussetzungen":
                eligibility_req = remove_html_tags(detail["text"])
                break
    
    # Populate the dictionary with the extracted information
    properties = {
    "name": full_description["name"],
    "idlb": full_description["id"],
    "ars": full_description["ars"],
    "eligibility_req": eligibility_req
    }
    
    return properties

def save_reqs_to_csv(services: list, save_dir: str, filename: str) -> None:
    """
    Take a list of dictionaries and save them to a CSV file.
    """
    save_path = os.path.join(save_dir, filename)

    # If file already exists, do not generate it again
    if save_path_exists(save_path, save_dir, "save eligibility requirements to csv"):
        return save_path

    try:
        with open(save_path, 'w') as file:
            file.write("Name|ID-LB|ARS|Eligibility Requirements\n")
            for service in services:
                file.write(f"{service['name']}|{service['idlb']}|{service['ars']}|{service['eligibility_req']}\n")
        print(f"Eligibility requirements saved to {save_path}.")
    except Exception as e:
        print(f"Failed to save eligibility requirements to {save_path}: {e}")

if __name__ == "__main__":
    # Retrieve the JSON files with service descriptions
    service_descriptions_dir = "scraping/data/service_descriptions"
    service_descriptions = os.listdir(service_descriptions_dir)
    nof_service_description = len(service_descriptions)

    eligibility_reqs = []

    # Extract the eligibility requirements from each JSON file
    for idx, json_file in enumerate(service_descriptions):
        filepath = os.path.join(service_descriptions_dir, json_file)
        eligibility_reqs_dict = extract_properties(filepath)
        eligibility_reqs.append(eligibility_reqs_dict)

        progress = (idx + 1) / nof_service_description * 100
        print(f"Progress: File {idx+1}/{nof_service_description}. {progress:.2f}% completed.")

        # For testing: break after 10 files
        if idx == 10:
            break
    
    # Save the eligibility requirements to a single csv file
    save_dir = "scraping/data/eligibility_requirements"
    filename = os.path.join("eligibility_requirements.csv")
    save_reqs_to_csv(eligibility_reqs, save_dir, filename)