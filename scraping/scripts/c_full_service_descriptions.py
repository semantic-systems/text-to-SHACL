"""
 c_extract_eligibiliy_requirements.py

 Master's Thesis
 Seike Appold
 
 - Use the Suchdienst API (https://anbindung.pvog.cloud-bdc.dataport.de/docs/sud/sud-ueberblick/)
 to download the full descriptions of all administrative services in JSON format. Additionally, 
 save the descriptions of "Sozialleistungen" (social services) separately.
"""

import os
import json
import shutil
import datetime
import pandas as pd
from utils import download_file, remove_html_tags, save_path_exists

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

def is_social_service(filepath: str) -> bool:
    """
    Return true if a service description at the given location is a social
    service, else false.
    """
    try:
        with open(filepath, 'r') as file:
            service_description = json.load(file)

        personal_matters = service_description.get('personalMatters')[0]
        personal_matters_child = personal_matters.get('children')[0]

        if personal_matters_child.get('code') == "1140000":
            return True
        
        return False

    except (IndexError, KeyError, FileNotFoundError) as e:
        print(f"Error accessing data: {e}")
        return False


def save_reqs_to_csv(services: list, save_dir: str, filename: str) -> None:
    """
    Take a list of dictionaries and save them to a CSV file.
    """
    save_path = os.path.join(save_dir, filename)

    # If file already exists, do not generate it again
    if save_path_exists(save_dir, save_path, "save eligibility requirements to CSV"):
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
    start_time = datetime.datetime.now()

    # Retrieve the unique ID-LBs and matching ARS
    idlbs_filepath = "scraping/data/processed/valid_unique_idlbs.csv" 
    unique_services = pd.read_csv(idlbs_filepath, dtype=str)
    nof_unique_services = len(unique_services)

    all_descriptions_save_dir = "scraping/data/raw/service_descriptions"
    social_services_save_dir = "scraping/data/raw/social_services"

    # eligibility_reqs = []

    # Download the service description for each ID-LB
    for idx, service in unique_services.iterrows():
        idlb = service["ID-LB"]
        ars = service["ARS"]
        idlb_without_dot = idlb.replace('.', '_')
        description_filename = f"{idlb_without_dot}.json"
        url = f"https://public.demo.pvog.cloud-bdc.dataport.de/suchdienst/api/v5/servicedescriptions/{ars}/detail"

        # For each ID-LB, download the full service description
        description_path = download_file(url=url, params={"q": idlb}, save_dir=all_descriptions_save_dir, filename=description_filename)

        # Save descriptions of social services ("Sozialleistungen") separately  
        if is_social_service(description_path) and not save_path_exists(social_services_save_dir, description_filename, activity="save social service file separately"):
            # Save file to social_services_dir
            shutil.copy(description_path, social_services_save_dir)


        # Extract the eligibility requirements from the full description
        # eligibility_reqs_dict = extract_properties(full_descrpition_path)
        # eligibility_reqs.append(eligibility_reqs_dict)

        progress = (idx + 1) / nof_unique_services * 100
        print(f"Progress: Service {idx+1}/{nof_unique_services}. {progress:.2f}% completed.")

        # For testing: break after 10 services
        # if idx == 10:
        #    break
    
    # Save the eligibility requirements to a CSV file
    # save_dir = "scraping/data/processed"
    # filename = os.path.join("eligibility_requirements.csv")
    # save_reqs_to_csv(eligibility_reqs, save_dir, filename)

    end_time = datetime.datetime.now()
    duration = end_time - start_time
    print(f"Starttime: {start_time}. Endtime: {end_time}. Duration: {duration}.")