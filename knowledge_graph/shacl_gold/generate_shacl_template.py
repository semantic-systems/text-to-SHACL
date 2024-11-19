"""
 generate_shacl_template.py

 Master's Thesis
 Seike Appold
 
 - From input JSON with the full description of an adminitsrative service,
    generate a Turtle file template for a SHACL shapes graph that already 
    includes common prefixes and metadata but no constraints. Note: Manually
    checking the output is recommended.
"""
import json
import re
import sys
from bs4 import BeautifulSoup 

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.text.strip()

def generate_template_content(name, description, idlb, prerequisites):
    return f"""@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@base <https://foerderfunke.org/default#> .

#################################################################
#    METADATA
#################################################################

<{name}> a <FundingProgram> ;
    <idlb> "{idlb}" ;
    dc:title "{name}"@de ;
    dc:description "{description}"@de . 

#################################################################
#    CONSTRAINTS
#################################################################
"""

# Main function to process input file and generate output file
def main(input_file_path, output_file_path):
    # Read the JSON input file
    with open(input_file_path, 'r', encoding='utf-8') as f:
        full_description = json.load(f)

    # Extract required information
    name = full_description["name"]
    description = remove_html_tags(full_description["description"])
    idlb = full_description["id"].replace('_', '.')
    prerequisites = ""

    # Extract eligibility requirements (prerequisites)
    for detail in full_description["details"]:
        if detail["title"] == "Voraussetzungen":
            prerequisites = remove_html_tags(detail["text"])

    # Generate the Turtle content
    turtle_content = generate_template_content(name, description, idlb, prerequisites)

    # Generate a new file called output_file_path
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(turtle_content)

    print(f"Turtle file generated successfully at {output_file_path}")

# Run the script with command line arguments
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_shacl_template.py <input_file_path> <shacl_file_path>")
    else:
        input_file_path = sys.argv[1]
        output_file_path = sys.argv[2]
        main(input_file_path, output_file_path)