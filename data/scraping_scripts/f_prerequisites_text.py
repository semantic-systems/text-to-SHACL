""" 
e_prerequisites_text.py

 Master's Thesis
 Seike Appold
 
 - From full service descriptions in JSON format, extract the prerequisites text only
 and save to text file.
"""

import json
import sys
import textwrap
from utils import remove_html_tags

def extract_eligibility_requirements(input_filepath, output_filepath, max_line_length=100):
    """
    Extract 'Voraussetzungen' from the input JSON file and save it to a text file.

    :param input_filepath: Path to the input JSON file.
    :param output_filepath: Path to the output text file.
    """
    try:
        # Load the JSON data from the input file
        with open(input_filepath, 'r', encoding='utf-8') as f:
            full_description = json.load(f)

        # Extract the eligibility requirements
        eligibility_req = None
        for detail in full_description.get("details", []):
            if detail.get("title") == "Voraussetzungen":
                eligibility_req = remove_html_tags(detail.get("text", ""))
                break

        # Save the extracted text to the output file
        if eligibility_req:
            wrapped_text = textwrap.fill(eligibility_req, width=max_line_length)
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(wrapped_text)
            print(f"Eligibility requirements saved to {output_filepath}")
        else:
            print("No 'Voraussetzungen' found in the input file.")

    except FileNotFoundError:
        print(f"Error: File not found at {input_filepath}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {input_filepath}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) not in [3, 4]:
        print("Usage: python e_prerequisites_text.py <input_filepath> <output_filepath> [<max_line_length>]")
    else:
        input_filepath = sys.argv[1]
        output_filepath = sys.argv[2]
        if len(sys.argv) == 4:
            max_line_length = int(sys.argv[3])
        else:
            max_line_length = 100
        
        extract_eligibility_requirements(input_filepath, output_filepath, max_line_length)