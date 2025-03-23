""" 
GetServiceDescriptions.py

- Extract unique IDLBs from service catalogs
- For each IDLB, download the full administrative service description
    using the Suchdienst API (https://anbindung.pvog.cloud-bdc.dataport.de/docs/api/suchdienst-api)
    by the Portalverbund Online-Gateway (PVOG)
"""

import os
import re
import json
import argparse
import pandas as pd
from tqdm import tqdm
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from Utils.FileHandling import download_and_save_file
from Utils.Logger import setup_logger
from Utils.Parsing import search_dict_in_file
from resources.schemata.ids_schema import ars_to_name

logger = setup_logger(__name__, log_file="logs/GetServiceDescriptions.log")

SERVICE_CATALOG_ENDPOINT = os.getenv("SUCHDIENST_SERVICE_CATALOG")
SERVICE_DESCRIPTION_ENDPOINT = os.getenv("SUCHDIENST_SERVICE_DESCRIPTION")


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
            if valid_idlb_pattern.match(str(row['ID-LB'])):
                idlb = str(row['ID-LB']).replace(".","_")
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
        filename = f"{idlb}.json"
        file_path = os.path.join(save_dir, filename)

        # Download service description if it does not yet exist locally
        idlb_dot = idlb.replace('_', '.')
        if not os.path.isfile(file_path):
            url = base_url.replace("{ars}", ars)
            download_and_save_file(url=url, params={"q": idlb_dot}, save_dir=save_dir, filename=filename)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_download_description, idlb, ars) for idlb, ars in idlb_to_ars.items()]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading Service Descriptions", unit="description"):
            try:
                future.result()
            except Exception as e:
                logger.warning(f"Failed to download service description: {e}")

def download_service_catalog(ars: str, idlb_to_ars: Dict[str,str], service_catalogs_dir: str, service_catalog_url:str) -> str:
    """ 
    Downloads service catalog for a given ARS to the specified directory
    and adds the services it contains to the IDLB to ARS mapping.
    
    :param ars: ARS for the service catalog.
    :param idlb_to_ars: Mapping of IDLB to ARS.
    :param service_catalogs_dir: Directory to save the service catalog.
    :param service_catalog_url: URL to the service catalog.
    """
    filename = f"ars_{ars}.csv"
    save_path = os.path.join(service_catalogs_dir, filename)

    # Only download service catalog if it does not yet exist locally
    if not os.path.isfile(save_path):
        try:
            download_and_save_file(url=service_catalog_url, params={"ars":ars}, save_dir=service_catalogs_dir, filename=filename)
        except Exception as e:
            logger.error(f"Failed to download service catalog for ARS {ars}: {e}")
            return None

    # Update mapping with IDLBs from the service catalog
    try:
        idlb_to_ars.update(update_idlb_dicts(service_catalog=save_path, ars=ars, idlb_to_ars=idlb_to_ars))
    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")

def main(service_catalogs_dir: str, 
         all_service_descriptions_dir: str, 
         ids_schema_path: str, 
         service_catalog_url: str=SERVICE_CATALOG_ENDPOINT, 
         service_desc_url: str=SERVICE_DESCRIPTION_ENDPOINT):
    """
    Retrieves detailed descriptions for all administrative services.

    Downloads the descriptions for all services accessible via the PVOG
    Suchdienst API (JSONs, order of 17,000). This requires a mapping of
    service ID (IDLB) to ARS; if it does not exist yet, it is created by
    downloading and processing the service catalogs for all ARS (CSVs, 
    order of 11,000). If the description for a given service already
    exists, it is skipped.
    
    :param service_catalogs_dir: Directory to save the service catalogs.
    :param all_service_descriptions_dir: Directory to save the service descriptions.
    :param ids_schema_path: Path to save the IDLB-to-ARS mapping.
    :param service_catalog_url: API endpoint to download a service catalog.
    :param service_desc_url: API endpoint to download a service description.
    """
    idlb_to_ars = search_dict_in_file(ids_schema_path, "idlb_to_ars")
    
    # If IDLB to ARS mapping does not yet exist, create it from scratch
    if idlb_to_ars is None:
        ars_list = ars_to_name.keys()
        logger.info(f"No IDLB to ARS mapping provided. Starting download of {len(ars_list)} service catalogs.")
        os.makedirs(service_catalogs_dir, exist_ok=True)
        
        # For each ARS, download the service catalog and add services to the mapping
        idlb_to_ars = {}
        for ars in tqdm(ars_list, desc="Downloading Service Catalogs", unit="catalog"):
            try:
                download_service_catalog(ars=ars, idlb_to_ars=idlb_to_ars, service_catalogs_dir=service_catalogs_dir, service_catalog_url=service_catalog_url)
            except Exception as e:
                logger.error(f"Error processing ARS {ars}: {e}")
        logger.info(f"Service catalogs saved to {service_catalogs_dir}")
        
        # Save the updated IDLB to ARS mapping
        with open(ids_schema_path, "a", encoding="utf-8") as file:
            file.write("\n\nidlb_to_ars = ")
            file.write(json.dumps(idlb_to_ars, indent=4, ensure_ascii=False))
    
    # Download full service descriptions for all IDLBs
    os.makedirs(all_service_descriptions_dir, exist_ok=True)
    download_service_descriptions(base_url=service_desc_url, idlb_to_ars=idlb_to_ars, save_dir=all_service_descriptions_dir)
    logger.info(f"Service descriptions saved to {all_service_descriptions_dir}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloads all adminsitrative service descriptions.")
    parser.add_argument("service_catalogs_dir", type=str, help="Directory to save the service catalogs.")
    parser.add_argument("all_service_descriptions_dir", type=str, help="Directory to save the service descriptions.")
    parser.add_argument("ids_schema_path", type=str, help="Path to save the IDLB-to-ARS mapping.")
    parser.add_argument("--service_catalog_url", type=str, default=SERVICE_CATALOG_ENDPOINT, help="API endpoint to download a service catalog.")
    parser.add_argument("--service_desc_url", type=str, default=SERVICE_DESCRIPTION_ENDPOINT, help="API endpoint to download a service descriptions.")
    
    args = parser.parse_args()
    main(args.service_catalogs_dir, args.all_service_descriptions_dir, args.ids_schema_path, args.service_catalog_url, args.service_desc_url)