"""
GraphValidation.py

Functions for testing whether a given SHACL shapes graph validates RDF
graphs as expected.
"""
import os
from rdflib import Graph
from pyshacl import validate

def run_validation(shacl_path, rdf_path):
    """
    Validates a single RDF graph against a SHACL shapes graph.

    :param shacl_path: Path to the SHACL shapes graph.
    :param rdf_path: Path to the RDF data graph.
    :return: "eligible" if it conforms, "ineligible" if it does not, None if validation fails.
    """
    shacl_graph = Graph()
    shacl_graph.parse(shacl_path, format="turtle")

    rdf_graph = Graph()
    rdf_graph.parse(rdf_path, format="turtle")
    
    try:
        conforms, _, report = validate(
            data_graph=rdf_graph,
            shacl_graph=shacl_graph,
            meta_shacl=True,  # Ensure SHACL graph itself is valid
        )

        # Case 1: SHACL graph is ill-formed (MetaSHACL validation fails)
        if "SHACL File does not validate against the SHACL Shapes SHACL" in report:
            return None  # SHACL graph error

        return "eligible" if conforms else "ineligible"

    except Exception as e:
        return None  # Unexpected validation failure


def run_unit_test(shacl_path, rdf_dir, expected_results):
    """
    Checks if a given SHACL shapes graph validates RDF graphs as expected.

    :param shacl_path: Path to the SHACL shapes graph.
    :param rdf_dir: Path to the directory containing RDF graphs.
    :param expected_results: Dictionary mapping RDF file names to expected
        results, i.e. "eligible" (conforms) or "ineligible" (does not conform).
    """
    failures = []
    
    for data_graph, expected_status in expected_results.items():
        data_graph_path = os.path.join(rdf_dir, data_graph)
        result = run_validation(shacl_path, data_graph_path)

        # Case: SHACL graph itself is invalid
        if result is None:
            print("ERROR: SHACL graph is ill-formed and does not conform to SHACL-SHACL. Aborting all tests.")
            return

        # Collect failures instead of stopping
        if result != expected_status:
            failures.append(f"FAIL: {data_graph} is {result}, expected {expected_status}")
        else:
            print(f"PASS: {data_graph} is {result}")
            
    # Print summary of failures
    if failures:
        print("\nTest completed with failures:\n" + "\n".join(failures))
    else:
        print("All tests passed successfully.")