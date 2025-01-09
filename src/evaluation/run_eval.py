""" 
run_eval.py

- Evaluate the quality of machine-generated SHACL-shapes.
"""
import os
import argparse
from eval_helpers import extract_configs_from_prompt_id, save_results_to_csv
from pyshacl import validate
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score
from typing import Dict
from graph_matching import extract_triples_from_turtle, get_triple_match, get_ged, get_gbert_score


def shacl_syntax_compliant(shacl_path: str) -> bool:
    """
    Validates a minimal graph against SHACL shapes graph to check for syntax errors.
    
    :param shacl_path: Path to SHACL shapes graph.
    :return: True if SHACL graph complies with syntax, False otherwise.
    """
    minimal_graph = """
    @prefix ex: <http://example.org/> .
    ex:Subject ex:hasProperty "object" .
    """
    try:
        conforms, _, _ = validate(
            data_graph=minimal_graph,
            shacl_graph=shacl_path,
            data_graph_format="turtle",
            shacl_graph_format="turtle",
            meta_shacl=True, # Check for syntax errors
        )
        return conforms
    # TODO: How to distinguish between syntax errors and other exceptions?
    except Exception:
        return False


def calculate_graph_metrics(generated_shacl_path: str, gold_shacl_path: str) -> Dict[str, float]:
    """
    Calculates graph similarity metrics (triple match, GED, and G-BERT score) 
    between a generated SHACL graph and a ground truth SHACL graph.
    
    :param generated_shacl_path: Path to the generated SHACL graph (Turtle format).
    :param gold_shacl_path: Path to the gold-standard SHACL graph (Turtle format).
    :return: A dictionary of computed metrics.
    """
    # Extract triples from SHACL graphs
    gen_graph = extract_triples_from_turtle(generated_shacl_path)
    gold_graph = extract_triples_from_turtle(gold_shacl_path) 
    triple_match = get_triple_match(gen_graph, gold_graph)
    ged = get_ged(gen_graph, gold_graph)
    
    # Convert triples to "sentences" (each edge is considered a sentence)
    gold_edges = [" ".join(edge) for edge in gold_graph]
    gen_edges = [" ".join(edge) for edge in gen_graph]
    g_bert_score = get_gbert_score(gen_edges, gold_edges)
    
    return {**triple_match, **ged, **g_bert_score}


def calculate_validation_performance(generated_shacl_path: str, gold_shacl_path: str, profiles_dir: str) -> Dict[str, float]:
    """
    Computs precision, recall, accuracy, and F1 score between validation
    results of a generated and a gold SHACL graph on synthetics user profiles.

    :param generated_shacl_path: Path to the generated SHACL graph.
    :param groundtruth_shacl_path: Path to the groundtruth SHACL graph.
    :param profiles_dir: Directory with synthetics user profiles.
    :return: Dictionary containing precision, recall, accuracy, and F1 score.
    """
    y_true, y_pred = [], []
    
    # For each profile, check if it conforms with the generated and groundtruth graphs
    for profile in os.listdir(profiles_dir):
        profile_path = os.path.join(profiles_dir, profile)
        try:
            conforms_with_gen, _, _ = validate(data_graph=profile_path, shacl_graph=generated_shacl_path)
            conforms_with_gold, _, _ = validate(data_graph=profile_path, shacl_graph=gold_shacl_path)
        except Exception as e:
            print(f"Error during validation of {profile_path}: {e}")
            continue
        
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
        "Validation Precision": precision,
        "Validation Recall": recall,
        "Validation Accuracy": accuracy,
        "Validation F1": f1
    }


def main(generated_shacl_dir, gold_shacl_dir, profiles_dir, results_dir):
    """
     Orchestrates the evaluation process for all generated SHACL graphs
     in a given directory.

    :param generated_shacl_dir:  Directory with generated SHACL shapes.
    :param gold_shacl_dir: Directory with groundtruth SHACL shapes.
    :param profiles_dir: Directory with syntehtics user profiles.
    :param results_dir: Directory to save results.
    
    :side effect: Creates a CSV file with per-file results and a CSV file with
    mean results for a given model and method.
    """
    os.makedirs(results_dir, exist_ok=True)
    results_per_file = []

    for file in os.listdir(generated_shacl_dir):
        method, model, benefit = extract_configs_from_prompt_id(file)
        generated_shacl_path = os.path.join(generated_shacl_dir, file)
        
        # If file is empty, model output was not parsable and all metrics
        # will be set to the worst value.
        if os.stat(generated_shacl_path).st_size == 0:
            results_per_file.append({
                "Prompt ID": os.path.splitext(file)[0],
                "Model": model,
                "Method": method,
                "Syntax Accuracy": 0,
                "Triple Precision": 0,
                "Triple Recall": 0,
                "Triple F1": 0,
                "GED": 1,
                "G-BERT F1": 0
            })
            continue
        
        gold_shacl_path = os.path.join(gold_shacl_dir, f"{benefit}.ttl")
        syntax_accuracy = 1 if shacl_syntax_compliant(generated_shacl_path) else 0
        graph_metrics = calculate_graph_metrics(generated_shacl_path, gold_shacl_path)
        validation_performance = calculate_validation_performance(generated_shacl_path, gold_shacl_path, profiles_dir)
    
        results_per_file.append({
            "Prompt ID": os.path.splitext(file)[0],
            "Model": model,
            "Method": method,
            "Syntax Accuracy": syntax_accuracy,
            **graph_metrics,
            **validation_performance,
        })

    # Save per-file results
    per_file_csv_path = os.path.join(results_dir, "per_file_results.csv")
    save_results_to_csv(results_per_file, per_file_csv_path)

    # Save mean results for a given model and method
    avg_csv_path = os.path.join(results_dir, "avg_results.csv")
    save_results_to_csv(results_per_file, avg_csv_path, mean=True)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process SHACL generation and comparison.")
    parser.add_argument("generated_shacl_dir", help="Directory with generated SHACL shapes")
    parser.add_argument("gold_shacl_dir", help="Directory with groundtruth SHACL shapes")
    parser.add_argument("profiles_dir", help="Directory with synthetic user profiles")
    parser.add_argument("results_dir", help="Directory to store results")
    args = parser.parse_args()
    
    main(args.generated_shacl_dir, args.gold_shacl_dir, args.profiles_dir, args.results_dir)