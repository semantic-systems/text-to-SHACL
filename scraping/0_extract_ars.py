"""
 0_extract_ars.py

 Master's Thesis
 Seike Appold
 
 - Extract the Amtliche Regionalschlüssel (ARS) that uniquely identify
 all German municipalities with 12-digit keys from XRepository 
 (https://www.xrepository.de/)
"""

import os
import requests
import pandas as pd
from pathlib import Path

def download_file(url: str, save_dir: str, filename: str) -> str:
    """
    Download a file from the URL and save it to the specified directory.

    :param url: URL of the file to download.
    :param save_dir: Directory where the downloaded file will be saved.
    :param file_name: Name of the file to save.
    :return: If the download was sucessfull path to file, else None.
    """
    # Create the save directory if it does not yet exist
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    save_path = os.path.join(save_dir, filename)

    # If file already exists locally, skip the download
    if os.path.isfile(save_path):
        print(f"File already exists at {save_path}. Skipping download.")
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

def extract_ars(excel_path: str, save_dir: str, filename: str) -> None:
    """
    Extract the ARS for all German municipalities from the excel at the 
    specified location and save as csv.

    :param excel_filepath: path to locally stored excel file.
    :param save_dir: directory where the csv will be saved.
    :param filename: name of the file to save.
    :return: None
    """
    # Create the save directory if it does not yet exist
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    # If file already exists, skip the extraction
    if os.path.isfile(save_path):
        print(f"File already exists at {save_path}. Skipping extraction.")
        return None

    # Extract ARS from excel file and save to CSV
    try:
        df = pd.read_excel(excel_path)
        column_data = df.iloc[7:, 1].dropna()  
        column_data.to_csv(save_path, index=False, header=False)
        print(f"CSV with ARS saved to: {save_path}")
    except Exception as e:
        print(f"Failed to extract ARS: {e}")

def main():
    EXCEL_URL = "https://www.xrepository.de/api/xrepository/urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs_2024-10-31/download/Regionalschl_ssel_2024-10-31.xlsx"  
    
    save_dir = "scraping/data/ars"
    
    filepath = download_file(EXCEL_URL, save_dir, filename="ars_raw.xlsx")
    
    # If the download was successful, extract the ARS
    if filepath:
        extract_ars(filepath, save_dir, filename="ars_only.csv")

if __name__ == "__main__":
    main()