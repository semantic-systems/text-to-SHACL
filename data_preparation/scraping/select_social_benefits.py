"""
select_social_benefits.py

Master's Thesis
Seike Appold

- From all administrative services, select social benefits to be analyzed.
- Save relevant information (name, IDLB, requirements text) for selected
benefits as JSON.
"""

import os
import json
import sys
from typing import List


def get_idlb_list(input_dir: str) -> List[str]:
    """Get a list of IDLBs for selected social benefits.

    Possible selection criteria:
        - idlb: prioritize Bund IDLB (for similar dataquality)
        - personalMatters: search for Geburt (1010000), Altersvorsorge und Ruhestand (1180000), Partnerschaft und Familie (1020000), Sozialleistungen (1140000), Schule, Ausbildung und Studium (1030000)
        - "addressees": "Bürger"
        - "typing"/"code": "1": Regelungs und Vollzugskompetenz des Bundes
        - leikakeys: specifically search for certain services
        - "validTo": "2999-12-31" -> only select benefits that are still valid
        - "externalLastUpdate"
    """
    # B100019_LB_581863: Kinderzuschlag
    # B100019_LB_106311931: Bürgergeld

    # IDLBS WITHOUT DOT!

    return ["B100019_LB_581863", "B100019_LB_106311931"]


def save_benefit_details(idlbs: List[str], input_dir: str, output_dir: str) -> None:
    """Extract details for the specified social benefits and save to JSON.

    :param idlbs: List of IDLBs for social benefits to be analyzed.
    :param input_dir: Directory containing all full service descriptions in JSON format.
    :param output_dir: Directory to save the extracted benefit details.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save name, idlb, requirements text for each selected benefit
    for idlb in idlbs:
        # Load full benefit description
        input_path = os.path.join(input_dir, f"{idlb}.json")
        with open(input_path, 'r') as file:
            full_description = json.load(file)

        # Extract benefit details
        name = full_description["name"]
        for detail in full_description["details"]:
            if detail["title"] == "Voraussetzungen":
                requirements = detail["text"]
        benefit_details = {
            "name": name,
            "short_name": "PLACEHOLDER",
            "idlb": idlb,
            "requirements": requirements
        }

        # Save extracted details to JSON file
        output_path = os.path.join(output_dir, f"{idlb}.json")
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(benefit_details, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python get_all_service_descriptions.py <input_dir> <output_dir>")
    else:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]

        # Get list of IDLBs for selected social benefits
        idlbs = get_idlb_list(input_dir)

        # Save metadate and requirements for selected benefits to JSON
        save_benefit_details(idlbs, input_dir, output_dir)