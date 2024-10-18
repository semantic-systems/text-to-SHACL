"""
 a_extract_ars.py

 Master's Thesis
 Seike Appold
 
 - Extract the Amtliche Regionalschlüssel (ARS) that uniquely identify all
 German municipalities with 12-digit keys from XRepository (https://www.xrepository.de/)
"""

import os
import requests
import pandas as pd
from pathlib import Path

EXCEL_URL = "https://www.xrepository.de/api/xrepository/urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs_2024-10-31/download/Regionalschl_ssel_2024-10-31.xlsx"  

def save_path_exists(save_path: str, save_dir: str, activity: str) -> str:
    """
    Check if a save path already exists and create save directory if it is 
    not already present. Return True if file already exists, else False.
    """
    # Create the save directory if it does not yet exist
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    # Check if the file already exists
    if os.path.isfile(save_path):
        print(f"File already exists at {save_path}. Skipping {activity}.")
        return True
    
    return False

def download_file(url: str, save_dir: str, filename: str) -> str:
    """
    Download file from URL and save to the specified directory. Return
    the path to the saved file if the download was completed or the file
    already existed, else None.
    """
    save_path = os.path.join(save_dir, filename)

    # If file already exists, do not download it again
    if save_path_exists(save_path, save_dir, "download"):
        return save_path
    
    # Download file from the specified URL
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded and saved to {save_path}.")
        return save_path
    except requests.RequestException as e:
        print(f"Failed to download file: {e}")
        return None

def extract_ars(input_filepath: str, save_dir: str, filename: str) -> None:
    """
    Extract ARS for all German municipalities from the input excel at the
    specified location and save as csv.
    """
    save_path = os.path.join(save_dir, filename)

    # If file already exists, do not extract ARS again
    if save_path_exists(save_path, save_dir, "extraction"):
        return save_path

    # Extract ARS from excel file and save to CSV
    try:
        df = pd.read_excel(input_filepath)
        column_data = df.iloc[7:, [1, 2]].dropna()
        column_data.columns = ["ARS", "Municipality"]
        column_data["ARS"] = column_data["ARS"].astype(str)  
        column_data.to_csv(save_path, index=False)
        print(f"CSV with ARS saved to: {save_path}")    
    except Exception as e:
        print(f"Failed to extract ARS: {e}")

if __name__ == "__main__":
    output_save_dir = "scraping/data/ars"
    
    # Download the excel file containing the ARS
    input_filepath = download_file(EXCEL_URL, output_save_dir, filename="ars_raw.xlsx")
    
    # If the download was successful, extract the ARS
    if input_filepath:
        extract_ars(input_filepath, output_save_dir, filename="ars_clean.csv")