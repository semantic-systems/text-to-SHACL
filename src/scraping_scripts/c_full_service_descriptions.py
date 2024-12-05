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
from utils import download_file, save_path_exists

def is_social_service(filepath: str) -> bool:
    """Check if the service described in the file is a social service.

    :param filepath: Path to the file containing the service description.
    :return: True if the service is a social service, False otherwise.
    """
    try:
        with open(filepath, 'r') as file:
            service_description = json.load(file)
        
        matters = service_description["personalMatters"]
        for matter in matters:
            if any(submatter["code"] == "1140000" for submatter in matter["children"]):
                return True

    except (IndexError, KeyError, FileNotFoundError) as e:
        print(f"Error accessing data: {e}")
    
    return False

def save_reqs_to_csv(services: list, save_dir: str, filename: str) -> None:
    """Save a list of administrative service descriptions to a CSV file.

    :param services: A list of dictionaries where each item describes an
    administrative service.
    :param save_dir: Directory to save the CSV file to.
    :param filename: Name of the CSV file.
    :return: None
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
    idlbs_filepath = "scraping/data/processed/unique_idlbs.csv" 
    unique_services = pd.read_csv(idlbs_filepath, dtype=str)
    nof_unique_services = len(unique_services)

    all_services_save_dir = "scraping/data/raw/service_descriptions"
    social_services_save_dir = "scraping/data/raw/social_services"

    req_profile_data = []

    # Download the service description for each ID-LB
    for idx, service in unique_services.iterrows():
        idlb = service["ID-LB"]
        ars = service["ARS"]
        
        idlb_without_dot = idlb.replace('.', '_')
        service_filename = f"{idlb_without_dot}.json"
        
        url = f"https://public.demo.pvog.cloud-bdc.dataport.de/suchdienst/api/v5/servicedescriptions/{ars}/detail"

        # For each ID-LB, download the full service description
        description_path = download_file(url=url, params={"q": idlb}, save_dir=all_services_save_dir, filename=service_filename)

        # Save descriptions of social services ("Sozialleistungen") separately  
        if description_path and is_social_service(description_path) and not save_path_exists(social_services_save_dir, service_filename, activity="save social service file separately"):
            shutil.copy(description_path, social_services_save_dir)

        progress = (idx + 1) / nof_unique_services * 100
        print(f"Progress: Service {idx+1}/{nof_unique_services}. {progress:.2f}% completed.")

    end_time = datetime.datetime.now()
    duration = end_time - start_time
    print(f"Starttime: {start_time}. Endtime: {end_time}. Duration: {duration}.")