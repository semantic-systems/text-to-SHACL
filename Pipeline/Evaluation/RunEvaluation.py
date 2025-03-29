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
    Validates a minimal RDF graph against a SHACL shapes graph to check for
    syntax errors.
    
    :param shacl_path: Path to the SHACL shapes graph.
    :return: 1 if the SHACL graph has no syntax errors, 0 if it has 
             syntax errors, None if an unexpected error occurs.
    """
    syntax_error_msg = (
        "SHACL File does not validate against the "
        "SHACL Shapes SHACL (MetaSHACL) file."
        )
    min_rdf_graph = (
        "@prefix ex: <http://example.org/> .\n"
        "ex:Subject ex:hasProperty 'object' ."
        )

    try:
        # Set meta_shacl to True to check for SHACL syntax errors
        validate(data_graph=min_rdf_graph, shacl_graph=shacl_path, debug=False, meta_shacl=True)
        return 1
    except ReportableRuntimeError as e:
        if syntax_error_msg in e.message:
            return 0
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None

def compute_average_metrics(per_file_performance: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes the average values of the metrics from all files for one experiment.
    
    :param per_file_performance: List of dictionaries with performance data for each file.
    :return: Average values of the metrics.
    """
    df = pd.DataFrame(per_file_performance)
    if "run_key" in df.columns:
        df = df.drop(columns=["run_key"])
    return {metric: round(value, 4) for metric, value in df.mean().to_dict().items()}

def compute_average_metadata(raw_outputs) -> Dict[str, Any]:
    """
    Computes the average inference time and token usage for one experiment.
    
    :param raw_outputs: List of raw output entries with metadata on each test file.
    :return: Average inference time, completion tokens, prompt tokens, and total tokens.
    """
    # Extract relevant information
    data = []
    for entry in raw_outputs:
        metadata = entry["metadata"]
        token_usage = metadata["token_usage"]
        data.append({
            "inference_time": round(metadata["inference_time"] / 1000, 2),
            "completion_tokens": token_usage["completion_tokens"],
            "prompt_tokens": token_usage["prompt_tokens"],
            "total_tokens": token_usage["total_tokens"]
        })
    
    # Average the results
    df = pd.DataFrame(data)
    averages = {metric: round(value, 4) for metric, value in df.mean().to_dict().items()}
    return averages

def append_to_overall_summary(experiment_metrics: Dict[str, Any], overall_summary_path: str):
    main_items = ["mode", "model", "valid_turtle", "valid_shacl", "graph_edit_distance", "gbert_f1", "triple_f1", "validation_f1", "inference_time", "total_tokens"]
    average_df = pd.DataFrame([{
        **{k: v for k, v in experiment_metrics.items() if k in main_items}
    }])
    if os.path.exists(overall_summary_path):
        overall_results = pd.read_csv(overall_summary_path)
        overall_results = pd.concat([overall_results, average_df], ignore_index=True)
    else:
        overall_results = average_df
    overall_results.to_csv(overall_summary_path, index=False)
    logger.info(f"Saved overall summary to {overall_summary_path}")

def evaluate_experiment(experiment_dir: str, shacl_gold_dir: str, user_profiles_dir: str, overall_summary_path: str):
    metrics_dir = os.path.join(experiment_dir, "metrics")
    os.makedirs(metrics_dir, exist_ok=True)
    
    # Load raw outputs
    raw_output_path = os.path.join(experiment_dir, "output", "raw_output.json")
    with open(raw_output_path, "r") as file:
        raw_output = json.load(file)
    
    per_file_performance = []
    for run in raw_output:
        run_key = run["run_key"]
        is_valid_turtle = run["metadata"]["valid_turtle"]
        
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
        
        # Compute compliance with SHACL syntax
        parsed_output_path = run["metadata"]["parsed_output_path"]
        syntax_compliant = shacl_syntax_compliant(parsed_output_path)
        
        # Compare generated SHACL graph with groundtruth SHACL graph
        shacl_gold_path = os.path.join(shacl_gold_dir, f"{run["metadata"]["test_file"]}.ttl")
        matcher = GraphMatcher(parsed_output_path, shacl_gold_path)
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


def main(mode: str, results_dir: str, shacl_gold_dir: str, user_profiles_dir: str):
    experiment_dir = os.path.join(results_dir, mode)
    logger.info(f"Running evaluation for {mode} experiment.")
    overall_summary_path = os.path.join(results_dir, "performance_by_experiment.csv")
    
    # For baseline, compute the metrics for each tested model
    if mode == "baseline":
        baseline_summary_metrics = []
        model_directories = [directory for directory in os.listdir(experiment_dir) if os.path.isdir(os.path.join(experiment_dir, directory))]
        for model_dir in model_directories:
            baseline_experiment_dir = os.path.join(experiment_dir, model_dir)
            experiment_metrics = evaluate_experiment(baseline_experiment_dir, shacl_gold_dir, user_profiles_dir, overall_summary_path)
            baseline_summary_metrics.append(experiment_metrics)
        return baseline_summary_metrics
    
    # For other experiments, compute the metrics directly
    experiment_metrics = evaluate_experiment(experiment_dir, shacl_gold_dir, user_profiles_dir, overall_summary_path)
    return experiment_metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute evaluation metrics for a given experiment.")
    parser.add_argument("experiment_dir", help="Directory with results for the experiment to be evaluated.")
    parser.add_argument("results_dir", help="Directory with results from all experiments.")
    parser.add_argument("shacl_gold_dir", help="Directory with groundtruth SHACL shapes.")
    parser.add_argument("user_profiles_dir", help="Directory with synthetic user profiles.")
    
    args = parser.parse_args()
    main(args)