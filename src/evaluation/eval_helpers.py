import os
from typing import List, Tuple, Dict
import pandas as pd

def extract_configs_from_prompt_id(prompt_id: str) -> Tuple[str, str, str]:
    """
    Extracts the model and method used for a given prompt from pompt ID.

    Args:
        prompt_id (str): Prompt ID in the format "<method>_<model>_<benefit>", e.g. "baseline_gpt2_kindergeld"

    Returns:
        List[str, str]: The model and method used for the prompt
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
    Save results to a CSV file.

    :param results: List of result dictionaries.
    :param file_path: Path to the CSV file.
    :param mean: If True, average the results before writing.
    :side effect: Creates a CSV file at the specified location.
    """
    df = pd.DataFrame(results)
    if mean:
        df = df.mean(numeric_only=True).to_frame().T
        # Add "model" and "method" columns from results
        df.insert(0, "method", results[0]["method"])
        df.insert(1, "model", results[0]["model"])
    df.to_csv(file_path, index=False)