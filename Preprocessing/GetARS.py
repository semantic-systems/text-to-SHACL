"""
GetARS.py

- Create a mapping of Amtliche Regionalschlüssel (ARS), which uniquely
  identify political entities in Germany, to entity names based on
  codelists from XRepository (https://www.xrepository.de/)
- Example: {"010010000000": "Flensburg, Stadt"}
"""

import os
import json
import argparse
import pandas as pd
from Utils.FileHandling import download_and_save_file
from Utils.Logger import setup_logger

# Codelists with ARS and names
CODELIST_MUNICIPALITIES = os.getenv("XREPOSITORY_CODELIST_MUN")
CODELIST_STATES = os.getenv("XREPOSITORY_CODELIST_STATES")

logger = setup_logger(__name__, log_file="logs/GetARS.log")

def load_codelist(file_url: str, save_dir: str, filename: str) -> pd.DataFrame:
    """
    Downloads and reads an Excel codelist, extracting relevant columns.

    :param file_url: URL of the Excel file.
    :param save_dir: Directory to save the downloaded file.
    :param filename: Name of the saved file.
    :return: Processed DataFrame with ARS codes and names.
    """
    file_path = download_and_save_file(url=file_url, params={}, save_dir=save_dir, filename=filename)
    df = pd.read_excel(file_path, engine="openpyxl")

    # Extract relevant columns and drop NaNs
    df_filtered = df.iloc[7:, [1, 2]].dropna()
    df_filtered.columns = ["ARS", "Name"]

    return df_filtered


def pad_state_codes(state_df: pd.DataFrame) -> pd.DataFrame:
    """
    Brings 2-digit-federal-state-codes into valid 12-digit-ARS format.

    :param state_df: DataFrame containing state ARS codes and names.
    :return: Updated DataFrame with adjusted ARS codes.
    """
    state_df["ARS"] = state_df["ARS"].astype(str).apply(lambda x: x + "0" * 10)
    return state_df

def main(
    save_dir_codelists: str,
    mapping_output_path: str,
    municipality_codelist_url: str=CODELIST_MUNICIPALITIES,
    state_codelist_url: str=CODELIST_STATES,
):
    """
    Downloads ARS codelists and saves a combined ARS-to-name mapping.

    :param save_dir_codelists: Directory to save the downloaded codelists.
    :param mapping_output_path: Path to save the ARS-to-name mapping.
    :param municipality_codelist_url: URL of the municipality ARS codelist.
    :param state_codelist_url: URL of the federal states ARS codelist.
    """
    # Load municipality and state codelists
    municipality_mapping = load_codelist(municipality_codelist_url, save_dir_codelists, "ars_municipalities.xlsx")
    state_mapping = pad_state_codes(load_codelist(state_codelist_url, save_dir_codelists, "ars_federal_states.xlsx"))

    # Add manual mapping for the federal government
    federal_mapping = pd.DataFrame({"ARS": ["000000000000"], "Name": ["Bund"]})

    # Combine all mappings
    combined_mapping = pd.concat([municipality_mapping, state_mapping, federal_mapping], ignore_index=True)
    ars_to_name = dict(zip(combined_mapping["ARS"], combined_mapping["Name"]))

    with open(mapping_output_path, "a", encoding="utf-8") as file:
        file.write("\n\nars_to_name = ")
        file.write(json.dumps(ars_to_name, indent=4, ensure_ascii=False))

    logger.info(f"ARS mapping successfully saved to {mapping_output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve ARS-to-name mapping.")
    parser.add_argument("save_dir_codelists", type=str, help="Directory to save the downloaded codelists.")
    parser.add_argument("mapping_output_path", type=str, help="Path to save the ARS-to-name mapping.")
    parser.add_argument("--municipality_codelist_url", type=str, default=CODELIST_MUNICIPALITIES, help="URL of the municipality ARS codelist.")
    parser.add_argument("--state_codelist_url", type=str, default=CODELIST_STATES, help="URL of the federal states ARS codelist.")
    
    args = parser.parse_args()
    main(args.save_dir_codelists, args.mapping_output_path, args.municipality_codelist_url, args.state_codelist_url)