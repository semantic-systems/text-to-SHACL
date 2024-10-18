"""
 1_identify_administrative_services.py

 Master's Thesis
 Seike Appold
 
 - Use the Suchdienst API (https://anbindung.pvog.cloud-bdc.dataport.de/docs/sud/sud-ueberblick/)
 and the extracted ARS to generate a set of the ID-LB of all administrative services.
"""

import os
import re
import csv
import requests
import pandas as pd
from pathlib import Path
from a_extract_ars import save_path_exists

SUCHDIENST_URL = "https://public.demo.pvog.cloud-bdc.dataport.de/suchdienst/api/v5/servicedescriptions/csv"

def download_csv(url: str, ars: str, save_dir: str, filename) -> str:
    """
    Call the Suchdienst API to fetch a CSV file for the given ARS and
    save it to the specified directory.

    :param url: The base URL to download the CSV from.
    :param ars: The ARS for which the CSV is fetched.
    :param save_dir: Directory where the downloaded file will be saved.
    :param filename: Name of the file to save.
    :return: The path to the saved CSV file.
    """
    # Create the save directory if it does not yet exist
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    save_path = os.path.join(save_dir, filename)

    # If file already exists locally, skip the download
    if os.path.isfile(save_path):
        print(f"File already exists at {save_path}. Skipping download.")
        return save_path
    
    try:
        response = requests.get(SUCHDIENST_URL, params={"ars": ars})
        response.raise_for_status()
        
        with open(save_path, 'wb') as file:
            file.write(response.content)
        
        print(f"CSV for ARS {ars} saved to {save_path}.")
        return save_path

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def extract_idlb(filepath: str) -> set:
    """
    Extract valid ID-LB entries from a CSV file.

    :param filepath: Path to the CSV file.
    :return: A set of valid ID-LB entries.
    """
    idlbs = set()
    # valid_idlb_pattern = "^[B|L]\d{6}\.LB\.[\d{9}|\d{6}]$"

    try:
        df = pd.read_csv(filepath, delimiter="|")
        # valid_idlbs = [idlb for idlb in df["ID-LB"] if re.match(valid_idlb_pattern, idlb)]
        valid_idlbs = df["ID-LB"]
        idlbs.update(valid_idlbs)
        return idlbs
    
    except Exception as e:
        print(f"Failed to extract ID-LB from {filepath}: {e}")
        return set()

def save_idlbs_to_csv(idlbs: set, save_dir: str, filename: str) -> None:
    """
    Save a set of ID-LBs to a CSV file.

    :param data: The set of ID-LBs to save.
    :param save_dir: Directory where the file will be saved.
    :param filename: Name of the file to save.
    """
    # Create the save directory if it does not yet exist
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    # If file already exists locally, skip the download
    if os.path.isfile(save_path):
        print(f"File already exists at {save_path}. Skipping download.")
        return save_path

    df = pd.DataFrame(list(idlbs), columns=["ID-LB"])
    df.to_csv(save_path, index=False)

    print(f"Set of ID-LBs saved to {save_path}.")
    
if __name__ == "__main__":
    ars_path = "scraping/data/ars/ars_clean.csv"
    ars_df = pd.read_csv(ars_path, dtype ='str')
    nof_ars = len(ars_df["ARS"])

    unique_idlbs = set()
    services_dir = "scraping/data/services"

    for idx, ars in enumerate(ars_df["ARS"]):
        services_filename = f"ars_{ars}.csv"
        services_path = download_csv(SUCHDIENST_URL, ars, services_dir, services_filename)

        if services_path:
            idlbs = extract_idlb(services_path)
            unique_idlbs.update(idlbs)

        progress = (idx + 1) / len(ars_df["ARS"]) * 100
        print(f"Progress: {progress:.2f}% completed")

        if idx == 5:
            break
    
    idlbs_filename = "unique_idlbs.csv"
    save_set_to_csv(unique_idlbs, services_dir, idlbs_filename)