import os
from typing import List, Tuple, Dict
import pandas as pd
from pyshacl import validate

def extract_configs_from_prompt_id(prompt_id: str) -> Tuple[str, str, str]:
    """
    Extracts model, method, and name of social benefit from pompt ID.

    :prompt_id: Prompt ID in the format "<method>_<model>_<benefit>", e.g. "baseline_gpt2_kindergeld"
    :returns: Model, method, and benefit for a given prompt.
    """
    # Remove suffix, if input string is a filename
    prompt_id, _ = os.path.splitext(prompt_id)
    parts = prompt_id.split('_')
    
    # Ensure valid prompt ID format
    if len(parts) < 2:
        raise ValueError("Invalid prompt ID format")
    
    # Extract the prompt configs
    method, model, benefit = parts[0], parts[1], parts[2]

    return method, model, benefit

def save_results_to_csv(results: List[Dict], file_path: str, mean: bool = False):
    """
    Save evaluation results to a CSV file.

    :param results: List of result dictionaries.
    :param file_path: Path to the CSV file.
    :param mean: If True, average the results before writing.
    :side effect: Creates a CSV file at the specified location.
    """
    df = pd.DataFrame(results)
    if mean:
        df = df.mean(numeric_only=True).to_frame().T
        df.insert(0, "Method", results[0]["Method"])
        df.insert(1, "Model", results[0]["Model"])
    df.to_csv(file_path, index=False)

def norm_string(string: str) -> str:
    """Normalize a string by lowercasing and stripping it."""
    return str(string).lower().strip()

def shacl_validation(profiel_path: str, shacl_path: str) -> bool:
    try:
        conforms, _, _ = validate(data_graph=profiel_path, shacl_graph=shacl_path)
    except Exception as e:
        print(f"Error during SHACL validation: {e}")
        return False
    return conforms