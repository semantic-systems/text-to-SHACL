"""
d_eligibiliy_requirements.py

 Master's Thesis
 Seike Appold
 
 - From full service descriptions in JSON format, extract the relevant objects,
 including identificatory information, eligibility requirements in text and
 legal basis. Save the extracted information to a CSV file.
"""
import os
import csv
import json
from utils import remove_html_tags, save_path_exists

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
    
    # Populate dictionary with relevant information
    properties = {
    "Name": full_description["name"],
    "ID-LB": full_description["id"],
    "ARS": full_description["ars"],
    "Eligibility Requirements": eligibility_req
    }
    
    return properties

def save_reqs_to_csv(services: list, save_dir: str, filename: str) -> None:
    """
    Take a list of dictionaries and save them to a CSV file.
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
    eligibility_reqs = []
    descriptions_dir = "scraping/data/raw/service_descriptions"

    for filename in os.listdir(descriptions_dir):
        description_path = os.path.join(descriptions_dir, filename)
        eligibility_reqs_dict = extract_properties(description_path)
        eligibility_reqs.append(eligibility_reqs_dict)
    
    save_dir = "scraping/data/processed"
    filename = os.path.join("all_eligibility_reqs.csv")
    save_reqs_to_csv(eligibility_reqs, save_dir, filename)