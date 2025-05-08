""" 
Parsing.py

Utility functions for analyzing text and extracting information.
"""
import ast
import re
import rdflib
import logging
import os
from typing import Optional, Any, Dict, Tuple
from resources.schemata.ids_schema import idlb_to_labels
from resources.schemata.method_schema import supported_modes
from Utils.Logger import setup_logger


def retrieve_parsable_turtle(input_string: str, logfile: str = "logs/Parsing.py") -> Optional[str]:
    """
    Return parsable Turtle content from input string, if any.
    
    :param input_string: Input string to extract Turtle content from.
    :param logfile: Path to the log file.
    :return: Valid Turtle content, if found, None otherwise.
    """
    logger = setup_logger(__name__, logfile)
    prefixes = ["@prefix", "@base", "<http://", "PREFIX"]
    
    # If Turtle flags are present, extract everything in between
    if '```turtle' in input_string and '```' in input_string:
        start = input_string.find('```turtle') + len('```turtle')
        end = input_string.find('```', start)
        turtle_candidate = input_string[start:end].strip()
    # If a prefix is present, extract everything after the first occurrence
    elif any(opener in input_string for opener in prefixes):
        start = input_string.find(next(term for term in prefixes if term in input_string))
        turtle_candidate = input_string[start:].strip()
    else:
        turtle_candidate = input_string.strip()
    
    # Do not count empty outputs as valid Turtle
    if turtle_candidate.strip() == "":
        return None
    
    # Check if the data is parsable
    graph = rdflib.Graph()
    try:
        graph.parse(data=turtle_candidate, format="turtle")
    except Exception as e:
        logger.warning(f"Turtle candidate not parsable: {e}")
        return None

    return turtle_candidate


def norm_string(input: Any) -> str:
    """Converts input into a lowercased string without leading or trailing white spaces."""
    return str(input).lower().strip()


def search_dict_in_file(file_path: str, dict_name: str) -> Dict[str,str]:
    """Returns the dictionary if a non-empty dictionary with the given name
    exists in a Python file, otherwise returns None."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == dict_name:
                    if isinstance(node.value, ast.Dict) and node.value.keys:
                        return {ast.literal_eval(key): ast.literal_eval(value) for key, value in zip(node.value.keys, node.value.values)}

    return None


def get_idlb_from_label(label_value: str, label_type: str, logfile: str = "logs/Parsing.log", idlb_to_labels: Dict[str,Any]=idlb_to_labels) -> str:
    """Returns the IDLB corresponding to the given label.
    
    Supports conversion from "german label", "english label", and "short label" to IDLB.

    :param label_value: The value of the input label.
    :param label_type: The type of the input label.
    :param logfile: Path to the log file.
    :param idlb_to_labels: Mapping from IDLB to labels.
    
    :return: The IDLB that corresponds to the input label.
    """
    logger = setup_logger(__name__, logfile)
    for idlb, details in idlb_to_labels.items():
        if details.get(label_type).lower() == label_value:
            return idlb
        
    logger.warning(f"Label '{label_value}' of type '{label_type}' not found in the provided schema.")
    return None


def normalize_mode(mode: str) -> str:
    """Convert synonyms to standard mode name."""
    mode = mode.lower()
    for key, mode_data in supported_modes.items():
        if mode == key or mode in mode_data["synonyms"]:
            return key
    # Mode not found in modes schema
    return mode


def get_idlb_from_intro(intro: str) -> Tuple[str, str]:
    "Returns the name and IDLB from introductory sentence of benefits description."
    pattern = r"^Es folgen die Bedingungen für die Sozialleistung '(.+?)' mit der IDLB (\S+)\."
    match = re.match(pattern, intro)
    if match:
        name, idlb = match.groups()
        return name, idlb
    return None, None


def get_decomposition_section(file_path: str, logger: logging.Logger) -> str:
    """Extracts the requirements decomposition from a markdown file also
    including other sections above."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start = None
    for line_index, line in enumerate(lines):
        # Start after the line with the relevant section heading
        if "<b>Requirements decomposition</b>:" in line:
            start = line_index + 1
            break

    if start is not None:
        # Join everything from the "Requirements decomposition" line onward
        decomposition_text = ''.join(lines[start:]).strip()
        return decomposition_text
    else:
        logger.error("Failed to extract 'Requirements decomposition' for chain of thought example.")


def save_turtle_output(turtle_output: Optional[str], parsed_output_dir: str, run_key: str, logfile: str = "logs/Parsing.log") -> Optional[str]:
    """Writes the given Turtle content to a file if the content is not empty.

    :param turtle_output: The Turtle-formatted RDF content to be saved. 
        If None or empty, nothing is saved.
    :param parsed_output_dir: Directory to save the parsed output file.
    :param run_key: Identifier for naming the output file.
    :param logfile: Path to the log file.
    
    :return: The path to the saved file if successful, otherwise None.
    """
    logger = setup_logger(__name__, logfile)
    
    if not turtle_output:
        return None

    output_path = os.path.join(parsed_output_dir, f"{run_key}.ttl")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(turtle_output)
        logger.info(f"Saved parsed output to {os.path.abspath(output_path)}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save parsed output: {e}")
        return None