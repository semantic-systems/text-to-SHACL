""" 
GetServiceDescriptions.py

Download all administrative service descriptions accessible via the
Suchdienst API (https://anbindung.pvog.cloud-bdc.dataport.de/docs/api/suchdienst-api)
by the Portalverbund Online-Gateway (PVOG). Steps include:
    1. Retrieving all ARS and downloading corresponding service catalogs.
    2. Extracting all unique IDLBs from service catalogs and mapping them to ARS.
    3. Using the mapping to download service descriptions.
"""

import os
import re
import sys
import tempfile
import requests
import argparse
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
from Utils.FileHandling import download_file
from Utils.Logger import setup_logger

logger = setup_logger(__name__, log_file="logs/GetServiceDescriptions.log")

def get_ars_from_excel(url: str) -> List[str]:
    """
    Downloads Excel file and extracts all ARS.
    
    :param url: URL to the ARS Excel file.
    :return: List of ARS.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
            else:
                logger.error(f"Failed to download ARS Excel file: {response.status_code}")
                sys.exit(1)
                
            # Extract ARS data
            df = pd.read_excel(temp_file.name, engine="openpyxl")
            data = df.iloc[7:, [1, 2]].dropna()
            data.columns = ["ARS", "Municipality"]
            data["ARS"] = data["ARS"].astype(str)

            # Add ARS for federal services
            ars_bund = pd.DataFrame({"ARS": ["000000000000"], "Municipality": ["Bund"]})
            data = pd.concat([data, ars_bund], ignore_index=True)
            return data["ARS"].tolist()
    except Exception as e:
        logger.error(f"Failed to process ARS Excel file: {e}")
        sys.exit(1)

def download_service_catalog(base_url: str, ars: str, save_dir: str) -> str:
    """
    Downloads service catalog for a given ARS to the specified directory.
    
    :param base_url: Base URL for the API.
    :param ars: ARS for the service catalog.
    :param save_dir: Directory to save the service catalog.
    :return: If service catalog was downloaded, path to file. Otherwise, None.
    """
    service_catalog_filename = f"ars_{ars}.csv"
    service_catalog_path = os.path.join(save_dir, service_catalog_filename)

    if os.path.exists(service_catalog_path):
        logger.info(f"Service catalog for ARS {ars} already exists. Skipping download.")
        return service_catalog_path

    try:
        return download_file(url=base_url, params={"ars": ars}, save_dir=save_dir, filename=service_catalog_filename)
    except Exception as e:
        logger.warning(f"Error downloading service catalog with ARS {ars}: {e}")
        return None

def update_idlb_dicts(service_catalog: str, ars: str, idlb_to_ars: Dict[str,str]) -> Dict[str,str]:
    """
    Update the IDLB to ARS mapping with the service catalog.
    
    :param service_catalog: Path to the service catalog.
    :param ars: ARS for the service catalog.
    :param idlb_to_ars: Current mapping of IDLB to ARS.
    :return: Updated IDLB to ARS mapping.
    """
    try:
        df = pd.read_csv(service_catalog, delimiter="|", usecols=["ID-LB", "Name"])
        valid_idlb_pattern = re.compile(r'^[A-Z]\d{6}.*$')
        
        for _, row in df.iterrows():
            idlb = row['ID-LB']
            if valid_idlb_pattern.match(str(idlb)):
                idlb_to_ars[idlb] = ars
    except Exception as e:
        logger.warning(f"Failed to process service catalog {os.path.basename(service_catalog)}: {e}")
    
    return idlb_to_ars

def download_service_descriptions(base_url: str, idlb_to_ars: Dict[str,str], save_dir: str):
    """
    Download service descriptions for all IDLBs.
    
    :param base_url: Base URL for the API.
    :param idlb_to_ars: Mapping of IDLB to ARS.
    :param save_dir: Directory to save the service descriptions.
    """
    os.makedirs(save_dir, exist_ok=True)
    logger.info(f"Starting download of {len(idlb_to_ars)} service descriptions.")

    def _download_description(idlb: str, ars: str) -> str:
        """Downloads a single service description and returns filepath."""
        idlb_safe = idlb.replace('.', '_')
        filename = f"{idlb_safe}.json"
        url = base_url.replace("{ars}", ars)
        download_file(url=url, params={"q": idlb}, save_dir=save_dir, filename=filename)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_download_description, idlb, ars) for idlb, ars in idlb_to_ars.items()]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading Service Descriptions", unit="description"):
            try:
                future.result()
            except Exception as e:
                logger.warning(f"Failed to download service description: {e}")

def main(raw_data_dir: str, ars_excel_url: str, service_catalog_url: str, service_desc_url: str):
    """
    Orchestrates the downloading of service descriptions. Skips downloads if files already exist.
    
    :param raw_data_dir:  Directory to store data.
    :param ars_excel_url: URL to the ARS Excel file.
    :param service_catalog_url: API endpoint for service catalogs.
    :param service_desc_url: API endpoint for service descriptions.
    :side effects: Downloads service catalogs (CSV, order of 11,000) and 
                    service descriptions (JSON, order of 17,000).
    """
    service_catalog_dir = os.path.join(raw_data_dir, "service_catalogs")
    service_desc_dir = os.path.join(raw_data_dir, "service_descriptions")
    
    os.makedirs(service_catalog_dir, exist_ok=True)
    os.makedirs(service_desc_dir, exist_ok=True)

    # Step 1: Get all ARS
    all_ars = get_ars_from_excel(ars_excel_url)
    logger.info(f"Retrieved {len(all_ars)} ARS from {ars_excel_url}.")

    # Step 2: Download service catalogs and populate IDLB-to-ARS mapping
    idlb_to_ars = {}
    logger.info(f"Starting download of {len(all_ars)} service catalogs.")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(download_service_catalog, base_url=service_catalog_url, ars=ars, save_dir=service_catalog_dir): ars for ars in all_ars}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading Service Catalogs", unit="catalog"):
            ars = futures[future]
            service_catalog_path = future.result()
            if service_catalog_path:
                idlb_to_ars = update_idlb_dicts(service_catalog_path, ars, idlb_to_ars)  
    num_catalogs = len([catalog for catalog in os.listdir(service_catalog_dir)])
    logger.info(f"Downloaded {num_catalogs} service catalogs to {service_catalog_dir}.")
    
    # Step 3: Download detailed service descriptions
    download_service_descriptions(base_url=service_desc_url, idlb_to_ars=idlb_to_ars, save_dir=service_desc_dir)
    num_service_desc = len([desc for desc in os.listdir(service_desc_dir)])
    logger.info(f"Downloaded {num_service_desc} service descriptions to {service_desc_dir}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloads all adminsitrative service descriptions.")
    parser.add_argument("raw_data_dir", type=str, help="Directory to store data.")
    parser.add_argument("ars_excel_url", type=str, help="URL to the ARS Excel file.")
    parser.add_argument("service_catalog_url", type=str, help="API endpoint for service catalogs.")
    parser.add_argument("service_desc_url", type=str, help="API endpoint for service descriptions.")

    args = parser.parse_args()
    main(args.raw_data_dir, args.ars_excel_url, args.service_catalog_url, args.service_desc_url)