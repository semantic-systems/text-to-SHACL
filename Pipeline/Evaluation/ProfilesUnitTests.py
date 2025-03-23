import os
import unittest
import pyshacl
from typing import Tuple

def run_validation(data_graph: str, shacl_graph: str) -> Tuple[str, str, str]:
    """Run SHACL validation on a single data graph.
    
    :param data_graph: Path to the data graph file
    :param shacl_graph: Path to the SHACL shapes graph file
    :return: Tuple of (conforms, report_graph, report_text)
    """
    results = pyshacl.validate(
            data_graph=data_graph,
            shacl_graph=shacl_graph,
            data_graph_format="ttl",
            shacl_graph_format="ttl",
            serialize_report_graph=True,
            inference='none',
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=True,
            meta_shacl=True,
            advanced=False,
            debug=False,
            )
    return results


class TestSHACLValidation(unittest.TestCase):

    def __init__(self, methodName="runTest", shacl_file=None, user_profiles_dir=None, expected_results=None):
        super().__init__(methodName)
        self.shacl_file = shacl_file
        self.user_profiles_dir = user_profiles_dir
        self.expected_results = expected_results

    def test_user_profiles(self):
        """Test SHACL validation for multiple user profiles."""
        for filename, expected_outcome in self.expected_results.items():
            with self.subTest(user_profile=filename):
                user_profile_path = os.path.join(self.user_profiles_dir, filename)
                results = run_validation(user_profile_path, self.shacl_file)
                _, _, report_text = results
                if "Conforms: False" in report_text:
                    result = "Ineligible"
                elif "Conforms: True" in report_text:
                    result = "Eligible"
                
                success = result == expected_outcome
                self.assertEqual(result, expected_outcome, 
                                 f"Failed for {filename}: expected {expected_outcome}, got {result}")
                
                # Print success/failure message
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"[{status}] {filename}: Expected '{expected_outcome}', got '{result}'",flush=True)

# Factory function to generate test cases dynamically
def create_test_suite(shacl_file, user_profiles_dir, expected_results):
    suite = unittest.TestSuite()
    suite.addTest(TestSHACLValidation("test_user_profiles", shacl_file, user_profiles_dir, expected_results))
    return suite