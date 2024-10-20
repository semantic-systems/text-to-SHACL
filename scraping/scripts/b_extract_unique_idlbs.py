"""
 b_extract_unique_idlbs.py

 Master's Thesis
 Seike Appold
 
 - Use the Suchdienst API (https://anbindung.pvog.cloud-bdc.dataport.de/docs/sud/sud-ueberblick/)
 to extract all unique ID-LBs of administrative services and save them in a CSV file along with
 one of the ARS that the service is associated with.
"""

import os
import datetime
import pandas as pd
from utils import download_file, save_path_exists

SUCHDIENST_URL = "https://public.demo.pvog.cloud-bdc.dataport.de/suchdienst/api/v5/servicedescriptions/csv"

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
    if save_path_exists(save_dir, save_path, "generation of ID-LB file"):
        return save_path

    df = pd.DataFrame(idlb_dict.items(), columns=["ID-LB", "ARS"])
    df.to_csv(save_path, index=False)
    print(f"ID-LBs with ARS saved to {save_path}.")
    
if __name__ == "__main__":
    start_time = datetime.datetime.now()

    # Retrieve the ARS from locally stored file
    ars_path = "scraping/data/processed/all_ars.csv"
    ars_df = pd.read_csv(ars_path, dtype ='str')
    nof_ars = len(ars_df["ARS"])

    idlb_dict= {}
    services_save_dir = "scraping/data/raw/service_catalogs"

    # For each ARS, download the catalog of services
    for idx, ars in enumerate(ars_df["ARS"]):
        services_filename = f"ars_{ars}.csv"

        services_filepath = download_file(url=SUCHDIENST_URL, params={"ars": ars}, save_dir=services_save_dir, filename=services_filename)

        # If the download was successful, add ID-LBs to dictionary
        if services_filepath:
            idlb_dict = update_idlb_dict(services_filepath, ars, idlb_dict)

        # Provide feedback on progress
        progress = (idx + 1) / len(ars_df["ARS"]) * 100
        print(f"Progress: File {idx+1}/{nof_ars}. {progress:.2f}% completed.")

        # For testing: break after 10 files
        #if idx == 50:
            #break
    
    # Save unique ID-LBs to a CSV file
    idlbs_filename = "unique_idlbs.csv"
    idlbs_save_dir = "scraping/data/processed"
    save_idlbs_to_csv(idlb_dict=idlb_dict, save_dir=idlbs_save_dir, filename=idlbs_filename)

    end_time = datetime.datetime.now()
    duration = end_time - start_time
    print(f"Starttime: {start_time}. Endtime: {end_time}. Duration: {duration}.")