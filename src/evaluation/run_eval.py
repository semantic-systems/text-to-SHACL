""" 
run_eval.py

- Evaluate the quality of machine-generated SHACL-shapes
"""

import sys
import os
import random
import argparse
from eval_helpers import check_shacl_syntax, extract_configs_from_prompt_id, save_results_to_csv
from preprocessing.utils import make_dir
from typing import List
from pyshacl import validate
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score
from typing import Dict, Tuple

def check_shacl_syntax(shacl_path: str) -> bool:
    """
    Evaluates whether a SHACL shapes graph complies with SHACL syntax
    by validating a minimal RDF graph against it.
    
    :param shacl_path: Path to the generated SHACL shapes graph.
    :return: True if shapes graph complies with SHACL syntax, False otherwise.
    """
    # If the file is empty, the model output was not parsable
    if os.stat(shacl_path).st_size == 0:
        return False
    
    # Define a minimal RDF graph
    minimal_rdf_graph = """
    @prefix ex: <http://example.org/> .
    ex:Subject ex:hasProperty "object" .
    """
    
    # Validate the minimal graph against the generated SHACL shapes graph
    try:
        conforms, _, _ = validate(
            data_graph=minimal_rdf_graph,
            shacl_graph=shacl_path,
            data_graph_format="turtle",
            shacl_graph_format="turtle",
            meta_shacl=True # Check for syntax errors
        )
        return conforms
    except Exception as e:
        print(f"Error during validation: {e}")
        return False

def calculate_graph_metrics(shacl_gen_path, shacl_gold_path):
    # DUMMY
    value = random.randint(0, 1)
    return value

def calclate_validation_performance(shacl_gen_path: str, shacl_gold_path: str, profiles_dir: str) -> Dict[str, float]:
    """
    Compute precision, recall, accuracy, and F1 score based on SHACL validation
    results of a generated and a groundtruth shapes graph for a set of
    synthetic user profiles.

    :param generated_shacl_path: Path to the generated SHACL graph.
    :param groundtruth_shacl_path: Path to the groundtruth SHACL graph.
    :param profiles_dir: Directory with synthetics user profiles.
    :return: Dictionary containing precision, recall, accuracy, and F1 score.
    """
    y_true, y_pred = [], []
    
    # For each profile, check if it conforms with the generated and groundtruth graphs
    for profile in os.listdir(profiles_dir):
        profile_path = os.path.join(profiles_dir, profile)
        conforms_with_gen, _, _ = validate(data_graph=profile_path, shacl_graph=shacl_gen_path)
        conforms_with_gold, _, _ = validate(data_graph=profile_path, shacl_graph=shacl_gold_path)

        # Profile conforms with both graphs (TP)
        if conforms_with_gen and conforms_with_gold:
            y_pred.append(1)
            y_true.append(1)
        # Profile violates both graphs (TN)
        elif not conforms_with_gen and not conforms_with_gold:
            y_pred.append(0)
            y_true.append(0)
        # Profile conforms with generated graph but not with groundtruth (FP)
        elif conforms_with_gen and not conforms_with_gold:
            y_pred.append(1)
            y_true.append(0)
        # Profile violates generated graph but conforms with groundtruth (FN)
        else:
            y_pred.append(0)
            y_true.append(1)
            
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    return {
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "f1": f1
    }


def main(shacl_gen_dir, shacl_gold_dir, profiles_dir, results_dir):
    """
    Orchestrates the evaluation process for all generated SHACL graphs in
    a given directory.

    :param shacl_gen_dir:  Directory with generated SHACL shapes.
    :param shacl_gold_dir: Directory with groundtruth SHACL shapes.
    :param profiles_dir: Directory with syntehtics user profiles.
    :param results_dir: Directory to save results.
    """
    make_dir(results_dir)

    results_per_file = []

    for file in os.listdir(shacl_gen_dir):
        method, model, benefit = extract_configs_from_prompt_id(file)
        shacl_gold_path = os.path.join(shacl_gold_dir, f"{benefit}.ttl")
        shacl_gen_path = os.path.join(shacl_gen_dir, file)

        # Check if file complies with SHACL syntax
        syntax_accuracy = 1 if check_shacl_syntax(shacl_gen_path) else 0
        
        # Compare generated and groundtruth SHACL graphs
        graph_metrics = calculate_graph_metrics(shacl_gen_path, shacl_gold_path) # DUMMY
        
        # Assess validation performance over a set of synthetic user profiles
        validation_performance = calclate_validation_performance(shacl_gen_path, shacl_gold_path, profiles_dir)
    
        results_per_file.append({
            "prompt_id": os.path.splitext(file)[0],
            "model": model,
            "method": method,
            "syntax_accuracy": syntax_accuracy,
            "graph_metrics": graph_metrics,
            **validation_performance,
        })

    # Save per-file results
    per_file_csv_path = os.path.join(results_dir, "per_file_results.csv")
    save_results_to_csv(results_per_file, per_file_csv_path)

    # Save mean results for a given model and method
    summary_csv_path = os.path.join(results_dir, "summary.csv")
    save_results_to_csv(results_per_file, summary_csv_path, mean=True)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process SHACL generation and comparison.")
    parser.add_argument("shacl_gen_dir", help="Directory with generated SHACL shapes")
    parser.add_argument("shacl_gold_dir", help="Directory with groundtruth SHACL shapes")
    parser.add_argument("profiles_dir", help="Directory with synthetic user profiles")
    parser.add_argument("results_dir", help="Directory to store results")
    args = parser.parse_args()
    
    main(args.shacl_gen_dir, args.shacl_gold_dir, args.profiles_dir, args.results_dir)