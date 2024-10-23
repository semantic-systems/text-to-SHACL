"""
 a_download_ars.py

 Master's Thesis
 Seike Appold
 
 - Extract the Amtliche Regionalschlüssel (ARS) that uniquely identify all
 German municipalities with 12-digit keys from XRepository (https://www.xrepository.de/)
"""

import os
import pandas as pd
from utils import download_file, save_path_exists

EXCEL_URL = "https://www.xrepository.de/api/xrepository/urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs_2024-10-31/download/Regionalschl_ssel_2024-10-31.xlsx"  

def extract_ars(input_filepath: str, save_dir: str, filename: str) -> None:
    """service_description
    Extract ARS for all German municipalities from the input excel at the
    specified location and save as csv.
    """
    save_path = os.path.join(save_dir, filename)

    # If file already exists, do not extract ARS again
    if save_path_exists(save_dir, save_path, "extraction of ARS"):
        return save_path

    # Extract ARS from excel file and save to CSV
    try:
        df = pd.read_excel(input_filepath)
        column_data = df.iloc[7:, [1, 2]].dropna()
        column_data.columns = ["ARS", "Municipality"]
        column_data["ARS"] = column_data["ARS"].astype(str)  
        column_data.to_csv(save_path, index=False)
        print(f"ARS extracted ad saved to {save_path}")    
    except Exception as e:
        print(f"Failed to extract ARS: {e}")

if __name__ == "__main__":
    ars_raw_save_dir = "scraping/data/raw/ars"
    ars_processed_save_dir = "scraping/data/processed"

    # Download excel file with all ARS
    input_filepath = download_file(url=EXCEL_URL, params=None, save_dir=ars_raw_save_dir, filename="ars_raw.xlsx")
    
    # If the download was successful, extract the ARS
    if input_filepath:
        extract_ars(input_filepath, ars_processed_save_dir, filename="all_ars.csv")