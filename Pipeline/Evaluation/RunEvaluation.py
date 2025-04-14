""" 
RunEvaluation.py

Compute evaluation metrics for a given experiment.
"""


import argparse
import json
import os
import pandas as pd
from pyshacl import validate
from pyshacl.errors import ReportableRuntimeError
from typing import Optional, List, Dict, Any
from Utils.Logger import setup_logger
from Utils.FileHandling import save_dict_to_json
from .GraphMatch import GraphMatcher

logger = setup_logger(__name__, "logs/RunEvaluation.log")

def shacl_syntax_compliant(shacl_path: str) -> Optional[bool]:
    """
    Checks if the given SHACL graph is syntactically valid using meta-SHACL.
    
    :param shacl_path: Path to the SHACL shapes graph.
    
    :return: 1 if the SHACL graph is well-formed, 0 if it is ill-formed,
        None if an unexpected error occurs.
    """
    syntax_error_msg = (
        "SHACL File does not validate against the "
        "SHACL Shapes SHACL (MetaSHACL) file."
        )
    min_rdf_graph = (
        "@prefix ex: <http://example.org/> .\n"
        "ex:Subject ex:hasProperty 'object' ."
        )

    # Try validating a minimal RDF graph with the generated SHACL graph
    try:
        validate(data_graph=min_rdf_graph, shacl_graph=shacl_path, debug=False, meta_shacl=True)
        return 1
    except ReportableRuntimeError as e:
        # Return 0 if a SHACL syntax error is detected
        if syntax_error_msg in e.message:
            return 0
    except Exception as e:
        logger.error(f"Unexpected error in SHACL validation: {e}")
    # Return None if an unexpected error occurred
    return None

def compute_average_metrics(per_file_performance: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes two types of average metrics across test files:
    - avg_all: Mean over all test files
    - avg_valid: Mean only over files where valid_turtle and valid_shacl are both 1

    :param per_file_performance: List of performance metrics for individual test files.
    
    :return: Dictionary containing both sets of averaged metrics.
    """
    df = pd.DataFrame(per_file_performance)
    df = df.drop(columns=["run_key"], errors="ignore")

    def compute_averages(df_subset, suffix, exclude=()):
        return {
            f"{col}_{suffix}": round(val, 4)
            for col, val in df_subset.mean().items()
            if col not in exclude
        }

    # Compute average for all test files
    avg_all = compute_averages(df, "all")
    
    # Compute average for runs with valid SHACL output only
    valid_subset = df[(df["valid_turtle"] == 1) & (df["valid_shacl"] == 1)]
    avg_valid = compute_averages(valid_subset, "valid_only", exclude=("valid_turtle", "valid_shacl"))

    return {**avg_all, **avg_valid}

def compute_average_metadata(raw_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes average inference time and token usage from raw outputs.
    
    :param raw_outputs: Raw model outputs including metadata per test file.
    
    :return: Average inference time, completion tokens, prompt tokens, and total tokens.
    """
    # Extract relevant information
    data = []
    for entry in raw_outputs:
        metadata = entry["metadata"]
        token_usage = metadata["token_usage"]
        data.append({
            "inference_time": metadata["inference_time"],
            "completion_tokens": token_usage["completion_tokens"],
            "prompt_tokens": token_usage["prompt_tokens"],
            "total_tokens": token_usage["total_tokens"]
        })
    
    # Average the results
    df = pd.DataFrame(data)
    avg_metadata = {metric: round(value, 4) for metric, value in df.mean().to_dict().items()}
    
    return avg_metadata

def append_to_overall_summary(experiment_metrics: Dict[str, Any], overall_summary_path: str):
    """
    Appends summarized metrics for an experiment to a CSV file.

    :param experiment_metrics: Dictionary of average metrics for the experiment.
    :param overall_summary_path: Path to the CSV file storing overall summaries.
    """
    # Select information to include in the summary
    main_items = [
        'mode', 'model', 'valid_turtle_all', 'valid_shacl_all', 'graph_edit_distance_all',
        'gbert_f1_all', 'triple_f1_all', 'validation_f1_all', 'graph_edit_distance_valid_only',
        'gbert_f1_valid_only', 'triple_accuracy_valid_only', 'triple_f1_valid_only', 
        'validation_f1_valid_only', 'inference_time'
    ]
    
    average_df = pd.DataFrame([{
        **{k: v for k, v in experiment_metrics.items() if k in main_items}
    }])
    
    # Append to overall summary, if it exists, or create new file otherwise
    if os.path.exists(overall_summary_path):
        overall_results = pd.read_csv(overall_summary_path)
        overall_results = pd.concat([overall_results, average_df], ignore_index=True)
    else:
        overall_results = average_df
    
    overall_results.to_csv(overall_summary_path, index=False)
    logger.info(f"Saved overall summary to {overall_summary_path}")

def evaluate_experiment(experiment_dir: str, shacl_gold_dir: str, user_profiles_dir: str, overall_summary_path: str) -> Dict[str, Any]:
    """
    Compute all relevant performance metrics for a single experiment.
    
    :param experiment_dir: Path to the directory containing experiment outputs.
    :param shacl_gold_dir: Directory containing groundtruth SHACL files.
    :param user_profiles_dir: Directory containing synthetic user profiles.
    :param overall_summary_path: Path to the CSV file storing summary of all
        experiments.
    
    :return: Dictionary with average metrics for the experiment.
    """
    metrics_dir = os.path.join(experiment_dir, "metrics")
    os.makedirs(metrics_dir, exist_ok=True)
    
    with open(os.path.join(experiment_dir, "output", "raw_output.json"), "r") as f:
        raw_output = json.load(f)
    
    per_file_performance = []
    
    # For each inference run, compute the metrics
    for run in raw_output:
        run_key = run["run_key"]
        metadata = run["metadata"]
        is_valid_turtle = metadata["valid_turtle"]
        
        # If the model did not output valid Turtle, set worst metrics
        if is_valid_turtle == 0:
            per_file_performance.append(
                {
                    "run_key": run_key,
                    "valid_turtle": is_valid_turtle,
                    "valid_shacl": 0,
                    "graph_edit_distance": 1,
                    **{metric: 0 for metric in ["gbert_precision", "gbert_recall", "gbert_f1"]},
                    **{metric: 0 for metric in ["triple_accuracy", "triple_precision", "triple_recall", "triple_f1"]},
                    **{metric: 0 for metric in ["validation_accuracy", "validation_precision", "validation_recall", "validation_f1"]},
                })
            continue
        
        # Check compliance with SHACL syntax
        parsed_output_path = metadata["parsed_output_path"]
        syntax_compliant = shacl_syntax_compliant(parsed_output_path)
        
        # Compare generated SHACL graph with groundtruth SHACL graph
        shacl_gold_path = os.path.join(shacl_gold_dir, f"{metadata["test_file"]}.ttl")
        matcher = GraphMatcher(shacl_gold_path, parsed_output_path)
        triple_match = matcher.compute_triple_match()
        ged = matcher.compute_ged()
        gbert = matcher.compute_gbert()
        
        # Compute validation performance only for well-formed SHACL graphs
        if syntax_compliant:
            validation_performance = matcher.compute_validation_performance(user_profiles_dir)
        else:
            validation_performance = {
                "validation_accuracy": 0,
                "validation_precision": 0,
                "validation_recall": 0,
                "validation_f1": 0
            }
                  
        per_file_performance.append({
            "run_key": run_key,
            "valid_turtle": is_valid_turtle,
            "valid_shacl": syntax_compliant,
            "graph_edit_distance": ged,
            "ged_timeout": matcher.ged_timeout,
            **gbert,
            **triple_match,
            **validation_performance
        })
    
    # Save per file metrics
    per_file_performance_path = os.path.join(metrics_dir, "per_file_metrics.json")
    save_dict_to_json(per_file_performance, per_file_performance_path)
    logger.info(f"Saved per file metrics to {per_file_performance_path}")
    
    # Compute average metrics
    average_performance = {
        "mode": run["metadata"]["mode"],
        "model": run["metadata"]["model"],
        **compute_average_metrics(per_file_performance),
        **compute_average_metadata(raw_output),
    }
    
    # Save detailed experiment summary
    average_performance_path = os.path.join(metrics_dir, "average_performance.json")
    save_dict_to_json(average_performance, average_performance_path)
    logger.info(f"Saved average results to {average_performance_path}")
    
    # Save key metrics to overall summary
    append_to_overall_summary(average_performance, overall_summary_path)
    return average_performance


def main(mode: str, results_dir: str, shacl_gold_dir: str, user_profiles_dir: str) -> List[Dict[str, Any]]:
    """ 
    Orchestrates evaluation of a single experiment depending on the mode.
    
    :param mode: Experiment mode (e.g., "baseline", "fewshot").
    :param results_dir: Directory containing results from all experiments.
    :param shacl_gold_dir: Directory containing groundtruth SHACL files.
    :param user_profiles_dir: Directory containing synthetic user profiles.
    
    :return: List of dictionaries with average metrics for the experiment.
    """
    experiment_dir = os.path.join(results_dir, mode)
    logger.info(f"Running evaluation for {mode} experiment.")
    overall_summary_path = os.path.join(results_dir, "performance_by_experiment.csv")
    
    # For baseline, compute the metrics for each tested model
    if mode == "baseline":
        baseline_summary_metrics = []
        models = [directory for directory in os.listdir(experiment_dir) if os.path.isdir(os.path.join(experiment_dir, directory))]
        for model in models:
            model_dir = os.path.join(experiment_dir, model)
            experiment_metrics = evaluate_experiment(model_dir, shacl_gold_dir, user_profiles_dir, overall_summary_path)
            baseline_summary_metrics.append(experiment_metrics)
        return baseline_summary_metrics
    
    # For other experiments, compute the metrics directly
    return evaluate_experiment(experiment_dir, shacl_gold_dir, user_profiles_dir, overall_summary_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute evaluation metrics for a given experiment.")
    parser.add_argument("experiment_dir", help="Directory with results for the experiment to be evaluated.")
    parser.add_argument("results_dir", help="Directory with results from all experiments.")
    parser.add_argument("shacl_gold_dir", help="Directory with groundtruth SHACL shapes.")
    parser.add_argument("user_profiles_dir", help="Directory with synthetic user profiles.")
    
    args = parser.parse_args()
    main(args.experiment_dir, args.results_dir, args.shacl_gold_dir, args.user_profiles_dir)