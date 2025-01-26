""" 
Parsing.py

Utility functions for analyzing text and extracting information.
"""
from typing import Tuple, Optional, List, Any
import networkx as nx
import os
import rdflib
import logging

def retrieve_parsable_turtle(input_string: str, logger: logging.Logger) -> Optional[str]:
    """
    Return parsable Turtle content from input string, if any.
    
    :param input_string: Input string to extract Turtle content from.
    :param logger: Logger object.
    :return: Valid Turtle content, if found, None otherwise.
    """
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

def get_run_key_components(run_key: str) -> Tuple[str, str, str]:
    """
    Extracts model, method, and idlb of social benefit from the run key.

    :run_key: Run key in the format "<method>_<model>_<idlb>".
    :returns: Method, model, and benefit name for a given prompt.
    """
    # Remove suffix, if input string is a filename
    run_key = os.path.splitext(run_key)[0]
    components = run_key.split('_')

    # Ensure valid prompt ID format
    if len(components) < 2:
        raise ValueError("Invalid prompt ID format")

    # Extract the prompt configs
    method, model, idlb = components[0], components[1], '_'.join(components[2:])
    return method, model, idlb

def norm_string(input: Any) -> str:
    """Converts input into a lowercased string without leading or trailing white spaces."""
    return str(input).lower().strip()