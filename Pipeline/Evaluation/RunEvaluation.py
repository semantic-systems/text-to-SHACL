""" 
RunEvaluation.py

Compute evaluation metrics for a given experiment.
"""

import argparse
import os
import logging
import time
import pandas as pd
from pyshacl import validate
from rdflib import Graph
from pyshacl.errors import ReportableRuntimeError
from typing import Optional, List, Dict, Any
from Utils.Logger import setup_logger
from Utils.FileHandling import save_dict_to_json, load_file
from .GraphMatch import GraphMatcher


def shacl_syntax_compliant(shacl_path: str, logger: logging.Logger) -> Optional[bool]:
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

    data_graph = Graph()
    data_graph.parse(data=min_rdf_graph, format="turtle")
    shacl_graph = Graph()
    shacl_graph.parse(shacl_path, format="turtle")
    
    # Try validating a minimal RDF graph with the generated SHACL graph
    try:
        validate(data_graph=data_graph,
                 shacl_graph=shacl_graph, 
                 debug=False, 
                 meta_shacl=True)
        return 1
    except ReportableRuntimeError as e:
        # Return 0 if a SHACL syntax error is detected
        if syntax_error_msg in e.message:
            return 0
    except Exception as e:
        logger.error(f"Unexpected error in SHACL validation: {e}")
    
    return None


def compute_average_metrics(metrics_per_run: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes average performance metrics for each run.

    :param metrics_per_run: Performance metrics for each run.
    :return: Dictionary with average metrics.
    """
    df = pd.DataFrame(metrics_per_run)
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


def compute_average_metadata(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes average inference time and token usage from results.
    
    :param result: Results for each run including metadata.
    :return: Average inference time, completion tokens, prompt tokens, and total tokens.
    """
    # Extract relevant information
    data = []
    for entry in results:
        metadata = entry.get("metadata", {})
        token_usage = metadata.get("token_usage")
        
        # Skip runs without token usage or runtime information
        if token_usage is None or "runtime (sec)" not in metadata:
            continue
        
        data.append({
            "runtime (sec)": metadata["runtime (sec)"],
            "completion_tokens": token_usage["completion_tokens"],
            "prompt_tokens": token_usage["prompt_tokens"],
            "total_tokens": token_usage["total_tokens"]
        })
    
    # Average the results
    df = pd.DataFrame(data)
    avg_metadata = {metric: round(value, 4) for metric, value in df.mean().to_dict().items()}
    
    return avg_metadata


def compute_average_performance(metrics_dir: str, 
                                results: List[Dict[str,Any]],
                                metrics_per_run: List[Dict[str,Any]], 
                                model_name: str, 
                                experiment: str,
                                logger: logging.Logger) -> Dict[str, Any]:
    """
    Computes two types of average metrics across test files:
    - avg_all: Mean over all test files
    - avg_valid: Mean only over files for which valid SHACL was generated

    :param metrics_dir: Directory where metrics will be saved.
    :param results: List of dictionaries containing raw model outputs.
    :param metrics_per_run: List of dictionaries containing metrics for each run.
    :param model_name: Name of the model used in the experiment.
    :param experiment: Name of the experiment.
    :param logger: Logger instance.
    
    :return: Dictionary containing avg_all and avg_valid.
    """
    # Compute average metrics
    average_performance = {
        "experiment": experiment,
        "model": model_name,
        **compute_average_metrics(metrics_per_run),
        **compute_average_metadata(results)
    }
    
    # Save detailed experiment summary
    average_performance_path = os.path.join(metrics_dir, "average_performance.json")
    save_dict_to_json(average_performance, average_performance_path)
    logger.info(f"Saved average results to {average_performance_path}")

    return average_performance


def append_to_evaluation_summary(average_performance: Dict[str, Any], metrics_by_experiment_path: str, logger: logging.Logger):
    """
    Appends average metrics for an experiment to a summary CSV file.

    :param average_performance: Dictionary of average metrics for the experiment.
    :param metrics_by_experiment_path: Path to the CSV file storing overall summaries.
    :param logger: Logger instance.
    """
    # Select information to include in the summary
    main_items = [
        'experiment', 'model', 'valid_turtle_all', 'valid_shacl_all', 'graph_edit_distance_all',
        'gbert_f1_all', 'triple_f1_all', 'validation_f1_all', 'graph_edit_distance_valid_only',
        'gbert_f1_valid_only', 'triple_f1_valid_only', 
        'validation_f1_valid_only', 'ged_timeout_all', 'runtime (sec)'
    ]
    
    average_df = pd.DataFrame([{
        **{k: v for k, v in average_performance.items() if k in main_items}
    }])
    
    # Append to overall summary, if it exists, or create new file otherwise
    if os.path.exists(metrics_by_experiment_path):
        existing_results = pd.read_csv(metrics_by_experiment_path)
        average_df = pd.concat([existing_results, average_df], ignore_index=True)
    
    average_df.to_csv(metrics_by_experiment_path, index=False)
    logger.info(f"Saved metrics by experiment to {metrics_by_experiment_path}")


def compute_metrics_per_run(metrics_dir:str,
                            results: List[Dict[str, Any]],
                            shacl_gold_dir: str, 
                            profiles_dir: str,
                            logger: logging.Logger) -> List[Dict[str, Any]]:
    """
    Computes preformance metrics for each file in the output directory.
    
    :param metrics_dir: Directory where metrics will be saved.
    :param results: List of dictionaries containing raw model outputs.
    :param shacl_gold_dir: Directory containing groundtruth SHACL files.
    :param profiles_dir: Directory containing synthetic user profiles.
    :param logger: Logger instance.
    
    :return: Metrics for each run in a given experiment.
    """
    skipped_runs = 0
    metrics_per_run = []
    for i, result in enumerate(results):
        # If the model failed to generate a response, skip the run
        if result.get("raw_response") is None:
            skipped_runs += 1
            logger.warning(f"Run {i+1}/{len(results)}: No response, skipping.")
            continue
        
        # If the model did not output valid Turtle, set worst metrics
        if result["metadata"]["valid_turtle"] == 0:
            logger.info(f"Run {i+1}/{len(results)}: Invalid Turtle output, setting worst metrics.")
            metrics_per_run.append(
                {
                    "run_key": result["run_key"],
                    "valid_turtle": 0,
                    "valid_shacl": 0,
                    "graph_edit_distance": 1,
                    **{metric: 0 for metric in ["gbert_precision", "gbert_recall", "gbert_f1"]},
                    **{metric: 0 for metric in ["triple_accuracy", "triple_precision", "triple_recall", "triple_f1"]},
                    **{metric: 0 for metric in ["validation_accuracy", "validation_precision", "validation_recall", "validation_f1"]},
                })
            continue
        
        logger.info(f"Run {i+1}/{len(results)}: Starting evaluation.")
        
        # Check compliance with SHACL syntax
        parsed_output_path = result["metadata"]["parsed_output_path"]
        syntax_compliant = shacl_syntax_compliant(parsed_output_path, logger)
        
        # Compare generated SHACL graph with groundtruth SHACL graph
        shacl_gold_path = os.path.join(shacl_gold_dir, f"{result["metadata"]["test_benefit"]}.ttl")
        matcher = GraphMatcher(shacl_gold_path, parsed_output_path, logfile=logger.log_file)
        triple_match = matcher.compute_triple_match()
        ged = matcher.compute_ged()
        gbert = matcher.compute_gbert()
        
        # Compute validation performance only for well-formed SHACL graphs
        if syntax_compliant:
            validation_performance = matcher.compute_validation_performance(profiles_dir)
        else:
            validation_performance = {
                "validation_accuracy": 0,
                "validation_precision": 0,
                "validation_recall": 0,
                "validation_f1": 0
            }
                  
        metrics_per_run.append({
            "run_key": result["run_key"],
            "valid_turtle": result["metadata"]["valid_turtle"],
            "valid_shacl": syntax_compliant,
            "graph_edit_distance": ged,
            "ged_timeout": matcher.ged_timed_out,
            **gbert,
            **triple_match,
            **validation_performance
        })
    
    # Save per run metrics if they are not empty
    if len(metrics_per_run) > 0:
        metrics_per_run_path = os.path.join(metrics_dir, "metrics_per_run.json")
        save_dict_to_json(metrics_per_run, metrics_per_run_path)
        logger.info(f"Saved metrics per run to {metrics_per_run_path}.") 
    
    logger.info(f"Skipped {skipped_runs} runs without response.")
    return metrics_per_run

def evaluate_experiment(experiment: str, 
                        results_dir: str, 
                        shacl_gold_dir: str, 
                        profiles_dir: str) -> List[Dict[str, Any]]:
    """ 
    Orchestrates evaluation of a single experiment depending on the mode.
    
    :param experiment: Name of the experiment to evaluate.
    :param results_dir: Directory containing results from all experiments.
    :param shacl_gold_dir: Directory containing groundtruth SHACL files.
    :param profiles_dir: Directory containing synthetic user profiles.
    
    :return: List of dictionaries with average metrics for the experiment.
    """
    start_time_total = time.time()
    logger = setup_logger(__name__, f"logs/{experiment}_eval.log")
    experiment_dir = os.path.join(results_dir, experiment)

    for model_name in os.listdir(experiment_dir):
        logger.info(f"Evaluating {experiment} with model: {model_name}")
        
        output_dir = os.path.join(experiment_dir, model_name, "output")
        metrics_dir = os.path.join(experiment_dir, model_name, "metrics")
        os.makedirs(metrics_dir, exist_ok=True)
        
        results = load_file(os.path.join(output_dir, "raw_output.json"), logger, as_json=True)
        
        metrics_per_run = compute_metrics_per_run(
            metrics_dir, results, shacl_gold_dir, profiles_dir, logger
        )
        
        # If there are no valid runs, skip the average computation
        if len(metrics_per_run) > 0:
            avg_performance = compute_average_performance(
                metrics_dir, results, metrics_per_run, model_name, experiment, logger
            )
            append_to_evaluation_summary(
                avg_performance, os.path.join(results_dir, "metrics_by_experiment.csv"), logger
            )
        else:
            logger.warning(f"No valid runs found for model {model_name} in experiment {experiment}.")
    
    elapsed_seconds = time.time() - start_time_total
    logger.info(f"Evaluation completed! Runtime: {elapsed_seconds/60:.2f} minutes.")
        
       
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute evaluation metrics for a given experiment.")
    parser.add_argument("--experiment", required=True, help="Name of the experiment to evaluate.")
    parser.add_argument("--results_dir", required=True, help="Directory containing results from all experiments.")
    parser.add_argument("--shacl_gold_dir", required=True, help="Directory with groundtruth SHACL shapes.")
    parser.add_argument("--profiles_dir", required=True, help="Directory with synthetic user profiles.")
    
    args = parser.parse_args()
    evaluate_experiment(
        experiment = args.experiment_name,
        results_dir=args.results_dir,
        shacl_gold_dir=args.shacl_gold_dir,
        profiles_dir=args.profiles_dir
    )