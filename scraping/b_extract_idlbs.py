"""
 1_identify_administrative_services.py

 Master's Thesis
 Seike Appold
 
 - Use the Suchdienst API (https://anbindung.pvog.cloud-bdc.dataport.de/docs/sud/sud-ueberblick/)
 and the extracted ARS to generate a set of the ID-LB of all administrative services.
"""

import os
# import re
import requests
import pandas as pd
from pathlib import Path
from a_extract_ars import save_path_exists

SUCHDIENST_URL = "https://public.demo.pvog.cloud-bdc.dataport.de/suchdienst/api/v5/servicedescriptions/csv"

def download_csv(url: str, ars: str, save_dir: str, filename) -> str:
    """
    Call the Suchdienst API to fetch a CSV file for the given ARS and
    save it to the specified directory. Return the path to the saved file
    if the download was completed or the file already existed, else None.
    """
    save_path = os.path.join(save_dir, filename)

    # If file already exists, do not download it again
    if save_path_exists(save_path, save_dir, "download"):
        return save_path
    
    try:
        response = requests.get(url, params={"ars": ars})
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"CSV for ARS {ars} saved to {save_path}.")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def update_idlb_dict(filepath: str, ars: str, idlb_dict: dict) -> dict:
    """
    Append the ID-LBs from the input file to the dictionary, where ID-LBs
    are the keys (hence, unique) and the ARS are the values. Return the
    updated dictionary.
    """
    # valid_idlb_pattern = "^[B|L]\d{6}\.LB\.[\d{9}|\d{6}]$"

    try:
        df = pd.read_csv(filepath, delimiter="|")
        # valid_idlbs = [idlb for idlb in df["ID-LB"] if re.match(valid_idlb_pattern, idlb)]
        valid_idlbs = df["ID-LB"]
        for idlb in valid_idlbs:
            idlb_dict[idlb] = ars
    except Exception as e:
        print(f"Failed to extract ID-LB from {filepath}: {e}")
    
    return idlb_dict

def save_idlbs_to_csv(idlb_dict: dict, save_dir: str, filename: str) -> None:
    """
    Save a dictionary of ID-LBs and corresponding ARS to a CSV file.
    """
    save_path = os.path.join(save_dir, filename)

    # If file already exists, do not generate it again
    if save_path_exists(save_path, save_dir, "generation of ID-LB file"):
        return save_path

    df = pd.DataFrame(idlb_dict.items(), columns=["ID-LB", "ARS"])
    df.to_csv(save_path, index=False)
    print(f"Dictionary of ID-LBs saved to {save_path}.")
    
if __name__ == "__main__":
    # Retrieve the ARS from locally stored file
    ars_path = "scraping/data/ars/ars_clean.csv"
    ars_df = pd.read_csv(ars_path, dtype ='str')
    nof_ars = len(ars_df["ARS"])

    idlb_dict= {}
    services_save_dir = "scraping/data/service_catalogs"

    # For each ARS, download the catalog of services
    for idx, ars in enumerate(ars_df["ARS"]):
        service_catalog_filename = f"ars_{ars}.csv"
        service_catalog_path = download_csv(SUCHDIENST_URL, ars, services_save_dir, service_catalog_filename)

        if service_catalog_path:
            idlb_dict = update_idlb_dict(service_catalog_path, ars, idlb_dict)

        # Provide feedback on progress
        progress = (idx + 1) / len(ars_df["ARS"]) * 100
        print(f"Progress: File {idx+1}/{nof_ars}. {progress:.2f}% completed.")

        # FOR TESTING: Process only the first 5 ARS
        if idx == 5:
            break
    
    # Save the set of unique ID-LBs to a CSV file
    idlbs_filename = "unique_idlbs_all.csv"
    idlbs_save_dir = "scraping/data/idlbs"
    save_idlbs_to_csv(idlb_dict, idlbs_save_dir, idlbs_filename)