"""
a_download_ars.py

Master's Thesis
Seike Appold

- Extract the Amtliche Regionalschlüssel (ARS) that uniquely identify all
German municipalities with 12-digit keys from XRepository (https://www.xrepository.de/)
"""

import os
import sys
import pandas as pd
import tempfile
from utils import download_file, save_path_exists

EXCEL_URL = "https://www.xrepository.de/api/xrepository/urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs_2024-10-31/download/Regionalschl_ssel_2024-10-31.xlsx"

def extract_ars(input_filepath: str, save_dir: str, filename: str) -> None:
    """From input file, generate a CSV file with all ARS and municipality names.

    Extract the ARS and corresponding Municipality from input file and add
    ARS for federal services. Save extracted data to a CSV file.

    :param input_filepath: Path to the input file with ARS and municipality names.
    :param save_dir: Directory to save the extracted ARS.
    :param filename: Name of the CSV file to save the extracted ARS.
    :return: None
    """
    save_path = os.path.join(save_dir, filename)

    # If file already exists, do not extract ARS again
    if save_path_exists(save_dir, save_path, "extraction of ARS"):
        return save_path

    # Extract ARS from excel file and save to CSV
    try:
        df = pd.read_excel(input_filepath, engine="openpyxl")
        data = df.iloc[7:, [1, 2]].dropna()
        data.columns = ["ARS", "Municipality"]
        data["ARS"] = data["ARS"].astype(str)

        # Add ARS for federal services
        ars_bund = pd.DataFrame({"ARS": ["000000000000"], "Municipality": ["Bund"]})
        data = pd.concat([data, ars_bund], ignore_index=True)

        data.to_csv(save_path, index=False)

        print(f"ARS extracted and saved to {save_path}")
    except Exception as e:
        print(f"Failed to extract ARS: {e}")

def main(output_directory: str, output_filename: str):
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Download excel file with all ARS to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
        # NOTE: When asked to overwrite the temporary file, the user should always answer "y"
        input_filepath = download_file(
            url=EXCEL_URL,
            params=None,
            save_dir=os.path.dirname(temp_file.name),
            filename=os.path.basename(temp_file.name)
        )

        # Save a cleaned version of the file to specified output directory
        if input_filepath:
            extract_ars(input_filepath, output_directory, output_filename)
        
    # Close and thereby delete temporary file
    temp_file.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python a_download_ars.py <output_directory> <output_filename>")
    else:
        output_directory = sys.argv[1]
        output_filename = sys.argv[2]
        main(output_directory, output_filename)