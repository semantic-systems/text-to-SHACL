"""
GraphValidation.py

Functions for testing whether a given SHACL shapes graph validates RDF
graphs as expected.
"""
import os
import unittest
from pyshacl import validate
from typing import Tuple


def validate_data_graph(data_graph: str, shacl_graph: str) -> Tuple[str,str,str]:
    """Check if a given data graph conforms with a SHACL shapes graph.

    :param data_graph: Path to the data graph file in Turtle format.
    :param shacl_graph: Path to the SHACL shapes graph file in Turtle format.
    :return: Tuple of (conforms, results_graph, report), where conforms is
                None and report contains the error message if SHACL graph is 
                ill-formed or validation fails for an unexpected reason.
    """
    try:
        conforms, results_graph, report = validate(
            data_graph=data_graph,
            shacl_graph=shacl_graph,
            meta_shacl=True,
        )
        
        # Check if SHACL graph is ill-formed (Meta-SHACL validation fails)
        if "SHACL File does not validate against the SHACL Shapes SHACL" in report:
            return None, results_graph, report
    
        return conforms, results_graph, report
       
    except Exception as e:
        return None, None, str(e)

class TestSHACLValidation(unittest.TestCase):
    """ 
    Usage:
    
    shacl_file = "/path/to/shacl_file.ttl"
    user_profiles_dir = "/path/to/user_profiles_dir"
    expected_results = {
        "profile_1.ttl": "eligible", 
        "profile_2.ttl": "ineligible"
        ...
        }

    suite = unittest.TestSuite()
    suite.addTest(TestSHACLValidation("test_shacl_graph", shacl_file, user_profiles_dir, expected_results))

    runner = unittest.TextTestRunner()
    runner.run(suite)
    """

    def __init__(self, methodName="runTest", shacl_file=None, user_profiles_dir=None, expected_results=None):
        """Initialize test parameters for testing a given SHACL shapes graph.
        
        :param shacl_file: Path to the SHACL shapes graph file.
        :param user_profiles_dir: Path to the directory containing user profiles,
                                    i.e. data graphs to be tested.
        :param expected_results: Dictionary mapping user profile filenames to
                                    expected results ("eligible" or "ineligible")
        """
        super().__init__(methodName)
        self.shacl_file = shacl_file
        self.user_profiles_dir = user_profiles_dir
        self.expected_results = expected_results
        
    def test_shacl_graph(self):
        """Test if SHACL shapes graph validates user profiles as expected"""
        for filename, expected_outcome in self.expected_results.items():
            with self.subTest(user_profile=filename):
                user_profile_path = os.path.join(self.user_profiles_dir, filename)
                conforms, _, report = validate_data_graph(user_profile_path, self.shacl_file)   
                
                # Ensure validation did not fail
                self.assertIsNotNone(conforms, f"SHACL validation failed for {filename}: {report}")
                
                # Determine result based on SHACL output
                if "Conforms: False" in report:
                    result = "ineligible"
                elif "Conforms: True" in report:
                    result = "eligible"
                
                # Assert expected vs actual result
                self.assertEqual(result, expected_outcome, 
                                    f"Failed for {filename}: expected {expected_outcome}, got {result}")

                status = "SUCCESS" if result == expected_outcome else "FAILED"
                print(f"[{status}] {filename}: Expected '{expected_outcome}', got '{result}'")