""" 
GetMappingsFromDescription.py

Create and save mappings from administrative service descriptions including:
- IDLB to service name, e.g. {"L100001_LB_11022214": "Mobiler Bürgerservice"}
- Addressee code to addressee name, e.g. {"Bürger": "1000000"}
- Personal matter code to personal matter name, e.g. {"Arbeit": "1040000"}
- IDLB prefix to editorial system, e.g. {"L100012": "Schleswig-Holstein"}
"""

import os
import argparse
import json
from typing import Dict, Tuple
from Utils.Logger import setup_logger
from resources.schemata.ids_schema import ars_to_name

logger = setup_logger(__name__, log_file="logs/GetServiceNames.log")

def save_mappings(mapping_output_dir: str, 
                  idlb_to_name: Dict[str,str], 
                  addressees: Dict[str,str], 
                  personal_matters: Dict[str,str],
                  prefix_to_state: Dict[str,str]):
    os.makedirs(mapping_output_dir, exist_ok=True)
    identifier_schema_path = os.path.join(mapping_output_dir, "identifier.py")
    with open(identifier_schema_path, "a", encoding="utf-8") as pf:
        pf.write("\n\nidlb_to_name = ")
        pf.write(json.dumps(idlb_to_name, indent=4, ensure_ascii=False))
        pf.write("\n\nprefix_to_state = ")
        pf.write(json.dumps(prefix_to_state, indent=4, ensure_ascii=False))
    logger.info(f"IDLB to name and prefix to state mappings saved to {identifier_schema_path}")
    
    service_desc_schema_path = os.path.join(mapping_output_dir, "service_desc_schema.py")
    with open(service_desc_schema_path, "a", encoding="utf-8") as pf:
        pf.write("\n\naddressees = ")
        pf.write(json.dumps(addressees, indent=4, ensure_ascii=False))
        pf.write("\n\npersonal_matters = ")
        pf.write(json.dumps(personal_matters, indent=4, ensure_ascii=False))
    logger.info(f"Addressee and personal matter mappings saved to {service_desc_schema_path}")

def parse_service_descriptions(all_service_desc_dir: str) -> Tuple[Dict[str,str], Dict[str,str], Dict[str,str]]:
    idlb_to_name = {}
    addressees = {}
    personal_matters = {}
    prefix_to_state = {}
    
    for service in os.listdir(all_service_desc_dir):
        try:
            with open(os.path.join(all_service_desc_dir, service), "r", encoding="utf-8") as f:
                full_desc = json.load(f)
        except Exception as e:
            logger.error(f"Error reading file {service}: {e}")
            
        # IDLB to service name
        idlb = str(full_desc["id"]).replace(".", "_")
        idlb_to_name[idlb] = full_desc["name"]
        
        # Addressee code to name
        all_first_level_matters = full_desc["personalMatters"]
        for matter in all_first_level_matters:
            addressees[matter["name"]] = matter["code"]
            
            # Personal matter code to name
            all_second_level_matters = matter.get("children", [])
            for submatter in all_second_level_matters:
                personal_matters[submatter["name"]] = submatter["code"]

        # IDLB prefix to federal state
        prefix = service.split("_")[0]
        if prefix not in prefix_to_state.keys():
            prefix_to_state[prefix] = []
        
        # Add ARS if it's not already in the list (unique ARS values only)
        for ars in full_desc.get("ars", []):
            municipality = ars_to_name.get(ars, ars)
            prefix_to_state[prefix].append(municipality)

    # For each prefix, keep the name of the matching editorial system
    # NOTE: There is one editorial system per federal state and one for the federal government
    editorial_systems = {
        "Schleswig-Holstein",
        "Hessen",
        "Sachsen",
        "Hamburg",
        "Berlin",
        "Rheinland-Pfalz",
        "Thüringen",
        "Nordrhein-Westfalen",
        "Bund",
        "Sachsen-Anhalt",
        "Niedersachsen",
        "Baden-Württemberg",
        "Mecklenburg-Vorpommern",
        "Bayern",
        "Brandenburg",
        "Saarland",
        "Bremen"
        }
    prefix_to_state = {
        prefix: next((name for name in names if name in editorial_systems), None)
        for prefix, names in prefix_to_state.items()
    }
                
    return idlb_to_name, addressees, personal_matters, prefix_to_state

def main(service_desc_dir: str, schemata_dir: str):
    idlb_to_name, addressees, personal_matters, prefix_to_state = parse_service_descriptions(service_desc_dir)
    save_mappings(schemata_dir, idlb_to_name, addressees, personal_matters, prefix_to_state)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract service name mappings from administrative descriptions.")
    parser.add_argument("service_desc_dir", help="Directory containing service description JSON files")
    parser.add_argument("schemata", help="Directory to save the extracted mappings")
    
    args = parser.parse_args()
    main(args.service_desc_dir, args.schemata)