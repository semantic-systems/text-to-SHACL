"""
 c_extract_service_description.py

 Master's Thesis
 Seike Appold
 
 - Use the Suchdienst API (https://anbindung.pvog.cloud-bdc.dataport.de/docs/sud/sud-ueberblick/)
 to download and save the descriptions of administrative services by ID-LB and ARS in JSON format.
"""

import os
import requests
import pandas as pd
from a_extract_ars import save_path_exists

def download_service_description(idlb: str, ars: str, save_dir: str, filename: str) -> str:
    """
    Call the Suchdienst API to fetch a JSON file for the given ID-LB and
    save it to the specified directory. Return the path to the saved file
    if the download was completed or the file already existed, else None.
    """
    save_path = os.path.join(save_dir, filename)

    # If file already exists, do not download it again
    if save_path_exists(save_path, save_dir, "download"):
        return save_path
    
    url = f"https://public.demo.pvog.cloud-bdc.dataport.de/suchdienst/api/v5/servicedescriptions/{ars}/detail"
    
    try:
        response = requests.get(url, params={"q": idlb})
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Description of service with ID {idlb} saved to {save_path}.")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Retrieve the unique ID-LB and matching ARS
    idlbs_filepath = "scraping/data/idlbs/unique_idlbs_all.csv" 
    unique_services = pd.read_csv(idlbs_filepath, dtype=str)
    nof_unique_services = len(unique_services)

    save_directory = "scraping/data/service_descriptions" 

    # Download the service description for each ID-LB
    for idx, service in unique_services.iterrows():
        idlb = service["ID-LB"]
        ars = service["ARS"]
        filename = f"{idlb}.json"
        download_service_description(idlb, ars, save_directory, filename)

        progress = (idx + 1) / nof_unique_services * 100
        print(f"Progress: Service {idx+1}/{nof_unique_services}. {progress:.2f}% completed.")