"""
get_mappings.py

Master's Thesis
Seike Appold

- Extract the Amtliche Regionalschlüssel (ARS) that uniquely identify all German municipalities
with 12-digit keys from XRepository (https://www.xrepository.de/) and maps them to their municipalities
- Extract all unique ID-LBs of administrative services and maps them to a corresponding ARS using the
Suchdienst API (https://anbindung.pvog.cloud-bdc.dataport.de/docs/sud/sud-ueberblick/)
- Save mappings as Python dictionaries in a separate file
"""

import os
import re
import sys
import pprint
import os.path
import pandas as pd
from typing import Dict
from utils import get_filename_from_url, download_file

XREPOSITORY_URL = "https://www.xrepository.de/api/xrepository/urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs_2024-10-31/download/Regionalschl_ssel_2024-10-31.xlsx"
SUCHDIENST_URL_SERVICE_CATALOG = "https://public.demo.pvog.cloud-bdc.dataport.de/suchdienst/api/v5/servicedescriptions/csv"


def generate_ars_dict(input_filepath: str) -> Dict[str, str]:
    """Generates a dictionary mapping ARS to Municipality."""
    try:
        df = pd.read_excel(input_filepath, engine="openpyxl")
        data = df.iloc[7:, [1, 2]].dropna()
        data.columns = ["ARS", "Municipality"]
        data["ARS"] = data["ARS"].astype(str)

        # Add ARS for federal services
        ars_bund = pd.DataFrame(
            {"ARS": ["000000000000"], "Municipality": ["Bund"]})
        data = pd.concat([data, ars_bund], ignore_index=True)

        ars_to_municipality = dict(zip(data["ARS"], data["Municipality"]))
        return ars_to_municipality
    except Exception as e:
        print(f"Failed to generate ARS dictionary: {e}")
        return {}


def update_idlb_dicts(filepath: str, ars: str, idlb_to_ars: dict, idlb_to_name: dict) -> Dict[str, str]:
    """Appends valid ID-LBs with corresponding ARS and name to the respective dictionary."""
    df = pd.read_csv(filepath, delimiter="|", usecols=["ID-LB", "Name"])
    
    # Define valid ID-LB pattern
    valid_idlb_pattern = re.compile(r'^[A-Z]\d{6}.*$')
    
    for index, row in df.iterrows():
        idlb = row['ID-LB']
        name = row['Name']
        
        # Update dictionaries with valid ID-LBs
        if valid_idlb_pattern.match(str(idlb)):
            idlb_to_ars[idlb] = ars
            idlb_to_name[idlb] = name
    
    return idlb_to_ars, idlb_to_name


def save_mappings_to_file(save_filepath: str, ars_dict: dict, idlb_to_ars: dict, idlb_to_name: dict) -> None:
    """Saves ARS and ID-LB mappings as Python Dictionaries."""
    try:
        with open(save_filepath, "w") as f:
            f.write("from typing import Dict\n\n")
            f.write("ars_to_municipality: Dict[str,str] = ")
            f.write(pprint.pformat(ars_dict, width=120))
            f.write("\n\n")
            f.write("idlb_to_ars: Dict[str,str] = ")
            f.write(pprint.pformat(idlb_to_ars, width=120))
            f.write("\n\n")
            f.write("idlb_to_name: Dict[str,str] = ")
            f.write(pprint.pformat(idlb_to_name, width=120))
    except Exception as e:
        print(f"Failed to save mappings: {e}")

    print(f"Mappings saved to {save_filepath}")


def main(output_filepath: str, intermediate_dir: str):
    # Ensure the intermediate directory exists
    os.makedirs(intermediate_dir, exist_ok=True)

    # Download the Excel file containing the ARS
    input_filename = get_filename_from_url(XREPOSITORY_URL)
    input_filepath = download_file(
        url=XREPOSITORY_URL, params=None, save_dir=intermediate_dir, filename=input_filename)

    if input_filepath:
        # Extract all ARS and their corresponding municipalities
        ars_to_municipality = generate_ars_dict(input_filepath)

        # Ensure that the service catalogs directory exists
        service_catalogs_dir = os.path.join(
            intermediate_dir, "service_catalogs")
        os.makedirs(service_catalogs_dir, exist_ok=True)
        
        # Extract unique ID-LBs with a corresponding ARS
        idlb_to_ars = {}
        idlb_to_name = {}
        for idx, ars in enumerate(ars_to_municipality.keys()):
            service_catalog_filename = f"ars_{ars}.csv"
            service_catalog_path = download_file(
                url=SUCHDIENST_URL_SERVICE_CATALOG,
                params={"ars": ars},
                save_dir=service_catalogs_dir,
                filename=service_catalog_filename
            )

            # Update the ID-LB dictionary with ID-LBs from the service catalog
            if service_catalog_path:
                idlb_to_ars, idlb_to_name = update_idlb_dicts(
                    service_catalog_path, ars, idlb_to_ars, idlb_to_name)

            # Report progress
            progress = (idx + 1) / len(ars_to_municipality) * 100
            print(f"Progress: File {idx+1}/{len(ars_to_municipality)}. {progress:.2f}% completed.")

        # Save the ARS and IDLB dictionaries to a Python file
        save_mappings_to_file(output_filepath, ars_to_municipality, idlb_to_ars, idlb_to_name)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_mappings.py <output_filepath> <intermediate_dir>")
    else:
        output_filepath = sys.argv[1]
        intermediate_dir = sys.argv[2]
        main(output_filepath, intermediate_dir)
