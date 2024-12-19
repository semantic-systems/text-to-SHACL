"""
get_all_service_descriptions.py

Download and save the full descriptions of all administrative services in JSON format using
the Suchdienst API (https://anbindung.pvog.cloud-bdc.dataport.de/docs/sud/sud-ueberblick/).
"""

import os
import sys
import datetime
from mappings import idlb_to_ars
from data_preparation.utils import download_file

SUCHDIENST_URL_SERVICE_DESCRIPTION = "https://public.demo.pvog.cloud-bdc.dataport.de/suchdienst/api/v5/servicedescriptions/{ars}/detail"

def download_and_save_service_descriptions(intermediate_files: str) -> None:
    """Download all service descriptions and save them to the specific directory."""
    start_time = datetime.datetime.now()

    # Ensure the save directory exists
    save_dir = os.path.join(intermediate_files, "all_service_descriptions")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Download the service description for each ID-LB
    for idx, (idlb, ars) in enumerate(idlb_to_ars.items()):
        idlb_without_dot = idlb.replace('.', '_')
        service_filename = f"{idlb_without_dot}.json"
        url = SUCHDIENST_URL_SERVICE_DESCRIPTION.replace("{ars}", ars)
        
        download_file(url=url, params={"q": idlb}, save_dir=save_dir, filename=service_filename)

        # Report progress
        progress = (idx + 1) / len(idlb_to_ars) * 100
        print(f"Progress: Service {idx+1}/{len(idlb_to_ars)}. {progress:.2f}% completed.")

    end_time = datetime.datetime.now()
    duration = end_time - start_time
    print(f"Starttime: {start_time}. Endtime: {end_time}. Duration: {duration}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_all_service_descriptions.py <intermediate_dir>")
    else:
        intermediate_dir = sys.argv[1]
        download_and_save_service_descriptions(intermediate_dir)